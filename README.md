# ER Patient Flow

**Where do waits pile up in an emergency department, and what do long waits cost?** A simulated year of ER visits, analyzed with Python.

> **All data is simulated.** No real patients, hospitals, or protected health information (PHI) are used, and nothing here comes from my work. The numbers describe my simulated dataset and are not real-world findings. I built it because I'm interested in healthcare operations and wanted to practice the kind of patient-flow analysis hospital operations teams do.

## What it does
1. `generate_data.py` creates about 20,000 fake ER visits for 2025 with arrival time, acuity level (ESI 1-5, where 1 is most urgent), age group, providers on shift, wait time, whether the patient left without being seen (LWBS), length of stay, and disposition. Arrival patterns and staffing levels are my assumptions.
2. `analysis.py` measures waits by acuity, by hour and weekday, and the link between wait time and LWBS.

## Results (from the simulated data)
- **Overall:** 20,039 visits, median wait 25 minutes, 3.7% left without being seen, median length of stay 3.2 hours for patients who were seen.
- **Waits peak midday.** For lower-acuity patients (ESI 3-5), median waits were longest for arrivals between 10am and 1pm (about 38-42 minutes), and worst on Monday around noon.
- **Long waits drive walkouts.** LWBS rose from 1.1% for waits of 30 minutes or less to 15.6% for waits of 91-120 minutes and 57.1% beyond two hours.
- **Illustration:** if lower-acuity waits for arrivals between 11am and 2pm never exceeded 60 minutes, the model estimates roughly 70% fewer walkouts in that window (about 232 down to 61 visits). This is a best-case illustration, since it assumes all long waits disappear, not a staffing recommendation.

## Limitations
The simulated waits depend on staffing and arrival assumptions I chose, so the midday pattern is built in. The value of the project is the analysis approach: segmenting by acuity, finding peak-demand windows, and connecting waits to an outcome that matters (patients leaving before care). A real analysis would use de-identified hospital data and account for patient mix, bed availability, and lab turnaround.

## Run it
```
pip install -r requirements.txt
python generate_data.py
python analysis.py
```
Charts are saved in `charts/` and the full output in `results.md`.
