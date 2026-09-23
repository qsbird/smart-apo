#!/usr/bin/env python3
"""Offline teacher/student autotuning for Smart Apo Rev.A1 CSV logs.

This is deliberately deterministic: raw files are never modified, time blocks
are never shuffled, and a candidate is promoted only from validation metrics.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, find_peaks, sosfiltfilt

from event_metrics import event_metrics
from csv_input import load_numeric_csv


REQ_AWA = ("timestamp_us", "ax", "ay", "az", "gx", "gy", "gz", "pressure")
REQ_UW = REQ_AWA + ("tension_gf",)


def load_csv(path: Path, required: tuple[str, ...]) -> dict[str, np.ndarray]:
    columns = load_numeric_csv(path, required)
    return {name: np.asarray(values, dtype=float) for name, values in columns.items()}


def amag(d):
    return np.sqrt(d["ax"] ** 2 + d["ay"] ** 2 + d["az"] ** 2)


def marker_times(d: dict[str, np.ndarray]) -> np.ndarray:
    """Return separated impact times for the start/end triple-tap markers."""
    t = d["timestamp_us"] * 1e-6
    a = amag(d)
    dt = max(np.median(np.diff(t)), 1e-4)
    pulse = np.abs(highpass(a, 1/dt, 1.0))
    z = np.abs(robust_scale(pulse))
    peaks, props = find_peaks(z, height=8.0, distance=max(1, int(0.20 / dt)))
    if len(peaks) < 3:
        raise ValueError("fewer than three synchronization impacts detected")
    # Select up to three strongest peaks from each recording end.
    edge = max(2.0, 0.18 * (t[-1] - t[0]))
    candidates = np.r_[peaks[t[peaks] <= t[0] + edge], peaks[t[peaks] >= t[-1] - edge]]
    if len(candidates) < 3:
        candidates = peaks[np.argsort(props["peak_heights"])[-6:]]
    candidates = np.unique(candidates)
    if len(candidates) > 6:
        candidates = candidates[np.argsort(z[candidates])[-6:]]
    # Quadratic interpolation improves alignment beyond the IMU sample period.
    refined=[]
    for i in np.sort(candidates):
        if 0 < i < len(z)-1:
            den=z[i-1]-2*z[i]+z[i+1]
            frac=.5*(z[i-1]-z[i+1])/den if abs(den)>1e-12 else 0.0
            refined.append(t[i]+float(np.clip(frac,-.5,.5))*dt)
        else: refined.append(t[i])
    return np.asarray(refined)


@dataclass
class TimeMap:
    scale: float
    offset_s: float
    rms_ms: float
    marker_count: int

    def apply(self, t_s):
        return self.scale * t_s + self.offset_s


def estimate_time_map(awa, uw) -> TimeMap:
    ta, tu = marker_times(awa), marker_times(uw)
    n = min(len(ta), len(tu))
    if n < 3:
        raise ValueError("not enough paired synchronization impacts")
    # Pair in chronological order; the protocol requires the same tap sequence.
    ta, tu = ta[:n], tu[:n]
    scale, offset = np.polyfit(tu, ta, 1)
    residual = ta - (scale * tu + offset)
    return TimeMap(float(scale), float(offset), float(np.sqrt(np.mean(residual**2)) * 1000), n)


def highpass(x, fs, hz):
    sos = butter(2, hz, btype="highpass", fs=fs, output="sos")
    return sosfiltfilt(sos, x)


def robust_scale(x):
    med = np.median(x)
    return (x - med) / (1.4826 * np.median(np.abs(x - med)) + 1e-9)


def teacher_labels(tension, fs):
    hp = highpass(tension, fs, 0.7)
    z = np.abs(robust_scale(hp))
    raw = z > 6.0
    # Merge high-pass lobes belonging to one pull, then add label tolerance.
    hit=np.flatnonzero(raw)
    groups=[]
    for i in hit:
        if not groups or i-groups[-1][-1] > int(.80*fs): groups.append([i])
        else: groups[-1].append(i)
    pre, post = int(.04 * fs), int(.25 * fs)
    y = np.zeros_like(raw, dtype=bool)
    for g in groups:
        y[max(0, g[0]-pre):min(len(y), g[-1]+post+1)] = True
    return y, z


def features(awa, grid, fs):
    ta = awa["timestamp_us"] * 1e-6
    ai = np.interp(grid, ta, amag(awa))
    gi = np.interp(grid, ta, np.sqrt(awa["gx"]**2 + awa["gy"]**2 + awa["gz"]**2))
    pi = np.interp(grid, ta, awa["pressure"])
    win = max(3, int(.10 * fs))
    acc = np.sqrt(uniform_filter1d(highpass(ai, fs, .7)**2, win))
    gyro = np.sqrt(uniform_filter1d(highpass(gi, fs, .7)**2, win))
    dp = np.abs(np.gradient(highpass(pi, fs, .25), 1/fs))
    return np.c_[np.abs(robust_scale(acc)), np.abs(robust_scale(gyro)), np.abs(robust_scale(dp))]


def debounce(raw, fs, minimum_ms, hold_ms=140):
    need=max(1,int(minimum_ms*fs/1000)); hold=max(1,int(hold_ms*fs/1000))
    out=np.zeros_like(raw,dtype=bool); run=0; until=-1
    for i,v in enumerate(raw):
        run=run+1 if v else 0
        if run>=need: until=max(until,i+hold)
        if i<=until: out[i]=True
    return out


def tune(X, y, fs, slices):
    weights=((1,.5,.25),(1,1,.25),(1,.5,.5),(1,1,.5),(1,1,1))
    best=None
    for w in weights:
        score=X@np.asarray(w)
        for threshold in np.arange(3.0,10.1,.5):
            for minimum_ms in (20,40,60,80,120):
                pred=debounce(score>threshold,fs,minimum_ms)
                m=event_metrics(y[slices["validation"]],pred[slices["validation"]],
                                len(y[slices["validation"]])/fs)
                objective=m["event_f1"]-min(m["false_events_per_hour"],60)/600
                item=(objective,m,w,float(threshold),minimum_ms,pred)
                if best is None or item[0]>best[0]: best=item
    _,vm,w,threshold,minimum_ms,pred=best
    return {"weights":{"acc":w[0],"gyro":w[1],"pressure_rate":w[2]},
            "threshold":threshold,"minimum_ms":minimum_ms,"hold_ms":140}, vm, pred


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("awa",type=Path); ap.add_argument("underwater",type=Path)
    ap.add_argument("-o","--output",type=Path,default=Path("autotune_result.json"))
    args=ap.parse_args()
    awa=load_csv(args.awa,REQ_AWA); uw=load_csv(args.underwater,REQ_UW)
    tm=estimate_time_map(awa,uw)
    tu=tm.apply(uw["timestamp_us"]*1e-6)
    fs=100.0; lo=max(awa["timestamp_us"][0]*1e-6,tu[0]); hi=min(awa["timestamp_us"][-1]*1e-6,tu[-1])
    grid=np.arange(lo,hi,1/fs)
    tension=np.interp(grid,tu,uw["tension_gf"])
    y,tz=teacher_labels(tension,fs); X=features(awa,grid,fs)
    n=len(grid); slices={"train":slice(0,int(.6*n)),"validation":slice(int(.6*n),int(.8*n)),"test":slice(int(.8*n),n)}
    params,vm,pred=tune(X,y,fs,slices)
    result={"format":"smart-apo-autotune-v1","time_map":tm.__dict__,"sample_rate_hz":fs,
            "parameters":params,"validation":vm,
            "test":event_metrics(y[slices["test"]],pred[slices["test"]],len(y[slices["test"]])/fs),
            "teacher":{"method":"NAU7802 tension high-pass robust z-score","threshold_mad":6.0},
            "promotion_gate":{"requires_new_unseen_trip":True,"automatic_flash":False}}
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__ == "__main__": main()
