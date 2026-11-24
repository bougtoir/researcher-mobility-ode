Article type: Full Length Article

Approximate word count (main text incl. tables, excl. references): 7303

Author information removed for double-anonymised review

# Abstract

Researcher mobility is measured as stocks and net flows, but those
quantities do not say whether a research system can still reproduce its
own workforce. We build a reproducible measurement pipeline that turns
open bibliometric records into cohort career-transition rates, a
six-compartment dynamical model, and a monitoring indicator pair: the
equilibrium active pool relative to a minimum viable coauthor scale
($T/M$) and the proximity of that equilibrium to a model-implied
viability boundary. The two are linked by construction and form one
diagnostic scale, not two independent tests. Applied to an OpenAlex
AI/ML cohort (2000-2023) across 9 research macro-regions, all systems
exceed their minimum scale, but distance to the boundary is governed by
relative scale rather than size: the lowest $T/M$ is 215.76 (Anglosphere
ex-US), and the closest boundary is in Anglosphere ex-US, where
exogenous entry rate ($I_{0}$) reduced to 0.5% of its current value-a
99.5% reduction-would drive the active pool to its threshold. Dropout,
which drains every compartment, is the most elastic lever in every
macro-region. Transition rates estimated from the 2011-2016 career-start
window imply a smaller equilibrium pool than 2000-2010 rates in 1 of 9
macro-regions. Seven origin specifications never reverse a
macro-region\'s mobility direction, and six PI definitions leave the
$T$-side rankings structurally invariant while the P-side varies. The
pipeline is field-agnostic; AI/ML is the case study. The ranking is
conditional on the operational $M$, and we claim no validated predictive
power.

**Keywords:** researcher mobility; research evaluation; science of
science; minimum viable scale; compartment model; bibliometric
indicators; artificial intelligence

## Highlights

- A reproducible pipeline from bibliometric records to research-system
  viability

- Distance to the boundary follows relative scale $T/M$, not system size

- Closest boundary: Anglosphere ex-US, $I_{0}$ at 0.5% of baseline

- Dropout, which drains every career stage, is the most elastic lever
  everywhere

- Seven origin rules and six PI definitions audited in the main results

## Data and Code Availability

