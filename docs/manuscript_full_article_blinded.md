Article type: Research Article

Approximate word count (main text incl. tables, excl. references): 9972

Author information removed for double-blind review

# Abstract

Artificial intelligence (AI) and machine learning (ML) research is
increasingly concentrated, raising the risk that smaller communities
fall below a minimum viable coauthor pool. We model each civilisation as
a six-compartment system of domestic and abroad early-career,
high-impact, and principal-investigator (PI) researchers, and estimate
transition rates from OpenAlex AI/ML data (subfield 1702). The minimum
viable threshold is M = k × c_bar, where c_bar is the mean authors per
work and k is the median number of distinct last-author groups per year.
Across 9 groups, equilibrium active pools remain above their thresholds,
but the closest point of no return (PNR) is observed for the Other
Western group, where the exogenous entry rate (I0) must be multiplied by
0.332× (a 67% proportional reduction) to drive the active pool to its
threshold. A simulated reduction in dropout yields the largest margin
gain in every group in the fitted model. The 2017-2023 projection has
RMSE 10190.39 and a conservative, non-standard MAPE of 129.0%
(count_obs + 1 denominator). The high error is expected because the
projection is an early-warning indicator of directional drift, not a
precise forecast. Historical counterfactuals and bootstrap uncertainty
show that the model is most sensitive to exogenous entry and attrition.
These results provide a quantitative framework for early,
safety-factor-bound policy scenarios that preserve civilisational
diversity in AI/ML research.

**Keywords:** researcher mobility; artificial intelligence; civilisation
grouping; ordinary differential equations; PNR; innovation studies

## Highlights

- Nine civilisations modelled as six-compartment ODEs fitted to OpenAlex
  AI/ML data.

- Closest PNR: Other Western via I0 (factor 0.332×).

- Dropout reduction yields the largest margin gain across all groups.

## Data and Code Availability

This study uses the OpenAlex database (subfield 1702, Artificial
Intelligence; 2000--2023), accessed via the OpenAlex API. The analysis
is bundled with a pre-extracted cohort and a stratified sample of works;
the country-to-civilisation mapping, code, and result CSVs used to
generate this manuscript will be made available in a public repository
upon acceptance. The extracted cohort SQLite database (a derived
aggregate of OpenAlex records) is available from the corresponding
author on request, subject to the OpenAlex CC0 licence and any
applicable local data-use policies.

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

**Acknowledgments:** \[Removed for double-blind review\]

# 1. Introduction

Most debates on research mobility focus on net flows: which country
gains researchers and which loses them. Net-flow accounting is useful
for headlines, but it hides the transition rates that actually move
researchers between career stages and locations. A small proportional
change in one of those rates can, over time, push a research community
below the minimum coauthor pool it needs to remain viable. Once the pool
falls below that threshold, recovery becomes difficult or impossible,
even if policy is later reversed. That is the point of no return (PNR)
that motivates this paper. The contribution of this paper is to
translate that qualitative insight into an empirically tractable model.
We estimate transition rates from open bibliometric data, solve the
steady state of a compartment model, and identify which rate in which
civilisation is closest to a threshold. The approach is deliberately
stylised: it sacrifices demographic realism for transparency and for the
ability to compare multiple civilisations with the same accounting
framework.

Artificial intelligence (AI) and machine learning (ML) have become the
archetypal general-purpose technologies of the current era ^\[1\]^, and
their development depends on a relatively small, highly mobile workforce
of doctoral and post-doctoral researchers, principal investigators
(PIs), and research engineers ^\[1\]^. The geographic concentration of
this workforce has generated both scientific and geopolitical concern.
Policymakers in the United States, China, Europe, Japan, India and
elsewhere now treat AI talent as a strategic input, and several
governments have introduced incentives to attract or retain researchers
^\[2\]^. Most of those policies are evaluated by their immediate
net-flow effects. They rarely ask which transition in the career
pipeline is the binding constraint, or how close a community is to a
threshold where the field can no longer sustain itself. The economic
literature on science has long emphasised that researchers are a scarce
input and that their mobility responds to career incentives and
institutional quality ^\[3\]^. That literature provides the
microfoundation for our rates: individuals decide where to train,
whether to go abroad, when to return, and when to leave academia. We
aggregate those individual decisions into civilisation-level transition
rates and ask what the resulting dynamics imply for community survival.

The civilisation framework offers a natural way to partition the global
research population into culturally and institutionally coherent arenas
^\[4\]^. We adapt Huntington\'s nine civilisations for AI/ML mobility by
keeping the United States, China (Sinic), India and nearby South Asian
countries (Hindu), Japan, and the Islamic world as distinct groups,
splitting the Western bloc into the United States, Anglosphere excluding
the United States, Continental Europe and Other Western, and merging the
smaller Latin American, Orthodox and African communities into Other
Civilizations. This grouping reflects the empirical size and mobility
patterns observed in the data rather than a normative claim about
civilisational identity.

The central argument of the paper is that preserving civilisational
diversity in AI/ML is not only a normative preference but also a
safeguard against technological dead ends. When a single region or a
small oligopoly dominates a field, the set of research questions,
evaluation norms, and institutional incentives narrows ^\[5\]^. A
diverse ecosystem generates competing approaches, which increases the
probability that unexpected breakthroughs and error correction survive
^\[5\]^. If transition rates can be observed with enough temporal
resolution, policy can intervene before a community reaches the PNR.
Early, proportionate interventions can prevent the emergence of a
monopoly or oligopoly without requiring large ex post rescues.

We therefore address five research questions. First, how close is each
civilisation to the PNR in its AI/ML research community? Second, which
transition rates have the largest effect on community size? Third, how
have transition rates changed between earlier and later career cohorts,
and what would have happened if those rates had persisted? Fourth, what
safety-factor-bound single-lever and multi-lever policy scenarios can
widen the margin before a PNR is reached? Fifth, can the fitted rates be
estimated year by year and used to project near-term population
composition, and how well do those projections reproduce observed
2017-2023 counts? The key policy intuition is that, with an
appropriately chosen time step and an early warning signal, intervention
can be calibrated in safety margins rather than after collapse. This
prevents any single civilisation from cornering the supply of critical
talent, and thereby preserves the competitive diversity that drives
long-run innovation.

The contribution is a reproducible, data-driven transition-rate model
that links OpenAlex publication records to a system of ordinary
differential equations (ODEs) ^\[6\]^. The model is intentionally
simple: it does not explain why a rate is high or low, but it identifies
which rate is closest to a threshold and therefore where early
intervention is most urgent.

# 2. Literature and conceptual framework

Researcher mobility has long been studied under the headings of brain
drain, brain circulation and brain gain ^\[7\]^. Thorn and Holm-Nielsen
argue that the mobility of researchers from developing countries can
become a gain when return migration and diaspora networks are supported,
but it can become a drain when local research environments cannot retain
or reproduce talent ^\[7\]^. Appelt et al., using a gravity framework
for 1996-2011, find that scientific collaboration, economic convergence
and visa restrictions are the strongest correlates of bilateral mobility
^\[2\]^. Their analysis shows that mobility is multi-directional: a
large share of researcher movement is better described as circulation
than as one-way migration.

The AI/ML literature has documented the same patterns at higher
resolution. MacroPolo\'s Global AI Talent Tracker finds that the United
States remains the leading destination for top-tier AI researchers,
while China and India are expanding domestic retention ^\[1\]^. AlShebli
et al. show that U.S.-China collaboration in AI is more impactful than
either country working alone, and that most mobile AI scientists retain
collaboration links with their origin country ^\[8\]^. Yuan et al. find
that the brain-drain problem for AI scientists is increasingly serious
in developing countries, and that the ties among AI elites are highly
clustered ^\[9\]^. These studies establish that AI/ML talent is mobile,
concentrated and strategically important.

What is missing is a formal link between individual transition rates and
the long-run viability of a research community. The concept of a minimum
viable population, introduced by Shaffer, captures the smallest isolated
population that has a high probability of persisting despite
demographic, environmental and genetic stochasticity ^\[10\]^.
Transferred to science, the equivalent idea is a minimum viable coauthor
pool: the smallest number of active researchers that can continue to
produce work at the field\'s observed coauthor intensity. Below that
pool, collaboration networks fragment, mentorship chains break, and the
field enters a self-reinforcing decline.

This framing generates four testable hypotheses. H1: Across all groups,
the equilibrium active pool exceeds the minimum viable threshold, but
the distance to the threshold varies widely. H2: Dropout is the
transition rate with the largest negative effect, because attrition
removes researchers from every compartment. H3: The largest positive
transition lever is domestic hit generation (h_D), followed by
principal-investigator promotion (p_D). H4: Smaller civilisations, and
those with older cohort structures, sit closer to their PNR.

A final literature stream emphasises the consequences of concentrated
research agendas. Aghion et al. provide evidence that the relationship
between competition and innovation follows an inverted-U shape, with the
strongest innovative performance in markets that are neither perfectly
collusive nor perfectly monopolistic ^\[5\]^. Translated to global
science, this suggests that a single dominant region or a tight
oligopoly may slow the rate of methodological and conceptual
breakthroughs. Maintaining multiple centres of AI/ML research is
therefore not merely a distributional concern; it may increase the
long-run productivity of the field.

