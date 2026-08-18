# Formal Hengsha Shoal analysis: paired inference → hierarchical GAMM → interaction/transition → HSQ2 event composite

## Frozen scientific claim

**tidal-energy forcing → current/mixing → mixing–resuspension state shift → vertical hydro-biogeochemical reorganization**

The formal analysis does not force a universal velocity threshold, a simple resuspension-driven deoxygenation pathway, or definitive causality.

## Instrument/unit interpretation

The field protocol documents RBR CTD / RBRmaestro water-quality instrumentation with optical dissolved oxygen, chlorophyll-a and CDOM/fDOM. RBR physical output is calibration-converted; the RBR oxygen channel reports concentration in µmol/L. Formal AOU/saturation calculations therefore interpret the uploaded DO values as µmol/L and use Garcia & Gordon oxygen solubility. FDOM is retained as instrument-output units because serial-specific optical calibration metadata are not carried in the workbook headers.

## 1. Formal paired station-level inference

Strict hydro-sedimentary station pairs: **HSQ1, HSQ2, HSQ4, HSQ5**.

All four stations moved in the same physical direction from small to large tide:

- current speed: median paired increase **+0.414 m/s**;
- profile-mean SSC: median geometric ratio **3.345×**;
- bottom SSC: **4.137×**;
- vertical SSC contrast: **5.573×**;
- |bottom–surface salinity|: **0.180×**, i.e. approximately **82% weaker stratification**.

Because n=4 independent station pairs, the exact two-sided sign-flip/Wilcoxon p-value is **0.125** even when all four stations are concordant. Hourly profiles are treated as repeated observations, not independent spatial replicates.

Paired water-quality profiles are available for three stations (HSQ1, HSQ2, HSQ4). FDOM bottom–surface changed by a station-median **+4.192 instrument-output units** and Chl-a by **+40.924 µg/L** (both spatially concordant; exact p=0.25). AOU is not concordant (p=0.75), so oxygen depletion is not the main endpoint.

## 2. Hierarchical GAMM

Penalized B-spline GAMM-like models include nested ridge-penalized station and station×tide random intercepts, with smoothing/variance penalties selected by GCV.

**SSC model:** n=155 station-hour profiles; marginal R²=**0.416**, conditional R²=**0.684**.

**Stratification model:** n=155; marginal R²=**0.513**, conditional R²=**0.589**.

At a common current speed near 0.60 m/s, fitted large-tide profile-mean SSC remains approximately **2.36×** the small-tide prediction, whereas fitted large-tide stratification is only approximately **0.181×** the small-tide prediction. Thus instantaneous current speed alone does not collapse the spring–neap state dependence.

## 3. Interaction and transition range

Segmented regressions yield nominal current-speed breakpoints around 0.31 m/s (SSC) and 0.47 m/s (stratification), but station-block bootstrap 95% ranges are broad (~0.21–0.73 m/s) and hinge terms are not significant. **No stable universal velocity threshold is supported.** Use *transition range* or *state dependence* instead.

For HSQ1/2/4 (n=114 hourly profiles, 6 station×tide campaigns), station/tide-adjusted cluster-robust interactions are:

- stratification × SSC → FDOM vertical gradient: β=**-1.392**, 95% CI **[-2.320, -0.465]**, p=**0.0033**, R²=**0.585**;
- stratification × SSC → Chl-a gradient: β=-6.230, p=0.049 (supportive/borderline because only 6 campaign clusters);
- stratification × SSC → AOU gradient: p=0.829 (unsupported).

The strongest hydro-biogeochemical bridge is therefore **FDOM vertical organization**, not simple deoxygenation.

## 4. HSQ2 event composite

Events are defined from hydrodynamic forcing only: upward crossing of current-speed P75=0.820 m/s after a lower-energy preceding hour, acceleration ≥0.2 m/s, and ≥4 h event separation. SSC is not used to select events.

Seventeen events are retained:

- median SSC peak timing = **+1.67 h** after the hydrodynamic onset;
- IQR = **+0.83 to +2.00 h**;
- **76.5%** of SSC peaks occur within 0–2 h;
- median SSC peak = **2.99×** pre-event baseline.

Because SSC sometimes begins rising before the formal P75 crossing, the defensible wording is **near-synchronous to short-lagged sediment response during tidal acceleration**, not a universal fixed lag.

## Water Research readiness

The core physical process is large and spatially concordant, hierarchical modelling supports a state-based interpretation, FDOM provides a credible hydro-biogeochemical bridge, and HSQ2 provides process-scale temporal consistency. This is strong enough to develop a Water Research process manuscript.

The principal inferential limitation is that the present dataset contains one small-tide and one large-tide campaign per paired station. It is spatially replicated but not replicated across multiple spring–neap cycles. This must be stated explicitly; hourly rows must not be presented as independent spring–neap replicates.

A metadata issue also requires documentation before submission: the implementation plan gives the planned large-tide HSQ1–5 dates as 31 Aug–1 Sep, whereas the uploaded large-tide instrument workbooks carry 29–30 Aug timestamps. The analysis uses instrument timestamps; the field record should explain the schedule change.

## Recommended manuscript claim

> Spring–neap tidal energy reorganized the Hengsha Shoal between low-energy stratified and high-energy mixed–resuspension states. This state transition was spatially concordant across paired stations and remained evident after conditioning on instantaneous current speed. The resulting vertical hydro-biogeochemical reorganization was strongest for FDOM, whereas neither a universal velocity threshold nor a simple resuspension-driven deoxygenation response was supported.

## Versioned formal outputs

- `formal_results/paired_inference_summary.csv`
- `formal_results/hierarchical_gamm_summary.csv`
- `formal_results/interaction_tests.csv`
- `formal_results/transition_range_summary.csv`
- `formal_results/hsq2_event_timing.json`

The complete analysis package (including editable SVG/PDF Figures 2–5, figure-source data and the full Python driver) is generated by the companion formal analysis workflow.