All bibliometric data used in this study come from OpenAlex
(https://openalex.org), an open scholarly database released under a CC0
licence; works were retrieved through the OpenAlex API for the
Artificial Intelligence subfield (subfield 1702) and publication years
2000 to 2023. The country-to-macro-region mapping with its documented
overrides, the estimated transition rates for every macro-region, and
every aggregate result table underlying the figures and numbers reported
here will be deposited in a public repository upon acceptance. The same
repository contains the Python code for cohort extraction, rate
estimation, the ODE model and its endogenous-inflow variant, the
bootstrap, the sensitivity and robustness analyses, the coupled
nine-region simulation, and the script that regenerates this manuscript,
its figures, tables and Supplementary Material. The author-level cohort
and the underlying work and authorship records are derivatives of
OpenAlex data and are not redistributed; the single reproduction command
(reproduce.sh) re-extracts them from the OpenAlex API with the scripts
provided, using the same subfield, year window and inclusion rules, and
then rebuilds all results from that extraction. OpenAlex is updated
continuously, so a fresh extraction reproduces the reported rates,
rankings and thresholds up to small snapshot differences of the kind
reported in Section 3.6. No proprietary or restricted data were used.

## Declarations

**Funding:** \[To be completed by the authors at submission.\]

**Competing interests:** \[To be completed by the authors at
submission.\]

**Author contributions:** \[To be completed by the authors at
submission.\]

**Declaration of generative AI in scientific writing:** During the
preparation of this work the authors used AI-assisted tools to draft,
code, and revise the manuscript. All claims, data, and interpretations
were reviewed and approved by the authors.

**Acknowledgments:** \[Removed for double-anonymised review\]

# 1. Introduction

Researcher mobility is a central subject of bibliometric and informetric
research \[1\]: foreign-born shares of national workforces \[2\], the
drivers of international moves \[3,4\], affiliation-based migration
tracks in large indexes \[5,6\], mobility\'s association with
productivity, impact and collaboration \[7,8,9,10,11\], the geography
and stratification of careers \[12,13\], and knowledge transfer through
mobile ties \[14\]. These measures describe redistribution among
systems, but they do not tell an evaluator whether a research system
retains the capacity to reproduce its own workforce.

The bibliometric records behind such measures also carry substantial
measurement ambiguity. Author name disambiguation splits and merges
careers \[15,16\]; authors hold several institutional and country
affiliations at once \[17\]; the operational assignment of a
researcher\'s origin to one system is a modelling choice;
authorship-order conventions determine who counts as leading a work
\[18,19\]; and the end of a researcher\'s activity is observed only
through publication absence. Each choice shifts the resulting rates, so
measurement sensitivity must be reported rather than assumed away.

At the individual level, career science has quantified persistence,
reputation and the impact of collaboration ties over a career
\[20,21,22\] and the long-run consequences of early-career events
\[23\]. What this literature generally does not do is link observed
career transitions to a community-level dynamical model: individual
rates are estimated, but they are rarely propagated into a system-level
state variable measured against an explicitly defined operational scale
benchmark. Existing mobility studies characterise researcher stocks and
flows rather than the dynamics of the research communities that produce
them.

This paper supplies that link as a reproducible bibliometric measurement
framework: career-transition rates estimated from publication histories
are propagated through a community-level compartment model, every
operational definition is stress-tested by propagating alternatives
through the same model, and the sensitivity of community-level rankings
to the chosen scale benchmark is quantified rather than concealed. The
framework is calibrated and illustrated on a cohort of 623,176 AI/ML
authors across 9 research macro-regions \[24\].

Artificial intelligence (AI) and machine learning (ML) research is an
informative case: its methods are a general-purpose technology being
embedded across science, industry and public administration \[25\], its
senior researchers are unusually mobile and its talent, compute and data
are concentrating in a small number of systems \[26,27,28,29,30\], and
governments compete for this population through visas, fellowships and
salaries \[3,31,32\].

The mechanism behind the indicators has four steps. (i)
Career-transition rates-entry ($I_{0}$), early-career moves abroad
($\alpha$), return ($\beta$), high-impact production ($h_{D}$, $h_{A}$),
promotion to independent authorship ($p_{D}$, $p_{A}$) and dropout
($d$)-determine the equilibrium domestic active pool $T$. (ii)
Recruitment exhibits a network externality: principal investigators
(PIs) train students and attract post-doctoral researchers, so inflow
rises with the PI stock \[33\], making the pool self-reinforcing. (iii)
From the field\'s observed coauthor structure we construct an
operational benchmark, the minimum viable coauthor scale $M$ (the median
number of independent last-author groups times the mean number of
coauthors per work) \[34\], against which each system\'s equilibrium
scale can be normalised. (iv) In the model, an equilibrium active pool
below $M$ classifies the system as sub-scale relative to the field\'s
observed coauthor intensity. Whether a real community that crosses such
a benchmark stops reproducing its PI stock, loses research programmes,
or fails irreversibly is an empirical question this paper does not claim
to have answered; the path-dependent intuition behind such losses is
Arthur\'s \[35\]. The research questions are: for each research system,
how far is the active pool from its minimum viable scale, which
transition governs that distance, and has the distance been shrinking?
Four propositions are derived before seeing the results: P1, distance to
the boundary is governed by $T/M$ rather than absolute $T$ (a structural
implication used diagnostically); P2, dropout is more elastic than
early-career outflow; P3, the transition closest to the defined boundary
is the one feeding the reproduction loop from outside ($I_{0}$); P4,
equilibria drift between career windows. P2-P4 are falsifiable by the
fitted model; P1 is checked for consistency.

The contribution is primarily methodological: a reproducible framework
linking bibliometrically observed career transitions to community-level
dynamical diagnostics, with explicit propagation of measurement
uncertainty and operational-definition sensitivity. Empirically, we
provide comparative estimates of career-transition rates, minimum viable
scale and proximity to a model-implied viability boundary (MVB) for the
macro-regions; the output is a recomputable monitoring diagnostic ($T/M$
and its closest-lever reading, MVB proximity). AI/ML serves as the case
study; we make no claim that the specific findings generalise to other
fields, only that the pipeline transfers. Section 2 specifies data and
measurement, Section 3 reports observed, model and sensitivity results,
Section 4 discusses implications and limitations, and Section 5
concludes.

# 2. Data and measurement

## 2.1 Data source and cohort

We extracted AI/ML works and author histories from the OpenAlex API for
subfield 1702 (Artificial Intelligence), 2000-2023 \[24\]. OpenAlex
provides open, CC0 metadata on authors, affiliations, countries,
publication dates and citations. Author histories were built by
following each author\'s sequence of works and affiliations, assigning a
country per work and an origin macro-region by the modal group of
recorded affiliations.

Authors enter the cohort if their first observed AI/ML publication is in
2000-2016 and they have at least two AI/ML works in 2000-2023; authors
with only unknown affiliations are excluded, giving 623,176 authors. An
author is active with at least one AI/ML work in 2020-2023 and has
dropped out otherwise. A hit is a top-decile AI/ML paper for its year,
observed within the first eight career years; a PI is an author whose
first last-author paper (single-authored papers count) appears in the
window \[36\]-deliberately broad proxies: a PI here is any author with
one independent last-author paper, not a tenured group leader. PIs
account for 55-71% and hit authors for 31-62% of each macro-region\'s
cohort (Table 1); the PI compartment is an operational proxy for the
population able to lead work and recruit, and $M$ in Section 2.9 counts
distinct last-author groups under the same definition, so the two are
consistent. The abroad flag is set for affiliation in a non-origin
macro-region within the first six career years. OpenAlex coverage is
incomplete for non-English venues and disambiguation is imperfect, so
absolute counts are model-implied stocks rather than a census; relative
comparisons are preserved because the same rules apply to every
macro-region. The China-centred, Continental Europe and United States
macro-regions contribute the largest author counts; a smaller cohort
with low coauthor intensity can be more resilient than a larger one,
which is why $T$ and $M$ must be compared jointly (P1).

  --------------------------------------------------------------------------------------------------------
  **Group**       **Authors**   **Works**   **Active      **Hit       **PIs**   **Mean    **Abroad
                                            2020-2023**   authors**             career    early-career**
                                                                                start**   
  --------------- ------------- ----------- ------------- ----------- --------- --------- ----------------
  Anglosphere     54017         701927      23366         32061       36149     2007.4    12564
  ex-US                                                                                   

  China-centred   163971        1556825     91523         56710       116531    2009.1    15962

  Continental     147366        1853004     63639         83782       97387     2008.0    17174
  Europe                                                                                  

  Islamic world   45983         381930      25466         18556       31215     2011.2    6363

  Japan           28681         309340      10165         9390        15905     2006.8    2695

  Other Western   3685          52066       1661          2303        2284      2007.4    1008
  (Israel)                                                                                

  Other regions   46189         383971      21030         14511       29822     2009.9    4471

  South Asia      26869         243272      16064         11657       18214     2011.5    3117

  United States   106415        1224020     45631         65018       70141     2007.4    15733
  --------------------------------------------------------------------------------------------------------

*Table 1. Descriptive statistics for the extracted AI/ML cohort by
research macro-region. Labels are operational aggregations of OpenAlex
country-affiliation patterns.*

## 2.2 Researcher identification

Each researcher is an OpenAlex author identifier, linked across works by
OpenAlex\'s own disambiguation. Author disambiguation is
imperfect-careers can be split across duplicate identifiers or merged
across namesakes-and benchmark comparisons show large method-dependent
differences \[15\]; constructing individual-level author histories at
scale requires explicit, auditable rules \[16\], which we do not
re-disambiguate beyond. We read cohort sizes and rates as comparable
operational quantities rather than exact headcounts, carrying
disambiguation uncertainty into the Section 3.7 audit.

## 2.3 Geographic attribution and origin

Each work carries the affiliation countries recorded for the author on
that work; a work with several affiliations contributes all of its
countries. An author\'s origin is an operational construct, not
birthplace or nationality: the modal research macro-region of their
affiliations over their first three observed career years (ties broken
toward the earliest year). Affiliation-based origin and mobility
assignment is the standard bibliometric approach to tracking scientific
migration \[5,6\], and the window rule used here is one specification
among several; Section 3.7 reports results under seven origin rules, so
that no conclusion rests on this single choice. Two consequences are
measured rather than assumed: multi-affiliated authors (a single
\'location\' in a year is unobserved) and authors whose origin changes
under alternative rules; \'zero direction reversals\' in Section 3.7
refers to regional aggregates, not individual trajectories.

## 2.4 Mobility transitions

From each author\'s origin and yearly affiliations we define the career
transitions the model uses: the abroad flag records affiliation in a
non-origin macro-region within the first six career years; return is
recorded when a subsequent affiliation again includes the origin
macro-region; hit and PI years are defined in Section 2.1 and 2.5; and
dropout is inferred when no further AI/ML work is observed. Affiliation
changes are a proxy for mobility: they do not observe physical moves,
remote collaboration or short visits, and a researcher can hold
affiliations in several systems at once. These limitations are
quantified in Section 3.7.

## 2.5 PI operationalisation

The baseline PI proxy follows AI/ML authorship conventions: the senior
or group-lead author is listed last or flagged corresponding, a
convention documented empirically across career stages \[18,19\].
Because the concept \'principal investigator\' has no direct
bibliometric field, we define six operationalisations and propagate each
through the full model (Section 3.7): ever-last-author (baseline),
ever-corresponding-author, at least two last-author papers, at least
eight observed career years, coauthor-network centrality in the top
decile of the author\'s macro-region, and a combined union of the three
career-stage definitions. The absolute PI share is proxy-dependent and
we report the full range; the model\'s $T$-side equilibria are
structurally invariant to the proxy because the inflow calibration
anchors total entry to observed entry (Section 2.8), so only P-side
quantities vary-an asymmetry we report rather than hide.

## 2.6 Community aggregation

The unit of analysis is the research macro-region: a set of countries
treated as one recruitment pool under the assumption that their AI/ML
researchers share funding systems, labour markets, languages and
mobility corridors closely enough for aggregate rates to be meaningful.
The initial partition follows Huntington\'s taxonomy \[37\], which
predicts the structure of global communication networks \[38\] and of
scientific mobility \[39\]; it is a documented starting heuristic, and
the groups are operational research systems, not civilisations. It was
adjusted to the size and mobility structure of AI/ML and to documented
global collaboration structure \[40\]: the United States is separated as
the dominant destination; Continental Europe is kept distinct for its
intra-European mobility and EU funding; small-count countries are merged
into Other regions. The final 9 macro-regions are: United States,
Anglosphere ex-US, Continental Europe, China-centred, Japan, South Asia,
Islamic world, Other Western (Israel), Other regions. Anglosphere ex-US
is in practice a single national system: United Kingdom of Great Britain
and Northern Ireland accounts for 45% of its 2022-2023 AI/ML works, so
its results read as those of a small, high-impact national system.
Figure 1 maps the partition and overlays the largest observed
inter-region early-career flows. The full country mapping is in
Supplementary Material.

![](media/image1.png){width="6.3in" height="3.2953849518810148in"}

*Figure 1. Research macro-regions and the largest inter-region
early-career flows, 2000-2023. Country outlines from Natural Earth
(public domain); arrow width is proportional to accumulated abroad
author-years by origin and destination; the legend gives each region\'s
equilibrium* $T/M$ *ratio.*

## 2.7 Dynamical model

Each macro-region is represented by six compartments: domestic
early-career ($D$), abroad early-career ($A$), domestic hit ($H_{D}$),
abroad hit ($H_{A}$), domestic PI ($P_{D}$) and abroad PI ($P_{A}$)
researchers. Transition rates are early-career outflow ($\alpha$),
return ($\beta$), hit generation ($h_{D}$, $h_{A}$), PI promotion
($p_{D}$, $p_{A}$) and dropout from all compartments ($d$). Figure 2
shows the structure; the equations are:

$${\frac{dD}{dt} = IP_{D}\  + \ \beta A\  - \ (\alpha\  + \ h_{D}\  + \ d)D}{\frac{dA}{dt} = \alpha D\  - \ (\beta\  + \ h_{A}\  + \ d)A}{\frac{dH_{D}}{dt} = h_{D}D\  + \ \beta H_{A}\  - \ (p_{D}\  + \ d)H_{D}}{\frac{dH_{A}}{dt} = h_{A}A\  - \ (\beta\  + \ p_{A}\  + \ d)H_{A}}{\frac{dP_{D}}{dt} = p_{D}H_{D}\  + \ \beta P_{A}\  - \ dP_{D}}{\frac{dP_{A}}{dt} = p_{A}H_{A}\  - \ (\beta\  + \ d)P_{A}}$$

![](media/image2.png){width="6.0in" height="3.0545450568678914in"}

*Figure 2. Compartment structure of the model for one research
macro-region. Solid arrows are per-year transition rates; the dashed
arrow is the endogenous recruitment feedback from the domestic PI stock;
grey arrows are dropout from every compartment. The active pool* $T$ *is
compared with the minimum viable coauthor scale* $M$*.*

Constant per-year rates and three observed career layers keep the model
estimable from OpenAlex; it is a diagnostic monitoring device, not a
demographic projection, with no claimed predictive performance.

Step (ii) of the mechanism is implemented by making entry depend on the
domestic PI stock. The linear form is $IP_{D} = I_{0} + rP_{D}$, where
$I_{0}$ is exogenous entry and $r$ is the PI reproduction rate, capped
at 0.50× the stability-critical value (the most constrained fitted
macro-region realises 0.40×). A saturating alternative,
$IP_{D} = I_{0} + \frac{rP_{D}}{1\  + \ \varepsilon \times P_{D}}$, is
used as a robustness check for P3. The cap prevents runaway growth when
observed $r$ exceeds the critical value, a common finding because
observed recruitment is bounded by the data window. Given $r$, $I_{0}$
is calibrated so that total equilibrium entry
$I_{0}\  + \ r\  \times \ P_{D}$ equals the observed annual entry of
each macro-region; the equilibrium size of the active pool is therefore
anchored to observed entry, and the PI feedback redistributes rather
than rescales it.

## 2.8 Calibration and estimation

Rates are estimated as constant per-year hazards from observed
transitions over exposure time, with a Laplace pseudocount of 1 per
outcome; because the data are right-censored, rates are lower bounds and
equilibria conservative. Steady states are solved with a trust-region
Newton method. The equilibrium $T$ is the asymptotic pool of an open
system with continuing entry and is therefore larger than the 2020-2023
active count of the closed cohort in Table 1 (by a factor of 2.5-3.1);
all claims rest on relative quantities ($T/M$, elasticities, proximity,
rankings), not on absolute $T$. Elasticities perturb each rate by 1% and
record the percentage change in $T$ (P2); historical drift (P4) compares
equilibria under rates estimated from the 2000-2010 and 2011-2016 career
windows; policy counterfactuals perturb single rates by ±10% and rank
levers by margin gain, with 200-draw author bootstrap intervals. All
counterfactuals are mechanical perturbations of fitted rates: they
identify sensitive transitions, not causal effects of programmes. An
annual layer re-estimates rates year by year and projects them to
2017-2026; it is exploratory and reported in Supplementary Material
Section S2 (Supplementary Figures S1-S3, Tables S2-S5).

## 2.9 The boundary

Step (iii) is implemented as $M\  = \ k\  \times \ c\bar{}$, where
$\overline{c}$ is the mean number of authors per work and $k$ the median
number of distinct last-author groups per recent year. When the
equilibrium active pool $T\  = \ D\  + \ H_{D}\  + \ P_{D}$ falls below
$M$, the system is classified as sub-scale relative to the field\'s
observed coauthor intensity-a model-implied, operational condition, not
a demonstrated failure. Crossing $M$ does not by itself establish that
research production stops, that the community collapses, or that any
loss is irreversible: $M$ is a benchmark built from coauthor structure,
not an empirically validated survival threshold, and it enters the model
only as a comparison target, not as part of the fitted dynamics. For the
boundary proximity measure we scale each rate until $T$ reaches $M$ and
record the critical factor and its proximity \|critical factor - 1\|.

Terminology matters for interpretation. $M$ is a defined classification
boundary-a function of observed coauthor structure, not an object inside
the ODE dynamics; the solutions do not \'feel\' $M$. Approaching it (a
falling margin) is a statement about fitted equilibria, not about time;
a model crossing is an algebraic property of a perturbed rate, not a
simulated or observed event; empirical collapse of a real system is
something the data do not contain, since no observed macro-region is
below $M$. Irreversibility enters only through the collapse rule of the
coupled scenario (Section 2.10), an assumption rather than an empirical
finding. We therefore speak throughout of a boundary, never of a point
of no return.

## 2.10 Sensitivity design and the talent-concentration scenario

Sensitivity is assessed along three axes (Sections 3.4-3.7): functional
form (linear versus saturating recruitment feedback), the value of $M$
(multipliers around the fitted $k$ and $\overline{c}$), and the
measurement layer (origin rules, mobility specifications, PI
definitions, missing-data treatment).

To examine what the mechanism implies when one research system
deliberately concentrates talent, we couple the nine fitted
single-region models through the observed inter-regional mobility matrix
(Figure 1) and simulate a stylised talent-concentration strategy:
early-career outflow from every other region rises from $\alpha$ to
$\alpha$(1 + φ), the increment is directed to the focal region,
researchers pulled this way return at $\beta$/(1 + φ), and exogenous
entry is adjusted so the coupled system reproduces the fitted
equilibria. Two rules link the scenario to the mechanism: once a
region\'s active pool falls below $M$ its PI-driven recruitment stops
permanently (Section 2.9), and hit generation is multiplied by the
effective number of macro-regions raised to a variety elasticity γ
($\gamma\  = \ 0$ is the fitted model; $\gamma\  > \ 0$ encodes the
hypothesis that a more concentrated field generates fewer independent
contributions). We run φ ∈ {0.5, 1.0, 2.0, 4.0, 8.0} for the two largest
observed host regions, report all quantities relative to a
$\varphi\  = \ 0$ baseline, and search for the smallest γ at which the
field\'s, and the focal region\'s own, hit stock falls below baseline.
Time is reported in units of the characteristic time
$\tau\  = \ 1/\overline{d}$, the mean career duration ($\tau$ ≈ 24 years
at fitted rates); the horizon is 4.2 $\tau$-about 4 researcher
generations-so the ordering of outcomes, not the calendar dates, is the
result. φ, γ, the retention and collapse rules and the horizon are
stylised assumptions (Supplementary Table S8); the transition rates,
equilibria, thresholds and host shares are fitted. The scenario is a
model-consistent projection of the mechanism, not a forecast.

# 3. Results

Results are reported in three layers that are kept distinct throughout:
observed quantities estimated directly from the cohort, model-implied
quantities computed from the fitted ODE, and sensitivity results showing
how both layers move under alternative measurement and modelling
choices.

## 3.1 Observed cohort and transition rates

The observed transition rates vary widely across macro-regions (Table 1
describes the cohort): early-career outflow $\alpha$ spans 0.016 to
0.053, the share affiliated abroad within six career years spans 0.094
to 0.274, return $\beta$ spans 0.023 to 0.069, and annual dropout $d$
spans 0.029 to 0.058. These are observed hazards with Laplace
regularisation, not model outputs; every model quantity below is
downstream of them.

## 3.2 Equilibrium pools and minimum viable scale (P1)

Table 2 reports the equilibrium domestic active pool $T$, the minimum
viable scale $M$ and the inflow parameters for the 9 macro-regions. All
exceed their threshold under the fitted model, but the ratio $T/M$
ranges from 215.76 (Anglosphere ex-US) to 404.87 (China-centred). The
China-centred, Continental Europe and United States macro-regions have
the largest absolute pools; Other Western (Israel) has both the smallest
pool and the narrowest absolute margin. Figure 3 visualises the gap
between $T$ and $M$.

  -----------------------------------------------------------------------------------------------------------------
  **Group**       $T$      $M$     **Margin**   $I_{0}$   $r$            $r$              $r$              $T/M$
                                                          **(fitted)**   **(observed)**   **(critical)**   
  --------------- -------- ------- ------------ --------- -------------- ---------------- ---------------- --------
  Anglosphere     57452    266     57185        1589      0.0616         0.0879           0.1231           215.76
  ex-US                                                                                                    

  Continental     172499   522     171977       4334      0.0573         0.0890           0.1146           330.60
  Europe                                                                                                   

  South Asia      50492    162     50330        790       0.0280         0.0868           0.0560           311.91

  Islamic world   73408    293     73116        1352      0.0367         0.0867           0.0734           250.94

  Japan           26399    90      26309        1005      0.1061         0.1061           0.2624           292.95

  Other regions   56523    194     56329        1359      0.0704         0.0911           0.1409           291.60

  Other Western   4242     18      4225         108       0.0580         0.0949           0.1161           238.05
  (Israel)                                                                                                 

  China-centred   279915   691     279223       4823      0.0375         0.0828           0.0750           404.87

  United States   120369   457     119912       3130      0.0591         0.0892           0.1181           263.11
  -----------------------------------------------------------------------------------------------------------------

*Table 2. Equilibrium domestic active pool, minimum viable coauthor
scale and endogenous inflow parameters by research macro-region.*

![](media/image3.png){width="5.8in" height="3.19in"}

*Figure 3. Equilibrium domestic active pool (*$T$*) and minimum viable
coauthor scale (*$M$*) by research macro-region.*

## 3.3 Which transitions govern the pool (P2)

Table 3 lists the three transition-rate elasticities with the largest
absolute effect on $T$ in each macro-region. Dropout ($d$) is the
largest negative lever everywhere, with elasticity from -2.79 to -2.31,
whereas the largest absolute elasticity of early-career outflow
($\alpha$) is 0.24; $|e_{d}|$ exceeds $|e_{\alpha}|$ in 9 of 9
macro-regions, as P2 predicts. The largest positive transition lever is
domestic hit generation ($h_{D}$), followed by principal-investigator
promotion ($p_{D}$). The United States macro-region shows the strongest
response to PI promotion ($p_{D}$). Attrition removes researchers from
every compartment, whereas outflow moves them to compartments from which
return and contribution remain possible.

  ---------------------------------------------------------------------------------------------
  **Group**       **1st      **1st          **2nd      **2nd          **3rd      **3rd
                  rate**     elasticity**   rate**     elasticity**   rate**     elasticity**
  --------------- ---------- -------------- ---------- -------------- ---------- --------------
  Anglosphere     $d$        -2.66          $h_{D}$    0.44           $p_{D}$    0.35
  ex-US                                                                          

  China-centred   $d$        -2.63          $h_{D}$    0.37           $p_{D}$    0.25

  Continental     $d$        -2.65          $h_{D}$    0.36           $p_{D}$    0.36
  Europe                                                                         

  Islamic world   $d$        -2.60          $h_{D}$    0.40           $p_{D}$    0.24

  Japan           $d$        -2.31          $h_{D}$    0.40           $p_{D}$    0.30

  Other Western   $d$        -2.73          $p_{D}$    0.37           $h_{D}$    0.33
  (Israel)                                                                       

  Other regions   $d$        -2.79          $h_{D}$    0.49           $p_{D}$    0.32

  South Asia      $d$        -2.52          $h_{D}$    0.35           $p_{D}$    0.21

  United States   $d$        -2.64          $h_{D}$    0.38           $p_{D}$    0.37
  ---------------------------------------------------------------------------------------------

*Table 3. Top transition-rate elasticities of the domestic active pool*
$T$ *by research macro-region.*

## 3.4 Viability-boundary proximity and endogenous recruitment (P1, P3)

Table 4 reports, for each macro-region, the single rate that reaches the
active-pool threshold with the smallest proportional change, and Figure
4 ranks macro-regions by that proximity. $I_{0}$ is the closest
viability-boundary lever for the active researcher pool in every group,
consistent with P3: the transition that feeds the reproduction loop from
outside is the binding one. The closest boundary is in Anglosphere
ex-US, where $I_{0}$ multiplied by 0.0046-that is, the rate reduced to
0.5% of its current value, a 99.5% reduction-drives the active pool to
$M$. Across macro-regions the Spearman correlation between boundary
proximity and $T/M$ is 1.00, whereas that between proximity and absolute
$T$ is 0.43. Because the $I_{0}$ lever rescales the whole equilibrium,
proximity is close to a deterministic function of $T/M$ in the linear
model: the first correlation is the consistency check P1 calls for
rather than an independent test, and the diagnostic content is that
rankings by size and by proximity diverge.

  ----------------------------------------------------------------------------
  **Group**       **Closest      **Current      **Critical     **Proximity**
                  rate**         value**        factor**       
  --------------- -------------- -------------- -------------- ---------------
  Anglosphere     $I_{0}$        1588.7         0.005          0.995
  ex-US                                                        

  Other Western   $I_{0}$        108.4          0.004          0.996
  (Israel)                                                     

  Islamic world   $I_{0}$        1352.4         0.004          0.996

  United States   $I_{0}$        3129.9         0.004          0.996

  Other regions   $I_{0}$        1358.5         0.003          0.997

  Japan           $I_{0}$        1005.2         0.003          0.997

  South Asia      $I_{0}$        790.3          0.003          0.997

  Continental     $I_{0}$        4334.3         0.003          0.997
  Europe                                                       

  China-centred   $I_{0}$        4822.7         0.002          0.998
  ----------------------------------------------------------------------------

*Table 4. Closest boundary for the active researcher pool by research
macro-region.*

![](media/image4.png){width="5.8in" height="3.2222222222222223in"}

*Figure 4. Closest viability-boundary proximity by research
macro-region. Smaller values mean a smaller proportional change in the
listed rate reaches the threshold.*

Replacing the linear recruitment feedback with a saturating one changes
the equilibrium pool by below 0.001% for every group (Table 5), and the
closest lever is unchanged in every macro-region while the rank order of
proximity has Spearman $\rho\  = \ 0.97$ between the two variants
(Supplementary Table S7). The second part of P3 is therefore supported:
the ranking of systems by fragility does not depend on the functional
form of the network externality.

  -----------------------------------------------------------------------
  **Group**         **Linear** $T$    **Saturating**    $\varepsilon$
                                      $T$               
  ----------------- ----------------- ----------------- -----------------
  Anglosphere ex-US 57452             57452             0.00001

  Continental       172499            172499            0.00000
  Europe                                                

  South Asia        50492             50492             0.00001

  Islamic world     73408             73408             0.00001

  Japan             26399             26399             0.00001

  Other regions     56523             56523             0.00001

  Other Western     4242              4242              0.00009
  (Israel)                                              

  China-centred     279915            279915            0.00000

  United States     120369            120369            0.00000
  -----------------------------------------------------------------------

*Table 5. Equilibrium* $T$ *under linear and saturating PI-driven
inflow.*

## 3.5 Historical drift in transition rates (P4)

Table 6 compares the equilibrium implied by early- (2000-2010) versus
late-window (2011-2016) rates; Figure 5 plots the change in margin. All
9 macro-regions have dual-window support. Under late-window rates the
margin shrinks in Japan and grows in Islamic world, China-centred, South
Asia, Other regions, Continental Europe, United States, Anglosphere
ex-US, Other Western (Israel). The late window\'s rates rest on less
exposure, so the comparison is a sensitivity exercise rather than a
forecast; it supports P4 in its weak form-equilibria differ across
windows, so distance to the threshold is not stationary, and where
margins shrink the mechanism implies ongoing drift.

  --------------------------------------------------------------------------------------
  **Group**       $T$         $T$        $\Delta T$   **Margin   **Margin   $\Delta$
                  **early**   **late**   **(%)**      early**    late**     **margin**
  --------------- ----------- ---------- ------------ ---------- ---------- ------------
  Anglosphere     53748       67487      25.6         53481      67221      13739.3
  ex-US                                                                     

  Continental     156777      205006     30.8         156255     204484     48228.9
  Europe                                                                    

  South Asia      20498       107308     423.5        20336      107146     86810.5

  Islamic world   34790       147020     322.6        34498      146727     112229.8

  Japan           27891       24101      -13.6        27801      24011      -3790.5

  Other regions   37346       92916      148.8        37152      92722      55570.4

  Other Western   3901        5097       30.7         3883       5080       1196.9
  (Israel)                                                                  

  China-centred   244735      350394     43.2         244043     349702     105659.0

  United States   108959      150719     38.3         108501     150262     41760.7
  --------------------------------------------------------------------------------------

*Table 6. Equilibrium active pool and safety margin under early
(2000-2010) versus late (2011-2016) transition-rate regimes.*

![](media/image5.png){width="5.8in" height="3.2222222222222223in"}

*Figure 5. Change in safety margin between early and late rate regimes;
negative means the late-window rates shrink the margin. Point estimates
only.*

## 3.6 Policy counterfactuals and uncertainty

Table 7 reports the mechanical counterfactual with the largest margin
gain per 10% lever change in each macro-region. Reducing dropout is the
dominant positive lever in every macro-region, consistent with P2. The
gain from a 10% reduction in $d$ ranges from about 495 active
researchers (Other Western (Israel)) to about 31,801 (China-centred).
Blocking early-career outflow is not the efficient response: a
researcher abroad remains in the global system and may return, whereas a
researcher who leaves research is lost to every compartment.

  ----------------------------------------------------------------------------
  **Group**       **Lever**      **Direction**   **Change (%)** **Gain per
                                                                10%**
  --------------- -------------- --------------- -------------- --------------
  Anglosphere     $d$            decrease        -10            6509
  ex-US                                                         

  Continental     $d$            decrease        -10            19429
  Europe                                                        

  South Asia      $d$            decrease        -10            5773

  Islamic world   $d$            decrease        -10            8400

  Japan           $d$            decrease        -10            2875

  Other regions   $d$            decrease        -10            6312

  Other Western   $d$            decrease        -10            495
  (Israel)                                                      

  China-centred   $d$            decrease        -10            31801

  United States   $d$            decrease        -10            13537
  ----------------------------------------------------------------------------

*Table 7. Top positive mechanical counterfactual per research
macro-region (margin gain per 10% proportional lever change).*

We also evaluated multi-lever policy packages for the three
smallest-margin groups. The package with the largest margin gain in each
group was: Other Western (Israel) (retention: +529 active researchers);
Japan (retention: +2,973 active researchers); South Asia (return plus
retention: +6,036 active researchers). These packages combine dropout
reduction with return or PI-pipeline levers, showing that the framework
can compare multi-lever interventions as well as single-rate
perturbations.

Figure 6 shows bootstrap 95% intervals for $T$ (values in Supplementary
Table S6). Intervals are wide, and for the smallest macro-regions the
lower bound lies closer to $M$, so point estimates of proximity should
be read as indicative. The lower bounds nevertheless remain above $M$
for every macro-region, which supports the qualitative conclusion that
no system is below its threshold under the fitted model.

![](media/image6.png){width="5.8in" height="3.1762685914260715in"}

*Figure 6. Bootstrap 95% confidence intervals for equilibrium* $T$ *by
research macro-region.*

Two further robustness checks address definitional choices in the
mechanism. First, the PI proxy. Re-extracting the full cohort from a
later OpenAlex snapshot (623,176 authors under the same inclusion rules;
the difference from Table 1 reflects OpenAlex updates to author and
affiliation records between the two extractions) and replacing the
baseline definition (first last-author paper) with the first
corresponding-author paper or with recurrence as last author (two or
more last-author papers) changes the share of authors classified as PIs
(mean across macro-regions 68.0%, 52.0% and 50.3% respectively), the
promotion rates $p_{D}$ and $p_{A}$, the equilibrium PI pool $P_{D}$ and
the split of recruitment between exogenous entry and PI-driven feedback.
Because $I_{0}$ is calibrated so that total equilibrium entry equals
observed entry (Section 2.8), the active pool $T$, $T/M$ and the
proximity of the entry lever are invariant to the proxy by construction;
the informative test is therefore whether the proxy-dependent quantities
reorder the macro-regions. The ordering is largely preserved: Spearman
rho with the baseline is at least 1.00 for the equilibrium PI pool and
1.00 for the proximity of the PI pool to its own threshold, the
elasticity of $T$ to $p_{D}$ rises from 0.21-0.37 under the baseline to
0.30-0.54 under the stricter proxies (Spearman rho of the elasticity
ranking with the baseline at least 0.68), and the closest lever for the
PI pool is unchanged in every macro-region (Supplementary Tables
S9-S10). Second, the threshold. Multiplying $M$ by 0.50-2.00 leaves no
macro-region below its threshold (minimum $T/M$ 107.88 at the largest
multiplier), preserves the ranking by $T/M$ and by proximity exactly
(Spearman rho = 1.00 and 1.00), keeps \|elasticity to $d$\| \>
\|elasticity to alpha\| in every macro-region at every multiplier, and
the closest lever is unchanged in every macro-region (Supplementary
Table S11). Because $M$ enters the linear model only as the target, its
level shifts distances without reordering systems under a common
multiplier; that invariance is algebraic, not evidential. Perturbing
each macro-region\'s $M$ independently over the same multiplicative
range reverses the picture: all 36 of 36 region pairs can exchange order
within their $T/M$ intervals, every macro-region can occupy every rank,
and under independent uniform perturbations the baseline minimum
(Anglosphere ex-US) is lowest in only 36% of draws (next: Other Western
(Israel) 23%, Islamic world 16%). Japan spans ranks 1-9. The closest
lever remains the exogenous entry rate at every multiplier, a structural
property of the fitted model rather than a robustness result. The $T/M$
ranking is therefore conditional on the operational $M$: it is a
monitoring diagnostic, not a determinate fragility ranking, and pinning
down $M$ empirically is part of the validation agenda.

The exploratory annual layer\'s rate-level projections reach a skill
ratio of 0.77 against a historical-mean baseline-a drift monitor, not a
forecast (Supplementary Material S2).

## 3.7 Measurement sensitivity: origin, PI definition, multi-affiliation and missingness

Origin specification. Re-estimating the cohort under 7 origin rules
leaves the qualitative results intact: with $M$ held at its baseline
value, the lowest-$T/M$ macro-region is Anglosphere ex-US under every
rule, matching Table 2 (recomputing $M$ inside each rule instead makes
Other Western (Israel) lowest, because its small pool of independent
groups shrinks its $M$-that variant conflates the origin question with
threshold construction and is flagged in the repository tables). In all
54 group-rule cells, no macro-region\'s aggregate $p_{abroad}$ crosses
the 50% direction (0 reversals); individual authors do change assigned
origin (baseline agreement 94-99.8%), so the stability is at the level
of the regional statistics the model consumes, not individual
trajectories, and is not a full validation of origin estimation.

Multi-affiliation and missingness. 8.4% of cohort authors record
affiliations in more than one macro-region in at least one year;
fractional and exclusion specifications change the outputs by at most a
few percent, so multi-affiliation is a measurement ambiguity to disclose
rather than a driver of results. Country is missing on 4.2% of cohort
authorship rows (non-random, concentrated in earlier years), 5.7% of
authors have careers left-censored at the 2000 window edge, and 28% of
observed spans are shorter than five years. The first two push the
reported rates toward underestimates of mobility; the short spans widen
the bootstrap intervals, which is one reason rankings are reported
rather than precise margins.

PI proxy. Across the 6 PI operationalisations the cohort PI share ranges
from 10% to 87%, so the absolute PI share is not robust to the proxy and
is never reported as a fact about the field. The $T$-side equilibria,
$T/M$, elasticities and boundary proximities are structurally invariant
to the PI definition because the inflow calibration fixes total entry to
observed entry (Section 2.8); this invariance is a property of the
calibration, not evidence that the PI measurement is valid. What does
vary is the P-side: the domestic-PI equilibrium $P_{D}$ relative to its
PI-scale threshold $M_{P}$ spans 30--6,010x across definitions, and the
closest P-side lever is exogenous entry rate ($I_{0}$), early-career
outflow rate ($\alpha$), return rate ($\beta$) in every definition, so
the qualitative findings survive while the absolute PI-stock numbers
move.

These sensitivity results are summarised in Supplementary Table S13;
per-rule and per-definition tables are in the public repository.

## 3.8 Worked example: Japan

Japan illustrates the mechanism in a large research system with
comparatively low $T/M$: fitted $T\  = \ 26,399$ against $M\  = \ 90$,
so $T/M\  = \ 292.95$, and the closest boundary is $I_{0}$ (a fall to
0.3% of its current level brings $T$ to $M$). Early-career outflow
($\alpha\  = \ 0.016$) and PI promotion ($p_{D}\  = \ 0.063$) are
comparatively low, return ($\beta\  = \ 0.025$) and hit generation
($h_{D}\  = \ 0.044$) moderate (Figure 7). Low leakage but a thin
promotion pipeline is the configuration P1-P2 describe: distance to the
threshold is governed by scale and attrition rather than by mobility.
Figure 8 generalises the diagnostic to all macro-regions (lower-left:
low buffer with a small required change), and the same panel applies to
any macro-region with sufficient coverage.

![](media/image7.png){width="6.0in" height="3.3094969378827646in"}

*Figure 7. Japan in the six-compartment model, with a ladder of fitted
transition rates across research macro-regions (Japan highlighted).*

![](media/image8.png){width="5.8in" height="4.511111111111111in"}

*Figure 8. Equilibrium safety ratio (*$T/M$*) versus closest
viability-boundary proximity for all research macro-regions. Japan is
shown in red.*

## 3.9 Talent concentration: short-run dominance, field-level loss

Under the coupled scenario, the dominant region\'s hosted pool and share
rise monotonically with φ while the effective number of macro-regions
falls: the strategy wins the short run it was designed for, at a direct
variety cost to the field (Figure 9). No region\'s active pool
approaches $M$ within the horizon (the collapse rule never activates),
so these outcomes do not depend on that assumption. Whether the field\'s
hit stock also falls depends on γ: it declines even at $\gamma\  = \ 0$
for the United States, and only past a moderate γ for the second-largest
host; the dominant region itself ends worse off only at a larger γ still
(γ\* = 3.9 at the strongest pull). γ is not identified by our data; the
variety loss is the robust finding.

![](media/image9.png){width="6.5in" height="4.727272528433946in"}

*Figure 9. Talent-concentration scenario with the United States as the
dominant region (fitted rates unless stated). (a) Hosted active pool vs*
$\varphi\  = \ 0$ *baseline; (b) effective number of macro-regions; (c)
field hit stock vs baseline at* $\varphi\  = \ 2.0$ *for three variety
elasticities γ; (*$d$*) smallest γ at which the field\'s, and the
dominant region\'s, hit stock falls below baseline (points on the dotted
line: not reached). Time in* $\tau$ *units (upper axis: years at fitted
rates). φ, γ stylised.*

  --------------------------------------------------------------------------------------------------------------------
  **Dominant      **Pull      **Hosted pool **Share of    **Effective   **Regions   **Field hit   **γ\*     **γ\*
  region**        intensity   at end of     hosted        number of     below** $M$ stock at end  field**   dominant
                  φ**         horizon (×    researchers   regions at                of horizon (×           region**
                              baseline)**   at end of     end of                    baseline)**             
                                            horizon (%)** horizon**                                         
  --------------- ----------- ------------- ------------- ------------- ----------- ------------- --------- ----------
  United States   0.5         1.40          21            5.1           0           1.03          not       not
                                                                                                  reached   reached

  United States   1.0         1.84          27            5.0           0           1.06          5.76      not
                                                                                                            reached

  United States   2.0         2.64          38            4.7           0           1.12          2.65      not
                                                                                                            reached

  United States   4.0         3.81          53            3.8           0           1.20          1.20      not
                                                                                                            reached

  United States   8.0         5.07          68            2.5           0           1.28          0.71      3.90

  China-centred   0.5         1.16          37            4.8           0           1.00          0 (fitted 4.59
                                                                                                  model)    

  China-centred   1.0         1.33          42            4.4           0           1.00          0 (fitted 3.76
                                                                                                  model)    

  China-centred   2.0         1.60          50            3.7           0           0.99          0 (fitted 2.79
                                                                                                  model)    

  China-centred   4.0         1.98          62            2.8           0           0.97          0 (fitted 2.04
                                                                                                  model)    

  China-centred   8.0         2.36          74            2.0           0           0.95          0 (fitted 1.61
                                                                                                  model)    
  --------------------------------------------------------------------------------------------------------------------

