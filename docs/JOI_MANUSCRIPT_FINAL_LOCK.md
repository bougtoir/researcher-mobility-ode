Article type: Full Length Article

Approximate word count (main text incl. tables, excl. references): 8809

Corresponding author: \[To be completed at submission\]

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
pipeline is field-agnostic; AI/ML is the case study. The indicators give
a recomputable monitoring diagnostic; its ranking is conditional on the
operational $M$ and we claim no validated predictive power.

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
here are available in the public GitHub repository
https://github.com/bougtoir/researcher-mobility-ode. The same repository
contains the Python code for cohort extraction, rate estimation, the ODE
model and its endogenous-inflow variant, the bootstrap, the sensitivity
and robustness analyses, the coupled nine-region simulation, and the
script that regenerates this manuscript, its figures, tables and
Supplementary Material. The author-level cohort and the underlying work
and authorship records are derivatives of OpenAlex data and are not
redistributed; the single reproduction command (reproduce.sh)
re-extracts them from the OpenAlex API with the scripts provided, using
the same subfield, year window and inclusion rules, and then rebuilds
all results from that extraction. OpenAlex is updated continuously, so a
fresh extraction reproduces the reported rates, rankings and thresholds
up to small snapshot differences of the kind reported in Section 3.6. No
proprietary or restricted data were used.

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