## 2.1 Researcher mobility

Researcher mobility has been studied from several angles. A large
empirical literature documents net flows of scientists and inventors
across countries and regions, often using patent or publication records
^\[11\]^. That work consistently finds that the United States, parts of
Europe and, increasingly, China and India are central nodes in the
global mobility network. It also finds that mobility responds to wages,
funding, institutional quality and career prospects, but that it is
path-dependent: once a community loses its senior cohort, it becomes
harder to rebuild.

## 2.2 Scientific collaboration and diversity

A second strand of work emphasises the structure of scientific
collaboration. Multi-university and international teams now produce a
growing share of high-impact research, and the geographic dispersion of
teams does not necessarily reduce their impact ^\[12\]^. This literature
suggests that global AI/ML is not a zero-sum race in which every
researcher in one location subtracts from another. It also implies that
sustaining a domestic community is compatible with, rather than opposed
to, international collaboration. The question is therefore not whether
researchers move, but whether the domestic pipeline that replaces them
is robust enough to keep the field alive.

## 2.3 Minimum viable populations and critical thresholds

The third relevant literature concerns population viability and critical
thresholds. In conservation biology, the minimum viable population
concept identifies the smallest number of individuals that can sustain a
population in the wild ^\[10\]^. We borrow that intuition and apply it
to a research community. A field needs a minimum number of active
researchers to produce work, train successors, and maintain peer review
and conference communities. Below that threshold, positive feedback
loops weaken: fewer researchers produce fewer students, fewer students
produce fewer researchers, and the community enters a downward spiral.
This is the PNR.

## 2.4 This paper\'s framework

The present paper bridges these literatures by estimating transition
rates from open bibliometric data and embedding them in a compartment
model. The model is closest in spirit to Stephan\'s economic model of
science, in which researchers move through career stages and respond to
incentives ^\[3\]^, but it adds a civilisational partition and a minimum
viable coauthor threshold. The civilisational partition reflects the
clustering of career incentives, language, funding systems and
institutional networks along civilisational lines, which shape mobility
beyond national borders alone ^\[4\]^. It also draws on the
innovation-systems literature, in which technological trajectories are
shaped by sectoral and national systems of innovation
^\[13\]\ \[14\]\ \[15\]\ \[16\]^. In that view, technological change is
path-dependent and distributed: routines, organisations and institutions
co-evolve, so the loss of a research community is not merely a decline
in headcount but a reduction in the variety from which future
trajectories can be generated. The PNR is therefore an
innovation-systems problem: once a community falls below the minimum
scale needed to sustain distinct research programmes, the path-dependent
process of search and selection that produces new trajectories is
impaired. This connects that macro-level, innovation-systems view of
path-dependent technological change to individual career-transition
data: the transition rates and PNR distances reported below can be read
as an empirical early-warning indicator of whether a particular
civilisational innovation system retains enough researchers to sustain a
distinct technological trajectory. The result is a framework that can be
updated as new data arrive and can compare the fragility of different
research communities using a common metric. Because it is built on open
bibliometric data and transparent transition rates, the model can be
replicated and extended by other researchers and by policymakers who
need a common language for discussing mobility and capacity.

# 3. Data and grouping