*Table 8. Talent-concentration outcome at end of horizon (4.2* $\tau$ *≈
100 years) vs the* $\varphi\  = \ 0$ *baseline, fitted rates
(*$\gamma\  = \ 0$*), for the two largest hosts. γ\* is the smallest
variety elasticity losing the hit-stock comparison.*

Figure 10 shows the time paths for every macro-region at the strongest
pull ($\varphi\  = \ 8.0$), one panel per γ; the ordering of outcomes,
not the calendar dates, is the result.

![](media/image10.png){width="6.5in" height="2.269841426071741in"}

*Figure 10. Regional time paths under the talent-concentration strategy
exerted by the United States at* $\varphi\  = \ 8.0$*, for three γ.
Lines: each macro-region\'s domestic active pool as a multiple of* $M$
*(log scale; dashed line* $M$*); thick line: dominant region. No region
crosses* $M$ *in any run (minimum 20.7), so the collapse rule is never
activated. Time in* $\tau$ *units (≈24 years, upper axis).*

# 4. Discussion

## 4.1 Principal findings

P1 is consistent with the results in the sense that matters for policy:
rankings by absolute $T$ and by proximity to the threshold diverge
($\rho\  = \ 0.43$), so the largest systems are not the safest; this is
a diagnostic reading rather than a test. P2 is supported in every
macro-region: dropout is more elastic than early-career outflow, and
reducing dropout is the most efficient single lever. P3 is supported:
$I_{0}$ is the closest viability-boundary lever for the active
researcher pool in every group, and the ranking is invariant to the form
of the recruitment feedback. P4 is supported in its weak form:
equilibria differ between the two career-start windows in all 9
dual-window macro-regions. Together the results move the
researcher-mobility debate from net flows to the transition rates that
govern reproduction, giving an observable monitoring variable whose
predictive value for real community failure is a separate, unvalidated
question (Section 4.7).

