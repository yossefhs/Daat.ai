# -*- coding: utf-8 -*-
# Assemble chiour6_fr.srt + chiour6_fr.vtt à partir des 7 fichiers chiour6_part_N.json
# (traduits en parallèle par le workflow). Fin de chaque cue = début du suivant.

import json, glob, sys

VIDEO_END = 4507.0

cues = []
for f in sorted(glob.glob('chiour6_part_*.json'), key=lambda x: int(x.split('_')[-1].split('.')[0])):
    data = json.load(open(f, encoding='utf-8'))
    for c in data:
        cues.append((float(c['start']), c['text'].strip()))
    print(f'{f}: {len(data)} cues')

# tri par start, dédoublonnage des starts identiques (garde le premier)
cues.sort(key=lambda x: x[0])
dedup = []
for s, t in cues:
    if dedup and abs(dedup[-1][0] - s) < 0.001:
        continue
    dedup.append((s, t))
cues = dedup

def fmt(t, sep):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000: s += 1; ms = 0
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"

srt, vtt = [], ["WEBVTT", ""]
errors = 0
for i, (start, text) in enumerate(cues):
    end = cues[i+1][0] if i+1 < len(cues) else VIDEO_END
    if end <= start:
        end = start + 2.0  # garde-fou si starts trop proches
        errors += 1
    srt.append(str(i+1))
    srt.append(f"{fmt(start,',')} --> {fmt(end,',')}")
    srt.append(text)
    srt.append("")
    vtt.append(f"{fmt(start,'.')} --> {fmt(end,'.')}")
    vtt.append(text)
    vtt.append("")

open("chiour6_fr.srt", "w", encoding="utf-8").write("\n".join(srt))
open("chiour6_fr.vtt", "w", encoding="utf-8").write("\n".join(vtt))
longest = max(cues[i+1][0]-cues[i][0] for i in range(len(cues)-1)) if len(cues) > 1 else 0
print(f"OK — {len(cues)} sous-titres écrits (chiour6_fr.srt + chiour6_fr.vtt)")
print(f"garde-fous durée: {errors}, cue max: {longest:.1f}s, fin: {VIDEO_END}s")
