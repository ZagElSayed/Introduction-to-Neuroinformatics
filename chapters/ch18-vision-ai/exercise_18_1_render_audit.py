"""Synthetic waveform -> numeric PSD -> pixels -> audited vision prediction."""
import argparse
import csv
import hashlib
import io
import json
import platform
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import PIL
from PIL import Image
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import torch
from torch import nn

DEFAULT = dict(seed=18,participants=48,windows=4,samples=256,sampling_rate=128,
    segment=64,hop=32,image_size=64,db_min=-40.0,db_max=-5.0,
    signal=0.15,epochs=25,learning_rate=0.003)


def validate(c):
    if set(c)!=set(DEFAULT): raise ValueError('Use every documented config key')
    for k in ('seed','participants','windows','samples','sampling_rate','segment','hop','image_size','epochs'):
        if type(c[k]) is not int: raise ValueError(k+' must be an integer')
    if c['seed']<0 or c['participants']<24 or c['participants']%2 or c['windows']<2:
        raise ValueError('Even participants >=24, windows >=2, nonnegative seed required')
    if c['sampling_rate']!=128 or not 16<=c['segment']<=c['samples'] or not 1<=c['hop']<=c['segment'] or c['image_size']<16 or c['epochs']<1:
        raise ValueError('Invalid waveform, segment, hop, image or epoch contract')
    for k in ('db_min','db_max','signal','learning_rate'):
        if isinstance(c[k],bool) or not isinstance(c[k],(float,int)) or not np.isfinite(c[k]): raise ValueError(k+' must be finite')
    if c['db_min']>=c['db_max'] or c['signal']<0 or c['learning_rate']<=0:
        raise ValueError('Require ordered dB bounds and nonnegative signal, positive learning rate')
    return c