## 4.2 Comparison with existing informetric research

Bibliometric mobility measurement has moved from country-level
stock-and-flow accounting \[5,6\] to author-level indicators linking
mobility to productivity, impact and collaboration \[7,9,10\], return
migration \[11\] and knowledge transfer \[14\]. Career-science studies
quantify individual trajectories-persistence, reputation, tie effects
and early-career shocks \[20,21,22,23\]-but stop at the researcher. The
present framework sits downstream of that literature: it reuses the same
affiliation-based transition measurement, then propagates the rates
through a community-level compartment model, so the unit of
interpretation shifts from the mobile researcher to the research system
that must reproduce itself. The closest existing indicators are the
author-level mobility typologies of Robinson-García et al. and the
migration tracks of Moed et al.; what is added is not another mobility
typology but a dynamical state variable ($T/M$ and its closest-lever
reading) plus a quantified account of how sensitive any such
community-level ranking is to the operational definitions chosen.

The economics of science supplies the microfoundation (individuals
respond to career incentives \[36\]), and evolutionary and
innovation-systems economics supplies the threshold concepts-variety
generation and selection, lock-in through increasing returns
\[35,41,42\]-but its unit of analysis is the firm, the technology or the
sector. The AI-specific homogenisation concerns the framework connects
to are documented elsewhere \[28,43,44,45,46,47,48\], the scale of the
leading models intensifies the concentration \[27,49,50\], and
historical cases of fields that narrowed onto a dominant approach and
stagnated are documented \[51,52,53\]. Evidence that large fields slow
canonical progress and that papers become less disruptive makes the
variety question empirical rather than rhetorical \[54,55\]; diversity
aids problem solving \[56\], and internationally distributed teams
retain high impact \[57,58\].

