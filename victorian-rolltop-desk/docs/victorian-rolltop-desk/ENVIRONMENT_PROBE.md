# ENVIRONMENT PROBE — measured, 2026-11-26T14:43Z

Raw measurements from `scripts/probe_hardware.py` on this sandbox (Blender 4.5.3 LTS, CPU Cycles only).

```
$ blender -b --factory-startup --python scripts/probe_hardware.py -- 10
blender 4.5.3 LTS | rss_baseline_mb=224
RESULT {"subdiv_level": 10, "evaluated_faces": 4194304, "evaluated_tris": 8388608, "eval_seconds": 1.3, "peak_rss_mb": 654, "mesh_bytes_per_tri": 81.8}

$ ... -- 11
blender 4.5.3 LTS | rss_baseline_mb=226
```

Kernel message for the failed level:

```
[  294.958653] Out of memory: Killed process 2076 (blender) total-vm:3827580kB, anon-rss:1295516kB, file-rss:0kB, shmem-rss:0kB, UID:1000 pgtables:3624kB oom_score_adj:100
```