We extracted AI/ML works and author histories from the OpenAlex API for
subfield \`subfields/1702\` (Artificial Intelligence), using works
published between 2000 and 2023 ^\[6\]^. OpenAlex provides open, CC0
bibliographic metadata including authors, affiliations, countries,
publication dates, venues and citation links. We built author histories
by following each author\'s sequence of works and affiliations,
assigning them to a country for each work and then to a civilisation by
the modal country of their recorded affiliations. The cohort is
restricted to authors whose career-start year (first observed AI/ML
publication year) is between 2000 and 2016 and who have at least two
AI/ML works in the 2000-2023 window. An author is treated as active if
they have at least one AI/ML work in 2020-2023, and as having dropped
out otherwise. An author is classified as a principal investigator (PI)
if their first last-author paper appears during the observation window;
single-authored papers are treated as last-author papers so that
culturally varying coauthorship norms do not bias the seniority proxy
^\[3\]^. A \'hit\' work is a paper whose citation count places it in the
top 10% of AI/ML works in the same publication year, observed within the
first eight career years, regardless of the author\'s position on the
author list. The abroad flag is set if the author is affiliated with a
non-origin civilisation within the first six career years. The final
groups are: United States, Anglosphere ex-US, Continental Europe, Sinic,
Japanese, Hindu, Islamic, Other Western, and Other Civilizations.

## 3.1 Country-to-civilisation mapping

The grouping follows Huntington\'s civilisation taxonomy but is adjusted
for sample-size and mobility reality in AI/ML. The United States is
separated from the broader Anglosphere because it is the dominant
destination for AI/ML researchers and because its higher-education and
funding systems differ systematically from those of other
English-speaking countries. Continental Europe is kept distinct from the
Anglosphere because intra-European mobility and EU research funding
create a separate mobility bloc. Latin American, Orthodox and
sub-Saharan African countries are merged into Other Civilizations
because their AI/ML author counts in the sample are too small to
estimate stable transition rates separately. These civilisation labels
are operational categories based on observed publication-affiliation
patterns; they are not normative claims about cultural or political
identity, and they are reported in full in Supplementary Material.
Civilisation-level categories have also been shown to predict
large-scale digital-communication networks ^\[17\]^ and country-capacity
clusters in scientific mobility and collaboration ^\[18\]^, which
supports the use of this aggregation as a cross-national research
heuristic.

## 3.2 Sample selection and variable definitions

Authors enter the cohort if their first observed AI/ML publication year
is between 2000 and 2016 and they have at least two AI/ML works in the
2000-2023 observation window. The career-start year is the first
observed AI/ML publication year. Authors with exclusively unknown
affiliations or with all affiliations outside the mapped countries are
excluded. For each author we record the country of the majority of their
affiliations and the civilisation to which that country maps. An author
is active if they have at least one AI/ML work in 2020-2023; otherwise
they are recorded as having dropped out. A hit is a paper in the top 10%
of AI/ML citations for its publication year, observed within the first
eight career years, regardless of the author\'s position. A PI is an
author whose first last-author paper appears during the observation
window; single-authored papers are treated as last-author papers. The
abroad flag is set if the author appears in a non-origin civilisation
within the first six career years. The final cohort of 723,647 authors
is a model-implied sample extracted from OpenAlex; the objective is to
build a reproducible pipeline and demonstrate the transition-rate
framework, not to provide a definitive census.

## 3.3 OpenAlex coverage and known biases

OpenAlex coverage has improved over time but remains incomplete for
works before 2000 and for non-English publications. Author
disambiguation is imperfect, especially for common names and authors
with multiple name variants. Affiliation metadata are supplied by
publishers and are sometimes missing or refer to the primary institution
rather than the country of residence. For these reasons, the absolute
counts reported here are lower bounds on the true global AI/ML
workforce. The analysis nevertheless preserves relative comparisons
across civilisations because the same extraction rules are applied
uniformly. Replication from a clean OpenAlex snapshot should produce
very similar transition rates and point-of-no-return rankings even if
absolute counts shift.

Table 1 reports the size and composition of the extracted cohort. The
Sinic and Continental Europe groups contribute the largest number of
works, followed by the United States and the Anglosphere ex-US. The
Japanese and Other Western groups are the smallest in terms of author
counts. The cohort of 723,647 authors is a model-implied sample
extracted from the OpenAlex snapshot; absolute counts should be
interpreted as model-implied stocks rather than population totals, and
the bootstrap intervals reported below give a more honest picture of the
uncertainty around those stocks. The relative sizes are nevertheless
informative. A civilisation with a small cohort but a low coauthor
intensity can be more resilient than a larger civilisation with a high
coauthor intensity, because the former needs fewer distinct PI groups to
sustain its output. This is why the minimum viable coauthor threshold
and the equilibrium active pool must be compared jointly.

  -----------------------------------------------------------------------------------------------------------
  **Group**       **n**    **works**   **active**   **hits**   **pis**   **career_start_mean**   **abroad**
  --------------- -------- ----------- ------------ ---------- --------- ----------------------- ------------
  Anglosphere     64122    700342      28218        35822      43628     2007.3                  16233
  ex-US                                                                                          

  Continental     168911   1766329     74004        90322      111466    2008.0                  26060
  Europe                                                                                         

  Hindu           28069    225684      17047        12043      19185     2011.3                  4289

  Islamic         51043    387001      29703        20435      35558     2011.4                  8131

  Japanese        32007    293437      11846        9915       18543     2006.7                  4417

  Other           50240    371952      23671        17128      32449     2009.2                  9136
  Civilizations                                                                                  

  Other Western   4397     49748       1981         2646       2848      2007.4                  1414

  Sinic           190051   1589023     103673       61738      140701    2008.7                  23956

  United States   134807   1298250     58969        74972      91029     2007.3                  27420
  -----------------------------------------------------------------------------------------------------------

*Table 1. Descriptive statistics for the extracted AI/ML cohort by
civilisation group. Civilisation labels are operational aggregations of
OpenAlex country-affiliation patterns and do not imply normative
cultural or political classification.*

# 4. Methods

## 4.1 Compartment model

Each civilisation is represented by six compartments: domestic
early-career researchers (D), abroad early-career researchers (A),
domestic hit researchers (H_D), abroad hit researchers (H_A), domestic
principal investigators (P_D), and abroad principal investigators (P_A).
Transition rates are early-career outflow (α), return (β), hit
generation at home and abroad (h_D and h_A), PI promotion at home and
abroad (p_D and p_A), and dropout from all compartments (d). The
equations are:

$${\frac{dD}{dt} = IP_{D}\  + \ \beta A\  - \ (\alpha\  + \ h_{D}\  + \ d)D}{\frac{dA}{dt} = \alpha D\  - \ (\beta\  + \ h_{A}\  + \ d)A}{\frac{dH\_ D}{dt} = h_{D}D\  + \ \beta H_{A}\  - \ (p_{D}\  + \ d)H_{D}}{\frac{dH\_ A}{dt} = h_{A}A\  - \ (\beta\  + \ p_{A}\  + \ d)H_{A}}{\frac{dP\_ D}{dt} = p_{D}H_{D}\  + \ \beta P_{A}\  - \ dP_{D}}{\frac{dP\_ A}{dt} = p_{A}H_{A}\  - \ (\beta\  + \ d)P_{A}}$$

The model makes several simplifying assumptions. It treats each
civilisation as a single aggregate, ignoring cross-civilisation
collaboration and spillovers. It assumes constant per-year transition
rates and a continuous-time Markov structure. Career stages are
collapsed into the three observed layers: early-career, hit researchers
and PIs. These simplifications are necessary to keep the model estimable
from OpenAlex and to make the point-of-no-return calculation
transparent. They also mean that the model is best interpreted as a
stylised early-warning device, not as a realistic demographic
projection.

## 4.2 Endogenous inflow

New entrants are modelled as a function of the domestic PI stock. The
linear form is $IP_{D} = I_{0} + rP_{D}$, where I_0 is the exogenous
entry rate, r is the PI reproduction rate, and r is capped at 0.50× the
stability-critical value (safety factor 0.50); the most constrained
fitted group realises 0.40×. A saturating alternative,
$IP_{D} = I_{0} + \frac{rP_{D}}{1\  + \ \varepsilon \times P_{D}}$, is
reported as a robustness check. The PI-driven inflow captures the idea
that senior researchers train graduate students, attract postdoctoral
researchers, and create the institutional infrastructure that produces
the next cohort. This is a strong assumption because it ignores
cross-border recruitment and non-PI sources of new researchers, but it
provides a transparent lower bound: if the domestic PI stock falls, the
model predicts a decline in new entrants. The safety factor prevents the
model from producing runaway growth when the observed r exceeds the
critical value, which is a common empirical finding because observed
recruitment is bounded by the data window.

## 4.3 Minimum viable coauthor threshold

For each group we computed the mean number of authors per work (c̄) and
the median number of distinct last-author groups observed per recent
year (k). The minimum viable domestic active pool is
$M\  = \ k\  \times \ c\bar{}$. When the equilibrium active pool
$T\  = \ D\  + \ H_{D}\  + \ P_{D}$ falls below M, the community can no
longer produce works at the observed coauthor intensity. In this sense,
falling below M is a sufficient condition for collapse, not a necessary
one; external shocks can push a community below viability even when the
equilibrium active pool remains above M. The threshold is deliberately
conservative: it assumes that each new work requires at least k distinct
PI groups and that each work has the average number of coauthors. This
overstates the number of distinct actors needed for a viable field,
which means that M is a soft lower bound and that observed margins are
probably smaller than they appear. A community with a margin just above
M is therefore more fragile than the number itself suggests.

## 4.4 Estimation, equilibrium and sensitivity

Transition rates are estimated as constant per-year hazards from
observed proportions within the cohort. For each group and each
transition, the rate is the ratio of observed transitions to the total
exposure time spent in the source compartment during the observation
window, using a Laplace pseudocount of 1 for each outcome so the
smoothed proportion is (successes + 1)/(n + 2). This avoids zero-rate
singularities when the cohort is small. Because the data are
right-censored at the end of the observation period, the resulting rates
are lower bounds on true long-run hazards; equilibrium solutions
therefore tend to be conservative. The non-linear steady-state equations
are solved numerically using a trust-region Newton method with
analytically supplied Jacobians. Elasticities are computed by perturbing
each rate by 1%, re-solving, and taking the percentage change in the
target stock. For point-of-no-return analysis we scale each rate until
the active pool T reaches its coauthor threshold M, or the domestic PI
pool P_D reaches k distinct last-author groups as a lower-bound PI-pool
threshold, and record the critical factor and its proximity, \|critical
factor − 1\|. A rate whose critical factor lies inside the scan window
and is close to 1.0 is the most fragile lever for that group. All
counterfactuals are mechanical perturbations of the fitted rates; they
reveal which transitions the model treats as sensitive, not the causal
impact of real-world policies.

## 4.5 Limitations

The main limitations are data quality and model scope. OpenAlex country
metadata are noisy, especially for older works and for authors with
multiple affiliations. Career stages are inferred from authorship order
and are imperfect proxies. The model does not include cross-civilisation
knowledge spillovers, bilateral migration costs, or firm-level mobility.
Finally, the assumption of constant rates is a strong approximation over
a 23-year window. We therefore emphasise rank-order and relative
sensitivity rather than point forecasts.

## 4.6 Annual transition-rate estimation and projection

The steady-state model in Sections 4.1-4.4 treats rates as constants. To
test whether the same framework can be used for short-run monitoring, we
reconstructed year-by-year compartment membership from the cohort data.
For each author and year we inferred location as domestic if the author
was in the origin civilisation and abroad otherwise. From these states
we computed annual transition counts for the six compartments, applied
Laplace smoothing with a pseudocount of 1 for each possible destination,
and derived the probabilities that map to α, β, h_D, h_A and p_D, p_A.
Dropout (d) is not directly observed year-by-year in the training window
because final attrition is right-censored before 2023, so we import the
cohort-level per-year hazard from the full-career data and treat it as a
constant annual rate for each group. Inter-civilisation flows are
approximated by assigning each abroad author-year to the author\'s
recent_group as the destination civilisation.

For the 2017-2026 projection we fit a linear trend to the observed
2000-2016 rates for each group and rate. If fewer than four observations
were available or the fit explained less than 10% of the variance, the
historical mean was used instead. Projected rates were clipped to values
between 0 and 1. Projected annual dropout was capped at 1.5 times the
90th percentile of observed annual dropout rates in the 2000-2016
training period. Projected total inflows were apportioned across
compartments using the first-compartment distribution observed over the
2000-2016 training period. Population composition was projected forward
with the discrete-time recursion N(t+1) = N(t)P(t) + b(t+1), where P(t)
is a 6×6 row-stochastic-in-expectation matrix that preserves dropout
mass: the row sum is 1 − d after scaling outgoing rates. This discrete
step is the operational counterpart of the continuous-time ODE; with an
annual dt it provides an early-warning signal one year ahead.

We compare the 2017-2023 projection with the observed annual stock. The
comparison is limited to years that have observed data, and the observed
stock is reindexed to the full group-year-compartment grid so that
zero-observed cells are not omitted from the accuracy metrics. Accuracy
is reported as root mean square error (RMSE) and mean absolute
percentage error (MAPE); MAPE here is computed against count_obs + 1 to
avoid division by zero and is therefore a conservative, non-standard
measure.

## 4.7 Correction pressures and theoretical bounds

The annual estimates contain several regularising pressures that bound
the model away from instability and fabrication. Laplace smoothing adds
a uniform prior of 1 to every possible destination, which shrinks sparse
cells toward 1/(number of destinations) and prevents zero-probability
singularities when a transition is unobserved in a small group-year. It
is equivalent to a weak Dirichlet prior and is a standard regulariser
for sparse multinomial transitions.

Clipping projected rates to values between 0 and 1 is a feasibility
pressure: rates outside the probability simplex are inadmissible. The
annual dropout rate is anchored to the cohort-level per-year hazard
rather than extrapolated from year-to-year transitions, because final
attrition is right-censored in the training window. The inflow
apportionment pressure keeps the composition of new entrants aligned
with the most recently observed recruitment pattern, rather than
inventing a new distribution. Finally, the endogenous inflow is capped
at a safety factor of 0.50 relative to the critical reproduction rate
(the most constrained fitted group realises 0.40), which keeps the
system inside the stability boundary. Together these pressures embody
the principle that projection should stay within observed empirical
support and within theoretical stability limits; they are not arbitrary
adjustments but transparent bounds that can be tightened or relaxed as
more data become available.

# 5. Results

Table 2 reports the equilibrium domestic active pool T, the minimum
viable threshold M, and the endogenous inflow parameters for the 9
groups. All groups remain above their threshold under the fitted model,
but margins differ by an order of magnitude. The Sinic, Continental
Europe, United States groups show the largest equilibrium active pools,
reflecting large cohorts and relatively low coauthor-intensity
thresholds. The Other Western group has the smallest equilibrium active
pool, and Other Western has the narrowest safety margin, although both
still exceed their minimum viable coauthor pool. The ratio T/M is a
summary resilience indicator, but absolute margin is the more direct
measure of proximity to the PNR.

  -----------------------------------------------------------------------------------------------------
  **Group**       **T_eq**   **M**   **Margin**   **I0**   **r**     **r_obs**   **r_crit**   **T/M**
  --------------- ---------- ------- ------------ -------- --------- ----------- ------------ ---------
  Anglosphere     67532      3183    64348        1886     0.06326   0.08646     0.12652      21.21
  ex-US                                                                                       

  Continental     195095     3923    191172       4968     0.05949   0.08914     0.11899      49.72
  Europe                                                                                      

  Hindu           53434      2249    51185        826      0.02729   0.08606     0.05457      23.76

  Islamic         88522      2255    86267        1501     0.03176   0.08444     0.06352      39.26

  Japanese        29332      1793    27539        1134     0.10154   0.10154     0.25545      16.36

  Other           59355      2069    57286        1478     0.06620   0.09108     0.13240      28.69
  Civilizations                                                                               

  Other Western   4824       1601    3223         129      0.05992   0.09082     0.11984      3.01

  Sinic           303935     3129    300805       5590     0.04199   0.07946     0.08399      97.12

  United States   147067     1844    145223       3965     0.06202   0.08711     0.12404      79.75
  -----------------------------------------------------------------------------------------------------

*Table 2. Equilibrium domestic active pool, minimum viable threshold,
and endogenous inflow parameters.*

Figure 1 visualises the gap between equilibrium and threshold. The
Sinic, Continental Europe, United States groups display the largest
equilibrium active pools, while the Other Western group is the smallest.
However, the point-of-no-return metric is not the absolute level of T
but the distance between T and M, which reflects both the stock of
researchers and the coauthor intensity of the field. Groups with high T
but also high c̄ and k can still be fragile if their margin is small.

![](media/image1.png){width="5.8in" height="3.19in"}

*Figure 1. Equilibrium domestic active pool (T) and minimum viable
coauthor threshold (M) by group.*

Table 3 shows the three transition-rate elasticities with the largest
absolute impact on T for each group. Dropout (d) is the largest negative
lever in every group; its active-pool elasticity ranges from -2.79 to
-2.27. Attrition removes researchers from every compartment, so a
proportional increase in d produces a larger proportional decline in the
active pool. The largest positive transition lever is domestic hit
generation (h_D), followed by principal-investigator promotion (p_D).
Early-career outflow (α) has a modest negative effect in most groups,
but because it moves researchers to the abroad compartment rather than
removing them entirely, its direct impact on the domestic active pool is
smaller than that of dropout. There is notable heterogeneity in the
magnitude of the positive levers. The United States group shows the
strongest response to PI promotion (p_D), indicating that improving the
promotion of hit researchers to PIs is an especially efficient way to
expand the domestic active pool in that community. In the largest
groups, p_D remains positive but its relative effect is smaller, because
the active pool is already large and a proportional change in promotion
has less marginal impact.

  ---------------------------------------------------------------------------------------------
  **Group**       **1st      **1st          **2nd      **2nd          **3rd      **3rd
                  rate**     elasticity**   rate**     elasticity**   rate**     elasticity**
  --------------- ---------- -------------- ---------- -------------- ---------- --------------
  Anglosphere     d          -2.68          h_D        0.47           p_D        0.34
  ex-US                                                                          

  Continental     d          -2.68          h_D        0.39           p_D        0.35
  Europe                                                                         

  Hindu           d          -2.54          h_D        0.34           p_D        0.21

  Islamic         d          -2.58          h_D        0.37           p_D        0.22

  Japanese        d          -2.27          h_D        0.39           p_D        0.27

  Other           d          -2.79          h_D        0.49           p_D        0.31
  Civilizations                                                                  

  Other Western   d          -2.74          h_D        0.37           p_D        0.35

  Sinic           d          -2.69          h_D        0.40           p_D        0.26

  United States   d          -2.67          h_D        0.45           p_D        0.36
  ---------------------------------------------------------------------------------------------

*Table 3. Top transition-rate elasticities for domestic active pool T.*

Table 4 reports, for each group, the single rate that reaches the
active-pool threshold with the smallest proportional change. The Other
Western group is the most fragile: I0 must be multiplied by 0.332× its
current value (equivalent to a 67% proportional reduction) to drive the
active pool to its minimum viable threshold. I0 is the closest
point-of-no-return lever for the active researcher pool in every group.
This is consistent with a recruitment-driven view of scientific
communities: if the pipeline of new researchers shuts or slows, the
active pool eventually falls below the minimum viable coauthor pool
regardless of how efficient return or promotion becomes. A global
retention programme that reduces dropout would benefit all groups, but
the most vulnerable groups may also need an expansion of the exogenous
entry rate.

  ----------------------------------------------------------------------------------------
  **Group**       **Target**        **Rate**    **Current**   **Critical   **Proximity**
                                                              factor**     
  --------------- ----------------- ----------- ------------- ------------ ---------------
  Other Western   domestic_active   I0          129.3235      0.332        0.668

  Japanese        domestic_active   I0          1134.4064     0.061        0.939

  Anglosphere     domestic_active   I0          1885.9412     0.047        0.953
  ex-US                                                                    

  Hindu           domestic_active   I0          825.5588      0.042        0.958

  Other           domestic_active   I0          1477.6471     0.035        0.965
  Civilizations                                                            

  Islamic         domestic_active   I0          1501.2647     0.025        0.975

  Continental     domestic_active   I0          4967.9706     0.020        0.980
  Europe                                                                   

  United States   domestic_active   I0          3964.9118     0.013        0.987

  Sinic           domestic_active   I0          5589.7353     0.010        0.990
  ----------------------------------------------------------------------------------------

*Table 4. Closest PNR for the active researcher pool by group.*

Figure 2 ranks groups by their closest point-of-no-return sensitivity.

![](media/image2.png){width="5.8in" height="3.2222222222222223in"}

*Figure 2. Closest point-of-no-return proximity by group. Smaller values
mean a smaller proportional change in the listed rate is required to
reach the threshold for the stated target pool.*

## 5.1 Saturating recruitment extension

We also test a saturating recruitment function in which each additional
PI adds fewer entrants. With the capacity parameter calibrated to
observed PI stocks, the saturating equilibrium is below 0.001% for every
group at the displayed precision, so the linear safety-factor bound
remains the operative constraint. Table 5 reports the fitted epsilon
values; the near-zero differences show that the results are not driven
by unbounded linear growth, but they do not rule out stronger saturation
at higher PI densities.

  -----------------------------------------------------------------------
  **Group**         **Linear T**      **Saturating T**  **ε**
  ----------------- ----------------- ----------------- -----------------
  Anglosphere ex-US 67532             67532             0.00000

  Continental       195095            195095            0.00000
  Europe                                                

  Hindu             53434             53434             0.00001

  Islamic           88522             88522             0.00001

  Japanese          29332             29332             0.00001

  Other             59355             59355             0.00001
  Civilizations                                         

  Other Western     4824              4824              0.00007

  Sinic             303935            303935            0.00000

  United States     147067            147067            0.00000
  -----------------------------------------------------------------------

*Table 5. Equilibrium T under linear and saturating PI-driven inflow.*

The closest point-of-no-return lever is the same under the saturating
alternative for every civilisation: exogenous entry (I0) is the rate
that requires the smallest proportional change to push the active pool
to its minimum viable threshold. Table 5a reports the proportional
factor and proximity for the active-pool threshold under both
assumptions. The rank order of civilisational fragility is preserved
(Spearman ρ = 1.0), and the absolute proximity values move in the same
direction. This confirms that the policy ranking---exogenous entry
first, then dropout, then domestic promotion and return---is robust to
replacing the linear feedback with a saturating one.

  --------------------------------------------------------------------------------------------------------------------------------------------------------------
  **origin_group**   **linear_closest**   **linear_factor**   **linear_proximity**   **saturating_closest**   **saturating_factor**   **saturating_proximity**
  ------------------ -------------------- ------------------- ---------------------- ------------------------ ----------------------- --------------------------
  United States      I0                   0.0125              0.9875                 I0                       0.0112                  0.9888

  Anglosphere ex-US  I0                   0.0471              0.9529                 I0                       0.0424                  0.9576

  Continental Europe I0                   0.0201              0.9799                 I0                       0.0178                  0.9822

  Sinic              I0                   0.0103              0.9897                 I0                       0.0089                  0.9911

  Japanese           I0                   0.0611              0.9389                 I0                       0.0585                  0.9415

  Hindu              I0                   0.0421              0.9579                 I0                       0.0344                  0.9656

  Islamic            I0                   0.0255              0.9745                 I0                       0.0212                  0.9788

  Other Western      I0                   0.3319              0.6681                 I0                       0.3074                  0.6926

  Other              I0                   0.0349              0.9651                 I0                       0.0312                  0.9688
  Civilizations                                                                                                                       
  --------------------------------------------------------------------------------------------------------------------------------------------------------------

*Table 5a. Closest PNR lever and proximity under linear and saturating
endogenous inflow (active-pool threshold).*

## 5.2 Historical counterfactual

Table 6 compares the equilibrium that would have emerged if the
transition rates estimated for the early career window (2000-2010) or
the late window (2011-2016) had persisted indefinitely. The late window
is shorter and its rates are estimated from younger cohorts, so the
comparison should be read as a sensitivity exercise rather than a
forecast. Only 9 groups have enough dual-window support for reliable
rate estimation in both windows; they are listed in the table. Groups
that would see smaller safety margins under late-window rates: Japanese.
Groups that would see larger safety margins under late-window rates:
Islamic, Hindu, Sinic, Continental Europe, Other Civilizations, United
States, Anglosphere ex-US, Other Western. This pattern shows that global
AI/ML mobility is not moving in a single direction; different
civilisations are on different trajectories, and a uniform policy
response would ignore this heterogeneity. Because the late cohort is
younger, the late-window equilibrium is likely biased downward for
groups where career progression has not yet run its course. Even so, the
exercise shows that the current regime is not the only possible one,
which is why counterfactual policy analysis is useful.

  ---------------------------------------------------------------------------------
  **Group**       **T        **T late** **ΔT (%)** **Margin   **Margin   **Δ
                  early**                          early**    late**     margin**
  --------------- ---------- ---------- ---------- ---------- ---------- ----------
  Anglosphere     64779      75245      16.2       61596      72062      10466.2
  ex-US                                                                  

  Continental     177460     231958     30.7       173536     228035     54498.4
  Europe                                                                 

  Hindu           23397      110377     371.8      21148      108128     86979.8

  Islamic         37899      186245     391.4      35644      183990     148346.1

  Japanese        31781      25052      -21.2      29989      23259      -6729.5

  Other           42881      91930      114.4      40812      89861      49049.3
  Civilizations                                                          

  Other Western   4450       5731       28.8       2849       4129       1280.2

  Sinic           278159     360991     29.8       275030     357861     82831.4

  United States   139401     169788     21.8       137557     167943     30386.5
  ---------------------------------------------------------------------------------

*Table 6. Historical counterfactual: equilibrium active pool and safety
margin under early versus late transition-rate regimes.*

Figure 3 shows the change in safety margin between the early and late
transition-rate regimes.

![](media/image3.png){width="5.8in" height="3.2222222222222223in"}

*Figure 3. Change in safety margin between early and late
transition-rate regimes. Positive values mean the late-window rates
would produce a larger safety margin than the early-window rates if they
persisted; negative values mean the margin would shrink. The comparison
is across two point estimates; uncertainty is substantial because the
two windows have different cohort sizes and the steady-state model does
not capture policy shocks.*

## 5.3 Policy counterfactuals

Table 7 reports the single mechanical counterfactual with the largest
margin gain per 10% lever change for each group. Reducing dropout is the
dominant positive lever for every civilisation, which is consistent with
the elasticity results in Table 3. The gain from a roughly 10%
proportional reduction in d ranges from about 567 additional active
researchers for the Other Western group to about 34739 for the Sinic
group, reflecting differences in cohort size and baseline attrition. No
other single lever comes close to dropout reduction in terms of
simulated margin gain per unit proportional change, although
combinations of levers may be more efficient for some groups. The
results also imply that policy need not focus on blocking early-career
outflow. Reducing attrition among researchers who remain in the domestic
system is a more efficient way to protect the active pool than
preventing researchers from going abroad, because a researcher abroad is
still in the global AI/ML system and may return. For the smallest
groups, increasing the exogenous entry rate or improving the promotion
of hit researchers to PIs can add additional margin, but dropout
reduction remains the first-order model-implied target.

  -------------------------------------------------------------------------------
  **Group**       **Lever**   **Direction**   **Change    **Margin    **Gain per
                                              (%)**       gain**      10%**
  --------------- ----------- --------------- ----------- ----------- -----------
  Anglosphere     d           decrease        -10         7660        7659.7
  ex-US                                                               

  Continental     d           decrease        -10         22093       22093.1
  Europe                                                              

  Hindu           d           decrease        -10         6184        6184.2

  Islamic         d           decrease        -10         10239       10238.9

  Japanese        d           decrease        -10         3194        3193.8

  Other           d           decrease        -10         6723        6723.1
  Civilizations                                                       

  Other Western   d           decrease        -10         567         567.3

  Sinic           d           decrease        -10         34739       34739.2

  United States   d           decrease        -10         16560       16560.4
  -------------------------------------------------------------------------------

*Table 7. Top positive mechanical counterfactual per group, measured by
margin gain per 10% proportional lever change.*

We also evaluated multi-lever policy packages for the three
smallest-margin groups. The package with the largest margin gain in each
group was: Other Western (retention: +616 active researchers); Japanese
(return_plus_retention: +3369 active researchers); Hindu (retention:
+6536 active researchers). These packages combine dropout reduction with
return or PI-pipeline levers, showing that the framework can compare
multi-lever interventions as well as single-rate perturbations.

## 5.4 Uncertainty

Supplementary Table 5 reports bootstrap 95% confidence intervals for the
equilibrium active pool T and the domestic PI pool P_D. The intervals
are wide, reflecting the model-implied cohort scale and the
extrapolation from observed author-career exposure to long-run steady
states. For some groups the upper bound is an order of magnitude larger
than the lower bound, indicating that the equilibrium is sensitive to
resampling variation in the transition rates. This uncertainty should be
interpreted as a warning against over-interpreting point estimates and
as a reason to view the point-of-no-return distances as indicative
rather than precise thresholds. Despite the width, the lower bounds for
most groups remain above the minimum viable threshold, which supports
the qualitative conclusion that all groups are currently above the PNR.
For the smallest groups the lower bound is closer to M, reinforcing the
need for continued monitoring and for policy buffers.

Figure 4 displays the bootstrap intervals graphically.

![](media/image4.png){width="5.8in" height="3.1780522747156605in"}

*Figure 4. Bootstrap 95% confidence intervals for equilibrium T by
group.*

## 5.5 Synthesis

Taken together, the results provide a consistent picture. Exogenous
entry and dropout are the two rates that most strongly determine the
long-run viability of an AI/ML research community. Communities that are
large in absolute terms are not necessarily safe if their coauthor
intensity is high; conversely, small communities can be robust if their
attrition is low and their recruitment pipeline is stable. The
historical counterfactual shows that the current regime is not
preordained: a shift in transition rates at the start of the AI boom
would have produced different steady states for different civilisations.
This is precisely why the framework is useful: it identifies which rate
in which community is closest to a threshold, allowing policy to
intervene before rather than after a collapse. The policy message is
therefore both diagnostic and preventative. By tracking transition rates
rather than net flows, policymakers can see which civilisation is
approaching a PNR and which lever offers the largest safety margin per
unit of effort.

## 5.6 Annual transition rates and inter-civilisation flows

Figure 5 plots the observed 2000-2016 transition rates and the projected
2017-2026 rates for each civilisation. Rates are displayed by group and
by transition type, so that the reader can see whether a particular
transition is trending toward a boundary. Because the projections are
linear trend fits regularised by the correction pressures described in
Section 4.7, they are not forecasts of specific future events; they are
the model\'s one-year-ahead extrapolation of the recent historical
trajectory.

![](media/image5.png){width="6.0in" height="5.1962259405074365in"}

*Figure 5. Observed (solid) and projected (dashed) transition rates by
civilisation, 2000-2026.*

The mean observed annual transition rates by group between 2000 and
2016, distinguishing early-career outflow (α), return (β), domestic and
abroad hit generation (h_D, h_A), PI promotion (p_D), dropout (d), and
total inflow (I_total), are provided in Supplementary Table 3.
Similarly, the cross-origin-destination pairs with the largest
accumulation of abroad author-years are listed in Supplementary Table 4.
These supplementary tables keep the main text focused on the PNR and
policy conclusions while preserving the empirical detail needed for
replication and extension.

Figure 6 shows the cross-civilisation accumulation of abroad
author-years. Rows represent the origin civilisation and columns
represent the destination civilisation, approximated by the author\'s
recent_group while abroad. Origin-destination cells with the same
civilisation and destinations labelled Unknown are excluded because the
reconstruction cannot observe the actual host civilisation. The
remaining cells are a lower-bound proxy for the true inter-civilisation
pipelines.

![](media/image6.png){width="5.8in" height="4.714864391951006in"}

*Figure 6. Cross-civilisation abroad author-year accumulation by origin
(rows) and destination (columns) (same-civilisation cells and Unknown
destinations excluded; lower-bound proxy).*

## 5.7 Out-of-sample projection, 2017-2023

The 2017-2023 projection is compared with observed annual stocks in
Figure 7. Stock-level accuracy is RMSE 10190.39 and MAPE 129.0% (a
non-standard, conservative measure computed against count_obs + 1 to
avoid division by zero). These stock-level metrics are not a fair test
of the model: the estimation cohort is fixed to authors whose careers
began by 2016, so observed post-2016 counts cannot include the new
entrants that the projection adds each year. The projection therefore
necessarily diverges from observed stocks for any civilisation with
positive recruitment. A cleaner validation is at the rate level: the
projected transition rates have RMSE 0.0892 and MAE 0.0364, and the
model\'s skill relative to a historical-mean baseline is 0.99. By rate,
the best relative skill is for h_A (1.48× the historical-mean RMSE),
while the weakest is for p_D (0.66×). These figures show that the annual
layer captures rate drift at least as well as a naive mean forecast, and
should be read as a directional early-warning indicator of drift and
threshold proximity rather than as a precise population forecast.

Direction and threshold-alarm diagnostics support this interpretation.
Year-to-year direction agreement between projected and observed
compartment counts is 21.6%, ranging from Hindu to Japanese. For the
active pool T = D + H_D + P_D, the projection correctly classifies
whether T is below the minimum viable threshold M in 92.1% of
group-years (sensitivity 0.0%, specificity 100.0%). The observed
threshold-crossing group-years (n = 5) all occur for the smallest
civilisation in the post-2016 fixed cohort; they reflect the depletion
of that cohort as careers mature, not a projected collapse. The
projection, by construction, adds new entrants each year and therefore
does not predict such within-cohort depletion. A zero sensitivity in
this hold-out is thus a consequence of the fixed-cohort validation
design, not evidence that the model misses genuine collapse events.
These metrics confirm that the annual layer is useful for directional
and threshold-crossing surveillance, not for precise population counts.
The modest year-to-year direction-agreement value is expected for small
compartments and sparse transitions, and it reinforces that the
projection layer should be treated as a drift-and-threshold alarm rather
than a population forecast.

![](media/image7.png){width="6.0in" height="3.8268711723534556in"}

*Figure 7. Observed (solid) and projected (dashed) compartment counts by
civilisation, 2017-2023. The vertical dotted line marks the end of the
training period (2016).*

Detailed projection accuracy by civilisation and by compartment is
reported in Supplementary Material (Supplementary Tables 1 and 2). Among
compartments, the lowest RMSE is for H_A, while the highest RMSE is for
D and the highest MAPE is for D. P_D and H_D show larger errors because
small changes in PI and hit rates are amplified by the endogenous inflow
term.

## 5.8 Japan-specific compartment and transition-rate ladder

Figure 8 places the Japanese AI/ML research community in the compartment
model. The fitted equilibrium is T=29332 active researchers (D=16248,
H_D=5714, P_D=7370) against a minimum viable threshold of M=1793, so the
safety ratio T/M is 16.36. The right-hand ladder compares Japan\'s six
transition rates with those of the other civilisations. Japan\'s closest
PNR is the exogenous entry rate I0: if I0 were reduced to 6.1% of its
current level, the active pool would reach the minimum viable threshold.
In the fitted rates, early-career outflow (α=0.025) and domestic PI
promotion (p_D=0.064) are comparatively low, while return from abroad
(β=0.029) and domestic hit generation (h_D=0.040) are moderate. The
small absolute size of the abroad PI compartment (P_A) shows that few
Japanese researchers who leave eventually become PIs abroad, which makes
the domestic pipeline the critical margin.

![](media/image8.png){width="6.0in" height="3.3094969378827646in"}

*Figure 8. The Japanese AI/ML research community in the six-compartment
model, with a cross-civilisation ladder of fitted transition rates.
Japan is highlighted in the right-hand panel; longer bars represent
higher estimated rates.*

## 5.9 A combined model-evaluation view: T/M and PNR proximity

Figure 9 combines the long-run safety ratio T/M with the closest
point-of-no-return proximity for each civilisation. A point in the
lower-left corner has both a low equilibrium buffer and a small
proportional change needed to reach the threshold, so it is the most
fragile combination. Japan sits in this region alongside the \'Other
Civilizations\' group, even though its T/M ratio is above one. This dual
view is useful as a model-evaluation metric: a civilisation can have a
T/M ratio that looks comfortable but still be close to its PNR because
the PNR depends on the proportional change in the most sensitive rate,
not only on the level of T. Japan is presented here as an illustrative
case; the same diagnostic can be applied to any civilisation with
sufficient OpenAlex coverage.

![](media/image9.png){width="5.8in" height="4.511111111111111in"}

*Figure 9. Equilibrium safety ratio (T/M) versus closest
point-of-no-return proximity for all civilisations. Japan is shown in
red.*

# 6. Discussion

The results support a transition-rate view of research policy. Rather
than asking which country has a net inflow or outflow of researchers,
the model asks which rate must be altered to keep a community above its
minimum viable coauthor pool. This shift in focus has implications for
how we conceptualise brain drain, design science and technology policy,
and interpret civilisational diversity in AI/ML.

## 6.1 From net flows to transition rates

Most empirical studies of researcher mobility measure net flows, stocks
or collaboration counts ^\[11\]^. These indicators are useful for
describing patterns, but they do not reveal the mechanisms that sustain
or undermine a research community. A country may have a positive net
inflow while simultaneously losing its domestic PI base through
retirement or emigration, or it may have negative net flow but a healthy
pipeline of new entrants. The transition-rate framework disaggregates
these processes and shows that the same net flow can correspond to very
different vulnerability profiles. For example, a high early-career
outflow rate is less damaging than a high dropout rate because
researchers abroad may return; a high dropout rate removes researchers
from the system entirely. This distinction is lost in net-flow
accounting but is central to point-of-no-return analysis.

First, I0 is the closest point-of-no-return lever for the active
researcher pool in every group. A large proportional reduction in
baseline recruitment would drive most communities to their threshold
before mobility rates such as return or promotion became binding. This
is consistent with the observation that AI/ML fields depend on a
continuous pipeline of new graduate students and junior researchers
^\[1\]^. Policies that sustain that pipeline, such as doctoral funding,
visa routes for early-career researchers, and stable junior positions,
are therefore first-order defences against a PNR.

Second, among the mobility transition rates, dropout (d) is the dominant
negative lever; its active-pool elasticity ranges from -2.79 to -2.27
across groups, and in the policy counterfactuals a simulated reduction
in dropout yields the largest margin gain per unit proportional change.
Attrition matters because it removes researchers from every compartment,
not just one. A 10% proportional reduction in dropout expands the safety
margin more than comparably sized increases in return, hit generation or
promotion. For Other Western, the group with the smallest safety margin,
even modest attrition reductions may widen the margin. These
counterfactuals are mechanical perturbations of the fitted rates; they
identify the most sensitive transition levers, not the causal effect of
any specific policy programme.

Third, the largest positive transition lever is domestic hit generation
(h_D), followed by principal-investigator promotion (p_D). The United
States group shows the strongest response to PI promotion, suggesting
that for that community expanding the domestic PI pipeline is an
efficient lever. Return from abroad (β) is also positive for most
groups, though its effect is generally smaller than reducing attrition
directly. The implication for policy is that retention and promotion are
usually more efficient than trying to attract returnees, but a balanced
portfolio is still needed: a community without domestic PI growth cannot
reproduce itself through attrition reduction alone.

Fourth, the historical counterfactual shows that the late-window rates,
if they persisted, would alter equilibrium margins. Groups that would
see smaller safety margins under late-window rates: Japanese. Groups
that would see larger safety margins under late-window rates: Islamic,
Hindu, Sinic, Continental Europe, Other Civilizations, United States,
Anglosphere ex-US, Other Western. This pattern cautions against treating
AI/ML mobility as a single global trend. It also confirms that the model
can detect temporal changes in transition rates, which is the
prerequisite for the early intervention the framework is designed to
support.

The transition levers also interact in ways that a single-rate
elasticity cannot fully capture. For example, reducing dropout and
increasing PI promotion together are likely to have a larger effect than
the sum of the two individual perturbations, because more researchers
survive to become PIs and those PIs then train additional early-career
researchers through the endogenous inflow channel. Conversely, a
simultaneous fall in exogenous entry and a rise in dropout can push a
community to its threshold faster than either change alone. The model\'s
steady-state and one-at-a-time counterfactuals are therefore a starting
point; they identify the most sensitive margins but do not exhaust the
policy design space.

The connection to civilisational diversity is direct. Each group\'s
safety margin can be monitored over time, and interventions can be
adjusted before the margin disappears. Because the endogenous inflow is
capped at a safety factor of 0.50 relative to the critical reproduction
rate (the most constrained fitted group realises 0.40), the policy
recommendations are deliberately conservative: they do not push the
system toward instability. That bounded approach is consistent with the
goal of preserving diversity rather than maximising any single
country\'s share.

It is important to stress that the counterfactuals reported in Tables 3
and 7 are mechanical perturbations of the fitted transition rates, not
causal estimates of specific programmes. They identify which rates the
model treats as most sensitive, and therefore where empirical policy
evaluation is most urgent, but they do not by themselves show that a
given intervention would achieve the simulated change.

## 6.2 Civilisational diversity as an innovation input

A second implication concerns the normative status of civilisational
diversity. We treat diversity as an input to innovation rather than as a
distributional afterthought ^\[19\]^. A monocentric or tight-oligopoly
structure in AI/ML may produce short-run efficiency gains through scale
and agglomeration, but it also raises the risk of methodological
lock-in, selection bias in training data, and reduced error correction.
It is also an evolutionary dead end: it narrows the menu of innovation
options, removes healthy competitors whose alternative approaches keep
the field honest, and concentrates problem selection under a single
institutional and methodological line. When one civilisation or a small
oligopoly sets the dominant research agenda, problems that do not fit
its priorities, languages, or institutional incentives are less likely
to be addressed, leaving important scientific and social needs
unresolved. Recent work on multi-university teams shows that
geographically dispersed collaborations can retain high impact, which
suggests that distributing capacity across civilisations need not
sacrifice quality ^\[12\]^. By quantifying the safety margin for each
research community, the framework makes it possible to argue for support
of smaller communities on positive, innovation-systems grounds.
Preserving multiple centres of AI/ML research is not a matter of slowing
the frontier; it is a matter of ensuring that the frontier is not
defined by a single set of institutions, languages, or problems.

Japan is used as an illustrative case, not because it is the only group
of interest, but because it combines a small absolute margin with rich
data and a distinctive institutional lineage that makes the policy
translation concrete. It is the clearest example among the large
civilisations. Its fitted active-pool margin is T=29332 researchers,
with M=1793 (T/M=16.36). As Figure 8 shows, Japan\'s closest PNR is the
exogenous entry rate I0: if I0 fell to 6.1% of its current level, the
active pool would reach the minimum viable threshold. The same figure
shows that Japan\'s early-career outflow α (0.025) and domestic PI
promotion p_D (0.064) are comparatively low, while return from abroad β
(0.029) and domestic hit generation h_D (0.040) are moderate. These
numbers translate into policy levers: α through retention fellowships
and junior faculty positions; β through return grants and dual
appointments; h_D through independent-lab programmes such as SPREAD; p_D
through tenure-track conversion and startup packages; and d through
childcare, dual-career support, and stable non-tenure tracks. Weakening
the Japanese civilisation would not be neutral for the rest of the
world: it would remove a distinct institutional lineage, reduce the pool
of non-Anglophone problem framings, and leave a range of health, ageing,
robotics, and materials problems under-addressed. Maintaining Japan as a
viable AI/ML civilisation is therefore in the global interest, not only
in Japan\'s national interest. The Japan-specific analysis is intended
as a worked example; the same rate-ladder diagnostic can be applied to
any civilisation with sufficient OpenAlex coverage.

## 6.3 Policy and management implications, and early warning

The policy implications can be read as an early-warning architecture. A
single dashboard that tracks the fitted transition rates, their
bootstrap uncertainty, and the distance to M for each civilisation would
allow policymakers to detect divergence before a community enters an
irreversible decline. Interventions can then be calibrated to maintain a
minimum safety margin rather than to maximise any one stock. This is the
operational meaning of early intervention: not a forecast that a
particular collapse will occur, but a structured way to keep the system
away from a PNR. It also frames high-skilled mobility as a strategic
competition among jurisdictions for talent ^\[20\]^, in which the
central question is not only who wins the current round but whether the
global system retains enough diversity for future rounds ^\[21\]^. If
the response lag is short enough, the model can be updated annually and
divergence caught before any single civilisation approaches a PNR. It is
therefore a tool for ensuring that no single civilisation reaches a
self-sustaining collapse, and that the global AI/ML system retains the
diversity required for continued innovation. We introduce the acronym
SHIGA---Sustaining Heterogeneity through Interventions in Global AI/ML
Researcher Mobility---formed from the title.

Table 8 maps the most sensitive transition levers to policy instruments
and to the management actions that determine them. Policy instruments
set incentives, while management actions determine how those incentives
are implemented within institutions. Both are needed because a policy
without a corresponding management process rarely changes transition
rates.

  ------------------------------------------------------------------------
  **Lever**               **Policy instrument**   **Management action**
  ----------------------- ----------------------- ------------------------
  Dropout (d)             Early-career            Retain researchers in
                          fellowships, childcare  the domestic pipeline
                          and dual-career         beyond the first career
                          support, stable         years
                          non-tenure tracks       

  Exogenous entry (I0)    Research-master and     Widen the base of
                          undergraduate           incoming researchers
                          pipelines, doctoral     before they select a
                          fellowships,            field or location
                          recruitment visas       

  Return from abroad (β)  Return grants, diaspora Encourage mobile
                          networks, dual          researchers to
                          appointments,           re-establish domestic
                          overseas-experience     research groups
                          recognition             

  Domestic hit generation Independent-lab         Translate junior
  (h_D)                   programmes (e.g.        capacity into visible,
                          SPREAD-style),          high-impact work and
                          doctoral/postdoctoral   independent research
                          training, compute       lines
                          access                  

  PI promotion (p_D)      Tenure-track            Create durable
                          conversion, startup     principal-investigator
                          packages, project-based positions that train the
                          PI status               next cohort
  ------------------------------------------------------------------------

*Table 8. Transition levers, policy instruments, and management
actions.*

Operationally, the framework can be used in two complementary ways. As a
monitoring tool, it can be rerun whenever new OpenAlex data are
released, producing an updated set of transition rates, safety margins
and proximity-to-threshold estimates. As a scenario tool, it can
quantify how large a proportional change in a given rate would be
required to move a community toward or away from collapse, which helps
prioritise empirical policy evaluation. Both uses depend on transparent
assumptions and regular recalibration; the model should not be used to
justify one-off interventions without accompanying process evaluation.

Table 8 maps each lever to the actors that control it: I0 and h_D are
mainly owned by national funders and ministries; p_D and d by
universities and department heads; and β by diaspora networks, return
grants and private-sector recruiters. The model\'s management value is
to rank which local rates most urgently need intervention and the
proportional change needed to restore a safety margin.

## 6.4 Intra-civilisation alternatives when inter-civilisation mobility cannot be controlled

If a civilisation cannot control outflows to, or inflows from, other
jurisdictions---whether because of visa regimes, salary differentials,
language advantages, or targeted recruitment---it can still preserve its
research community by acting on the intra-civilisation levers identified
in the annual model. The annual rates show that the domestic active pool
T = D + H_D + P_D responds most strongly to the dropout rate d, the
domestic hit rate h_D, and the PI promotion rate p_D. Policies that
reduce early-career attrition, expand domestic postdoctoral positions,
or accelerate independent-lab formation therefore become defensive
substitutes when inter-civilisation poaching cannot be regulated. This
is the practical meaning of civilisational-diversity preservation under
sovereignty constraints: even without controlling the border of talent,
a community can increase the internal reproduction of active
researchers. The endogenous inflow is capped at a safety factor of 0.50
relative to the critical reproduction rate (the most constrained fitted
group realises 0.40), so the model prevents over-optimism about this
substitution effect; more ambitious domestic growth would require
corresponding evidence that the extra PIs can be absorbed without simply
raising dropout.

## 6.5 Annual updating as an early-warning layer

The 2017-2023 projection demonstrates that the framework can be rerun
annually with a one-year time step. Each new year of OpenAlex data
updates the observed transition rates, the fitted trends, and the
distance to the minimum viable coauthor threshold. Because the model is
regularised by the correction pressures, the one-year-ahead projection
is not easily derailed by a single noisy observation. Instead,
successive years reveal whether a particular transition rate is drifting
toward a boundary. That drift is the early-warning signal. Policymakers
can then intervene before the active pool falls below M, using the
rate-specific elasticities in Table 3 to prioritise the smallest
proportional change that restores a safety margin. This is the
operational mechanism for avoiding technology monopoly and oligopoly
dead ends: by keeping every major research community above its minimum
viable coauthor pool, annual monitoring sustains the competitive
diversity that underpins long-run technological progress. The framework
is therefore not a prediction that a particular civilisation will
collapse; it is a tool for ensuring that no single civilisation reaches
a point where its collapse becomes self-sustaining. The modest
year-to-year direction agreement in the 2017-2023 projection confirms
that this layer is a drift-and-threshold alarm, not a precise population
forecast. SHIGA therefore encapsulates the practical goal: keeping the
global AI/ML system heterogeneous enough that no single centre of power
can monopolise the technological frontier.

## 6.6 Limitations

Several limitations should be acknowledged. OpenAlex affiliation and
country assignments are noisy, especially for researchers with multiple
affiliations. The civilisation grouping is a coarse aggregation;
within-group heterogeneity is substantial. The annual model relies on a
discrete approximation of the continuous-time ODE and does not capture
within-year events or cross-civilisation spillovers. Inter-civilisation
flows are approximated by the author\'s recent_group while abroad, which
misses year-to-year destination switching. The civilisation label is a
pragmatic aggregation of publication-affiliation patterns. Historical
civilisational boundaries do not necessarily coincide with contemporary
political or value-based boundaries, and this study cannot determine
whether the diversity of research ideas maps more closely onto
historical civilisational groupings or onto current political and value
communities; for example, the Sinic grouping reflects current OpenAlex
country metadata and does not resolve the cultural and historical ties
between mainland China and Taiwan, which currently appear as separate
research arenas. This is treated as an empirical limitation of the
classification, not as a normative claim. The cohort is a model-implied
sample extracted from OpenAlex; absolute equilibrium numbers should be
interpreted as model-implied stocks rather than census counts. Authors
with many publications are over-weighted relative to less prolific
authors, so rate estimates reflect author-publication exposure rather
than a uniformly representative sample of individuals. The endogenous
inflow is capped at a safety factor of 0.50 relative to the critical
reproduction rate (the most constrained fitted group realises 0.40);
alternative values would shift equilibrium levels and should be reported
in future sensitivity tables. Finally, the point-of-no-return threshold
is a sufficient condition for collapse, not a necessary one: a community
may decline for reasons outside the model even if T remains above M.

Wide bootstrap confidence intervals, especially for smaller civilisation
groups, mean that the ordinal ranking of groups by equilibrium size or
proximity to threshold should be treated as descriptive rather than
definitive. The model identifies which transitions are most sensitive in
a mechanical sense; turning those sensitivities into reliable policy
priorities requires additional data on programme costs, implementation
lags, and behavioural responses that are outside the scope of this
paper.

From a security-studies perspective, the framework is intentionally
non-adversarial: it treats mobility as an aggregate transition process
and asks when a community becomes unable to reproduce itself, without
modelling deliberate recruitment campaigns, technology transfer, or
strategic denial. Future work could add a strategic layer by
distinguishing civilian from defence-relevant AI/ML pipelines, or by
modelling targeted recruitment in specific subfields.

# 7. Conclusion

We have proposed and implemented a transition-rate framework for
assessing how close AI/ML research communities are to a PNR. The model
converts OpenAlex publication records into civilisation-specific
transition rates and solves for the equilibrium active researcher pool.
All groups remain above their minimum viable coauthor threshold in the
fitted model, but the distance to that threshold varies by an order of
magnitude and is most sensitive to exogenous entry and dropout. Dropout
is the dominant negative lever (active-pool elasticity -2.79 to -2.27),
and a simulated reduction is the single most efficient model-implied
response for every civilisation. However, the closest PNR is exogenous
entry for all groups in the active-pool analysis, which means that
policies which sustain the pipeline of new researchers are first-order
defences. The historical counterfactual and the bootstrap intervals
remind us that the future is not determined by current rates; transition
rates can change, and policy can be directed at the most fragile lever
before a collapse.

The annual projection layer adds an operational dimension to this
conclusion. By estimating year-by-year transition rates and projecting
one year ahead, the model turns the steady-state diagnostic into an
early-warning dashboard. A one-year time step is short enough to detect
drift before the active pool approaches the minimum viable threshold,
and the correction pressures keep the projection within empirical and
theoretical bounds. When inter-civilisation mobility cannot be
controlled, the same framework points to intra-civilisation
levers---reducing dropout, raising domestic hit rates, and accelerating
PI promotion---that preserve T = D + H_D + P_D. These two layers,
steady-state and annual, together provide a coherent basis for early,
safety-factor-bound intervention.

The broader implication is that preserving civilisational diversity in
AI/ML is compatible with, and may reinforce, scientific progress. A
single dominant region or a tight oligopoly may achieve short-run scale
economies, but it also risks methodological lock-in and reduces the set
of problems that receive sustained attention. By monitoring transition
rates and safety margins, policymakers can detect divergence early and
intervene in a safety-factor-bound way. This is the practical meaning of
the aspiration to avoid technology monopoly and oligopoly dead ends: not
a prediction that any one civilisation will dominate, but a structured
method for keeping the global system away from points of no return.
Early, proportionate interventions that reduce attrition and sustain new
recruitment can widen safety margins and preserve civilisational
diversity in AI/ML.

## 7.1 Future work

Several extensions are natural. First, the model can be applied to other
security-relevant fields such as semiconductor physics, quantum
computing, biotechnology and energy materials, allowing cross-field
comparisons of vulnerability. Second, the civilisation partition can be
refined to a country or institution level, allowing bilateral migration
flows and network externalities to be incorporated. Third, the ODE can
be solved dynamically rather than at steady state, making it possible to
forecast the time to threshold under alternative policy scenarios.
Fourth, the minimum viable coauthor threshold can be made endogenous by
modelling coauthorship as a matching process. Fifth, the sensitivity of
equilibrium outcomes to the safety factor and to the saturating
parameter epsilon should be mapped systematically. Finally, the
framework can be integrated with policy cost data to produce
cost-effectiveness comparisons of alternative interventions, turning
mechanical sensitivities into actionable funding priorities.

# References

1\. MacroPolo. The Global AI Talent Tracker 2.0. Paulson Institute,
2023.
https://macropolo.org/digital-projects/the-global-ai-talent-tracker/

2\. Appelt S, van Beuzekom B, Galindo-Rueda F, de Pinho R. Which factors
influence the international mobility of research scientists? OECD
Science, Technology and Industry Working Papers 2015/02, 2015.
https://doi.org/10.1787/5js1tmrr2233-en

3\. Stephan P E. The Economics of Science. J Econ Lit.
1996;34(3):1199-1235.

4\. Huntington S P. The Clash of Civilizations and the Remaking of World
Order. New York: Simon & Schuster, 1996.

5\. Aghion P, Bloom N, Blundell R, Griffith R, Howitt P. Competition and
innovation: an inverted-U relationship. Q J Econ. 2005;120(2):701-728.

6\. Priem J, Piwowar H, Orr R. OpenAlex: A fully-open index of scholarly
works, authors, venues, institutions, and concepts. arXiv:2205.01833,
2022. https://doi.org/10.48550/arXiv.2205.01833

7\. Thorn K, Holm-Nielsen L B. International Mobility of Researchers and
Scientists: Policy Options for Turning a Drain into a Gain. UNU-WIDER
Research Paper No. 2006/83, 2006.
https://www.wider.unu.edu/sites/default/files/rp2006-83.pdf

8\. AlShebli B, Memon S A, Evans J A, Rahwan T. China and the U.S.
produce more impactful AI research when collaborating together. Sci Rep.
2024;14:28576. https://doi.org/10.1038/s41598-024-79863-5

9\. Yuan S, Shao Z, Wei X, Tang J, Hall W, Wang Y, et al. Science behind
AI: the evolution of trend, mobility, and collaboration. Scientometrics.
2020;124(2):993-1013. https://doi.org/10.1007/s11192-020-03423-7

10\. Shaffer M L. Minimum Population Sizes for Species Conservation.
BioScience. 1981;31(2):131-134.

11\. Franzoni C, Scellato G, Stephan P E. Foreign-born scientists:
mobility patterns for 16 countries. Nat Biotechnol.
2012;30(12):1250-1253.

12\. Jones B F, Wuchty S, Uzzi B. Multi-University Research Teams:
Shifting Impact, Geography, and Stratification in Science. Science.
2008;322(5905):1259-1262.

13\. Nelson R R, Winter S G. An Evolutionary Theory of Economic Change.
Cambridge, MA: Harvard University Press, 1982.

14\. Dosi G. Technological paradigms and technological trajectories: a
suggested interpretation of the determinants and directions of technical
change. Res Policy. 1982;11(3):147-162.

15\. Lundvall B-Å. National Systems of Innovation: Toward a Theory of
Innovation and Interactive Learning. London: Anthem Press, 1992.

16\. Malerba F. Sectoral systems of innovation and production. Res
Policy. 2002;31(2):247-264.

17\. State B, Park P, Weber I, Macy M. The mesh of civilizations in the
global network of digital communication. PLoS ONE. 2015;10(5):e0122543.
https://doi.org/10.1371/journal.pone.0122543

18\. Chinchilla-Rodríguez Z, Miao L, Murray D, Robinson-García N, Costas
R, Sugimoto C R. A global comparison of scientific mobility and
collaboration according to national scientific capacities. Front Res
Metr Anal. 2018;3:17. https://doi.org/10.3389/frma.2018.00017

19\. Freeman R B, Huang W. Collaboration: Strength in diversity. Nature.
2014;513(7518):305. https://doi.org/10.1038/513305a

20\. Shachar A. The Race for Talent: Highly Skilled Migrants and
Competitive Immigration Regimes. NYU Law Rev. 2006;81(1):148-206.

21\. Kerr W R. Global Talent and U.S. Immigration Policy. Harvard
Business School Working Paper No. 20-107, 2020.
https://www.hbs.edu/ris/Publication%20Files/20-107_0967f1ab-1d23-4d54-b5a1-c884234d9b31.pdf
