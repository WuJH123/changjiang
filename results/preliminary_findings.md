# Hengsha Shoal monitoring-data audit and preliminary process analysis

## 1. What was actually found in the uploaded archive

- 14 Excel workbooks were parsed.
- The monitoring station IDs present in the workbooks are: HSQ1, HSQ2, HSQ3, HSQ4, HSQ5, HSQ7, HSQ8, HSQ9, HSQ10, HSQ11.
- Although filenames use the range `HSQ1-HSQ11`, **HSQ6 is absent as a station ID in the supplied workbooks**. The user-provided coordinate table likewise lists 10 stations rather than 11 unique IDs.
- Coverage is strongly nested rather than uniform across stations.
- Current velocity is available at the broadest network scale; salinity/temperature/SSC cover an intermediate subset; DO/Chl-a/FDOM cover a smaller biogeochemical subset; pH is limited mainly to HSQ2/HSQ7.
- HSQ2 additionally has high-frequency bottom-mounted SSC/salinity and velocity/direction observations, plus LISST particle-size products, making it the strongest process-validation station.

## 2. Scientific analysis hierarchy recommended by the actual data

1. **Network hydrodynamic layer:** use current velocity + external tide to define recurrent physical states.
2. **Hydro-sedimentary layer:** quantify salinity stratification and SSC/resuspension across the stations where these profiles coexist.
3. **Biogeochemical response subset:** test whether DO/FDOM/Chl-a vertical structure changes with stratification/resuspension only where simultaneous measurements exist.
4. **HSQ2 process-intensive validation:** use 5–10 min bottom observations and LISST to test event timing and sediment-response consistency.

This nested design is more defensible than pretending all nominal stations contain identical variables.

## 3. Preliminary relationship checks

- Current speed vs profile-mean SSC: n=205, rho=0.456, p=6.7e-12; within station+tide rho=0.286.
- Current speed vs bottom SSC: n=205, rho=0.490, p=8.3e-14; within station+tide rho=0.345.
- Salinity bottom-surface difference vs DO bottom-surface difference: n=175, rho=0.067, p=0.375; within station+tide rho=0.301.
- Salinity bottom-surface difference vs FDOM bottom-surface difference: n=191, rho=-0.784; within station+tide rho=-0.704.
- SSC vs FDOM: n=155, rho=0.639, but within station+tide rho=0.114 (not significant at p=0.158), indicating strong between-station/regime confounding.
- SSC vs DO: n=139, rho=0.380; within station+tide rho=0.186.
- HSQ2 bottom current speed vs SSC: n=3252, rho=0.385.
- HSQ2 bottom salinity vs SSC: n=3252, rho=-0.537.

These are **screening diagnostics**, not final inferential results. The within-station+tide statistic is especially important because a strong global correlation can be driven by between-station differences rather than event-scale coupling.

## 4. Strongest preliminary physical result

Across the four paired stations with both small- and large-tide hydro-sedimentary observations (HSQ1, HSQ2, HSQ4, HSQ5), the median across station medians indicates that large-tide conditions have approximately:

- 2.02× the current speed;
- 3.33× the profile-mean SSC;
- 3.89× the bottom-minus-surface SSC difference;
- only 0.139× the bottom-minus-surface salinity difference of small-tide conditions.

The strongest emerging manuscript hypothesis is therefore a **tidal-energy-controlled mixing–resuspension trade-off**: higher tidal energy strengthens resuspension while weakening salinity stratification, whereas lower-energy conditions favor stronger vertical water-mass separation and lower SSC.

## 5. Critical QC issues before a Water Research submission

1. **Station count mismatch:** the supplied workbooks and coordinate table do not show HSQ6. Manuscript language should not claim 11 fully observed stations until this is resolved.
2. **Non-uniform variable coverage:** DO, pH, Chl-a and FDOM do not cover all hydrodynamic stations. Main-text claims must use complete-case nested subsets.
3. **DO units are not documented in the DO workbook:** reported values are approximately hundreds, so they should not be labeled mg/L. AOU/oxygen-saturation calculations are intentionally disabled until the sensor unit is verified.
4. **Chl-a and FDOM units also require instrument documentation** before publication-quality absolute interpretation.
5. **Tidal phase:** Sheshan tide stage should not automatically be equated with local flood/ebb current at every station.
6. **Lag:** raw cross-correlation in a tidal system can be dominated by shared periodicity; event composites/detrended distributed-lag analysis are required before claiming a lag mechanism.
7. **Causality:** the observational campaign can support nonlinear coupling, temporal ordering and mechanistic consistency, not definitive causal attribution.

## 6. Next manuscript-grade analysis stage

Verify units and station coverage, freeze three nested analysis datasets, then use paired small/large-tide inference, hierarchical/blocked GAM or mixed models, bootstrap transition ranges, and HSQ2 event-scale process validation. Do not add more algorithms before these data-contract issues are closed.
