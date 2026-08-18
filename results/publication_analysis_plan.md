# Manuscript-grade analysis plan after data audit

## Proposed evidence chain

**Tidal-range forcing -> hydrodynamic energy -> mixing/resuspension trade-off -> vertical hydro-biogeochemical structure.**

The actual data support a nested three-scale design:

1. **Network scale (10 station IDs present):** current velocity and tide.
2. **Hydro-sedimentary scale (8 stations):** current + salinity + temperature + SSC profiles.
3. **Biogeochemical scale (5–6 stations, variable dependent):** DO / FDOM / Chl-a; pH is only a focused HSQ2/HSQ7 response.
4. **Process-intensive HSQ2:** 5–10 min bottom velocity, SSC, salinity plus LISST products for event/process validation.

## Formal main hypotheses

H1. Large-tide conditions have higher current energy and SSC but weaker salinity stratification than small-tide conditions.

H2. The water-quality vertical structure is regime dependent; in particular, FDOM vertical separation should track salinity stratification if it primarily reflects water-mass mixing.

H3. Current–SSC coupling should persist after controlling for station/tide background, whereas any apparent SSC–FDOM or SSC–DO relationship must be tested for between-station confounding.

H4. At HSQ2, high-frequency data should be used to distinguish true event-scale resuspension response from shared tidal periodicity; raw cross-correlation alone is insufficient.

## Main-text analysis

- Paired large-/small-tide comparison across HSQ1, HSQ2, HSQ4, HSQ5.
- Hierarchical/blocked GAM or mixed model with station and tidal cycle as grouping structure.
- Response surfaces for current -> SSC and stratification -> FDOM/DO only where units and coverage are verified.
- Block/bootstrap uncertainty for transition ranges; do not label a visual bend a threshold without stable bootstrap support.
- HSQ2 event composites and detrended/first-difference lag analysis.

## Supplementary analyses

- Data-driven PCA/clustering as a robustness check for physics-defined regimes.
- Raw cross-correlations and wavelet diagnostics.
- Alternative ML algorithms; predictive accuracy is not the scientific endpoint.

## Claims to avoid until additional metadata are supplied

- AOU or oxygen-saturation calculations before DO units are verified.
- 11 fully observed stations (HSQ6 is absent from the supplied workbooks/table).
- One-month continuous network observations (most profile campaigns are concentrated on Aug 26–30; the HSQ2 bottom deployment extends ~11 days).
- Definitive causal attribution.
