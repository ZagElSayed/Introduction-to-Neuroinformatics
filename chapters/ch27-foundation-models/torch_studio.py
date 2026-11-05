"""Optional CPU-only tiny masked transformer experiment; not a foundation model.

Fixed schedules, no claimed results. Students must run and assess it themselves.
"""
import copy
import hashlib
import io
import json
import random
import time
from pathlib import Path
import torch
from torch import nn
from foundation_studio import (tokenize, fit_normalizer, split_audit, spectral_features,
                               logistic_fit, logistic_predict, metrics)


class TinyEncoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.project=nn.Linear(32,16)
        self.channel=nn.Embedding(2,16)
        self.position=nn.Embedding(16,16)
        self.mask_token=nn.Parameter(torch.zeros(16))
        layer=nn.TransformerEncoderLayer(d_model=16,nhead=2,dim_feedforward=32,
                                        dropout=0.0,batch_first=True)
        self.transformer=nn.TransformerEncoder(layer,num_layers=1,enable_nested_tensor=False)
        self.decoder=nn.Linear(16,32)
        self.head=nn.Linear(16,1)
        self.register_buffer("channel_ids",torch.tensor([0]*16+[1]*16))
        self.register_buffer("patch_ids",torch.tensor(list(range(16))*2))

    def contextualize(self,x,valid,masked=None):
        z=self.project(x)
        if masked is not None:
            z=torch.where(masked.unsqueeze(-1),self.mask_token.view(1,1,-1),z)
        z=z+self.channel(self.channel_ids)+self.position(self.patch_ids)
        return self.transformer(z,src_key_padding_mask=~valid)

    def forward(self,x,valid):
        z=self.contextualize(x,valid)
        pooled=(z*valid.unsqueeze(-1)).sum(1)/valid.sum(1,keepdim=True)
        return self.head(pooled).squeeze(-1)


def tensors(records,normalizer):
    rows=[tokenize(r,normalizer) for r in records]
    return (torch.tensor([r["tokens"] for r in rows],dtype=torch.float32),
            torch.tensor([r["valid"] for r in rows],dtype=torch.bool))


def fit_classifier(model,x,valid,y,steps,head_only):
    for name,p in model.named_parameters():
        p.requires_grad_(not head_only or name.startswith("head."))
    optimizer=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=.01)
    model.train()
    for _ in range(steps):
        optimizer.zero_grad()
        loss=nn.functional.binary_cross_entropy_with_logits(model(x,valid),y)
        loss.backward();optimizer.step()


def run_experiment(data,seed=2701,label_people=6,pretrain_steps=30,classifier_steps=40):
    if not isinstance(label_people,int) or not 1 <= label_people <= 12:
        raise ValueError("label_people must be 1..12")
    if pretrain_steps < 1 or classifier_steps < 1:
        raise ValueError("positive step counts required")
    random.seed(seed);torch.manual_seed(seed);torch.set_num_threads(1)
    split_counts=split_audit(data["records"])
    dev=[r for r in data["records"] if r["split"]=="development"]
    normalizer=fit_normalizer(dev)
    people=sorted({r["person_id"] for r in dev})[:label_people]
    labeled=[r for r in dev if r["person_id"] in people]
    x,valid=tensors(dev,normalizer);lx,lv=tensors(labeled,normalizer)
    ly=torch.tensor([data["labels"][r["record_id"]] for r in labeled],dtype=torch.float32)
    initial=TinyEncoder();pretrained=copy.deepcopy(initial)
    opt=torch.optim.Adam([p for n,p in pretrained.named_parameters() if not n.startswith("head.")],lr=.003)
    losses=[];start=time.perf_counter()
    for _ in range(pretrain_steps):
        # Exact 10 of 32 whole patches masked independently per development record.
        mask=torch.zeros_like(valid)
        for j in range(len(dev)):
            candidates=torch.where(valid[j])[0]
            chosen=candidates[torch.randperm(len(candidates))[:10]]
            mask[j,chosen]=True
        opt.zero_grad()
        reconstructed=pretrained.decoder(pretrained.contextualize(x,valid,mask))
        loss=((reconstructed-x)**2)[mask].mean()
        loss.backward();opt.step();losses.append(float(loss.detach()))
    pretrain_seconds=time.perf_counter()-start
    models={"random_frozen_probe":copy.deepcopy(initial),
            "masked_pretrained_probe":copy.deepcopy(pretrained),
            "supervised_from_scratch":copy.deepcopy(initial)}
    timings={}
    for name,model in models.items():
        start=time.perf_counter()
        fit_classifier(model,lx,lv,ly,classifier_steps,name!="supervised_from_scratch")
        timings[name]=time.perf_counter()-start
        model.eval()
    baseline=logistic_fit([spectral_features(r) for r in labeled],ly.tolist())
    reports={};predictions={}
    for split in ["validation","evaluation"]:
        rows=[r for r in data["records"] if r["split"]==split]
        sx,sv=tensors(rows,normalizer)
        y=[data["labels"][r["record_id"]] for r in rows]
        probabilities={"fixed_frequency_logistic":logistic_predict(baseline,[spectral_features(r) for r in rows])}
        with torch.no_grad():
            for name,model in models.items():
                probabilities[name]=torch.sigmoid(model(sx,sv)).tolist()
        reports[split]={name:metrics(y,p) for name,p in probabilities.items()}
        predictions[split]={"record_ids":[r["record_id"] for r in rows],"person_ids":[r["person_id"] for r in rows],
                            "labels":y,"probabilities":probabilities}
    report={"seed":seed,"torch":torch.__version__,"device":"cpu","split_people":split_counts,
            "torch_helper_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "label_people":people,"pretraining_record_ids":[r["record_id"] for r in dev],
            "pretrain_steps":pretrain_steps,"classifier_steps":classifier_steps,
            "pretrain_loss":losses,"pretrain_seconds":pretrain_seconds,"classifier_seconds":timings,
            "metrics":reports,"predictions":predictions,"normalizer":normalizer,
            "parameter_count":sum(p.numel() for p in initial.parameters()),
            "limitations":"toy waveform task; one seed; no uncertainty intervals; not matched total compute; no foundation/clinical claim"}
    checkpoints={name:copy.deepcopy(model.state_dict()) for name,model in models.items()}
    return report,{"models":checkpoints,"normalizer":normalizer,"baseline_weights":baseline,
                   "architecture":"TinyEncoder-v1","schema":"fixture-v1"}


def save_checkpoint(bundle,folder):
    buffer=io.BytesIO();torch.save(bundle,buffer)
    payload=buffer.getvalue();path=folder/"teaching_models.pt";path.write_bytes(payload)
    digest=hashlib.sha256(payload).hexdigest()
    receipt_path=folder/"hash_receipt.json"
    receipt=json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt[path.name]=digest
    receipt_path.write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    return {"file":path.name,"sha256":digest,
            "scope":"byte comparison only; load only trusted artifacts"}
