"""Configurable synthetic waveform learning. Not EEGNet or clinical EEG."""
import argparse
import csv
import hashlib
import json
import platform
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sklearn
import torch
from torch import nn
from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, average_precision_score, brier_score_loss, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

DEFAULT = dict(seed=17, participants=48, windows=6, channels=2, samples=128,
               sampling_rate=64, epochs=30, patience=8, batch_size=32,
               learning_rate=0.003, weight_decay=0.001, augmentation_noise=0.02,
               signal=0.08, device='cpu')


def validate(config):
    if set(config) != set(DEFAULT):
        raise ValueError('Configuration must contain exactly the documented keys')
    for key in ('seed','participants','windows','channels','samples','sampling_rate','epochs','patience','batch_size'):
        if type(config[key]) is not int:
            raise ValueError(key + ' must be an integer')
    if config['seed'] < 0 or config['participants'] < 24 or config['participants'] % 2:
        raise ValueError('Use nonnegative seed and even participants >=24')
    if config['windows'] < 2 or config['channels'] != 2 or config['samples'] < 64 or config['sampling_rate'] != 64:
        raise ValueError('Use windows >=2, channels=2, samples >=64 and sampling_rate=64')
    if min(config[k] for k in ('epochs','patience','batch_size')) < 1:
        raise ValueError('Epochs, patience and batch size must be positive')
    for key in ('learning_rate','weight_decay','augmentation_noise','signal'):
        v = config[key]
        if isinstance(v, bool) or not isinstance(v, (float,int)) or not np.isfinite(v) or v < 0:
            raise ValueError(key + ' must be finite and nonnegative')
    if config['learning_rate'] == 0 or config['device'] not in ('cpu','cuda'):
        raise ValueError('Learning rate must be positive; device must be cpu or cuda')
    if config['device'] == 'cuda' and not torch.cuda.is_available():
        raise ValueError('CUDA requested but unavailable; choose cpu')
    return config