## 4.3 Methodological contribution

For informetrics, the contribution is a measurement pipeline rather than
a single indicator. Origin assignment, mobility transitions, PI status,
community aggregation, calibration and the viability boundary are each
specified operationally and each is stress-tested in the main
results-origin under seven rules, mobility direction under each, PI
under six definitions propagated through the model, multi-affiliation
and missingness quantified. This is the level of measurement audit that
secondary-data mobility studies often leave implicit, and it is what
makes $T/M$ and boundary proximity usable as monitoring quantities. The
pipeline is field-agnostic: every step is parameterised on a subfield, a
year window and an authorship convention, and AI/ML is the case study.
We do not claim the findings generalise to other fields; we claim the
machinery does.

## 4.4 Implications for research evaluation

The indicators are designed for evaluators: $T/M$ and boundary proximity
can be recomputed with each OpenAlex release, and a declining margin
anywhere is a signal for the field. The separate closest-lever and
most-elastic-lever readings distinguish where monitoring should focus:
entry pipelines ($I_{0}$) bind first at the observed scale, while
attrition ($d$) is the most elastic. The annual layer adds year-by-year
tracking, but its direction-prediction skill is low-it is a monitor, not
a forecast. For individual universities, the PI stock is the node of the
network externality in the model: institutions that convert hit
researchers into PIs and retain them would, on the fitted mechanism,
regenerate their own inflow. The macro-regional ladder (Figure 7) could
in principle give a benchmark against which an institution\'s own
transition rates are read, but our estimates are at macro-region level
and institutional-scale validity is unvalidated until an institutional
calibration exercise is done. For early-career researchers, going abroad
is a smaller threat to a home system than net-flow accounting implies;
attrition is the larger one.

