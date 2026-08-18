# Hengsha Shoal high-frequency monitoring analysis

This repository contains a reproducible first-pass audit and process-oriented analysis of the uploaded 2023 Hengsha Shoal monitoring archive.

## Scientific logic

The analysis is organized around one evidence chain:

**tidal-range forcing → hydrodynamic energy → stratification/resuspension trade-off → vertical hydro-biogeochemical structure**

The uploaded archive does **not** contain identical variables at every nominal station, so the workflow uses a nested observational design rather than forcing a false 11-station complete matrix:

1. **Network hydrodynamics:** current velocity at 10 station IDs present in the workbooks.
2. **Hydro-sedimentary profiles:** salinity, temperature and SSC at 8 stations.
3. **Biogeochemical subset:** DO at 5 stations; Chl-a/FDOM at 6 stations; pH mainly at HSQ2/HSQ7.
4. **HSQ2 process-intensive station:** 5–10 min bottom velocity, SSC/salinity and LISST particle-size products.

## Key audit findings

- 14 Excel workbooks were parsed.
- Station IDs actually present: `HSQ1, HSQ2, HSQ3, HSQ4, HSQ5, HSQ7, HSQ8, HSQ9, HSQ10, HSQ11`.
- `HSQ6` is absent from the supplied workbooks and from the supplied coordinate table, so the present dataset has **10 identifiable station IDs, not 11**.
- Most profile campaigns are concentrated on **26–30 August 2023**, not a continuous one-month network record. The HSQ2 bottom deployment extends for about 11 days; the external tide/meteorology/discharge workbook covers a longer interval.
- DO, Chl-a and FDOM workbook headers do not document units. The pipeline therefore retains them as `*_reported` and does not calculate AOU/oxygen saturation until units are verified.

## Strongest preliminary physical result

Across the four stations with paired large-/small-tide hydro-sedimentary profiles (`HSQ1`, `HSQ2`, `HSQ4`, `HSQ5`), median values across station medians show:

- large-tide current speed ≈ **2.02×** small-tide current speed;
- large-tide profile-mean SSC ≈ **3.33×** small-tide SSC;
- large-tide bottom–surface SSC difference ≈ **3.89×** small-tide difference;
- large-tide bottom–surface salinity difference ≈ **0.139×** the small-tide difference (i.e. markedly weaker stratification).

The Sheshan tidal range increases from ~1.4–1.8 m during 26–27 Aug to ~3.8 m during 29–30 Aug, independently supporting the field `小潮/大潮` labels.

This suggests the paper should prioritize a **tidal-energy-controlled mixing–resuspension trade-off** rather than treating stratification and resuspension as unrelated parallel mechanisms.

## Screening associations

These are exploratory and not final inferential statistics:

- hourly current speed vs profile-mean SSC: Spearman ρ ≈ 0.456; within station+tide ρ ≈ 0.286;
- hourly current speed vs bottom SSC: ρ ≈ 0.490; within station+tide ρ ≈ 0.345;
- salinity bottom–surface difference vs FDOM bottom–surface difference: ρ ≈ -0.784; within station+tide ρ ≈ -0.704;
- SSC vs FDOM is strong globally but weak after within-station+tide centering, indicating substantial spatial/regime confounding;
- the DO vertical response is not a simple monotonic stratification/deoxygenation signal in this preliminary pass, so an oxygen-depletion narrative should **not** be forced before unit verification and hierarchical modelling.

## Run

```bash
python src/hengsha_pipeline.py \
  --zip "/path/to/2023八月横沙.zip" \
  --out results
```

Required Python packages:

```text
numpy
scipy
matplotlib
```

The script intentionally parses `.xlsx` files using Python standard-library XML/ZIP support, avoiding dependence on workbook-specific desktop software.

## Main outputs

- `results/data_inventory.csv`
- `results/station_variable_coverage.csv`
- `results/profile_hour_metrics.csv`
- `results/regime_contrast_summary.csv`
- `results/daily_forcing_summary.csv`
- `results/preliminary_statistics.csv`
- `results/sequential_r2_common_sample.csv`
- `results/hsq2_speed_ssc_lag.csv`
- `results/preliminary_findings.md`
- `results/publication_analysis_plan.md`
- `figures/*.svg`

`profile_long.csv` and the full aligned HSQ2 high-frequency table are generated locally by the pipeline but need not be versioned to reproduce the analysis.

## Publication guardrails

- Treat the study as observational: use *coupling*, *association*, *process consistency* and *temporal ordering*, not definitive causal attribution.
- Do not claim 11 fully observed stations unless missing HSQ6 data are supplied.
- Do not claim a continuous one-month multi-station profile record from the present files.
- Do not calculate AOU/DO saturation until the DO sensor unit is verified.
- Raw cross-correlation is not sufficient evidence of lagged causality in a tidal system because shared periodicity can create phase-shifted correlations.

## Literature context

The design is aligned with recent *Water Research* work emphasizing spring–neap water-mass variability, suspended-sediment dynamics, and process-oriented/interpretable analysis rather than prediction alone, including:

- *Bi-layered spring-neap variability of water masses in estuaries and the impact of human activities*, Water Research 266 (2024), 122413.
- *Multiscale spatio-temporal variability of suspended sediment front in the Yangtze River Estuary and its ecological effects*, Water Research 279 (2025), 123349.
- *Differentiating estuarine dissolved organic matter composition by unsupervised and supervised machine learning*, Water Research 284 (2025), 123900.
- *Aquatic deoxygenation associated with resuspension of anthropogenic organic matter*, Water Research 278 (2025), 123327.
