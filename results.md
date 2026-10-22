# Results (simulated data)

Visits: 20,039 | median wait 25 min | LWBS 3.7% | median length of stay (seen patients) 3.2 hr

By acuity:
```
           visits  median_wait  lwbs_pct
esi_level                               
1             212          1.0       0.0
2            2357         11.0       0.0
3            8098         27.0       3.2
4            6922         30.0       5.3
5            2450         26.0       4.5
```
Longest median waits by arrival hour (lower acuity):
```
              median_wait  lwbs_pct
arrival_hour                       
12                   42.0       7.8
11                   40.0       8.1
10                   38.0       7.9
```
LWBS % by wait bucket (lower acuity):
```
bucket
0-30       1.1
31-60      2.4
61-90      7.1
91-120    15.6
120+      57.1
```

Illustration: capping 11am-2pm lower-acuity waits at 60 min -> expected LWBS visits 232 -> 61 (73% fewer in that window)