## 4.5 Policy implications

Concentrating talent is individually advantageous for the large systems
pursuing it \[27,31,32\], but each round lowers $T/M$ in the systems
that lose researchers-a model-dependent risk of reduced field-level
diversity, not an unconditional forecast (Section 3.9). No single actor
captures the benefit of the variety it preserves, so the response has to
be shared: jointly funded early-career fellowships and return grants
aimed at low-$T/M$ systems, routine monitoring of the indicator pair,
and shared compute and data infrastructure acting on $h_{D}$ and $p_{D}$
where mobility cannot or should not be steered \[35,59\]. Supplementary
Table S14 maps each model lever to candidate instruments, the principal
actor, the available evidence, unintended consequences and the model
dependence of the link; lever rankings are model-conditional (they
follow from fitted rates and thresholds, not from causal effects of
programmes), and a pull that raises one region\'s inflow lowers
another\'s. Each instrument affects a model rate; the instrument-to-rate
link is argued from the literature, not measured here.

## 4.6 Limitations

OpenAlex affiliation and country assignments are noisy, especially for
multi-affiliated authors, and coverage of non-English venues is
incomplete. The $T/M$ ranking is sensitive to the operational $M$: under
independent per-region multipliers in \[0.5, 2.0\] every region pair can
exchange order, so the ranking conditions on the chosen threshold
definition (Section 3.6). The macro-regional grouping is coarse, with
substantial within-group heterogeneity, and grouping mainland China with
Taiwan follows OpenAlex country metadata rather than any resolution of
their relationship. Geographic variety is a proxy for the cognitive and
institutional variety the mechanism concerns: that macro-regions differ
in institutions, languages and funding is documented, but that they
carry distinct research programmes is assumed, not measured.
Irreversibility is a property of the collapse rule, not an empirical
finding: a real system below $M$ could rebuild through return migration
or new entry, which the model does not represent, and crossing $M$ does
not establish that endogenous recruitment ceases or that recovery is
impossible. The model omits cross-region spillovers, firm-level mobility
and within-year dynamics; rates are constant within windows; the cohort
over-weights prolific authors; bootstrap intervals are wide. The
endogenous inflow cap (0.50) is a modelling choice whose alternatives
should be mapped. Falling below $M$ is a sufficient condition only for
classification as sub-scale, neither necessary nor sufficient for
empirical collapse; the historical comparison rests on two point
estimates. The talent-concentration scenario couples regions through
observed host shares and stylised rules, holds rates constant over a
long horizon, and treats γ as a free parameter; its results rank
strategies, not predict dates. The PI and hit proxies follow AI/ML
authorship conventions; transferring the pipeline to fields with
alphabetical or consortium authorship requires redefining them (Section
3.7). Measurement limits quantified in Section 3.7-multi-affiliation,
non-random missing country, left-censored careers, short spans-mean the
reported rates are best read as comparable lower bounds. Finally, the
propositions are tested on nine macro-regions: correlational support for
P1 is indicative, and the strongest support is for P2 and P3, which hold
system by system.

