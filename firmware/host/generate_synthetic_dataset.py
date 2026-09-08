#!/usr/bin/env python3
"""Generate deterministic two-device logs for pipeline smoke testing."""
from __future__ import annotations
import csv
from pathlib import Path
import numpy as np

OUT=Path(__file__).resolve().parent/"example_data"

def make(kind, fs, offset, drift_ppm):
    rng=np.random.default_rng(240905 if kind=="awa" else 240906)
    global_t=np.arange(0,120,1/fs)
    device_t=(global_t-offset)/(1+drift_ppm*1e-6)
    wave=np.sin(2*np.pi*.18*global_t)
    taps=[1.0,1.35,1.70,118.0,118.35,118.70]
    fish=[76.2,84.4,102.5,108.3]  # validation and test blocks
    impact=sum(2.8*np.exp(-((global_t-x)/.018)**2) for x in taps)
    bite=sum(1.2*np.exp(-((global_t-x)/.08)**2) for x in fish)
    ax=.025*wave+.008*rng.normal(size=len(global_t))+impact+(.55 if kind=="awa" else .25)*bite
    ay=.015*np.sin(2*np.pi*.22*global_t)+.008*rng.normal(size=len(global_t))
    az=1+.04*wave+.008*rng.normal(size=len(global_t))
    gx=.6*wave+.04*rng.normal(size=len(global_t))+8*bite
    gy=.3*wave+.04*rng.normal(size=len(global_t)); gz=.04*rng.normal(size=len(global_t))
    pressure=1013+1.8*wave+.03*rng.normal(size=len(global_t))+.18*bite
    d={"timestamp_us":device_t*1e6,"ax":ax,"ay":ay,"az":az,"gx":gx,"gy":gy,"gz":gz,"pressure":pressure}
    if kind=="underwater": d["tension_gf"]=45+5*wave+.5*rng.normal(size=len(global_t))+180*bite
    return d

def write(path,d):
    keys=list(d); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="") as f:
        w=csv.writer(f);w.writerow(keys);w.writerows(zip(*(d[k] for k in keys)))

def main():
    write(OUT/"awa.csv",make("awa",104,.120,0))
    write(OUT/"underwater.csv",make("underwater",208,-.085,22))
    print(OUT)

if __name__=="__main__": main()