**Acknowledgments:** This study was motivated by a note.com essay by
Yamada Y (momentumyy) that framed researcher mobility in terms of
transition rates rather than net flows (Yamada Y (momentumyy). Kaigai de
ateta kenkyusha wa sonogo dou naru no ka \[What happens to researchers
who make their name abroad?\]. note.com, 2026.
https://note.com/momentumyy/n/n86df5d34282d (accessed 2026-08-09).).

# 1. Introduction

The science of science measures researcher mobility as stocks and net
flows: how many scientists a country has, how many leave and how many
arrive \[1,2,3\]. Those quantities describe redistribution, but they do
not tell an evaluator whether a research system can still reproduce its
own workforce. What is missing is a community-level state variable-an
observable quantity that tracks, in model terms, whether a system
retains the capacity to reproduce its workforce before the headcount
shows it. This paper builds that measurement pipeline end to end and
applies it to one field where the question is urgent.

Artificial intelligence (AI) and machine learning (ML) research is an
informative case. Its methods are a general-purpose technology being
embedded across science, industry and public administration \[4,5\]; its
senior researchers are unusually mobile internationally; and its talent,
compute and data are concentrating in a small number of systems
\[5,6,7\]. Governments compete for this population through visas,
fellowships and salaries \[3,8,9\]. The question echoes Jevons\'s coal
question---extended from an exhaustible input to a reproducible but
concentrating human one \[10,11\]. A measurement framework that converts
individual career-transition rates into system-level viability
indicators is therefore of direct interest to research evaluation and
science-of-science research, and AI/ML is the field where we calibrate
and illustrate it; the framework itself is field-agnostic.

The mechanism behind the indicators has four steps. (i)
Career-transition rates-entry ($I_{0}$), early-career moves abroad
($\alpha$), return ($\beta$), high-impact production ($h_{D}$, $h_{A}$),
promotion to independent authorship ($p_{D}$, $p_{A}$) and dropout
($d$)-determine the equilibrium domestic active pool $T$. (ii)
Recruitment exhibits a network externality: principal investigators
(PIs) train students and attract post-doctoral researchers, so inflow
rises with the PI stock \[12\], making the pool self-reinforcing. (iii)
A research system must exceed a minimum viable coauthor scale $M$-an
operational quantity computed from the field\'s observed number of
independent last-author groups and its coauthor intensity \[13\]-to
sustain its norms of production. (iv) Below $M$, the system can no
longer reproduce its PI stock, and the research programme it carried
leaves the field\'s menu of variety, a loss that is path-dependent in
Arthur\'s sense \[14,15,16\]. The research question is: for each
research system, how far is the active pool from its minimum viable
scale, which transition governs that distance, and has the distance been
shrinking?

Four propositions are derived from the mechanism before seeing the
results. P1 (relative scale): distance to the viability boundary is
governed by $T/M$ rather than absolute $T$; because the entry lever
rescales the whole equilibrium, this is a structural implication used
diagnostically, not a falsifiable hypothesis. P2 (asymmetric leakage):
dropout, which removes researchers from every compartment, is more
elastic than early-career outflow, which preserves return. P3
(endogenous recruitment): the transition closest to the threshold is the
one feeding the reproduction loop from outside ($I_{0}$), and the
fragility ranking is robust to the form of the recruitment feedback. P4
(historical drift): later-window rates imply different equilibria from
earlier-window rates, so proximity to the threshold is not stationary.
P2-P4 are falsifiable by the fitted model; P1 is checked for
consistency.

The contribution is primarily methodological. We assemble a fully
reproducible measurement pipeline-from OpenAlex extraction through
researcher identification, geographic attribution, mobility transitions,
PI operationalisation and community aggregation to a calibrated
six-compartment dynamical model-for a cohort of 623,176 AI/ML authors
across 9 research macro-regions \[17\]. Each measurement choice is
stress-tested: origin assignment under seven specifications, mobility
direction under each, PI status under six alternative definitions
propagated through the model, and a missingness and censoring audit; the
sensitivity results are reported in the Results section alongside the
model results, not relegated to footnotes. Empirically, we provide
comparative estimates of career-transition rates, minimum viable scale
and proximity to a model-implied viability boundary (MVB) for the
macro-regions. For research evaluation, the output is a recomputable
monitoring diagnostic ($T/M$ and its closest-lever reading, MVB
proximity) that can be recomputed with each OpenAlex release. AI/ML
serves as the case study; we make no claim that the specific findings
generalise to other fields, only that the pipeline transfers.

Section 2 specifies data and measurement, Section 3 reports observed,
model and sensitivity results in that order, Section 4 discusses
implications and limitations, and Section 5 concludes.

# 2. Data and measurement

## 2.1 Data source and cohort

We extracted AI/ML works and author histories from the OpenAlex API for
subfield 1702 (Artificial Intelligence), 2000-2023 \[17\]. OpenAlex
provides open, CC0 metadata on authors, affiliations, countries,
publication dates and citations. Author histories were built by
following each author\'s sequence of works and affiliations, assigning a
country per work and an origin macro-region by the modal group of
recorded affiliations.

Authors enter the cohort if their first observed AI/ML publication is in
2000-2016 and they have at least two AI/ML works in 2000-2023; authors
with only unknown affiliations are excluded, giving 623,176 authors. An
author is active if they have at least one AI/ML work in 2020-2023 and
has dropped out otherwise. A hit is a paper in the top 10% of AI/ML
citations for its publication year, observed within the first eight
career years. A PI is an author whose first last-author paper
(single-authored papers are treated as last-author) appears in the
window \[18\]. Both are deliberately broad operational definitions: a PI
in this sense is any author with at least one independent last-author
paper, not a tenured group leader, and a hit author is any author with
at least one top-decile paper. Because the cohort is restricted to
authors with at least two works, PIs account for 55-71% and hit authors
for 31-62% of each macro-region\'s cohort (Table 1). The PI compartment
therefore represents the population able to lead work and recruit, and
the minimum viable scale in Section 2.9 counts distinct last-author
groups per year under the same definition, so the two are consistent.
The abroad flag is set if the author is affiliated in a non-origin
macro-region within the first six career years. OpenAlex coverage is
incomplete for non-English venues and author disambiguation is
imperfect, so absolute counts are model-implied stocks rather than a
census; relative comparisons are preserved because the same rules are
applied to every macro-region. Table 1 reports the cohort by
macro-region. The China-centred, Continental Europe and United States
macro-regions contribute the largest author counts. A smaller cohort
with low coauthor intensity can be more resilient than a larger one with
high coauthor intensity, which is why $T$ and $M$ must be compared
jointly (P1).

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
OpenAlex\'s own disambiguation. Author disambiguation is imperfect:
careers can be split across duplicate identifiers or merged across
namesakes, and we do not re-disambiguate. Because every macro-region is
subjected to the same extraction rules, we read the cohort sizes and the
estimated rates as operational quantities that are comparable across
systems rather than as exact headcounts, and we carry the disambiguation
uncertainty into the measurement audit in Section 3.7.

## 2.3 Geographic attribution and origin

Each work carries the affiliation countries recorded for the author on
that work; a work with several affiliations contributes all of its
countries. An author\'s origin is an operational construct, not
birthplace or nationality: it is the modal research macro-region of the
author\'s affiliations over their first three observed career years
(ties broken toward the earliest year). This window rule is one
specification among several; Section 3.7 reports results under seven
origin rules (the three-year mode, first observed affiliation, two- and
five-year window modes, fractional assignment of multi-group years,
exclusion of multi-group years, and seeded probabilistic assignment), so
that no conclusion rests on this single choice. Two consequences of the
operational definition are measured rather than assumed:
multi-affiliated authors, for whom a single \'location\' in a year is
unobserved, and authors whose origin changes under an alternative rule.
The aggregate mobility statistics are regional aggregates, and \'zero
direction reversals\' in Section 3.7 refers to those aggregates, not to
individual trajectories.

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
or group-lead author is listed last or flagged corresponding. Because
the concept \'principal investigator\' has no direct bibliometric field,
we define six operationalisations and propagate each through the full
model (Section 3.7): ever-last-author (baseline),
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
whose AI/ML researchers share funding systems, labour markets, languages
and mobility corridors closely enough to be treated as one recruitment
pool. For reproducibility, the initial partition of countries was taken
from Huntington\'s taxonomy \[19\], which predicts the structure of
global communication networks \[20\] and of scientific mobility and
collaboration \[21\]; it serves only as a documented starting heuristic
and the resulting groups are operational research systems, not
civilisations. The partition was adjusted to the size and mobility
structure of AI/ML: the United States is separated from the rest of the
Anglosphere as the dominant destination with a distinct funding system;
Continental Europe is kept distinct because intra-European mobility and
EU funding form a separate bloc; Latin American, Orthodox and
sub-Saharan African countries are merged into Other regions because
their author counts are too small to estimate stable rates. The final 9
macro-regions are: United States, Anglosphere ex-US, Continental Europe,
China-centred, Japan, South Asia, Islamic world, Other Western (Israel),
Other regions. Anglosphere ex-US is in practice a single national
system: United Kingdom of Great Britain and Northern Ireland accounts
for 45% of its 2022-2023 AI/ML works, so results for this macro-region
should be read as results for a small, high-impact national system.
Figure 1 maps the partition and overlays the largest observed
inter-region early-career flows, which are the cross-region moves the
model tracks through the abroad compartments. The full country mapping
is in Supplementary Material.

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

The model treats each macro-region as one aggregate with constant
per-year rates and collapses careers into three observed layers. These
simplifications keep the model estimable from OpenAlex and the threshold
calculation transparent; the model is a diagnostic monitoring device,
not a demographic projection, and we do not claim validated predictive
performance.

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
outcome. Because the data are right-censored, rates are lower bounds and
equilibria conservative. Steady states are solved with a trust-region
Newton method. The equilibrium $T$ is the asymptotic pool of an open
system with continuing entry and is therefore larger than the 2020-2023
active count of the closed 2000-2016 cohort in Table 1 (by a factor of
2.5-3.1); the two are not comparable, and all claims rest on relative
quantities ($T/M$, elasticities, proximity and rankings), not on
absolute $T$. Elasticities perturb each rate by 1% and record the
percentage change in $T$ (P2). Historical drift (P4) compares equilibria
under rates estimated from the 2000-2010 and 2011-2016 career windows.
Policy counterfactuals perturb single rates by ±10% and rank levers by
margin gain; bootstrap resampling of authors (200 draws) gives 95%
intervals. All counterfactuals are mechanical perturbations of fitted
rates: they identify sensitive transitions, not causal effects of
programmes. An annual layer re-estimates rates year by year (2000-2016),
projects them to 2017-2026 and compares the projected compartment counts
with observed 2017-2023 stocks; it is an exploratory extension whose
estimation, regularisation, figures and accuracy metrics are reported in
Supplementary Material Section S2 (Supplementary Figures S1-S3,
Supplementary Tables S2-S5).

## 2.9 The boundary

Step (iii) is implemented as $M\  = \ k\  \times \ c\bar{}$, where
$\overline{c}$ is the mean number of authors per work and $k$ the median
number of distinct last-author groups per recent year. When the
equilibrium active pool $T\  = \ D\  + \ H_{D}\  + \ P_{D}$ falls below
$M$, the system cannot produce work at the field\'s coauthor intensity.
Falling below $M$ is a sufficient, not a necessary, condition for
collapse; $M$ is a soft lower bound, so observed margins are probably
smaller than they appear. For the boundary proximity measure we scale
each rate until $T$ reaches $M$ and record the critical factor and its
proximity \|critical factor - 1\|.

Terminology matters for interpretation. The boundary $M\  = \ k$ x
$\overline{c}$ is a defined classification boundary: it is a function of
observed coauthor structure and is not an object inside the ODE
dynamics; the ODE solutions do not \'feel\' $M$. Approaching the
boundary (a falling margin) is a statement about fitted equilibria, not
about time. A model crossing is what we compute when we perturb a rate
until the equilibrium $T$ reaches $M$-it is an algebraic property of the
fitted system, not a simulated or observed event in time. Empirical
collapse of a real system is something the data do not contain: no
observed macro-region is below $M$. Irreversibility, finally, enters
only through the collapse rule of the coupled scenario in Section 2.10,
where crossing $M$ switches off a region\'s PI-driven recruitment; it is
an assumption of that scenario, not an empirical finding, and we do not
claim that a real system below $M$ could not rebuild. We therefore speak
throughout of a boundary, and never of a point of no return.

## 2.10 Sensitivity design and the talent-concentration scenario

Sensitivity is assessed along three axes whose results appear in
Sections 3.4-3.7: functional form (linear versus saturating recruitment
feedback), the value of $M$ (multipliers around the fitted $k$ and
$\overline{c}$), and the measurement layer (origin rules, mobility
specifications, PI definitions and missing-data treatment). Bootstrap
resampling of authors (200 draws) gives 95% intervals on the equilibrium
quantities.

To examine what the mechanism implies when one research system
deliberately concentrates talent, we couple the nine fitted
single-region models through the observed inter-regional mobility matrix
(Figure 1) and simulate a stylised talent-concentration strategy. In the
baseline, each macro-region\'s abroad compartments are distributed over
host regions in proportion to observed off-diagonal abroad author-years
(Supplementary Figure S2), each host recruits into its early-career pool
in proportion to the PIs it hosts, and exogenous entry is adjusted so
that the coupled system reproduces the fitted equilibria exactly. The
concentration strategy is a pull of intensity φ exerted by one focal
region: early-career outflow from every other region rises from $\alpha$
to $\alpha$(1 + φ), the increment is directed to the focal region and
tracked in separate compartments, researchers pulled this way return at
$\beta$/(1 + φ), and the stock already abroad keeps its observed host
distribution, so every scenario starts from the same state. Two further
rules link the scenario to the mechanism. Once a region\'s active pool
falls below $M$, its PI-driven recruitment stops permanently (Section
2.9). Hit generation in all regions is multiplied by the effective
number of macro-regions (inverse Simpson index of domestic active pools)
relative to its baseline value, raised to a variety elasticity γ;
$\gamma\  = \ 0$ is the fitted model and $\gamma\  > \ 0$ encodes the
hypothesis that a more concentrated field generates fewer independent
contributions. We run φ ∈ {0.5, 1.0, 2.0, 4.0, 8.0} for the two largest
observed host regions, report all quantities relative to a
$\varphi\  = \ 0$ baseline, and search for the smallest γ at which the
field\'s, and the focal region\'s own, hit stock falls below baseline.
The clock of the model is set by the fitted transition rates, so we
report time in units of the characteristic time
$\tau\  = \ 1/\overline{d}$, the mean career duration implied by the
fitted dropout rates ($\tau$ ≈ 24 years); the horizon is 4.2 $\tau$, and
calendar years appear only as an annotation because the same trajectory
would unfold faster or slower in a field with faster or slower career
turnover. Read in this way, the horizon spans about 4 researcher
generations; in a field where careers last twice as long the same number
of generations would take twice as many years, and the policy
implication of a given $t/\tau$ shifts accordingly. φ, γ, the retention
and collapse rules and the horizon are stylised assumptions, listed with
their status in Supplementary Table S8; the transition rates,
equilibria, thresholds and host shares are fitted. The scenario is a
model-consistent projection of the mechanism, not a forecast.

# 3. Results

Results are reported in three layers that are kept distinct throughout:
observed quantities estimated directly from the cohort, model-implied
quantities computed from the fitted ODE, and sensitivity results showing
how both layers move under alternative measurement and modelling
choices.

## 3.1 Observed cohort and transition rates

Table 1 (Section 2.1) describes the cohort. The observed transition
rates vary widely across macro-regions: early-career outflow $\alpha$
spans 0.016 (Japan) to 0.053 (Other Western (Israel)), the share
affiliated abroad within six career years $p_{abroad}$ spans 0.094 to
0.274, return $\beta$ spans 0.023 to 0.069, and annual dropout $d$ spans
0.029 to 0.058. These are observed hazards with Laplace regularisation,
not model outputs; every model quantity in Sections 3.2-3.8 is
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
$T$ is 0.43. Because the $I_{0}$ lever scales the whole equilibrium,
proximity is close to a deterministic function of $T/M$ in the linear
model, so the first correlation is the consistency check that P1 calls
for rather than an independent test; the diagnostic content of P1 is
that the ranking by absolute size and the ranking by proximity diverge,
which the second correlation shows (Section 3.8 returns to individual
cases).

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

Table 6 compares the equilibrium that would emerge if rates estimated
from the early (2000-2010) or late (2011-2016) career window persisted;
Figure 5 plots the change in margin. All 9 macro-regions have
dual-window support for both estimates. Under late-window rates the
margin shrinks in Japan and grows in Islamic world, China-centred, South
Asia, Other regions, Continental Europe, United States, Anglosphere
ex-US, Other Western (Israel). The late window is shorter and its
cohorts younger, so its promotion and hit rates are estimated from less
exposure and its equilibria are less certain; the comparison is a
sensitivity exercise rather than a forecast. It nevertheless supports P4
in its weak form: equilibria differ across windows, so the distance to
the threshold is not stationary, and where margins shrink the mechanism
implies ongoing drift toward the threshold.

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

*Figure 5. Change in safety margin between early and late
transition-rate regimes. Negative values mean the late-window rates
would shrink the margin if they persisted. Point estimates only; the two
windows differ in cohort size.*

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

As an exploratory extension, the annual layer re-estimates the rates
year by year and projects them to 2017-2026; rate-level projections have
a skill ratio of 0.77 against a historical-mean baseline and the layer
is a drift monitor rather than a forecast, so its figures and accuracy
tables are reported in Supplementary Material Section S2 (Supplementary
Figures S1-S3, Supplementary Tables S2-S5).

## 3.7 Measurement sensitivity: origin, PI definition, multi-affiliation and missingness

Origin specification. Re-estimating the cohort under 7 origin rules
leaves the qualitative results intact: with $M$ held at its baseline
value, the lowest-$T/M$ macro-region is Anglosphere ex-US under every
rule, matching Table 2. (When $M$ is instead recomputed inside each
rule\'s re-estimated coauthor structure, Other Western (Israel) falls
lowest because its small pool of independent groups shrinks its $M$;
that variant conflates the origin question with threshold construction,
so we report the fixed-$M$ reading here and flag the alternative in the
repository tables.) Additionally, in 54 group-rule cells (6 alternative
rules x 9 macro-regions) the share affiliated abroad never crosses the
majority direction-that is, no macro-region\'s aggregate $p_{abroad}$
flips from below to above 50%, or vice versa (0 reversals). This
statement is about group-level aggregates: individual authors do change
assigned origin under the alternative rules (baseline agreement
94-99.8%), so the stability is at the level of the regional statistics
the model consumes, not of individual trajectories, and it is not a full
validation of origin estimation.

Multi-affiliation and missingness. 8.4% of cohort authors record
affiliations in more than one macro-region in at least one year;
fractional and exclusion specifications of those years change the
outputs by at most a few percent, so multi-affiliation is a measurement
ambiguity to disclose rather than a driver of results. Country is
missing on 4.2% of cohort authorship rows, and the missingness is not
random (it is concentrated in earlier years), 5.7% of authors have
careers left-censored at the 2000 window edge, and 28% of observed spans
are shorter than five years (24% are 15 years or more). The first two
push the reported rates toward underestimates of mobility; the short
spans widen the bootstrap intervals, which is one reason rankings are
reported rather than precise margins.

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

  ------------------------------------------------------------------------------
  **Choice varied**   **Quantity        **Observed effect**    **Caveat**
                      affected**                               
  ------------------- ----------------- ---------------------- -----------------
  Origin rule (7      Lowest-$T/M$      Invariant (Anglosphere Regional
  specs)              region (fixed     ex-US); 0/54 aggregate aggregates, not
                      $M$);             reversals              individuals
                      $p_{abroad}$                             
                      direction                                

  Multi-affiliation   All model outputs \<2% change under      Same-year
  (8.4% authors)                        fractional/exclusion   location
                                                               unobserved

  PI proxy (6 defs)   PI share          10-87%                 Absolute share
                                                               proxy-dependent

  PI proxy (6 defs)   $T/M$,            Structurally invariant Calibration
                      elasticities,     ($I_{0}$ calibration)  artefact, not
                      proximity                                validation
                      rankings                                 

  PI proxy (6 defs)   $P_{D}/M_{P}$,    30--6,010x; lever      P-side varies by
                      closest P-side    unchanged              construction
                      lever                                    

  Missing country     Rates             Toward underestimation Missingness
  (4.2% rows)                                                  non-random

  Left censoring      Career windows    Rates are lower bounds Pre-2000 careers
  (5.7%)                                                       unobserved

  Short spans (27.8%  Bootstrap         Wide intervals         Rankings
  \<5y)               intervals                                descriptive
  ------------------------------------------------------------------------------

*Table 8. Measurement-sensitivity summary. Every row is computed from
the cohort under the stated specification; details and per-rule tables
are in the public repository.*

## 3.8 Worked example: Japan

Japan illustrates the mechanism in a large research system with an
independent institutional lineage and comparatively low $T/M$. Its
fitted equilibrium is $T\  = \ 26,399$ active researchers
($D\  = \ 14,519$, $H_{D}\  = \ 5,452$, $P_{D}\  = \ 6,428$) against
$M\  = \ 90$, so $T/M\  = \ 292.95$. The closest boundary is $I_{0}$: a
fall to 0.3% of its current level would bring $T$ to $M$. Figure 7
places Japan\'s six compartments and compares its rates with the other
macro-regions: early-career outflow ($\alpha\  = \ 0.016$) and domestic
PI promotion ($p_{D}\  = \ 0.063$) are comparatively low, return
($\beta\  = \ 0.025$) and domestic hit generation ($h_{D}\  = \ 0.044$)
moderate, and dropout $d\  = \ 0.058$. Low leakage but a thin internal
promotion pipeline is the configuration P1 and P2 describe: the system
does not lose many researchers abroad, so its distance to the threshold
is governed by scale relative to $M$ and by attrition rather than by
mobility. Figure 8 generalises the diagnostic by plotting $T/M$ against
boundary proximity for all macro-regions; the lower-left corner combines
a low buffer with a small proportional change needed to reach $M$. The
same two-panel diagnostic applies to any macro-region with sufficient
OpenAlex coverage; Japan is a worked example, not a special case.

![](media/image7.png){width="6.0in" height="3.3094969378827646in"}

*Figure 7. Japan in the six-compartment model, with a ladder of fitted
transition rates across research macro-regions (Japan highlighted;
longer bars are higher rates).*

![](media/image8.png){width="5.8in" height="4.511111111111111in"}

*Figure 8. Equilibrium safety ratio (*$T/M$*) versus closest
viability-boundary proximity for all research macro-regions. Japan is
shown in red.*

## 3.9 Talent concentration: short-run dominance, field-level loss

Under the coupled scenario of Section 2.10, the dominant region\'s
hosted pool and share rise monotonically with the pull intensity φ,
while the effective number of macro-regions falls: the strategy wins the
short run it was designed for, at a direct variety cost to the field
(Figure 9). Within the simulated horizon no region\'s active pool
approaches $M$ (the collapse rule never activates in any run), so these
outcomes do not depend on that scenario assumption. Whether the field\'s
hit stock also falls depends on the variety elasticity γ: it declines
even at $\gamma\  = \ 0$ for the United States, and only once γ exceeds
a moderate value for the second-largest host. Whether the dominant
region itself ends worse off requires a larger γ still (γ\* = 3.9 at the
strongest pull). γ is not identified by our data; the variety loss is
the robust finding. Figure 10 shows the regional time paths at
$\varphi\  = \ 8.0$: the dominant pool rises, source regions decline
toward their thresholds, and each crossing of $M$ switches off that
region\'s PI-driven recruitment under the scenario\'s collapse rule-a
discrete model event, not an observed one.

![](media/image9.png){width="6.5in" height="4.727272528433946in"}

*Figure 9. Talent-concentration scenario with the United States as the
dominant region (coupled nine-region model, fitted rates unless stated).
(a) Hosted active pool relative to the* $\varphi\  = \ 0$ *baseline; (b)
effective number of macro-regions; (c) field hit stock relative to
baseline at* $\varphi\  = \ 2.0$ *for three variety elasticities γ;
(*$d$*) smallest γ at which the field\'s, and the dominant region\'s
own, hit stock falls below baseline within the horizon, for the two
largest host regions (points on the dotted line at the top of the panel:
not reached within the search range). Time in (a)-(c) is in units of*
$\tau\  = \ 1/\overline{d}$ *(upper axis: years at fitted rates). φ and
γ are stylised.*

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

*Table 9. Talent-concentration scenario at the end of the horizon (4.2*
$\tau$ *≈ 100 years at fitted rates) relative to the* $\varphi\  = \ 0$
*baseline, fitted rates (*$\gamma\  = \ 0$*), for the two largest
observed host regions. γ\* is the smallest variety elasticity at which
the hit stock falls below baseline within the horizon.*

Figure 10 shows the time paths behind these summaries for every
macro-region at the strongest pull we simulate ($\varphi\  = \ 8.0$),
one panel per γ. The timing scales with $\tau$: a field with faster
career turnover would reach the same crossings in proportionally fewer
years, so the ordering of outcomes, not the calendar dates, is the
result.

![](media/image10.png){width="6.5in" height="2.269841426071741in"}

*Figure 10. Regional time paths under the talent-concentration strategy
exerted by the United States at pull intensity* $\varphi\  = \ 8.0$*,
for three variety elasticities γ. Lines show each macro-region\'s
domestic active pool as a multiple of its minimum viable coauthor scale*
$M$ *(log scale; dashed line* $M$*); the thick line is the dominant
region. Crosses and dotted verticals mark when a region falls below*
$M$*, after which its PI-driven recruitment is switched off permanently
under the scenario\'s collapse rule. Time is in units of the
characteristic time* $\tau\  = \ 1/\overline{d}$ *(mean career duration;
≈24 years at fitted rates, upper axis). Fitted rates; φ, γ and the
collapse rule are stylised.*

# 4. Discussion

## 4.1 Principal findings

P1 is consistent with the results in the sense that matters for policy:
rankings by absolute $T$ and by proximity to the threshold diverge
($\rho\  = \ 0.43$), the largest systems are not the safest, and
proximity itself is governed by $T/M$ as the mechanism implies; this is
a diagnostic reading rather than a test. P2 is supported in every
macro-region: dropout is more elastic than early-career outflow, and
reducing dropout is the most efficient single lever. P3 is supported:
$I_{0}$ is the closest viability-boundary lever for the active
researcher pool in every group, and the ranking is invariant to the form
of the recruitment feedback. P4 is supported in its weak form:
equilibria differ between the two career-start windows in all 9
macro-regions with dual-window support, and the margin shrinks in Japan.
Together the results move the researcher-mobility debate from net flows
to the transition rates that govern reproduction, and they give an
empirically observable monitoring variable-one whose predictive value
for real community failure is a separate, unvalidated question (Section
4.7).

## 4.2 Methodological contribution

For informetrics, the contribution is a measurement pipeline rather than
a single indicator. Origin assignment, mobility transitions, PI status,
community aggregation, calibration and the viability boundary are each
specified operationally, and each is accompanied by a sensitivity result
reported in the main text: origin under seven rules, mobility direction
under each, PI under six definitions propagated through the model,
multi-affiliation and missingness quantified. This is the level of
measurement audit that secondary-data mobility studies often leave
implicit, and it is what makes the resulting indicators-$T/M$ and
viability-boundary proximity-usable as monitoring quantities. The
pipeline is field-agnostic in design: every step is parameterised on a
subfield, a year window and an authorship convention, and AI/ML is the
case study on which it is calibrated and illustrated. We do not claim
the findings generalise to other fields; we claim the machinery does,
with authorship conventions redefined per field.

## 4.3 Related literature

Researcher mobility has been studied under the headings of brain drain,
brain circulation and brain gain \[1\]. Outflows become a gain when
return migration and diaspora networks are supported \[1\]; bilateral
flows are driven by collaboration, economic convergence and visa
restrictions \[3\]; and cross-country shares of foreign-born scientists
vary widely \[2\]. In AI/ML, the United States is the dominant
destination, mobile scientists keep ties to origin systems \[5,22\], and
elite networks are highly clustered \[23\]. The economics of science
supplies the microfoundation: individuals respond to career incentives
\[18\]. What this literature measures is stocks and flows; it does not
specify a community-level state variable whose crossing makes the loss
self-reinforcing rather than recoverable. Evolutionary and
innovation-systems economics supplies the threshold concepts-variety
generation and selection, lock-in through increasing returns
\[14,15,16,24\], and frameworks for analysing the diversity of a
technological system \[25,26,27\]-but its unit of analysis is the firm,
the technology or the sector. The present framework connects the two:
the community-level state variable is the equilibrium active pool
relative to a coauthor-scale threshold, estimated from the career
transitions the mobility literature already measures. The AI-specific
homogenisation concerns it connects to-algorithmic monoculture,
benchmark and compute concentration, linguistic and data bias-are
documented elsewhere \[7,28,29,30,31,32,33\], and the scale of the
leading models intensifies the concentration \[6,34,35\]. Historical
cases of fields that narrowed onto a dominant approach and stagnated are
well documented-from the perceptrons controversy in AI itself, through
Lysenkoist biology, pre-2008 macroeconomics and string theory, to
agricultural monocultures \[36,37,38,39,40,41,42,43,44\]. Evidence that
large fields slow canonical progress and that papers become less
disruptive over time makes the variety question empirical rather than
rhetorical \[45,46\]; diversity demonstrably aids problem solving
\[47\], multi-site and internationally distributed teams retain high
impact \[48,49\], innovation is highest at intermediate competition
\[50\], and the processes are institutionally embedded in national and
sectoral systems \[51,52\].

## 4.4 Implications for research evaluation

The indicators are designed for evaluators rather than for national
accounting. $T/M$ and boundary proximity can be recomputed with each
OpenAlex release; a declining margin in any macro-region is a signal for
the field, not only for that region. Because the closest lever and the
most elastic lever are identified separately, the indicators also
distinguish where monitoring should focus: entry pipelines ($I_{0}$)
bind first at the observed scale, while attrition ($d$) is the most
elastic. The exploratory annual layer provides the machinery for
tracking rates year by year, although its current direction-prediction
skill is low and it should be read as a monitor rather than a forecast.
For individual universities, the PI stock is the node of the network
externality: institutions that convert hit researchers into PIs and
retain them regenerate their own inflow, and the macro-regional ladder
(Figure 7) gives a benchmark against which an institution\'s own
transition rates can be read. For early-career researchers, going abroad
is a smaller threat to a home system than net-flow accounting implies;
attrition is the larger one.

## 4.5 Policy implications

Concentrating talent is individually advantageous for the large systems
pursuing it: it raises short-run output \[6,8,9\], but each round of
concentration lowers $T/M$ in the systems that lose researchers, and the
collective outcome can be an evolutionary dead end for the field
(Section 3.9). No single actor captures the benefit of the variety it
preserves, so the response has to be shared: jointly funded early-career
fellowships and return grants aimed at low-$T/M$ systems, routine
monitoring of the indicator pair, and shared compute and data
infrastructure acting on the intra-regional levers $h_{D}$ and $p_{D}$
where mobility itself cannot or should not be steered \[14,26\]. Because
endogenous inflow is capped at 0.50× the critical reproduction rate, the
implied interventions are conservative: they aim to keep systems away
from the threshold, not to maximise any one system\'s share. Lever
rankings are model-conditional: they follow from the fitted rates and
thresholds and are not causal effects of programmes.

  --------------------------------------------------------------------------------------------------------------------------------------
  **Lever**    **Mechanism    **Policy instrument**   **Principal     **Empirical         **Unintended              **Uncertainty and
               (in model)**                           actor**         evidence**          consequences**            model dependence**
  ------------ -------------- ----------------------- --------------- ------------------- ------------------------- --------------------
  Dropout      Lowers $d$;    Early-career            Universities,   Indirect:           Lock-in of marginal       Rate elasticity
  ($d$)        raises $T$ and fellowships, childcare  department      early-career        researchers; subsidy      estimated;
               margin         and dual-career         heads           support is linked   capture by secure staff   instrument-to-rate
               directly; most support, stable                         to lower attrition                            link not measured
               elastic lever  non-tenure tracks                       in the                                        
                                                                      fellowship/tenure                             
                                                                      literature; AI/ML                             
                                                                      magnitude                                     
                                                                      unestablished                                 

  Exogenous    Raises         Research-master and     National        Strong generic:     Dilution of supervision   $I_{0}$ is
  entry        $I_{0}$;       undergraduate           funders,        doctoral expansion  quality; credential       calibrated to
  ($I_{0}$)    linearly       pipelines, doctoral     ministries      raises the research inflation                 observed entry;
               rescales all   fellowships,                            workforce; visa                               pipeline vs
               stocks;        recruitment visas                       effects on inflow                             migration not
               closest lever                                          documented                                    separable
               at observed                                                                                          
               scale                                                                                                

  Return from  Raises return  Return grants, diaspora Diaspora        Mixed: diaspora     Return-then-leave-again   Return measured from
  abroad       inflow into    networks, dual          networks,       policies show small churn; benefits           affiliations only;
  ($\beta$)    early-career   appointments,           funders,        positive return     concentrated on the       physical return
               pool           overseas-experience     recruiters      rates               already-mobile            unobserved
                              recognition                                                                           

  Domestic hit Raises hit     Independent-lab         National        Moderate:           Concentration on          $h_{D}$ bundles
  generation   generation;    programmes,             funders,        compute/data access incumbents; hardware      output quantity and
  ($h_{D}$)    builds the H   doctoral/postdoctoral   universities    is the              lock-in                   quality
               compartments   training, compute                       AI/ML-specific                                
               feeding P      access                                  bottleneck                                    

  PI promotion Raises         Tenure-track            Universities,   Indirect:           Premature promotion       Instrument-proxy
  ($p_{D}$)    promotion $D$  conversion, startup     funders         tenure-track        dilutes the PI proxy      mismatch possible;
               to $P_{D}$;    packages, project-based                 expansion raises    (measurement, not         ranking robust to
               feeds the      PI status                               senior-author       reality)                  $M$ only at observed
               reproduction                                           counts                                        scale
               loop                                                   (descriptive)                                 
  --------------------------------------------------------------------------------------------------------------------------------------

*Table 10. Levers, mechanisms, instruments, evidence and uncertainty.
Lever rankings are model-conditional; the instrument-to-rate links are
argued from the literature, not measured here.*

Each instrument affects a model rate; the instrument-to-rate link is
argued from the literature, not measured here, and estimated rate
elasticities do not establish that any single instrument moves any
single rate by the stated amount. Regional effects are two-sided: a pull
that raises one region\'s inflow lowers another\'s, and the coupled
scenario shows the sender regions, not only the receiver, pay the margin
cost.

## 4.6 Limitations

OpenAlex affiliation and country assignments are noisy, especially for
multi-affiliated authors, and coverage of non-English venues is
incomplete. The $T/M$ ranking is sensitive to the operational $M$: under
independent per-region multipliers in \[0.5, 2.0\] every region pair can
exchange order, so the ranking conditions on the chosen threshold
definition (Section 3.6). The macro-regional grouping is coarse;
within-group heterogeneity is substantial, and the grouping of, for
example, mainland China and Taiwan follows current OpenAlex country
metadata rather than any resolution of their relationship. Geographic
variety is a proxy for the cognitive and institutional variety the
mechanism concerns, and the model does not observe research content
directly; that macro-regions differ in institutions, languages and
funding is documented, but that they carry distinct research programmes
is assumed here, not measured, and claims about problem framings or
benchmarks should be read with that qualification. Irreversibility is
likewise a property of the collapse rule in the coupled scenario, not an
empirical finding: a real system that fell below $M$ could in principle
rebuild through return migration or new entry, which the model does not
represent, so the viability boundary denotes the threshold at which the
fitted feedback loop stops sustaining the pool, not a prediction that
recovery is impossible. The model omits cross-region spillovers,
firm-level mobility and within-year dynamics; rates are assumed constant
within windows; the cohort over-weights prolific authors; and bootstrap
intervals are wide, so rankings are descriptive. The endogenous inflow
cap (0.50) is a modelling choice whose alternatives should be mapped.
Falling below $M$ is a sufficient rather than necessary condition for
collapse, and the historical comparison rests on two point estimates.
The talent-concentration scenario couples the regions only through
observed host shares and stylised pull, retention and collapse rules,
holds fitted rates constant over a long horizon, and treats the variety
elasticity γ as a free parameter; its results are model-consistent
projections that rank strategies, not predictions of when any region\'s
advantage ends. The PI and hit proxies follow AI/ML authorship
conventions (group leader listed last or corresponding; hits scored
within the AI/ML subfield); the sensitivity battery shows the absolute
PI share varies widely across definitions while rankings survive, and
transfer of the pipeline to fields with alphabetical author order or
consortium authorship requires redefining these proxies. Measurement
limits quantified in Section 3.7-multi-affiliated authors, non-random
missing country, left-censored careers at the 2000 window edge, and
short observed spans-mean the reported rates are best read as comparable
lower bounds. Finally, the propositions are tested on nine
macro-regions, so correlational support for P1 is indicative; the
strongest support is for P2 and P3, which hold system by system.

## 4.7 Future validation agenda

Three extensions would test rather than extend the framework. First,
external validation of the viability boundary: back-testing the
indicator against historical cases of systems that contracted or lost a
research programme would show whether proximity predicts outcomes rather
than merely describing fitted equilibria. Second, identifying the
variety elasticity γ from disruption or novelty measures would determine
whether the talent-concentration scenario\'s field-level output loss is
a real possibility or a parameter artefact. Third, applying the pipeline
to a field with different authorship conventions-and to a deliberately
mis-specified macro-regional partition-would test which results are
measurement artefacts and which are structural. Each is executable on
open data with the released code.

# 5. Conclusion

We asked how far each AI/ML research system is from the scale below
which it can no longer reproduce its research workforce, which career
transition governs that distance, and whether the distance is shrinking.
The answer is delivered by a measurement pipeline that turns open
bibliometric records into cohort career-transition rates, a calibrated
compartment model, and a monitoring diagnostic pair ($T/M$ and its
closest-lever reading, viability-boundary proximity), with every
measurement choice stress-tested in the main results. All systems
currently exceed their minimum viable coauthor scale, but distance to
the threshold is governed by relative scale and by attrition rather than
by size or outflow; exogenous entry is the binding lever everywhere; the
ranking is robust to the form of the recruitment feedback; and rates
have drifted between career windows, shrinking the margin in Japan. For
research evaluation the contribution is a reproducible, field-agnostic
measurement framework for research-system viability; for AI/ML it
locates the systems whose margins are thin and the levers that matter.
Extensions include external validation of the boundary against
historical contractions, identification of the variety elasticity, finer
partitions with inter-regional spillovers, and application to other
general-purpose research fields.

# References

1\. Thorn K, Holm-Nielsen L B. International Mobility of Researchers and
Scientists: Policy Options for Turning a Drain into a Gain. UNU-WIDER
Research Paper No. 2006/83, 2006.
https://www.wider.unu.edu/publication/international-mobility-researchers-and-scientists

2\. Franzoni C, Scellato G, Stephan P E. Foreign-born scientists:
mobility patterns for 16 countries. Nat Biotechnol.
2012;30(12):1250-1253. https://doi.org/10.1038/nbt.2449

3\. Appelt S, van Beuzekom B, Galindo-Rueda F, de Pinho R. Which factors
influence the international mobility of research scientists? OECD
Science, Technology and Industry Working Papers 2015/02, 2015.
https://doi.org/10.1787/5js1tmrr2233-en

4\. Bresnahan T F, Trajtenberg M. General purpose technologies \'Engines
of growth\'? J Econom. 1995;65(1):83-108.
https://doi.org/10.1016/0304-4076(94)01598-T

5\. MacroPolo. The Global AI Talent Tracker 2.0. Paulson Institute,
2023.
https://macropolo.org/digital-projects/the-global-ai-talent-tracker/

6\. Sevilla J, Heim L, Ho A, Besiroglu T, Hobbhahn M, Villalobos P.
Compute trends across three eras of machine learning. In: 2022
International Joint Conference on Neural Networks (IJCNN). IEEE; 2022.
p. 1-8. https://doi.org/10.1109/IJCNN55064.2022.9891914

7\. Ahmed N, Wahed M. The de-democratization of AI: deep learning and
the compute divide in artificial intelligence research.
arXiv:2010.15581, 2020. https://doi.org/10.48550/arXiv.2010.15581

8\. Shachar A. The Race for Talent: Highly Skilled Migrants and
Competitive Immigration Regimes. NYU Law Rev. 2006;81(1):148-206.

9\. Kerr W R. Global Talent and U.S. Immigration Policy. Harvard
Business School Working Paper No. 20-107, 2020.
https://www.hbs.edu/ris/Publication%20Files/20-107_0967f1ab-1d23-4d54-b5a1-c884234d9b31.pdf

10\. Jevons W S. The Coal Question: An Inquiry Concerning the Progress
of the Nation, and the Probable Exhaustion of Our Coal-Mines. London:
Macmillan, 1865.

11\. Alcott B. Jevons\' paradox. Ecol Econ. 2005;54(1):9-21.
https://doi.org/10.1016/j.ecolecon.2005.03.020

12\. Katz M L, Shapiro C. Network externalities, competition, and
compatibility. Am Econ Rev. 1985;75(3):424-440.

13\. Shaffer M L. Minimum Population Sizes for Species Conservation.
BioScience. 1981;31(2):131-134. https://doi.org/10.2307/1308256

14\. Arthur W B. Competing technologies, increasing returns, and lock-in
by historical events. Econ J. 1989;99(394):116-131.
https://doi.org/10.2307/2234208

15\. Nelson R R, Winter S G. An Evolutionary Theory of Economic Change.
Cambridge, MA: Harvard University Press, 1982.

16\. Dosi G. Technological paradigms and technological trajectories: a
suggested interpretation of the determinants and directions of technical
change. Res Policy. 1982;11(3):147-162.
https://doi.org/10.1016/0048-7333(82)90016-6

17\. Priem J, Piwowar H, Orr R. OpenAlex: A fully-open index of
scholarly works, authors, venues, institutions, and concepts.
arXiv:2205.01833, 2022. https://doi.org/10.48550/arXiv.2205.01833

18\. Stephan P E. The Economics of Science. J Econ Lit.
1996;34(3):1199-1235.

19\. Huntington S P. The Clash of Civilizations and the Remaking of
World Order. New York: Simon & Schuster, 1996.

20\. State B, Park P, Weber I, Macy M. The mesh of civilizations in the
global network of digital communication. PLoS ONE. 2015;10(5):e0122543.
https://doi.org/10.1371/journal.pone.0122543

21\. Chinchilla-Rodríguez Z, Miao L, Murray D, Robinson-García N, Costas
R, Sugimoto C R. A global comparison of scientific mobility and
collaboration according to national scientific capacities. Front Res
Metr Anal. 2018;3:17. https://doi.org/10.3389/frma.2018.00017

22\. AlShebli B, Memon S A, Evans J A, Rahwan T. China and the U.S.
produce more impactful AI research when collaborating together. Sci Rep.
2024;14:28576. https://doi.org/10.1038/s41598-024-79863-5

23\. Yuan S, Shao Z, Wei X, Tang J, Hall W, Wang Y, et al. Science
behind AI: the evolution of trend, mobility, and collaboration.
Scientometrics. 2020;124(2):993-1013.
https://doi.org/10.1007/s11192-020-03423-7

24\. David P A. Clio and the economics of QWERTY. Am Econ Rev.
1985;75(2):332-337.

25\. Stirling A. A general framework for analysing diversity in science,
technology and society. J R Soc Interface. 2007;4(15):707-719.
https://doi.org/10.1098/rsif.2007.0213

26\. Saviotti P P. Technological Evolution, Variety and the Economy.
Cheltenham: Edward Elgar, 1996. https://doi.org/10.4337/9781035334858

27\. Metcalfe J S. Evolutionary Economics and Creative Destruction.
London: Routledge, 1998. https://doi.org/10.4324/9780203275146

28\. Kleinberg J, Raghavan M. Algorithmic monoculture and social
welfare. Proc Natl Acad Sci USA. 2021;118(22):e2018340118.
https://doi.org/10.1073/pnas.2018340118

29\. Hooker S. The hardware lottery. Commun ACM. 2021;64(12):58-65.
https://doi.org/10.1145/3467017

30\. Koch B, Denton E, Hanna A, Foster J G. Reduced, reused and
recycled: the life of a dataset in machine learning research.
arXiv:2112.01716, 2021. https://doi.org/10.48550/arXiv.2112.01716

31\. Joshi P, Santy S, Budhiraja A, Bali K, Choudhury M. The state and
fate of linguistic diversity and inclusion in the NLP world. In:
Proceedings of the 58th Annual Meeting of the Association for
Computational Linguistics. ACL; 2020. p. 6282-6293.
https://doi.org/10.18653/v1/2020.acl-main.560

32\. Bender E M, Gebru T, McMillan-Major A, Shmitchell S. On the dangers
of stochastic parrots: can language models be too big? In: Proceedings
of the 2021 ACM Conference on Fairness, Accountability, and Transparency
(FAccT \'21). ACM; 2021. p. 610-623.
https://doi.org/10.1145/3442188.3445922

33\. Raji I D, Bender E M, Paullada A, Denton E, Hanna A. AI and the
everything in the whole wide world benchmark. arXiv:2111.15366, 2021.
https://doi.org/10.48550/arXiv.2111.15366

34\. Kaplan J, McCandlish S, Henighan T, Brown T B, Chess B, Child R, et
al. Scaling laws for neural language models. arXiv:2001.08361, 2020.
https://doi.org/10.48550/arXiv.2001.08361

35\. Bommasani R, Hudson D A, Adeli E, Altman R, Arora S, von Arx S, et
al. On the opportunities and risks of foundation models.
arXiv:2108.07258, 2021. https://doi.org/10.48550/arXiv.2108.07258

36\. Olazaran M. A sociological study of the official history of the
perceptrons controversy. Soc Stud Sci. 1996;26(3):611-659.
https://doi.org/10.1177/030631296026003005

37\. Rumelhart D E, Hinton G E, Williams R J. Learning representations
by back-propagating errors. Nature. 1986;323(6088):533-536.
https://doi.org/10.1038/323533a0

38\. Joravsky D. The Lysenko Affair. Cambridge, MA: Harvard University
Press, 1970.

39\. Colander D, Goldberg M, Haas A, Juselius K, Kirman A, Lux T, et al.
The financial crisis and the systemic failure of the economics
profession. Crit Rev. 2009;21(2-3):249-267.
https://doi.org/10.1080/08913810902934109

40\. Smolin L. The Trouble with Physics: The Rise of String Theory, the
Fall of a Science, and What Comes Next. Boston: Houghton Mifflin, 2006.

41\. Ullstrup A J. The impacts of the southern corn leaf blight
epidemics of 1970-1971. Annu Rev Phytopathol. 1972;10:37-50.
https://doi.org/10.1146/annurev.py.10.090172.000345

42\. McCook S. Global rust belt: Hemileia vastatrix and the ecological
integration of world coffee production since 1850. J Glob Hist.
2006;1(2):177-195. https://doi.org/10.1017/S174002280600012X

43\. Avelino J, Cristancho M, Georgiou S, Imbach P, Aguilar L, Bornemann
G, et al. The coffee rust crises in Colombia and Central America
(2008-2013): impacts, plausible causes and proposed solutions. Food
Secur. 2015;7(2):303-321. https://doi.org/10.1007/s12571-015-0446-9

44\. Ploetz R C. Management of Fusarium wilt of banana: a review with
special reference to tropical race 4. Crop Prot. 2015;73:7-15.
https://doi.org/10.1016/j.cropro.2015.01.007

45\. Chu J S G, Evans J A. Slowed canonical progress in large fields of
science. Proc Natl Acad Sci USA. 2021;118(41):e2021636118.
https://doi.org/10.1073/pnas.2021636118

46\. Park M, Leahey E, Funk R J. Papers and patents are becoming less
disruptive over time. Nature. 2023;613(7942):138-144.
https://doi.org/10.1038/s41586-022-05543-x

47\. Hong L, Page S E. Groups of diverse problem solvers can outperform
groups of high-ability problem solvers. Proc Natl Acad Sci USA.
2004;101(46):16385-16389. https://doi.org/10.1073/pnas.0403723101

48\. Jones B F, Wuchty S, Uzzi B. Multi-University Research Teams:
Shifting Impact, Geography, and Stratification in Science. Science.
2008;322(5905):1259-1262. https://doi.org/10.1126/science.1158357

49\. Freeman R B, Huang W. Collaboration: Strength in diversity. Nature.
2014;513(7518):305. https://doi.org/10.1038/513305a

50\. Aghion P, Bloom N, Blundell R, Griffith R, Howitt P. Competition
and innovation: an inverted-U relationship. Q J Econ.
2005;120(2):701-728. https://doi.org/10.1162/0033553053970214

51\. Lundvall B-Å. National Systems of Innovation: Toward a Theory of
Innovation and Interactive Learning. London: Anthem Press, 1992.

52\. Malerba F. Sectoral systems of innovation and production. Res
Policy. 2002;31(2):247-264.
https://doi.org/10.1016/S0048-7333(01)00139-1