def generate(c):
    rng=np.random.default_rng(c['seed'])
    n,w,t=c['participants'],c['windows'],c['samples']
    labels=rng.permutation(np.tile([0,1],n//2));groups=np.repeat(np.arange(n),w);y=labels[groups]
    times=np.arange(t)/c['sampling_rate'];phase=rng.uniform(0,2*np.pi,(n*w,1))
    oscillation=(0.5+c['signal']*y[:,None])*np.sin(2*np.pi*10*times+phase)
    background=0.3*np.sin(2*np.pi*22*times+phase)+rng.normal(0,0.35,(n*w,t))
    return (background+oscillation).astype(np.float32),background.astype(np.float32),y,groups


def power_maps(x,c):
    starts=np.arange(0,x.shape[1]-c['segment']+1,c['hop'])
    tapered=np.hanning(c['segment'])
    windows=np.stack([x[:,s:s+c['segment']] for s in starts],axis=2)
    windows=windows-windows.mean(axis=1,keepdims=True)
    p=np.abs(np.fft.rfft(windows*tapered[None,:,None],axis=1))**2/(c['sampling_rate']*(tapered@tapered))
    p[:,1:-1 if c['segment']%2==0 else None,:]*=2
    return p


def render(p,c):
    # Absolute dB relative to one arbitrary-unit^2/Hz; low frequencies at bottom.
    db=10*np.log10(np.maximum(p,1e-12))
    values=np.rint(255*np.clip((db-c['db_min'])/(c['db_max']-c['db_min']),0,1)).astype(np.uint8)
    pixels=np.array(Image.fromarray(values[::-1,:]).resize((c['image_size'],c['image_size']),Image.Resampling.NEAREST))
    return pixels


def grouped_split(y,g,seed):
    ids,first=np.unique(g,return_index=True);labels=y[first]
    dev,test=train_test_split(ids,test_size=.25,stratify=labels,random_state=seed)
    train,val=train_test_split(dev,test_size=1/3,stratify=labels[dev],random_state=seed+1)
    return {k:np.flatnonzero(np.isin(g,v)) for k,v in [('train',train),('validation',val),('test',test)]}


class VisionCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net=nn.Sequential(nn.Conv2d(1,8,3,padding=1),nn.ReLU(),nn.AvgPool2d(2),
            nn.Conv2d(8,8,3,padding=1),nn.ReLU(),nn.AdaptiveAvgPool2d((4,4)),nn.Flatten(),nn.Linear(128,1))
    def forward(self,x): return self.net(x).squeeze(-1)


def infer(model,pixels):
    model.eval()
    with torch.inference_mode():
        return torch.sigmoid(model(torch.as_tensor(pixels[:,None,:,:].astype(np.float32)/255))).numpy()


def train(pixels,y,split,c):
    torch.manual_seed(c['seed']);torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    model=VisionCNN();optimizer=torch.optim.AdamW(model.parameters(),lr=c['learning_rate'],weight_decay=.001)
    xt=torch.as_tensor(pixels[split['train'],None].astype(np.float32)/255)
    yt=torch.as_tensor(y[split['train']].astype(np.float32))
    xv=torch.as_tensor(pixels[split['validation'],None].astype(np.float32)/255)
    yv=torch.as_tensor(y[split['validation']].astype(np.float32))
    loss=nn.BCEWithLogitsLoss();best=float('inf');curves=[];generator=torch.Generator().manual_seed(c['seed']+1)
    for epoch in range(1,c['epochs']+1):
        model.train();order=torch.randperm(len(xt),generator=generator)
        for batch in order.split(16):
            optimizer.zero_grad(set_to_none=True);objective=loss(model(xt[batch]),yt[batch]);objective.backward();optimizer.step()
        model.eval()
        with torch.inference_mode():
            tl=float(loss(model(xt),yt));vl=float(loss(model(xv),yv))
        curves.append(dict(epoch=epoch,train_loss=tl,validation_loss=vl))
        if vl<best:
            best,selected=vl,epoch;state={k:v.detach().clone() for k,v in model.state_dict().items()}
    model.load_state_dict(state)
    return model,state,curves,selected


def scores(y,p,g):
    ids=np.unique(g);yy=np.array([y[g==i][0] for i in ids]);pp=np.array([p[g==i].mean() for i in ids])
    return dict(accuracy=float(accuracy_score(yy,pp>=.5)),roc_auc=float(roc_auc_score(yy,pp)),brier=float(brier_score_loss(yy,pp)))


def jpeg(pixels):
    stream=io.BytesIO();Image.fromarray(pixels).save(stream,format='JPEG',quality=45)
    return np.array(Image.open(io.BytesIO(stream.getvalue())).convert('L'))


def resized(pixels):
    n=pixels.shape[0]
    return np.array(Image.fromarray(pixels).resize((n//2,n//2),Image.Resampling.BILINEAR).resize((n,n),Image.Resampling.BILINEAR))


def run(output_dir,config=None):
    c=validate(dict(DEFAULT) if config is None else config);out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    (out/'images').mkdir(exist_ok=True)
    x,background,y,g=generate(c);split=grouped_split(y,g,c['seed']);p=power_maps(x,c)
    pixels=np.stack([render(a,c) for a in p]);partition={int(i):name for name,rows in split.items() for i in rows}
    np.savez(out/'source_waveforms.npz',waveforms=x,labels=y,participants=g,sampling_rate=c['sampling_rate'])
    np.savez(out/'numeric_power_maps.npz',power=p,frequencies=np.fft.rfftfreq(c['segment'],d=1/c['sampling_rate']),
             segment_start_samples=np.arange(0,c['samples']-c['segment']+1,c['hop']))
    config_text=json.dumps(c,indent=2,sort_keys=True)+'\n';(out/'config.json').write_text(config_text)
    digest=lambda b:hashlib.sha256(b).hexdigest()
    renderer_hash=digest(config_text.encode());source_hash=digest((out/'source_waveforms.npz').read_bytes());manifest=[]
    for i,image in enumerate(pixels):
        path=out/'images'/f'window-{i:04}.png';Image.fromarray(image).save(path,compress_level=6)
        manifest.append(dict(image_id=f'window-{i:04}',path=str(path.relative_to(out)),source_path='source_waveforms.npz',source_row=i,
            participant=int(g[i]),label=int(y[i]),split=partition[i],renderer_version='chapter18-v1',config_sha256=renderer_hash,
            source_sha256=source_hash,png_sha256=digest(path.read_bytes()),decoded_pixel_sha256=digest(image.tobytes()),
            width=c['image_size'],height=c['image_size'],mode='L',frequency_origin='bottom',power_units='arbitrary-unit^2/Hz'))
    (out/'image_manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    (out/'split_manifest.json').write_text(json.dumps({k:dict(rows=v.tolist(),participants=np.unique(g[v]).tolist()) for k,v in split.items()},indent=2,sort_keys=True)+'\n')
    model,state,curves,selected=train(pixels,y,split,c);test=split['test'];reference=infer(model,pixels[test])
    frequencies=np.fft.rfftfreq(c['segment'],d=1/c['sampling_rate'])
    f=np.log10(np.maximum(p[:,(frequencies>=8)&(frequencies<=12),:].mean(axis=(1,2)),1e-12))[:,None]
    baseline=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=2000));baseline.fit(f[split['train']],y[split['train']])
    report=dict(config=c,data_kind='synthetic EEG-like waves, not measured EEG',cnn=scores(y[test],reference,g[test]),
        classical=scores(y[test],baseline.predict_proba(f[test])[:,1],g[test]),selected_epoch=selected,
        software=dict(python=platform.python_version(),numpy=np.__version__,torch=torch.__version__,Pillow=PIL.__version__,sklearn=sklearn.__version__),
        renderer=dict(db_reference='1 arbitrary-unit^2/Hz',window='symmetric Hann',detrend='segment mean',normalization='one-sided PSD',interpolation='nearest',quantization='8-bit',axes_or_text=False),robustness={})
    a,b=io.BytesIO(),io.BytesIO();Image.fromarray(pixels[test[0]]).save(a,format='PNG',compress_level=0);Image.fromarray(pixels[test[0]]).save(b,format='PNG',compress_level=9)
    decoded_a=np.array(Image.open(io.BytesIO(a.getvalue())));decoded_b=np.array(Image.open(io.BytesIO(b.getvalue())))
    report['lossless_control']=dict(file_bytes_differ=a.getvalue()!=b.getvalue(),decoded_pixels_equal=np.array_equal(decoded_a,decoded_b),
        prediction_equal=np.array_equal(infer(model,decoded_a[None]),infer(model,decoded_b[None])))
    transforms={'jpeg45':lambda a:jpeg(a),'resize_roundtrip':lambda a:resized(a),
                'gamma_1.2':lambda a:np.rint(255*(a/255)**1.2).astype(np.uint8)}
    variants={}
    prediction_rows=[dict(variant='reference',source_row=int(i),participant=int(g[i]),label=int(y[i]),probability=float(prob)) for i,prob in zip(test,reference)]
    for name,transform in transforms.items():
        altered=np.stack([transform(a) for a in pixels[test]]);prob=infer(model,altered);variants[name]=altered
        report['robustness'][name]=dict(metrics=scores(y[test],prob,g[test]),mean_abs_probability_change=float(np.abs(prob-reference).mean()),pixel_change_fraction=float((altered!=pixels[test]).mean()))
        prediction_rows.extend(dict(variant=name,source_row=int(i),participant=int(g[i]),label=int(y[i]),probability=float(v)) for i,v in zip(test,prob))
    # Direct negative control: a label-coded corner makes the target readable from style alone.
    marked=pixels[test].copy();marked[:,0:2,0:2]=y[test,None,None]*255
    guessed=(marked[:,0,0]>=128).astype(int)
    report['shortcut_control']=dict(description='deliberately embedded target label; invalid inference input',label_recoverable_from_corner=float((guessed==y[test]).mean()))
    removed=np.stack([render(a,c) for a in power_maps(background[test],c)])
    changed=infer(model,removed);report['removed_target_oscillation']=dict(metrics=scores(y[test],changed,g[test]),mean_abs_probability_change=float(np.abs(changed-reference).mean()))
    torch.save(dict(state_dict=state,config=c,selected_epoch=selected),out/'vision_checkpoint.pt')
    restored=VisionCNN();saved=torch.load(out/'vision_checkpoint.pt',weights_only=True);restored.load_state_dict(saved['state_dict'])
    assert np.array_equal(reference,infer(restored,pixels[test]))
    for name,rows in [('predictions.csv',prediction_rows),('training_curves.csv',curves)]:
        with (out/name).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    fig,axs=plt.subplots(2,3,figsize=(10,6),layout='constrained')
    views=[('Reference',pixels[test[0]]),('JPEG quality 45',variants['jpeg45'][0]),('Resize roundtrip',variants['resize_roundtrip'][0]),('Gamma 1.2',variants['gamma_1.2'][0]),('Target-coded corner',marked[0]),('10-Hz component removed',removed[0])]
    for ax,(name,image) in zip(axs.flat,views):ax.imshow(image,cmap='gray',vmin=0,vmax=255);ax.set_title(name);ax.axis('off')
    fig.suptitle('Synthetic representation audit: display only, not training panels',color='#142D4E');fig.savefig(out/'render_audit.png',dpi=180);plt.close(fig)
    (out/'model_card.md').write_text('# Synthetic vision model\n\nTeaching use only, no diagnostic or artifact-removal claim.\n'
        '\nInput is [batch,1,height,width]. Two 3x3 convolutional layers use eight feature channels; coarse 4x4 pooling preserves some frequency/time position before a linear logit head (793 parameters).\n'
        '\nFixed absolute PSD display range, one-sided Hann-periodogram maps, 8-bit grayscale and nearest resize. Model consumes only pixel arrays; filenames and manifest labels are not embedded in baseline images.\n'
        '\nParticipants are disjoint across train, validation and test. Validation loss selects the checkpoint. Metrics average window probabilities per participant. Classical baseline uses the same participants and fixed C=1.\n'
        '\nPNG compression control tests exact pixel preservation. JPEG, resizing and gamma are candidate rendering perturbations, not guaranteed scientific invariances. Target-coded corner is intentionally invalid leakage and is not used for fitting. Removing the synthetic oscillation changes the source data, not merely its style.\n'
        '\nOne split/seed supplies no clinical validation or confidence interval. No pretrained model, VLM API, saliency method, real EEG or site-held-out cohort is executed. CPU determinism is requested; versions and hardware changes can alter results. Checkpoint saves inference weights, not optimizer resume state.\n')
    report['source_code_sha256']=digest(Path(__file__).read_bytes());report['source_data_sha256']=source_hash
    report['artifact_sha256']={name:digest((out/name).read_bytes()) for name in ['config.json','image_manifest.json','split_manifest.json','numeric_power_maps.npz','vision_checkpoint.pt','predictions.csv','training_curves.csv','render_audit.png','model_card.md']}
    (out/'vision_report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--config',type=Path);parser.add_argument('--output-dir',type=Path,default=Path('outputs/ch18'))
    args=parser.parse_args();run(args.output_dir,json.loads(args.config.read_text()) if args.config else None)