## 4.7 Future validation agenda

Three extensions would test rather than extend the framework: external
validation of the boundary against historical systems that contracted or
lost a research programme; identifying γ from disruption or novelty
measures; and applying the pipeline to a field with different authorship
conventions or a deliberately mis-specified partition. Each is
executable on open data with the released code.

# 5. Conclusion

We asked how far each AI/ML research system is from an operational
benchmark scale derived from observed coauthor structure, which career
transition governs that distance, and whether the distance is shrinking.
The answer is a reproducible measurement pipeline that turns open
bibliometric records into career-transition rates, a calibrated
compartment model, and a monitoring diagnostic pair ($T/M$ and boundary
proximity), with every measurement choice stress-tested in the main
results. All systems exceed their minimum viable coauthor scale, but
distance to the threshold is governed by relative scale and attrition
rather than by size or outflow; exogenous entry is the binding lever
everywhere at the observed scale; the proximity ranking is robust to the
form of the recruitment feedback; and rates have drifted, shrinking the
margin in Japan. For research evaluation the contribution is a
field-agnostic measurement framework; for AI/ML it locates the systems
whose margins are thin and the levers that matter.

# References

1\. Fortunato S, Bergstrom C T, Börner K, Evans J A, Helbing D,
Milojević S, et al. Science of science. Science.
2018;359(6379):eaao0185. https://doi.org/10.1126/science.aao0185

2\. Franzoni C, Scellato G, Stephan P E. Foreign-born scientists:
mobility patterns for 16 countries. Nat Biotechnol.
2012;30(12):1250-1253. https://doi.org/10.1038/nbt.2449

3\. Appelt S, van Beuzekom B, Galindo-Rueda F, de Pinho R. Which factors
influence the international mobility of research scientists? OECD
Science, Technology and Industry Working Papers 2015/02, 2015.
https://doi.org/10.1787/5js1tmrr2233-en

4\. Thorn K, Holm-Nielsen L B. International Mobility of Researchers and
Scientists: Policy Options for Turning a Drain into a Gain. UNU-WIDER
Research Paper No. 2006/83, 2006.
https://www.wider.unu.edu/publication/international-mobility-researchers-and-scientists

5\. Moed H F, Aisati M, Plume A. Studying scientific migration in
Scopus. Scientometrics. 2013;94(3):929-942.
https://doi.org/10.1007/s11192-012-0783-9

6\. Robinson-García N, Sugimoto C R, Murray D, Yegros A, Larivière V,
Costas R. The many faces of mobility: using bibliometric data to measure
the movement of scientists. J Informetr. 2019;13(1):50-63.
https://doi.org/10.1016/j.joi.2018.11.002

7\. Sugimoto C R, Robinson-García N, Murray D S, Yegros-Yegros A, Costas
R, Larivière V. Scientists have most impact when they\'re free to move.
Nature. 2017;550(7674):29-31. https://doi.org/10.1038/550029a

8\. Halevi G, Moed H F, Bar-Ilan J. Does research mobility have an
effect on productivity and impact? Int High Educ. 2016;86:5-6.
https://doi.org/10.6017/ihe.2016.86.9360

9\. Zhao Z, Bu Y, Kang L, Min C, Bian Y, Tang L, et al. An investigation
of the relationship between scientists\' mobility to/from China and
their research performance. J Informetr. 2020;14(2):101037.
https://doi.org/10.1016/j.joi.2020.101037

10\. Liu M, Hu X. Movers\' advantages: the effect of mobility on
scientists\' productivity and collaboration. J Informetr.
2022;16(3):101311. https://doi.org/10.1016/j.joi.2022.101311

11\. Jonkers K, Tijssen R. Chinese researchers returning home: impacts
of international mobility on research collaboration and performance.
Scientometrics. 2008;77(2):309-333.
https://doi.org/10.1007/s11192-007-1971-x

12\. Deville P, Wang D, Sinatra R, Song C, Blondel V D, Barabási A-L.
Career on the move: geography, stratification, and scientific impact.
Sci Rep. 2014;4:4770. https://doi.org/10.1038/srep04770

13\. Petersen A M. Multiscale impact of researcher mobility. J R Soc
Interface. 2018;15(146):20180580. https://doi.org/10.1098/rsif.2018.0580

14\. Aman V. Transfer of knowledge through international scientific
mobility: introduction of a network-based bibliometric indicator. Quant
Sci Stud. 2020;1(2):565-581. https://doi.org/10.1162/qss_a_00028

15\. Tekles A, Bornmann L. Author name disambiguation of bibliometric
data: a comparison of several unsupervised approaches. Quant Sci Stud.
2020;1(4):1510-1528. https://doi.org/10.1162/qss_a_00081

16\. D\'Angelo C A, van Eck N J. Collecting large-scale publication data
at the level of individual researchers: a practical proposal.
Scientometrics. 2020;123(2):883-907.
https://doi.org/10.1007/s11192-020-03410-y

17\. Macháček V, Srholec M, Ferreira M R, Robinson-García N, Costas R.
Researchers\' institutional mobility: bibliometric evidence on academic
inbreeding and internationalisation. Sci Public Policy.
2022;49(1):85-97. https://doi.org/10.1093/scipol/scab064

18\. Costas R, Bordons M. Do age and professional rank influence the
order of authorship in scientific publications? Some evidence from a
micro-level perspective. Scientometrics. 2011;88(1):145-161.
https://doi.org/10.1007/s11192-011-0368-z

19\. Sauermann H, Haeussler C. Authorship and contribution disclosures.
Sci Adv. 2017;3(11):e1700404. https://doi.org/10.1126/sciadv.1700404