def generate(config):
    rng = np.random.default_rng(config['seed'])
    n, w, c, t = (config[k] for k in ('participants','windows','channels','samples'))
    labels = rng.permutation(np.tile([0,1], n//2))
    groups = np.repeat(np.arange(n), w)
    y = labels[groups]
    times = np.arange(t)/config['sampling_rate']
    phase = rng.uniform(0, 2*np.pi, (n*w,c,1))
    amplitude = 0.5 + config['signal']*y[:,None,None]
    identity = rng.normal(0,0.5,(n,c,1))[groups]
    x = (amplitude*np.sin(2*np.pi*8*times+phase) +
         0.3*np.sin(2*np.pi*18*times+phase) + identity +
         rng.normal(0,0.35,(n*w,c,t)))
    return x.astype(np.float32), y.astype(np.float32), groups


def partition(y, groups, seed, grouped):
    if grouped:
        units, first = np.unique(groups, return_index=True)
        labels = y[first]
    else:
        units, labels = np.arange(len(y)), y
    development, test = train_test_split(units, test_size=0.25, stratify=labels, random_state=seed)
    mapping = dict(zip(units.tolist(), labels.tolist()))
    train, validation = train_test_split(development, test_size=1/3,
        stratify=[mapping[int(i)] for i in development], random_state=seed+1)
    convert = lambda ids: np.flatnonzero(np.isin(groups, ids)) if grouped else np.sort(ids)
    return dict(train=convert(train), validation=convert(validation), test=convert(test))


def normalize_fit(x):
    return x.mean(axis=(0,2),keepdims=True), np.maximum(x.std(axis=(0,2),keepdims=True), 1e-6)


class CompactCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(nn.Conv1d(2,8,9,padding=4), nn.ReLU(),
            nn.AvgPool1d(2), nn.Conv1d(8,16,5,padding=2), nn.ReLU(), nn.AdaptiveAvgPool1d(1))
        self.head = nn.Linear(16,1)

    def forward(self, x):
        return self.head(self.features(x).squeeze(-1)).squeeze(-1)


def predict(model, x, device):
    model.eval()
    with torch.inference_mode():
        return torch.sigmoid(model(torch.as_tensor(x,device=device))).cpu().numpy()


def train_cnn(x, y, split, config):
    torch.manual_seed(config['seed'])
    if config['device'] == 'cuda':
        torch.cuda.manual_seed_all(config['seed'])
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    model = CompactCNN().to(config['device'])
    optimizer = torch.optim.AdamW(model.parameters(), lr=config['learning_rate'], weight_decay=config['weight_decay'])
    loss_function = nn.BCEWithLogitsLoss()
    xt = torch.as_tensor(x[split['train']],device=config['device'])
    yt = torch.as_tensor(y[split['train']],device=config['device'])
    xv = torch.as_tensor(x[split['validation']],device=config['device'])
    yv = torch.as_tensor(y[split['validation']],device=config['device'])
    generator = torch.Generator().manual_seed(config['seed']+2)
    curves, best, stale, checkpoint = [], float('inf'), 0, None
    start = time.perf_counter()
    for epoch in range(1,config['epochs']+1):
        model.train()
        order = torch.randperm(len(xt),generator=generator).tolist()
        for offset in range(0,len(order),config['batch_size']):
            batch = order[offset:offset+config['batch_size']]
            xb = xt[batch]
            if config['augmentation_noise']:
                xb = xb + torch.randn_like(xb)*config['augmentation_noise']
            optimizer.zero_grad(set_to_none=True)
            loss = loss_function(model(xb),yt[batch])
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.inference_mode():
            train_loss = float(loss_function(model(xt),yt))
            validation_loss = float(loss_function(model(xv),yv))
        if not np.isfinite(train_loss+validation_loss):
            raise ValueError('Nonfinite training loss')
        curves.append(dict(epoch=epoch,train_loss=train_loss,validation_loss=validation_loss))
        if validation_loss < best:
            best, stale, best_epoch = validation_loss, 0, epoch
            checkpoint = {key: value.detach().cpu().clone() for key,value in model.state_dict().items()}
        else:
            stale += 1
        if stale >= config['patience']:
            break
    model.load_state_dict(checkpoint)
    return model, checkpoint, curves, best_epoch, time.perf_counter()-start


def metrics(y, p):
    tn, fp, fn, tp = confusion_matrix(y, p>=0.5, labels=[0,1]).ravel()
    return dict(accuracy=float(accuracy_score(y,p>=0.5)),sensitivity=float(tp/(tp+fn)),
                specificity=float(tn/(tn+fp)),roc_auc=float(roc_auc_score(y,p)),
                average_precision=float(average_precision_score(y,p)),brier=float(brier_score_loss(y,p)))


def aggregate(y, p, groups):
    ids = np.unique(groups)
    return ids, np.array([y[groups==i][0] for i in ids]), np.array([p[groups==i].mean() for i in ids])


def features(x):
    # Explicit features: per-channel mean, standard deviation and 8-Hz rFFT power.
    spectrum = np.abs(np.fft.rfft(x,axis=2))**2/x.shape[2]**2
    frequencies = np.fft.rfftfreq(x.shape[2],d=1/64)
    band = spectrum[:,:,(frequencies>=7)&(frequencies<=9)].sum(axis=2)
    return np.concatenate([x.mean(axis=2),x.std(axis=2),band],axis=1)


def run(output_dir, config=None):
    config = validate(dict(DEFAULT) if config is None else config)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    x, y, groups = generate(config)
    report = dict(config=config,data_kind='synthetic EEG-like waveforms; not measured EEG',experiments={},
        software=dict(python=platform.python_version(),numpy=np.__version__,sklearn=sklearn.__version__,torch=torch.__version__),
        hardware=dict(device=config['device'],name=torch.cuda.get_device_name(0) if config['device']=='cuda' else platform.machine()))
    manifests, prediction_rows, plot_data = {}, [], {}
    for name, grouped in [('naive_rows',False),('grouped_participants',True)]:
        split = partition(y,groups,config['seed'],grouped)
        mean, scale = normalize_fit(x[split['train']])
        normalized = (x-mean)/scale
        model, checkpoint, curves, best_epoch, elapsed = train_cnn(normalized,y,split,config)
        test = split['test']
        p = predict(model, normalized[test],config['device'])
        ids, py, pp = aggregate(y[test],p,groups[test])
        overlaps = {f'{a}_{b}':len(set(groups[split[a]]) & set(groups[split[b]]))
                    for a,b in [('train','validation'),('train','test'),('validation','test')]}
        result = dict(row_metrics=metrics(y[test],p),participant_metrics=metrics(py,pp),
            participant_overlap=overlaps,best_epoch=best_epoch,epochs_run=len(curves),
            parameter_count=sum(t.numel() for t in model.parameters()),training_seconds=elapsed)
        if grouped:
            assert not any(overlaps.values())
            f = features(x)
            baseline = make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000))
            baseline.fit(f[split['train']],y[split['train']])
            bp = baseline.predict_proba(f[test])[:,1]
            _, by, bpp = aggregate(y[test],bp,groups[test])
            result['classical_participant_metrics'] = metrics(by,bpp)
            occluded = normalized[test].copy()
            occluded[:,0,:] = 0 # zero is the training-mean input after normalization
            op = predict(model,occluded,config['device'])
            result['occlusion_mean_abs_probability_change'] = float(np.abs(op-p).mean())
        torch.save(dict(state_dict=checkpoint,normalization_mean=torch.as_tensor(mean),
                        normalization_scale=torch.as_tensor(scale),config=config,best_epoch=best_epoch),out/f'{name}_checkpoint.pt')
        # Verify saved checkpoint predictions; evaluate only the selected state.
        restored = CompactCNN().to(config['device'])
        saved = torch.load(out/f'{name}_checkpoint.pt',map_location=config['device'],weights_only=True)
        restored.load_state_dict(saved['state_dict'])
        if not np.array_equal(p,predict(restored,normalized[test],config['device'])):
            raise AssertionError('Checkpoint reload changed predictions')
        with (out/f'{name}_curves.csv').open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(curves[0]));writer.writeheader();writer.writerows(curves)
        manifests[name] = {k:dict(rows=v.tolist(),participants=np.unique(groups[v]).tolist()) for k,v in split.items()}
        report['experiments'][name] = result
        prediction_rows.extend(dict(experiment=name,participant=int(g),target=int(a),probability=float(b)) for g,a,b in zip(ids,py,pp))
        plot_data[name]=(curves,py,pp,best_epoch)
    fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
    for (name,(curves,py,pp,best_epoch)),color in zip(plot_data.items(),['#D65473','#167D91']):
        axes[0].plot([c['epoch'] for c in curves],[c['train_loss'] for c in curves],color=color,label=name+' train')
        axes[0].plot([c['epoch'] for c in curves],[c['validation_loss'] for c in curves],'--',color=color,label=name+' validation')
        fraction,probability=calibration_curve(py,pp,n_bins=4)
        axes[1].plot(probability,fraction,'o-',color=color,label=name)
    axes[0].set(xlabel='Epoch',ylabel='Clean loss',title='Training and validation');axes[0].legend(fontsize=7)
    axes[1].plot([0,1],[0,1],'--',color='gray');axes[1].set(xlabel='Mean probability',ylabel='Observed fraction',title='Participant reliability');axes[1].legend(fontsize=7)
    g=report['experiments']['grouped_participants']
    axes[2].bar(['CNN','Classical'],[g['participant_metrics']['roc_auc'],g['classical_participant_metrics']['roc_auc']],color=['#7556A8','#D87C36'])
    axes[2].set(ylim=(0,1),ylabel='ROC-AUC',title='Same held-out participants')
    fig.savefig(out/'evaluation.png',dpi=180);plt.close(fig)
    (out/'config.json').write_text(json.dumps(config,indent=2,sort_keys=True)+'\n')
    (out/'split_manifest.json').write_text(json.dumps(manifests,indent=2,sort_keys=True)+'\n')
    with (out/'predictions.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(prediction_rows[0]));writer.writeheader();writer.writerows(prediction_rows)
    (out/'model_card.md').write_text('# Compact synthetic CNN\n\nTeaching use only; no clinical use or measured EEG.\n'
        '\nInput: float32 [batch,2,time], sampling rate 64 Hz, fixed channel ordering. Architecture: Conv(2,8,9), ReLU, average pool(2), Conv(8,16,5), ReLU, global mean pool, linear logit. This is not EEGNet.\n'
        '\nTrain-only per-channel normalization; noise augmentation on training batches only. Early stopping selects lowest validation BCE. Test data are used only after checkpoint selection.\n'
        '\nGrouped report uses one averaged test probability per participant. Naive partitions deliberately overlap participants. The classical baseline has fixed C=1 and uses the same grouped training/test rows.\n'
        '\nCalibration is assessed, not fitted. A single split and seed do not establish uncertainty or external validity. Occlusion is a synthetic sensitivity probe, not a neural mechanism or realistic missing-channel simulation.\n'
        '\nCPU runs request deterministic algorithms and one thread. Cross-version, cross-device and CUDA equivalence are not guaranteed; CUDA errors are surfaced rather than silently using a different device. Training time and checkpoint serialization bytes are not reproducibility invariants.\n'
        '\nFor resume training, save optimizer/scheduler/RNG state and batch order; this baseline stores inference checkpoints only. Do not load untrusted checkpoints.\n')
    report['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['data_sha256']=hashlib.sha256(x.tobytes()+y.tobytes()+groups.tobytes()).hexdigest()
    names=['config.json','split_manifest.json','predictions.csv','evaluation.png','model_card.md']
    names += [f'{n}_{suffix}' for n in manifests for suffix in ('checkpoint.pt','curves.csv')]
    report['artifact_sha256']={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in names}
    (out/'deep_report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path)
    parser.add_argument('--output-dir',type=Path,default=Path('outputs/ch17'))
    args=parser.parse_args()
    run(args.output_dir,json.loads(args.config.read_text()) if args.config else None)