20\. Petersen A M, Riccaboni M, Stanley H E, Pammolli F. Persistence and
uncertainty in the academic career. Proc Natl Acad Sci USA.
2012;109(14):5213-5218. https://doi.org/10.1073/pnas.1121429109

21\. Petersen A M, Fortunato S, Pan R K, Kaski K, Penner O, Rungi A, et
al. Reputation and impact in academic careers. Proc Natl Acad Sci USA.
2014;111(43):15316-15321. https://doi.org/10.1073/pnas.1323111111

22\. Petersen A M. Quantifying the impact of weak, strong, and super
ties in scientific careers. Proc Natl Acad Sci USA.
2015;112(34):E4671-E4680. https://doi.org/10.1073/pnas.1501444112

23\. Wang Y, Jones B F, Wang D. Early-career setback and future career
impact. Nat Commun. 2019;10:4331.
https://doi.org/10.1038/s41467-019-12189-3

24\. Priem J, Piwowar H, Orr R. OpenAlex: A fully-open index of
scholarly works, authors, venues, institutions, and concepts.
arXiv:2205.01833, 2022. https://doi.org/10.48550/arXiv.2205.01833

25\. Bresnahan T F, Trajtenberg M. General purpose technologies
\'Engines of growth\'? J Econom. 1995;65(1):83-108.
https://doi.org/10.1016/0304-4076(94)01598-T

26\. MacroPolo. The Global AI Talent Tracker 2.0. Paulson Institute,
2023.
https://macropolo.org/digital-projects/the-global-ai-talent-tracker/

27\. Sevilla J, Heim L, Ho A, Besiroglu T, Hobbhahn M, Villalobos P.
Compute trends across three eras of machine learning. In: 2022
International Joint Conference on Neural Networks (IJCNN). IEEE; 2022.
p. 1-8. https://doi.org/10.1109/IJCNN55064.2022.9891914

28\. Ahmed N, Wahed M. The de-democratization of AI: deep learning and
the compute divide in artificial intelligence research.
arXiv:2010.15581, 2020. https://doi.org/10.48550/arXiv.2010.15581

29\. Yuan S, Shao Z, Wei X, Tang J, Hall W, Wang Y, et al. Science
behind AI: the evolution of trend, mobility, and collaboration.
Scientometrics. 2020;124(2):993-1013.
https://doi.org/10.1007/s11192-020-03423-7

30\. AlShebli B, Memon S A, Evans J A, Rahwan T. China and the U.S.
produce more impactful AI research when collaborating together. Sci Rep.
2024;14:28576. https://doi.org/10.1038/s41598-024-79863-5

31\. Shachar A. The Race for Talent: Highly Skilled Migrants and
Competitive Immigration Regimes. NYU Law Rev. 2006;81(1):148-206.

32\. Kerr W R. Global Talent and U.S. Immigration Policy. Harvard
Business School Working Paper No. 20-107, 2020.
https://www.hbs.edu/ris/Publication%20Files/20-107_0967f1ab-1d23-4d54-b5a1-c884234d9b31.pdf

33\. Katz M L, Shapiro C. Network externalities, competition, and
compatibility. Am Econ Rev. 1985;75(3):424-440.

34\. Shaffer M L. Minimum Population Sizes for Species Conservation.
BioScience. 1981;31(2):131-134. https://doi.org/10.2307/1308256

35\. Arthur W B. Competing technologies, increasing returns, and lock-in
by historical events. Econ J. 1989;99(394):116-131.
https://doi.org/10.2307/2234208

36\. Stephan P E. The Economics of Science. J Econ Lit.
1996;34(3):1199-1235.

37\. Huntington S P. The Clash of Civilizations and the Remaking of
World Order. New York: Simon & Schuster, 1996.

38\. State B, Park P, Weber I, Macy M. The mesh of civilizations in the
global network of digital communication. PLoS ONE. 2015;10(5):e0122543.
https://doi.org/10.1371/journal.pone.0122543

39\. Chinchilla-Rodríguez Z, Miao L, Murray D, Robinson-García N, Costas
R, Sugimoto C R. A global comparison of scientific mobility and
collaboration according to national scientific capacities. Front Res
Metr Anal. 2018;3:17. https://doi.org/10.3389/frma.2018.00017

40\. Wagner C S, Park H W, Leydesdorff L. The continuing growth of
global cooperation networks in research: a conundrum for national
governments. PLoS ONE. 2015;10(7):e0131816.
https://doi.org/10.1371/journal.pone.0131816

41\. Nelson R R, Winter S G. An Evolutionary Theory of Economic Change.
Cambridge, MA: Harvard University Press, 1982.

42\. Dosi G. Technological paradigms and technological trajectories: a
suggested interpretation of the determinants and directions of technical
change. Res Policy. 1982;11(3):147-162.
https://doi.org/10.1016/0048-7333(82)90016-6

43\. Kleinberg J, Raghavan M. Algorithmic monoculture and social
welfare. Proc Natl Acad Sci USA. 2021;118(22):e2018340118.
https://doi.org/10.1073/pnas.2018340118

44\. Hooker S. The hardware lottery. Commun ACM. 2021;64(12):58-65.
https://doi.org/10.1145/3467017

45\. Koch B, Denton E, Hanna A, Foster J G. Reduced, reused and
recycled: the life of a dataset in machine learning research.
arXiv:2112.01716, 2021. https://doi.org/10.48550/arXiv.2112.01716

46\. Joshi P, Santy S, Budhiraja A, Bali K, Choudhury M. The state and
fate of linguistic diversity and inclusion in the NLP world. In:
Proceedings of the 58th Annual Meeting of the Association for
Computational Linguistics. ACL; 2020. p. 6282-6293.
https://doi.org/10.18653/v1/2020.acl-main.560

47\. Bender E M, Gebru T, McMillan-Major A, Shmitchell S. On the dangers
of stochastic parrots: can language models be too big? In: Proceedings
of the 2021 ACM Conference on Fairness, Accountability, and Transparency
(FAccT \'21). ACM; 2021. p. 610-623.
https://doi.org/10.1145/3442188.3445922

48\. Raji I D, Bender E M, Paullada A, Denton E, Hanna A. AI and the
everything in the whole wide world benchmark. arXiv:2111.15366, 2021.
https://doi.org/10.48550/arXiv.2111.15366

49\. Kaplan J, McCandlish S, Henighan T, Brown T B, Chess B, Child R, et
al. Scaling laws for neural language models. arXiv:2001.08361, 2020.
https://doi.org/10.48550/arXiv.2001.08361

50\. Bommasani R, Hudson D A, Adeli E, Altman R, Arora S, von Arx S, et
al. On the opportunities and risks of foundation models.
arXiv:2108.07258, 2021. https://doi.org/10.48550/arXiv.2108.07258

51\. Olazaran M. A sociological study of the official history of the
perceptrons controversy. Soc Stud Sci. 1996;26(3):611-659.
https://doi.org/10.1177/030631296026003005

52\. Joravsky D. The Lysenko Affair. Cambridge, MA: Harvard University
Press, 1970.

53\. Ullstrup A J. The impacts of the southern corn leaf blight
epidemics of 1970-1971. Annu Rev Phytopathol. 1972;10:37-50.
https://doi.org/10.1146/annurev.py.10.090172.000345

54\. Chu J S G, Evans J A. Slowed canonical progress in large fields of
science. Proc Natl Acad Sci USA. 2021;118(41):e2021636118.
https://doi.org/10.1073/pnas.2021636118

55\. Park M, Leahey E, Funk R J. Papers and patents are becoming less
disruptive over time. Nature. 2023;613(7942):138-144.
https://doi.org/10.1038/s41586-022-05543-x

56\. Hong L, Page S E. Groups of diverse problem solvers can outperform
groups of high-ability problem solvers. Proc Natl Acad Sci USA.
2004;101(46):16385-16389. https://doi.org/10.1073/pnas.0403723101

57\. Jones B F, Wuchty S, Uzzi B. Multi-University Research Teams:
Shifting Impact, Geography, and Stratification in Science. Science.
2008;322(5905):1259-1262. https://doi.org/10.1126/science.1158357

58\. Freeman R B, Huang W. Collaboration: Strength in diversity. Nature.
2014;513(7518):305. https://doi.org/10.1038/513305a

59\. Saviotti P P. Technological Evolution, Variety and the Economy.
Cheltenham: Edward Elgar, 1996. https://doi.org/10.4337/9781035334858
