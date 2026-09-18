Article type: Research Article

Approximate word count (main text incl. tables, excl. references): 10524

Author information removed for double-anonymised review

# Abstract

Artificial intelligence (AI) research talent is a general-purpose
infrastructural input, comparable to coal in Jevons\'s analysis of
industrial Britain. Its rapid concentration in a few centres raises a
question that neither researcher-mobility nor evolutionary innovation
studies answer: at what point does the loss of researchers from a
smaller research system become a lasting loss of variety for the field
as a whole? We derive a mechanism linking career-transition rates to a
minimum viable coauthor scale and to variety loss, and examine four
propositions with a six-compartment ordinary-differential-equation model
fitted to OpenAlex AI/ML records (2000-2023) for 9 research
macro-regions. All equilibrium active pools exceed their minimum viable
scale, but proximity to the point of no return depends on the ratio of
pool to threshold, not absolute size: the lowest ratio is 3.01 (Other
Western (Israel)), and the closest point of no return is in Other
Western (Israel), where a 67% reduction in the exogenous entry rate
($I_{0}$) would drive the active pool to its threshold. Dropout, which
drains every compartment, is the most elastic lever in every
macro-region. Transition rates estimated from the 2011-2016 career-start
window imply a smaller equilibrium pool than 2000-2010 rates in 1 of 9
macro-regions. Treating AI research capacity as a sociotechnical
infrastructure rather than a national asset, the analysis is mechanistic
and reproducible from open data, and gives governments, funders and
universities a common early-warning metric. Preserving variety across
research macro-regions is argued to benefit the whole field and society,
not only the systems at risk.

**Keywords:** researcher mobility; artificial intelligence; research
variety; minimum viable population; path dependence; compartment model;
technology policy

## Highlights

- AI research talent is framed as a general-purpose input, after
  Jevons\'s coal question

- Career transition rates linked to minimum viable scale and lasting
  variety loss

- Closest PNR: Other Western (Israel), via 67% change in $I_{0}$

- Dropout, which drains every career stage, is the most elastic lever
  everywhere

- Preserving macro-regional variety benefits the whole AI field, not
  only small systems

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
reported in Section 5.5. No proprietary or restricted data were used.

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

In 1865 William Stanley Jevons asked whether Britain\'s industrial
expansion could outlast the coal on which it ran \[1\]. His question was
not about a commodity but about a general-purpose input whose
availability conditioned every downstream industry. Artificial
intelligence (AI) and machine learning (ML) research talent occupies a
comparable position today: methods developed by a small, highly mobile
population of doctoral researchers, post-doctoral researchers and
principal investigators (PIs) are being embedded in science, industry
and public administration as a general-purpose technology \[2,3\].
Governments in the United States, China, Europe, Japan and India now
treat this population as a strategic input and compete for it through
visas, fellowships and salaries \[4,5\]. Unlike coal, however, research
talent is reproducible, mobile and subject to positive feedback:
researchers train researchers, and they cluster where other researchers
already are. The policy-relevant question is therefore not whether the
global stock of AI researchers will be exhausted, but whether the
distribution of that stock across research systems can pass a point
beyond which some systems can no longer reproduce themselves.

Two literatures speak to that question without answering it. Research on
scientist mobility describes brain drain, brain circulation and brain
gain in terms of stocks and net flows \[6,7\], and the economics of
science explains the individual career decisions behind those flows
\[8\]. Evolutionary and innovation-systems economics explains why
variety among research programmes matters for long-run technological
change and how positive feedback produces lock-in \[9,10,11\]. Neither
literature specifies the mechanism by which individual career-transition
rates in one research system translate into a lasting loss of variety
for the field as a whole. Without that mechanism, arguments for
sustaining smaller research systems remain either national (protect our
researchers) or purely normative (diversity is good), and they cannot
say how close a system is to a threshold or which transition would move
it there.

This paper supplies that mechanism and tests it. Section 2 reviews the
two literatures and the AI-specific evidence on concentration and
homogenisation, identifies the gap, and derives a four-step mechanism:
career-transition rates determine the active researcher pool; network
externalities in recruitment make the pool self-reinforcing; the pool
must exceed a minimum viable coauthor scale to keep producing work; and
falling below that scale removes a distinct research programme from the
global menu of variety. From this mechanism we derive one research
question and four propositions (P1-P4) about which research systems are
closest to their point of no return (PNR), which transitions govern the
distance, how endogenous recruitment shapes it, and whether historical
changes in transition rates have moved systems toward or away from the
threshold. Section 3 describes the OpenAlex cohort of 723,647 AI/ML
authors and the grouping of countries into 9 research macro-regions
\[12\]. Section 4 specifies a six-compartment
ordinary-differential-equation (ODE) model whose rates are estimated
from those data. Section 5 reports the propositions\' tests, and Section
6 discusses who benefits from preserving variety across research
macro-regions.

The contribution is threefold. Theoretically, it links
researcher-mobility research to evolutionary innovation studies through
an explicit threshold mechanism, and it extends Jevons\'s question from
an exhaustible resource to a reproducible but concentrating human input.
Empirically, it provides what are, to our knowledge, the first
comparative estimates of career-transition rates, minimum viable
coauthor scale and PNR proximity for AI/ML research macro-regions from
open bibliometric data. For technology and society, it reframes the case
for sustaining smaller research systems: the beneficiaries are not only
those systems but the field and the societies that depend on the variety
of problems, methods and evaluation norms it can generate.

# 2. Theoretical framework

## 2.1 Researcher mobility: from net flows to career transitions

Researcher mobility has been studied under the headings of brain drain,
brain circulation and brain gain \[6\]. Thorn and Holm-Nielsen argue
that outflows from smaller systems become a gain only when return
migration and diaspora networks are supported, and a drain when local
environments cannot retain or reproduce talent \[6\]. Appelt et al.,
using a gravity model for 1996-2011, find that collaboration, economic
convergence and visa restrictions are the strongest correlates of
bilateral flows, and that much movement is circulation rather than
one-way migration \[4\]. Franzoni et al. document large cross-country
differences in the share of foreign-born scientists \[7\]. In AI/ML
specifically, the United States remains the dominant destination while
China and India expand domestic retention \[3\]; mobile AI scientists
retain collaboration ties with their origin systems \[13\]; and elite AI
networks are highly clustered, with brain drain from developing systems
intensifying \[14\]. The economics of science provides the
microfoundation: individuals decide where to train, whether to go
abroad, when to return and when to leave research in response to career
incentives and institutional quality \[8\]. What this literature
measures, however, is stocks and flows. It does not specify a
community-level state variable whose crossing would make the loss of
researchers self-reinforcing rather than recoverable.

## 2.2 Variety, selection and lock-in in evolutionary innovation studies

Evolutionary economics treats technological change as a process of
variety generation and selection \[9\]. Research programmes are carried
by organisations with routines, and technological paradigms channel
search along trajectories that exclude alternatives \[10\]. Metcalfe
formalises selection as a replicator process in which the rate of change
of the population depends on the variety present in it \[15\], and
Saviotti shows that variety is both an output of and an input to
long-run development: without new variety, selection eventually exhausts
the options on which it operates \[16\]. Arthur and David show how
increasing returns and positive feedback lock a system into a
historically contingent trajectory that may be inferior to foregone
alternatives \[11,17\]. The national and sectoral innovation-systems
literature adds that these processes are institutionally embedded:
funding systems, labour markets and universities co-evolve with the
research they sustain \[18,19\]. Stirling\'s general framework
distinguishes variety (number of categories), balance (their relative
size) and disparity (how different they are), and argues that all three
matter for the resilience of a technological system \[20\]. Aghion et
al. provide complementary evidence that innovation is highest at
intermediate degrees of competition \[21\]. This literature explains why
the loss of a distinct research programme is costly and hard to reverse,
but its unit of analysis is the firm, the technology or the sector. It
does not connect variety to the career-transition rates of the
researchers who carry research programmes.

The danger is not hypothetical; several fields have narrowed onto a
dominant approach, lost the communities that carried alternatives, and
then stagnated until variety was rebuilt from outside or from marginal
survivors. AI itself provides the clearest case: after the perceptrons
controversy of the late 1960s, funding and students moved almost
entirely to symbolic approaches, connectionist research survived only in
a few peripheral groups, and the field waited nearly two decades for the
back-propagation revival \[22,23\]. Hooker\'s hardware lottery,
discussed below, reads the subsequent history in the same terms. In
Soviet biology, the state-enforced dominance of Lysenkoism removed
genetics as a research programme and left the country decades behind in
the life sciences once the programme was abandoned \[24\]. In economics,
the convergence of macroeconomics on a single class of equilibrium
models before 2008 is widely cited by economists themselves as a reason
the profession failed to see the financial crisis coming \[25\], and in
theoretical physics the concentration of positions and students on
string theory has been criticised from within the field for crowding out
alternatives without delivering testable progress \[26\]. Agricultural
monocultures show the same structure with a biological rather than
intellectual selection pressure: the 1970 southern corn leaf blight
spread through a maize crop in which most hybrids shared one cytoplasm
\[27\]; coffee leaf rust destroyed the Ceylon coffee industry in the
1870s-1880s once plantations of a single, genetically narrow Coffea
arabica stock were connected by trade, and the same pathogen caused the
2008-2013 crises in Colombia and Central America after resistance in the
dominant cultivars broke down \[28,29\]; and the Gros Michel banana was
eliminated commercially by Fusarium wilt, with its Cavendish successor
now facing the same fate \[30\]. At the level of science as a whole,
large fields have been shown to ossify around canonical work and
disruptive contributions have declined across disciplines \[31,32\].
These cases differ in mechanism and in how contested the diagnosis is,
and we do not claim that AI/ML is already in such a state; they
establish that a field can select its way into a position from which
recovery is slow and depends on the survival of communities outside the
dominant programme.

## 2.3 Why AI/ML is a special case: concentration and homogenisation

Several features of contemporary AI/ML research make the
variety-selection argument more than a general worry. First, Kleinberg
and Raghavan show formally that when many decision-makers converge on
the same algorithm, an algorithmic monoculture can lower social welfare
even if each adopter individually improves, because correlated errors
are no longer averaged out \[33\]. Second, Hooker\'s hardware lottery
argues that which research ideas succeed depends on their compatibility
with the dominant hardware and software stack, so that concentration of
compute concentrates the ideas that can be tested \[34\]. Third,
benchmark and dataset use has become increasingly concentrated on a
small number of datasets originating from a few institutions \[35\], and
the pursuit of general benchmarks embeds particular framings of what
counts as progress \[36\]. Fourth, the empirical success of scaling laws
\[37\] and foundation models \[38\] has produced a single dominant
paradigm whose compute requirements have grown by orders of magnitude
\[39\], shifting participation from universities toward a few large
firms and their partners \[40\]. Fifth, the data on which models are
trained are dominated by a few languages and by cultural framings
embedded in them \[41,42\]. Each of these is a channel through which the
geography of the research population shapes the variety of problems,
methods and evaluation norms in the field.

There are serious counterarguments. Compute and data exhibit economies
of scale, so concentration may be the efficient way to reach the
frontier, and open-source and open-weight releases diffuse frontier
methods to researchers everywhere at low cost \[38\]. Geographic or
macro-regional diversity is, moreover, only a coarse proxy for the
cognitive diversity that matters for problem-solving \[43\]; two
research systems in different regions may work on the same problems with
the same methods. We accept these points. The argument developed below
is not that concentration is inefficient in the short run, nor that
every region carries a distinct research programme. It is that when a
research system falls below the scale needed to reproduce itself,
whatever distinct problem framings, data, languages and institutional
experiments it carried are removed from the menu on which future
selection can operate, and that this loss is difficult to reverse
because the same positive feedbacks that produced it work against
recovery. Open diffusion of methods lowers the cost of using the
frontier; it does not by itself sustain the local PIs, students and
institutions needed to define problems differently.

## 2.4 The gap: an infrastructural input with a threshold

Bringing the literatures together exposes the gap. Mobility research has
the microdata on career transitions but no community-level threshold;
evolutionary innovation studies have the threshold concepts (lock-in,
loss of variety) but no link to career transitions. Jevons\'s coal
question is useful precisely because it framed a general-purpose input
in terms of a system-level constraint rather than individual mines, and
because it was refined by later work showing that efficiency gains can
increase rather than reduce demand \[1,44\]. The analogy has strict
limits. Researchers are human capital that reproduces through training;
they move across systems; and AI tools may raise rather than lower the
demand for researchers. We therefore do not claim that AI talent is
exhaustible. We claim that, like coal for Jevons, it is an input whose
distribution across systems determines what the whole can do, and that
for each system there is a scale below which the input is no longer
reproduced locally. Identifying that scale and the transitions that
govern distance to it is the missing mechanism.

## 2.5 Mechanism: transition rates, network externalities, minimum viable scale, variety loss

The mechanism has four steps. (i) Career-transition rates determine the
active pool. Within a research system, researchers enter (exogenous
entry $I_{0}$), move abroad early in their career ($\alpha$), return
($\beta$), produce high-impact work ($h_{D}$, $h_{A}$), become PIs
($p_{D}$, $p_{A}$) or leave research ($d$). Given these rates, the
domestic active pool $T\  = \ D\  + \ H_{D}\  + \ P_{D}$ has a
well-defined equilibrium. (ii) Network externalities make the pool
self-reinforcing. Recruitment is not exogenous: PIs train students and
attract post-doctoral researchers, so inflow rises with the PI stock.
This is a network externality in the sense of Katz and Shapiro---the
value of joining a research system rises with the number already in it
\[45\]. It implies that a decline in $T$ reduces future inflow, which
reduces $T$ further. (iii) The pool must exceed a minimum viable scale.
Following the minimum-viable-population concept in conservation biology
\[46\], we define an operational minimum viable coauthor scale
$M\  = \ k\  \times \ \overline{c}$ as the number of active researchers
needed to staff the field\'s observed number of distinct PI groups ($k$)
at its observed coauthor intensity ($\overline{c}$); hereafter $M$. It
is operational in that it is computed from observed publication
structure rather than derived from a demographic extinction model. Below
$M$ the system cannot produce work at the field\'s norms, mentorship
chains break and the feedback in step (ii) runs in reverse. (iv) Falling
below $M$ removes variety. Because research programmes are carried by
PIs and the institutions around them \[9,10\], a system that can no
longer reproduce its PI stock loses the programme, not just the
headcount. The loss is path-dependent in Arthur\'s sense \[11\]:
recovery requires rebuilding the feedback loop against competitors that
have grown stronger in the meantime. In the AI-specific channels of
Section 2.3, this means fewer independent sources of problems,
benchmarks, data and evaluation norms for the field as a whole.

## 2.6 Research question and propositions

The research question follows: for each AI/ML research macro-region, how
far is the active researcher pool from its minimum viable scale, which
career transition governs that distance, and has the distance been
shrinking? Four propositions are derived from the mechanism rather than
from the data.

P1 (relative scale; structural implication). Under network externalities
in recruitment, distance to the PNR is governed by the ratio $T/M$
rather than by absolute $T$. Systems with lower $T/M$ require a smaller
proportional change in a transition rate to reach $M$, so proximity
should track $T/M$ more closely than it tracks $T$. Because the entry
lever rescales the whole equilibrium, this is a structural implication
of the model rather than a hypothesis the data could reject; its
diagnostic content is that the ranking by absolute size and the ranking
by proximity diverge.

P2 (asymmetric leakage). A transition that removes researchers from
every compartment (dropout, $d$) has a larger equilibrium elasticity
than a transition that moves researchers between compartments within the
global system (early-career outflow, $\alpha$), because the latter
preserves the possibility of return ($\beta$) and of contribution from
abroad. Hence \|elasticity of $T$ with respect to $d$\| \> \|elasticity
with respect to $\alpha$\| in every system.

P3 (endogenous recruitment). Because inflow depends on the PI stock, the
transition closest to the threshold should be the one that feeds the
reproduction loop from outside---exogenous entry $I_{0}$---rather than a
mobility rate; and the ranking of systems by proximity should be robust
to the functional form of the recruitment feedback (linear versus
saturating).

P4 (historical drift). If transition rates estimated from the later
career window (2011-2016) differ from those of the earlier window
(2000-2010), the equilibrium implied by the later rates should differ
from that implied by the earlier rates; where the later equilibrium is
smaller, the system has been drifting toward its threshold and the
mechanism predicts ongoing variety loss unless rates change.

These propositions are mechanistic in the sense that each follows from a
specific step of Section 2.5. P2-P4 could be falsified by the fitted
model: P2 by any system in which $\alpha$ is more elastic than $d$, P3
by a mobility rate being the closest lever or by rank reversals under
saturation, and P4 by identical early- and late-window equilibria. P1 is
a diagnostic proposition: it is checked for consistency and used to read
the results, not tested.

# 3. Data and macro-regional grouping

We extracted AI/ML works and author histories from the OpenAlex API for
subfield 1702 (Artificial Intelligence), 2000-2023 \[12\]. OpenAlex
provides open, CC0 metadata on authors, affiliations, countries,
publication dates and citations. Author histories were built by
following each author\'s sequence of works and affiliations, assigning a
country per work and an origin macro-region by the modal country of
recorded affiliations.

## 3.1 Research macro-regions

The unit of analysis is the research macro-region: a set of countries
whose AI/ML researchers share funding systems, labour markets, languages
and mobility corridors closely enough to be treated as one recruitment
pool. For reproducibility, the initial partition of countries was taken
from Huntington\'s taxonomy \[47\], which predicts the structure of
global communication networks \[48\] and of scientific mobility and
collaboration \[49\]; it serves only as a documented starting heuristic
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
Other regions. Other Western (Israel) is in practice a single national
system: Israel accounts for 100% of its 2022-2023 AI/ML works, so
results for this macro-region should be read as results for a small,
high-impact national system. Figure 1 maps the partition and overlays
the largest observed inter-region early-career flows, which are the
cross-region moves the model tracks through the abroad compartments. The
full country mapping is in Supplementary Material.

![](media/image1.png){width="6.3in" height="3.2953849518810148in"}

*Figure 1. Research macro-regions and the largest inter-region
early-career flows, 2000-2023. Country outlines from Natural Earth
(public domain); arrow width is proportional to accumulated abroad
author-years by origin and destination; the legend gives each region\'s
equilibrium* $T/M$ *ratio.*

## 3.2 Cohort and variable definitions

Authors enter the cohort if their first observed AI/ML publication is in
2000-2016 and they have at least two AI/ML works in 2000-2023; authors
with only unknown affiliations are excluded, giving 723,647 authors. An
author is active if they have at least one AI/ML work in 2020-2023 and
has dropped out otherwise. A hit is a paper in the top 10% of AI/ML
citations for its publication year, observed within the first eight
career years. A PI is an author whose first last-author paper
(single-authored papers are treated as last-author) appears in the
window \[8\]. Both are deliberately broad operational definitions: a PI
in this sense is any author with at least one independent last-author
paper, not a tenured group leader, and a hit author is any author with
at least one top-decile paper. Because the cohort is restricted to
authors with at least two works, PIs account for 58-74% and hit authors
for 31-60% of each macro-region\'s cohort (Table 1). The PI compartment
therefore represents the population able to lead work and recruit, and
the minimum viable scale in Section 4.3 counts distinct last-author
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
  Anglosphere     64122         700342      28218         35822       43628     2007.3    16233
  ex-US                                                                                   

  China-centred   190051        1589023     103673        61738       140701    2008.7    23956

  Continental     168911        1766329     74004         90322       111466    2008.0    26060
  Europe                                                                                  

  Islamic world   51043         387001      29703         20435       35558     2011.4    8131

  Japan           32007         293437      11846         9915        18543     2006.7    4417

  Other Western   4397          49748       1981          2646        2848      2007.4    1414
  (Israel)                                                                                

  Other regions   50240         371952      23671         17128       32449     2009.2    9136

  South Asia      28069         225684      17047         12043       19185     2011.3    4289

  United States   134807        1298250     58969         74972       91029     2007.3    27420
  --------------------------------------------------------------------------------------------------------

*Table 1. Descriptive statistics for the extracted AI/ML cohort by
research macro-region. Labels are operational aggregations of OpenAlex
country-affiliation patterns.*

# 4. Methods

## 4.1 Compartment model

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
calculation transparent; the model is an early-warning device, not a
demographic projection.

## 4.2 Endogenous inflow (network externality)

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

## 4.3 Minimum viable coauthor scale

Step (iii) is implemented as $M\  = \ k\  \times \ c\bar{}$, where
$\overline{c}$ is the mean number of authors per work and $k$ the median
number of distinct last-author groups per recent year. When the
equilibrium active pool $T\  = \ D\  + \ H_{D}\  + \ P_{D}$ falls below
$M$, the system cannot produce work at the field\'s coauthor intensity.
Falling below $M$ is a sufficient, not a necessary, condition for
collapse; $M$ is a soft lower bound, so observed margins are probably
smaller than they appear.

## 4.4 Estimation, elasticities, PNR and counterfactuals

Rates are estimated as constant per-year hazards from observed
transitions over exposure time, with a Laplace pseudocount of 1 per
outcome. Because the data are right-censored, rates are lower bounds and
equilibria conservative. Steady states are solved with a trust-region
Newton method. The equilibrium $T$ is the asymptotic pool of an open
system with continuing entry and is therefore larger than the 2020-2023
active count of the closed 2000-2016 cohort in Table 1 (by a factor of
2.4-3.1); the two are not comparable, and all claims rest on relative
quantities ($T/M$, elasticities, proximity and rankings), not on
absolute $T$. Elasticities perturb each rate by 1% and record the
percentage change in $T$ (P2). For the PNR we scale each rate until $T$
reaches $M$ and record the critical factor and its proximity \|critical
factor − 1\| (P1, P3). Historical drift (P4) compares equilibria under
rates estimated from the 2000-2010 and 2011-2016 career windows. Policy
counterfactuals perturb single rates by ±10% and rank levers by margin
gain; bootstrap resampling of authors (200 draws) gives 95% intervals.
All counterfactuals are mechanical perturbations of fitted rates: they
identify sensitive transitions, not causal effects of programmes. An
annual layer re-estimates rates year by year (2000-2016), projects them
to 2017-2026 and compares the projected compartment counts with observed
2017-2023 stocks; it is an exploratory extension whose estimation,
regularisation, figures and accuracy metrics are reported in
Supplementary Material Section S2 (Supplementary Figures S1-S3,
Supplementary Tables S2-S5).

## 4.5 Talent-concentration scenario

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
4.3). Hit generation in all regions is multiplied by the effective
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
fitted dropout rates ($\tau$ ≈ 24 years); the horizon is 4.1 $\tau$, and
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

# 5. Results

## 5.1 Equilibrium pools and minimum viable scale (P1)

Table 2 reports the equilibrium domestic active pool $T$, the minimum
viable scale $M$ and the inflow parameters for the 9 macro-regions. All
exceed their threshold under the fitted model, but the ratio $T/M$
ranges from 3.01 (Other Western (Israel)) to 97.12 (China-centred). The
China-centred, Continental Europe and United States macro-regions have
the largest absolute pools; Other Western (Israel) has both the smallest
pool and the narrowest absolute margin. Figure 3 visualises the gap
between $T$ and $M$.

  ----------------------------------------------------------------------------------------------------------
  **Group**       $T$      $M$     **Margin**   $I_{0}$   $r$      $r$              $r$              $T/M$
                                                                   **(observed)**   **(critical)**   
  --------------- -------- ------- ------------ --------- -------- ---------------- ---------------- -------
  Anglosphere     67532    3183    64348        1886      0.0633   0.0865           0.1265           21.21
  ex-US                                                                                              

  Continental     195095   3923    191172       4968      0.0595   0.0891           0.1190           49.72
  Europe                                                                                             

  South Asia      53434    2249    51185        826       0.0273   0.0861           0.0546           23.76

  Islamic world   88522    2255    86267        1501      0.0318   0.0844           0.0635           39.26

  Japan           29332    1793    27539        1134      0.1015   0.1015           0.2554           16.36

  Other regions   59355    2069    57286        1478      0.0662   0.0911           0.1324           28.69

  Other Western   4824     1601    3223         129       0.0599   0.0908           0.1198           3.01
  (Israel)                                                                                           

  China-centred   303935   3129    300805       5590      0.0420   0.0795           0.0840           97.12

  United States   147067   1844    145223       3965      0.0620   0.0871           0.1240           79.75
  ----------------------------------------------------------------------------------------------------------

*Table 2. Equilibrium domestic active pool, minimum viable coauthor
scale and endogenous inflow parameters by research macro-region.*

![](media/image3.png){width="5.8in" height="3.19in"}

*Figure 3. Equilibrium domestic active pool (*$T$*) and minimum viable
coauthor scale (*$M$*) by research macro-region.*

## 5.2 Which transitions govern the pool (P2)

Table 3 lists the three transition-rate elasticities with the largest
absolute effect on $T$ in each macro-region. Dropout ($d$) is the
largest negative lever everywhere, with elasticity from -2.79 to -2.27,
whereas the largest absolute elasticity of early-career outflow
($\alpha$) is 0.27; $|e_{d}|$ exceeds $|e_{\alpha}|$ in 9 of 9
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
  Anglosphere     $d$        -2.68          $h_{D}$    0.47           $p_{D}$    0.34
  ex-US                                                                          

  China-centred   $d$        -2.69          $h_{D}$    0.40           $p_{D}$    0.26

  Continental     $d$        -2.68          $h_{D}$    0.39           $p_{D}$    0.35
  Europe                                                                         

  Islamic world   $d$        -2.58          $h_{D}$    0.37           $p_{D}$    0.22

  Japan           $d$        -2.27          $h_{D}$    0.39           $p_{D}$    0.27

  Other Western   $d$        -2.74          $h_{D}$    0.37           $p_{D}$    0.35
  (Israel)                                                                       

  Other regions   $d$        -2.79          $h_{D}$    0.49           $p_{D}$    0.31

  South Asia      $d$        -2.54          $h_{D}$    0.34           $p_{D}$    0.21

  United States   $d$        -2.67          $h_{D}$    0.45           $p_{D}$    0.36
  ---------------------------------------------------------------------------------------------

*Table 3. Top transition-rate elasticities of the domestic active pool*
$T$ *by research macro-region.*

## 5.3 PNR and endogenous recruitment (P1, P3)

Table 4 reports, for each macro-region, the single rate that reaches the
active-pool threshold with the smallest proportional change, and Figure
4 ranks macro-regions by that proximity. $I_{0}$ is the closest
point-of-no-return lever for the active researcher pool in every group,
consistent with P3: the transition that feeds the reproduction loop from
outside is the binding one. The closest PNR is in Other Western
(Israel), where $I_{0}$ multiplied by 0.332 (a 67% reduction) drives the
active pool to $M$. Across macro-regions the Spearman correlation
between PNR proximity and $T/M$ is 1.00, whereas that between proximity
and absolute $T$ is 0.93. Because the $I_{0}$ lever scales the whole
equilibrium, proximity is close to a deterministic function of $T/M$ in
the linear model, so the first correlation is the consistency check that
P1 calls for rather than an independent test; the diagnostic content of
P1 is that the ranking by absolute size and the ranking by proximity
diverge, which the second correlation shows (Section 5.6 returns to
individual cases).

  ----------------------------------------------------------------------------
  **Group**       **Closest      **Current      **Critical     **Proximity**
                  rate**         value**        factor**       
  --------------- -------------- -------------- -------------- ---------------
  Other Western   $I_{0}$        129.3          0.332          0.668
  (Israel)                                                     

  Japan           $I_{0}$        1134.4         0.061          0.939

  Anglosphere     $I_{0}$        1885.9         0.047          0.953
  ex-US                                                        

  South Asia      $I_{0}$        825.6          0.042          0.958

  Other regions   $I_{0}$        1477.6         0.035          0.965

  Islamic world   $I_{0}$        1501.3         0.025          0.975

  Continental     $I_{0}$        4968.0         0.020          0.980
  Europe                                                       

  United States   $I_{0}$        3964.9         0.013          0.987

  China-centred   $I_{0}$        5589.7         0.010          0.990
  ----------------------------------------------------------------------------

*Table 4. Closest PNR for the active researcher pool by research
macro-region.*

![](media/image4.png){width="5.8in" height="3.2222222222222223in"}

*Figure 4. Closest point-of-no-return proximity by research
macro-region. Smaller values mean a smaller proportional change in the
listed rate reaches the threshold.*

Replacing the linear recruitment feedback with a saturating one changes
the equilibrium pool by below 0.001% for every group (Table 5), and the
closest lever is unchanged in every macro-region while the rank order of
proximity has Spearman $\rho\  = \ 1.00$ between the two variants
(Supplementary Table S7). The second part of P3 is therefore supported:
the ranking of systems by fragility does not depend on the functional
form of the network externality.

  -----------------------------------------------------------------------
  **Group**         **Linear** $T$    **Saturating**    $\varepsilon$
                                      $T$               
  ----------------- ----------------- ----------------- -----------------
  Anglosphere ex-US 67532             67532             0.00000

  Continental       195095            195095            0.00000
  Europe                                                

  South Asia        53434             53434             0.00001

  Islamic world     88522             88522             0.00001

  Japan             29332             29332             0.00001

  Other regions     59355             59355             0.00001

  Other Western     4824              4824              0.00007
  (Israel)                                              

  China-centred     303935            303935            0.00000

  United States     147067            147067            0.00000
  -----------------------------------------------------------------------

*Table 5. Equilibrium* $T$ *under linear and saturating PI-driven
inflow.*

## 5.4 Historical drift in transition rates (P4)

Table 6 compares the equilibrium that would emerge if rates estimated
from the early (2000-2010) or late (2011-2016) career window persisted;
Figure 5 plots the change in margin. All 9 macro-regions have
dual-window support for both estimates. Under late-window rates the
margin shrinks in Japan and grows in Islamic world, South Asia,
China-centred, Continental Europe, Other regions, United States,
Anglosphere ex-US, Other Western (Israel). The late window is shorter
and its cohorts younger, so its promotion and hit rates are estimated
from less exposure and its equilibria are less certain; the comparison
is a sensitivity exercise rather than a forecast. It nevertheless
supports P4 in its weak form: equilibria differ across windows, so the
distance to the threshold is not stationary, and where margins shrink
the mechanism implies ongoing drift toward the threshold.

  --------------------------------------------------------------------------------------
  **Group**       $T$         $T$        $\Delta T$   **Margin   **Margin   $\Delta$
                  **early**   **late**   **(%)**      early**    late**     **margin**
  --------------- ----------- ---------- ------------ ---------- ---------- ------------
  Anglosphere     64779       75245      16.2         61596      72062      10466.2
  ex-US                                                                     

  Continental     177460      231958     30.7         173536     228035     54498.4
  Europe                                                                    

  South Asia      23397       110377     371.8        21148      108128     86979.8

  Islamic world   37899       186245     391.4        35644      183990     148346.1

  Japan           31781       25052      -21.2        29989      23259      -6729.5

  Other regions   42881       91930      114.4        40812      89861      49049.3

  Other Western   4450        5731       28.8         2849       4129       1280.2
  (Israel)                                                                  

  China-centred   278159      360991     29.8         275030     357861     82831.4

  United States   139401      169788     21.8         137557     167943     30386.5
  --------------------------------------------------------------------------------------

*Table 6. Equilibrium active pool and safety margin under early
(2000-2010) versus late (2011-2016) transition-rate regimes.*

![](media/image5.png){width="5.8in" height="3.2222222222222223in"}

*Figure 5. Change in safety margin between early and late
transition-rate regimes. Negative values mean the late-window rates
would shrink the margin if they persisted. Point estimates only; the two
windows differ in cohort size.*

## 5.5 Policy counterfactuals and uncertainty

Table 7 reports the mechanical counterfactual with the largest margin
gain per 10% lever change in each macro-region. Reducing dropout is the
dominant positive lever in every macro-region, consistent with P2. The
gain from a 10% reduction in $d$ ranges from about 567 active
researchers (Other Western (Israel)) to about 34,739 (China-centred).
Blocking early-career outflow is not the efficient response: a
researcher abroad remains in the global system and may return, whereas a
researcher who leaves research is lost to every compartment.

  ----------------------------------------------------------------------------
  **Group**       **Lever**      **Direction**   **Change (%)** **Gain per
                                                                10%**
  --------------- -------------- --------------- -------------- --------------
  Anglosphere     $d$            decrease        -10            7660
  ex-US                                                         

  Continental     $d$            decrease        -10            22093
  Europe                                                        

  South Asia      $d$            decrease        -10            6184

  Islamic world   $d$            decrease        -10            10239

  Japan           $d$            decrease        -10            3194

  Other regions   $d$            decrease        -10            6723

  Other Western   $d$            decrease        -10            567
  (Israel)                                                      

  China-centred   $d$            decrease        -10            34739

  United States   $d$            decrease        -10            16560
  ----------------------------------------------------------------------------

*Table 7. Top positive mechanical counterfactual per research
macro-region (margin gain per 10% proportional lever change).*

We also evaluated multi-lever policy packages for the three
smallest-margin groups. The package with the largest margin gain in each
group was: Other Western (Israel) (retention: +616 active researchers);
Japan (return plus retention: +3,369 active researchers); South Asia
(retention: +6,536 active researchers). These packages combine dropout
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
later OpenAlex snapshot (719,173 authors under the same inclusion rules;
the difference from Table 1 reflects OpenAlex updates to author and
affiliation records between the two extractions) and replacing the
baseline definition (first last-author paper) with the first
corresponding-author paper or with recurrence as last author (two or
more last-author papers) changes the share of authors classified as PIs
(mean across macro-regions 67.4%, 51.3% and 48.2% respectively), the
promotion rates $p_{D}$ and $p_{A}$, the equilibrium PI pool $P_{D}$ and
the split of recruitment between exogenous entry and PI-driven feedback.
Because $I_{0}$ is calibrated so that total equilibrium entry equals
observed entry (Section 4.2), the active pool $T$, $T/M$ and the
proximity of the entry lever are invariant to the proxy by construction;
the informative test is therefore whether the proxy-dependent quantities
reorder the macro-regions. The ordering is largely preserved: Spearman
rho with the baseline is at least 0.98 for the equilibrium PI pool and
1.00 for the proximity of the PI pool to its own threshold, the
elasticity of $T$ to $p_{D}$ rises from 0.21-0.36 under the baseline to
0.30-0.51 under the stricter proxies (Spearman rho of the elasticity
ranking with the baseline at least 0.73), and the closest lever for the
PI pool changes only in Other Western (Israel), where it becomes dropout
rate ($d$) under the stricter proxies (Supplementary Tables S9-S10).
Second, the threshold. Multiplying $M$ by 0.50-2.00 leaves no
macro-region below its threshold (minimum $T/M$ 1.51 at the largest
multiplier), preserves the ranking by $T/M$ and by proximity exactly
(Spearman rho = 1.00 and 1.00), keeps \|elasticity to $d$\| \>
\|elasticity to alpha\| in every macro-region at every multiplier, and
the closest lever changes only for Other Western (Israel) at multipliers
1.25, 1.50, 2.00, where the closest lever becomes the dropout rate ($d$)
(Supplementary Table S11). Because $M$ enters the linear model only as
the target, its level shifts distances without reordering systems; the
substantive results are relative.

As an exploratory extension, the annual layer re-estimates the rates
year by year and projects them to 2017-2026; rate-level projections have
a skill ratio of 0.99 against a historical-mean baseline and the layer
is a drift monitor rather than a forecast, so its figures and accuracy
tables are reported in Supplementary Material Section S2 (Supplementary
Figures S1-S3, Supplementary Tables S2-S5).

## 5.6 Worked example: Japan

Japan illustrates the mechanism in a large research system with an
independent institutional lineage and comparatively low $T/M$. Its
fitted equilibrium is $T\  = \ 29,332$ active researchers
($D\  = \ 16,248$, $H_{D}\  = \ 5,714$, $P_{D}\  = \ 7,370$) against
$M\  = \ 1,793$, so $T/M\  = \ 16.36$. The closest PNR is $I_{0}$: a
fall to 6.1% of its current level would bring $T$ to $M$. Figure 7
places Japan\'s six compartments and compares its rates with the other
macro-regions: early-career outflow ($\alpha\  = \ 0.025$) and domestic
PI promotion ($p_{D}\  = \ 0.064$) are comparatively low, return
($\beta\  = \ 0.029$) and domestic hit generation ($h_{D}\  = \ 0.040$)
moderate, and dropout $d\  = \ 0.055$. Low leakage but a thin internal
promotion pipeline is the configuration P1 and P2 describe: the system
does not lose many researchers abroad, so its distance to the threshold
is governed by scale relative to $M$ and by attrition rather than by
mobility. Figure 8 generalises the diagnostic by plotting $T/M$ against
PNR proximity for all macro-regions; the lower-left corner combines a
low buffer with a small proportional change needed to reach $M$. The
same two-panel diagnostic applies to any macro-region with sufficient
OpenAlex coverage; Japan is a worked example, not a special case.

![](media/image7.png){width="6.0in" height="3.3094969378827646in"}

*Figure 7. Japan in the six-compartment model, with a ladder of fitted
transition rates across research macro-regions (Japan highlighted;
longer bars are higher rates).*

![](media/image8.png){width="5.8in" height="4.511111111111111in"}

*Figure 8. Equilibrium safety ratio (*$T/M$*) versus closest
point-of-no-return proximity for all research macro-regions. Japan is
shown in red.*

## 5.7 Talent concentration: short-run dominance, field-level loss

Figure 9 and Table 8 summarise the scenario with China-centred as the
dominant region; it is the largest observed host of abroad researchers.
With the fitted rates ($\gamma\  = \ 0$) the pull works for the region
that exerts it: for φ from 0.5 to 8.0, its hosted active pool ends
22-155% above baseline and its share of all researchers hosted abroad
rises from 31% to as much as 77% (upper-left panel). The field pays in
concentration: the effective number of macro-regions falls from 5.2 to
4.8-1.8 (upper-right panel), and the lowest $T/M$ among source regions
ends at 0.50, with 1 source region below $M$ at the strongest pull. For
this host the field\'s total hit stock falls even without a variety
effect: it rises by at most 7.1% (peaking at t ≈ 0.4-0.5 $\tau$ (≈9-12
years at fitted rates)), drops below baseline from t ≈ 1.1-1.7 $\tau$
(≈28-41 years at fitted rates), and ends 0.3-5.5% below it (lower-left
panel), because the researchers it attracts, and the early-career
researchers they recruit, generate hits at the host\'s fitted domestic
rate, which ranks 2nd lowest of the nine (Figure 10), while PI-driven
recruitment in the source regions weakens. With the United States as the
dominant region the field\'s hit stock rises at $\gamma\  = \ 0$ (Table
8), because its fitted domestic rates are higher, and falls below
baseline once γ exceeds 0.5-4.9 at the pull intensities where the
threshold is reached within the search range. In both cases the dominant
region keeps a larger share of a more concentrated field; whether the
field is also smaller depends on the host\'s own reproduction rates and
on how much output owes to variety.

Whether the dominant region itself ends worse off depends on γ
(lower-right panel). With China-centred at $\varphi\  = \ 2.0$, its own
hit stock at the end of the horizon (4.1 $\tau$) is 98% above baseline
with $\gamma\  = \ 0$ and 18% above it with $\gamma\  = \ 2$, while the
field\'s is 45% below. The elasticity at which its own output falls
below baseline within the horizon is γ\* = 4.5 at $\varphi\  = \ 0.5$
and 1.5 at $\varphi\  = \ 8.0$: the harder it pulls, the less variety
dependence is needed for the strategy to turn against it. For the United
States the same threshold is reached within $\gamma\  \leq \ 6$ only at
the strongest pull. The field-level loss of variety is therefore the
robust finding; the field-level loss of output holds at $\gamma\  = \ 0$
for one host and above a moderate γ for the other; and the dominant
region\'s own loss requires the largest γ. γ is not identified by our
data, and it is the empirical quantity on which the difference between a
lasting relative advantage for the dominant region and a dead end for it
turns.

![](media/image9.png){width="6.5in" height="4.727272528433946in"}

*Figure 9. Talent-concentration scenario with China-centred as the
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
  China-centred   0.5         1.22          37            4.8           0           1.00          0 (fitted 4.47
                                                                                                  model)    

  China-centred   1.0         1.43          43            4.3           0           0.99          0 (fitted 3.46
                                                                                                  model)    

  China-centred   2.0         1.77          53            3.5           0           0.98          0 (fitted 2.48
                                                                                                  model)    

  China-centred   4.0         2.18          66            2.5           0           0.96          0 (fitted 1.80
                                                                                                  model)    

  China-centred   8.0         2.55          77            1.8           1           0.94          0 (fitted 1.45
                                                                                                  model)    

  United States   0.5         1.46          24            5.2           0           1.03          4.95      not
                                                                                                            reached

  United States   1.0         1.93          31            5.0           0           1.07          3.08      not
                                                                                                            reached

  United States   2.0         2.76          43            4.5           0           1.13          1.52      not
                                                                                                            reached

  United States   4.0         3.87          57            3.3           0           1.20          0.79      5.42

  United States   8.0         4.92          71            2.2           1           1.27          0.52      3.01
  --------------------------------------------------------------------------------------------------------------------

*Table 8. Talent-concentration scenario at the end of the horizon (4.1*
$\tau$ *≈ 100 years at fitted rates) relative to the* $\varphi\  = \ 0$
*baseline, fitted rates (*$\gamma\  = \ 0$*), for the two largest
observed host regions. γ\* is the smallest variety elasticity at which
the hit stock falls below baseline within the horizon.*

Figure 10 shows the time paths behind these summaries for every
macro-region at the strongest pull we simulate ($\varphi\  = \ 8.0$),
one panel per γ. The dominant region\'s active pool rises and stays
high, the source regions decline towards their thresholds at rates set
by their fitted transition rates, and each crossing of $M$ switches off
a region\'s PI-driven recruitment under the collapse rule, so that
within the simulation each crossing is a discrete loss for the field
rather than one more step in a smooth contraction. Other Western
(Israel) falls below $M$ at t ≈ 2.1, 1.7, 1.5 $\tau$ (≈50, 41, 37 years
at fitted rates) for γ of 0, 1 and 2 respectively; no other region
crosses within the horizon. Larger γ brings the crossing forward,
because the loss of variety lowers hit generation everywhere, including
in the dominant region. The other source regions end the horizon above
$M$ but on declining paths, so the horizon, not the mechanism, bounds
how many crossings the figure shows; the geographical extent of the
field (Figure 1) is traded for a shorter temporal one. The timing scales
with $\tau$: a field with faster career turnover would reach the same
crossings in proportionally fewer years, so the ordering of outcomes,
not the calendar dates, is the result.

![](media/image10.png){width="6.5in" height="2.269841426071741in"}

*Figure 10. Regional time paths under the talent-concentration strategy
exerted by China-centred at pull intensity* $\varphi\  = \ 8.0$*, for
three variety elasticities γ. Lines show each macro-region\'s domestic
active pool as a multiple of its minimum viable coauthor scale* $M$
*(log scale; dashed line* $M$*); the thick line is the dominant region.
Crosses and dotted verticals mark when a region falls below* $M$*, after
which its PI-driven recruitment is switched off permanently. Time is in
units of the characteristic time* $\tau\  = \ 1/\overline{d}$ *(mean
career duration; ≈24 years at fitted rates, upper axis). Fitted rates;
φ, γ and the collapse rule are stylised.*

# 6. Discussion

## 6.1 What the propositions show

P1 is consistent with the results in the sense that matters for policy:
rankings by absolute $T$ and by proximity to the threshold diverge
($\rho\  = \ 0.93$), the largest systems are not the safest, and
proximity itself is governed by $T/M$ as the mechanism implies; as
Section 2.6 notes, this is a diagnostic reading rather than a test. P2
is supported in every macro-region: dropout is more elastic than
early-career outflow, and reducing dropout is the most efficient single
lever. P3 is supported: $I_{0}$ is the closest point-of-no-return lever
for the active researcher pool in every group, and the ranking is
invariant to the form of the recruitment feedback. The primacy of the
entry lever is a property of the fitted thresholds rather than of the
mechanism: when $M$ is raised to 1.25× its fitted value or more, dropout
becomes the closest lever in Other Western (Israel) (Section 5.5), which
is why we read P3 as support for the entry lever being binding at the
observed scale, not as a general law. P4 is supported in its weak form:
equilibria differ between the two career-start windows in all 9
macro-regions with dual-window support, and the margin shrinks in Japan.
Together the results move the researcher-mobility debate from net flows
to the transition rates that govern reproduction, and they give the
evolutionary argument about variety an empirically observable
early-warning variable.

## 6.2 Variety loss as an evolutionary dead end

The mechanism implies that concentration in AI/ML research is not merely
distributional. Short-run efficiency from scale in compute and data is
real \[39\], but the same feedbacks that produce it narrow the
population on which selection operates. If a macro-region\'s active pool
falls below $M$, the PIs who framed problems from that system\'s
languages, data and institutional context stop being replaced \[41,42\];
the benchmarks and hardware paths they might have championed are not
tried \[34,35\]; and the field loses an independent check on correlated
errors of the kind Kleinberg and Raghavan describe \[33\]. In
Saviotti\'s terms, variety that is not regenerated is eventually
exhausted by selection \[16\]; in Arthur\'s, the outcome is locked in
\[11\]. Open-source diffusion widens access to methods but does not
regenerate the local PI stock, which in the fitted model feeds the
binding entry lever. This is the sense in which a research system\'s PNR
is an evolutionary dead end for the field rather than a loss for one
country.

## 6.3 Who benefits from preserving variety?

Because the argument is mechanistic rather than national, its
beneficiaries can be stated by actor.

Governments and funders of smaller research systems. The model tells
them which transition is binding and how large a proportional change
would reach the threshold. Because $I_{0}$ is the closest lever,
doctoral pipelines and early-career entry are first-order defences,
while dropout reduction is the most elastic single lever; blocking
outflow is not. Table 9 maps levers to instruments.

Universities and research institutes. The PI stock is the node of the
network externality: institutions that convert hit researchers into PIs
($p_{D}$) and retain them ($d$) regenerate their own inflow. The
framework lets a university read its own transition rates against the
macro-regional ladder in Figure 7.

Early-career researchers. In the fitted model, going abroad is a smaller
threat to a home system than net-flow accounting implies; attrition is
the larger one. Policies that support return and dual affiliation rather
than penalising mobility serve both the individual and the system.
Researchers in systems near their threshold face shrinking prospects of
independent PI positions, and the equilibrium diagnostic gives an early
indication of that risk.

The field as a whole. Multi-site and internationally distributed teams
retain high impact \[50,51\], and collaboration between the largest
systems is more impactful than either alone \[13\]. Sustaining the
systems that supply those collaborators keeps the field\'s menu of
problems, benchmarks and evaluation norms wide, which is what allows it
to correct errors and change paradigms.

Society. AI systems are deployed in health, education, administration
and language across societies whose data and languages are
under-represented in the dominant paradigm \[41,42\]. A field with more
independent research systems is more likely to build, test and contest
systems for those contexts. The competition for talent among
jurisdictions \[5,52\] is therefore not zero-sum at the level of
society: the losers of a round of concentration include the users of the
technology, not only the systems that lost researchers.

## 6.4 Policy levers and early warning

Table 9 maps the sensitive levers to instruments and to the actors who
control them. $I_{0}$ and $h_{D}$ are mainly set by national funders and
ministries; $p_{D}$ and $d$ by universities and department heads;
$\beta$ by diaspora networks, return grants and recruiters. The
framework can be rerun with each OpenAlex release to update rates,
margins and proximity; the exploratory annual layer in Supplementary
Material Section S2 provides the machinery for tracking rates year by
year, although its current direction-prediction skill is low and it
should be read as a monitor rather than a forecast. Because endogenous
inflow is capped at 0.50× the critical reproduction rate, the implied
interventions are conservative: they aim to keep systems away from the
threshold, not to maximise any one system\'s share. Where inter-regional
mobility cannot be regulated, intra-regional levers---$d$, $h_{D}$ and
$p_{D}$---remain available and, in the fitted model, are the more
elastic ones. All counterfactuals are mechanical; turning them into
policy priorities requires programme costs, lags and behavioural
responses that are outside this paper.

  -----------------------------------------------------------------------
  **Lever**               **Policy instrument**   **Principal actor**
  ----------------------- ----------------------- -----------------------
  Dropout ($d$)           Early-career            Universities,
                          fellowships, childcare  department heads
                          and dual-career         
                          support, stable         
                          non-tenure tracks       

  Exogenous entry         Research-master and     National funders,
  ($I_{0}$)               undergraduate           ministries
                          pipelines, doctoral     
                          fellowships,            
                          recruitment visas       

  Return from abroad      Return grants, diaspora Diaspora networks,
  ($\beta$)               networks, dual          funders, recruiters
                          appointments,           
                          overseas-experience     
                          recognition             

  Domestic hit generation Independent-lab         National funders,
  ($h_{D}$)               programmes,             universities
                          doctoral/postdoctoral   
                          training, compute       
                          access                  

  PI promotion ($p_{D}$)  Tenure-track            Universities, funders
                          conversion, startup     
                          packages, project-based 
                          PI status               
  -----------------------------------------------------------------------

*Table 9. Transition levers, policy instruments and principal actors.*

## 6.5 Implications for policy and for the field\'s future

The results also bear on the strategy that large research systems are
currently pursuing. Concentrating talent, compute and data is
individually advantageous for each of them taken alone: it raises
short-run output, and a system that stands aside loses ground to those
that do not \[5,39,52\]. The mechanism shows why the collective outcome
of that strategy can be an evolutionary dead end. Each round of
concentration lowers $T/M$ in the systems that lose researchers, and
once one of them falls below $M$ its PI stock stops reproducing and
whatever distinct problem framings, benchmarks and data it carried leave
the field\'s menu, with no route back in the model \[11,16,17\]. The
efficiency gains accrue to the concentrating systems immediately; the
loss of error-correcting capacity is borne later by the whole field,
including those systems, and by the societies that use the technology
\[33,34\]. This is a coordination problem of the kind that talent
competition between jurisdictions cannot solve on its own, because no
single actor captures the benefit of the variety it preserves. Current
debates about pacing AI development are usually framed around safety;
the present results suggest a second reason for restraint in the race
for talent, which is that the race narrows the population on which the
field\'s own future selection depends.

The scenario in Section 5.7 puts numbers on this argument within the
fitted model. A region that pulls early-career researchers from
everywhere else gains a larger hosted pool and a larger share for as
long as we simulate, and the field ends more concentrated in every
setting we examined. Whether the field also ends smaller depends on the
host\'s own reproduction rates and on the variety elasticity γ: for the
largest observed host it does so with the fitted rates alone, for the
second-largest once γ exceeds a moderate value. Whether the dominant
region itself eventually falls below its own baseline requires a larger
γ still. Our data do not identify γ, so the model does not say how long
the advantage lasts or whether it ends within a national time horizon.
The evaluation does not depend on that question. The mechanism in
Section 2 holds that variety is what lets the field correct correlated
errors and change paradigms; if that premise carries any weight, γ is
positive, and at the scale of the field, of society and of humanity the
strategy trades error-correcting capacity that everyone uses for a share
advantage that one system holds inside a more concentrated and, in the
long run, smaller field. A relative advantage sustained inside a
shrinking field is exactly the outcome the mechanism identifies as a
dead end. Enclosure of AI/ML talent can therefore be individually
rational and remain collectively a poor strategy, and the case for
coordination does not rest on showing that the enclosing region will
lose.

For a system that is weighing whether to recruit aggressively from
others, the same scenario gives the conditions under which the strategy
turns against the recruiter. In the simulation, the dominant region\'s
own hosted hit stock falls below its no-pull baseline within the horizon
once γ exceeds a threshold that decreases as the pull intensifies: from
4.5 at $\varphi\  = \ 0.5$ to 1.5 at $\varphi\  = \ 8.0$ with
China-centred as host, and only at the two strongest pull intensities
($\gamma\  = \ 5.4$ and 3.0) with the United States as host, whose
higher fitted domestic reproduction rates absorb more of the variety
loss. The field\'s PI stock, its capacity to reproduce the next
generation, ends below baseline once γ exceeds 0.17-0.45 for
China-centred and 0.75-4.97 for the United States, in each case well
below the γ at which the host\'s own output reverts. Three
qualifications bound this reading. The thresholds are outputs of a
stylised simulation under the assumptions in Supplementary Table S8, not
empirical estimates; γ is not identified by our data; and the values
depend on which region pulls, how hard, whether hosts recruit, and which
outcome is scored, so no single number applies across settings. The
result is therefore not that international recruitment is harmful as
such. It is that a recruiter cannot assume its gain is permanent: the
harder it pulls, and the more the field\'s output owes to variety, the
smaller the γ at which its own advantage in absolute output reverts,
while the field-level losses in variety and in PI reproduction arrive
earlier and at smaller γ still. For a system deciding whether to draw on
smaller systems, that is the case for restraint the fitted model
supports; for a system deciding how to respond to being drawn on, it
points back to the levers in Table 9 rather than to barriers on
mobility.

Three practical steps follow from the fitted model rather than from
national interest. First, multilateral early-career fellowships aimed at
systems with low $T/M$, funded jointly by the largest systems, act on
the two levers the model identifies as most consequential: $I_{0}$ as
the closest lever to the threshold and dropout as the most elastic one.
Return grants and dual appointments that keep researchers attached to
their origin system ($\beta$) complement them without penalising
mobility, which the fitted model finds to be a weak lever. Second,
funders, leading venues and research institutions can monitor regional
variety directly, using $T/M$ and point-of-no-return proximity as
indicators that can be recomputed with each OpenAlex release alongside
author-affiliation statistics, and treat a declining margin in any
macro-region as a signal for the field rather than for that region
alone. Third, shared compute and data infrastructure open to researchers
in smaller systems acts on $h_{D}$ and $p_{D}$, the intra-regional
levers that remain available where mobility itself cannot or should not
be steered.

On the field\'s trajectory, the comparison of career windows in Section
5.4 shows the margin shrinking in Japan while it widened in the other
macro-regions, so the macro-regions are not drifting in the same
direction. If those drifts persist, a system can move from a comfortable
$T/M$ to the threshold without any single year looking alarming, and the
field would come to depend on fewer independent sources of problems and
evaluation norms. This is a projection of current rates, not a forecast,
and rates can change with policy; the exploratory annual layer in
Supplementary Material exists to detect whether they do. The point of
the framework is to make that drift visible while the levers that
reverse it are still inexpensive, before proximity to $M$ turns a
distributional question into one that the model treats as irreversible.

## 6.6 Limitations

OpenAlex affiliation and country assignments are noisy, especially for
multi-affiliated authors, and coverage of non-English venues is
incomplete. The macro-regional grouping is coarse; within-group
heterogeneity is substantial, and the grouping of, for example, mainland
China and Taiwan follows current OpenAlex country metadata rather than
any resolution of their relationship. Geographic variety is a proxy for
the cognitive and institutional variety the mechanism concerns, and the
model does not observe research content directly; that macro-regions
differ in institutions, languages and funding is documented, but that
they carry distinct research programmes is assumed here, not measured,
and claims about problem framings or benchmarks should be read with that
qualification. Irreversibility is likewise a property of the collapse
rule, not an empirical finding: a real system that fell below $M$ could
in principle rebuild through return migration or new entry, which the
model does not represent, so \'PNR\' denotes the threshold at which the
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
within the AI/ML subfield); the Supplementary robustness check varies
the PI proxy, but transfer of the pipeline to fields with alphabetical
author order or consortium authorship requires redefining these proxies,
as documented in the public code. Finally, the propositions are tested
on nine macro-regions, so correlational support for P1 is indicative;
the strongest support is for P2 and P3, which hold system by system.

# 7. Conclusion

Jevons asked how long a general-purpose input would sustain a system
that depended on it. For AI/ML research talent the analogous question is
not exhaustion but distribution: at what point does the concentration of
a reproducible input leave some research systems unable to reproduce it?
We derived a mechanism from career-transition rates through network
externalities and minimum viable scale to variety loss, and examined
four propositions with a compartment model fitted to open bibliometric
data for nine research macro-regions. All systems currently exceed their
minimum viable coauthor scale, but distance to the threshold is governed
by relative scale and by attrition rather than by size or outflow;
exogenous entry is the binding lever everywhere; the ranking is robust
to the form of the recruitment feedback; and rates have drifted between
career windows, shrinking the margin in Japan. The case for preserving
variety across research macro-regions rests on these mechanics rather
than on national interest: the beneficiaries are the governments and
institutions that can act on specific levers, the early-career
researchers whose prospects depend on them, the field whose capacity for
error correction depends on independent systems, and the societies whose
problems, data and languages those systems represent. A coupled
simulation of an aggressive concentration strategy shows why: the region
that concentrates talent gains a larger share for as long as we
simulate, while the field loses macro-regional variety at once and
concentration can reduce total output after a transient gain, so
concentrating talent is individually rational for each large system and
can become, at the scale of the field, of society and of humanity, an
evolutionary dead end; how long the individual advantage lasts depends
on how much research output owes to variety, which is the open empirical
question. This is why the practical response has to be shared: jointly
funded early-career fellowships and return grants for low-$T/M$ systems,
routine monitoring of $T/M$ across macro-regions, and open compute and
data infrastructure. Extensions include finer partitions with explicit
inter-regional spillovers, dynamic solution of the ODE to estimate time
to threshold, endogenous coauthor thresholds, application to other
general-purpose research fields, and integration with programme cost
data.

# References

1\. Jevons W S. The Coal Question: An Inquiry Concerning the Progress of
the Nation, and the Probable Exhaustion of Our Coal-Mines. London:
Macmillan, 1865.

2\. Bresnahan T F, Trajtenberg M. General purpose technologies \'Engines
of growth\'? J Econom. 1995;65(1):83-108.
https://doi.org/10.1016/0304-4076(94)01598-T

3\. MacroPolo. The Global AI Talent Tracker 2.0. Paulson Institute,
2023.
https://macropolo.org/digital-projects/the-global-ai-talent-tracker/

4\. Appelt S, van Beuzekom B, Galindo-Rueda F, de Pinho R. Which factors
influence the international mobility of research scientists? OECD
Science, Technology and Industry Working Papers 2015/02, 2015.
https://doi.org/10.1787/5js1tmrr2233-en

5\. Shachar A. The Race for Talent: Highly Skilled Migrants and
Competitive Immigration Regimes. NYU Law Rev. 2006;81(1):148-206.

6\. Thorn K, Holm-Nielsen L B. International Mobility of Researchers and
Scientists: Policy Options for Turning a Drain into a Gain. UNU-WIDER
Research Paper No. 2006/83, 2006.
https://www.wider.unu.edu/publication/international-mobility-researchers-and-scientists

7\. Franzoni C, Scellato G, Stephan P E. Foreign-born scientists:
mobility patterns for 16 countries. Nat Biotechnol.
2012;30(12):1250-1253. https://doi.org/10.1038/nbt.2449

8\. Stephan P E. The Economics of Science. J Econ Lit.
1996;34(3):1199-1235.

9\. Nelson R R, Winter S G. An Evolutionary Theory of Economic Change.
Cambridge, MA: Harvard University Press, 1982.

10\. Dosi G. Technological paradigms and technological trajectories: a
suggested interpretation of the determinants and directions of technical
change. Res Policy. 1982;11(3):147-162.
https://doi.org/10.1016/0048-7333(82)90016-6

11\. Arthur W B. Competing technologies, increasing returns, and lock-in
by historical events. Econ J. 1989;99(394):116-131.
https://doi.org/10.2307/2234208

12\. Priem J, Piwowar H, Orr R. OpenAlex: A fully-open index of
scholarly works, authors, venues, institutions, and concepts.
arXiv:2205.01833, 2022. https://doi.org/10.48550/arXiv.2205.01833

13\. AlShebli B, Memon S A, Evans J A, Rahwan T. China and the U.S.
produce more impactful AI research when collaborating together. Sci Rep.
2024;14:28576. https://doi.org/10.1038/s41598-024-79863-5

14\. Yuan S, Shao Z, Wei X, Tang J, Hall W, Wang Y, et al. Science
behind AI: the evolution of trend, mobility, and collaboration.
Scientometrics. 2020;124(2):993-1013.
https://doi.org/10.1007/s11192-020-03423-7

15\. Metcalfe J S. Evolutionary Economics and Creative Destruction.
London: Routledge, 1998. https://doi.org/10.4324/9780203275146

16\. Saviotti P P. Technological Evolution, Variety and the Economy.
Cheltenham: Edward Elgar, 1996. https://doi.org/10.4337/9781035334858

17\. David P A. Clio and the economics of QWERTY. Am Econ Rev.
1985;75(2):332-337.

18\. Lundvall B-Å. National Systems of Innovation: Toward a Theory of
Innovation and Interactive Learning. London: Anthem Press, 1992.

19\. Malerba F. Sectoral systems of innovation and production. Res
Policy. 2002;31(2):247-264.
https://doi.org/10.1016/S0048-7333(01)00139-1

20\. Stirling A. A general framework for analysing diversity in science,
technology and society. J R Soc Interface. 2007;4(15):707-719.
https://doi.org/10.1098/rsif.2007.0213

21\. Aghion P, Bloom N, Blundell R, Griffith R, Howitt P. Competition
and innovation: an inverted-U relationship. Q J Econ.
2005;120(2):701-728. https://doi.org/10.1162/0033553053970214

22\. Olazaran M. A sociological study of the official history of the
perceptrons controversy. Soc Stud Sci. 1996;26(3):611-659.
https://doi.org/10.1177/030631296026003005

23\. Rumelhart D E, Hinton G E, Williams R J. Learning representations
by back-propagating errors. Nature. 1986;323(6088):533-536.
https://doi.org/10.1038/323533a0

24\. Joravsky D. The Lysenko Affair. Cambridge, MA: Harvard University
Press, 1970.

25\. Colander D, Goldberg M, Haas A, Juselius K, Kirman A, Lux T, et al.
The financial crisis and the systemic failure of the economics
profession. Crit Rev. 2009;21(2-3):249-267.
https://doi.org/10.1080/08913810902934109

26\. Smolin L. The Trouble with Physics: The Rise of String Theory, the
Fall of a Science, and What Comes Next. Boston: Houghton Mifflin, 2006.

27\. Ullstrup A J. The impacts of the southern corn leaf blight
epidemics of 1970-1971. Annu Rev Phytopathol. 1972;10:37-50.
https://doi.org/10.1146/annurev.py.10.090172.000345

28\. McCook S. Global rust belt: Hemileia vastatrix and the ecological
integration of world coffee production since 1850. J Glob Hist.
2006;1(2):177-195. https://doi.org/10.1017/S174002280600012X

29\. Avelino J, Cristancho M, Georgiou S, Imbach P, Aguilar L, Bornemann
G, et al. The coffee rust crises in Colombia and Central America
(2008-2013): impacts, plausible causes and proposed solutions. Food
Secur. 2015;7(2):303-321. https://doi.org/10.1007/s12571-015-0446-9

30\. Ploetz R C. Management of Fusarium wilt of banana: a review with
special reference to tropical race 4. Crop Prot. 2015;73:7-15.
https://doi.org/10.1016/j.cropro.2015.01.007

31\. Chu J S G, Evans J A. Slowed canonical progress in large fields of
science. Proc Natl Acad Sci USA. 2021;118(41):e2021636118.
https://doi.org/10.1073/pnas.2021636118

32\. Park M, Leahey E, Funk R J. Papers and patents are becoming less
disruptive over time. Nature. 2023;613(7942):138-144.
https://doi.org/10.1038/s41586-022-05543-x

33\. Kleinberg J, Raghavan M. Algorithmic monoculture and social
welfare. Proc Natl Acad Sci USA. 2021;118(22):e2018340118.
https://doi.org/10.1073/pnas.2018340118

34\. Hooker S. The hardware lottery. Commun ACM. 2021;64(12):58-65.
https://doi.org/10.1145/3467017

35\. Koch B, Denton E, Hanna A, Foster J G. Reduced, reused and
recycled: the life of a dataset in machine learning research.
arXiv:2112.01716, 2021. https://doi.org/10.48550/arXiv.2112.01716

36\. Raji I D, Bender E M, Paullada A, Denton E, Hanna A. AI and the
everything in the whole wide world benchmark. arXiv:2111.15366, 2021.
https://doi.org/10.48550/arXiv.2111.15366

37\. Kaplan J, McCandlish S, Henighan T, Brown T B, Chess B, Child R, et
al. Scaling laws for neural language models. arXiv:2001.08361, 2020.
https://doi.org/10.48550/arXiv.2001.08361

38\. Bommasani R, Hudson D A, Adeli E, Altman R, Arora S, von Arx S, et
al. On the opportunities and risks of foundation models.
arXiv:2108.07258, 2021. https://doi.org/10.48550/arXiv.2108.07258

39\. Sevilla J, Heim L, Ho A, Besiroglu T, Hobbhahn M, Villalobos P.
Compute trends across three eras of machine learning. In: 2022
International Joint Conference on Neural Networks (IJCNN). IEEE; 2022.
p. 1-8. https://doi.org/10.1109/IJCNN55064.2022.9891914

40\. Ahmed N, Wahed M. The de-democratization of AI: deep learning and
the compute divide in artificial intelligence research.
arXiv:2010.15581, 2020. https://doi.org/10.48550/arXiv.2010.15581

41\. Joshi P, Santy S, Budhiraja A, Bali K, Choudhury M. The state and
fate of linguistic diversity and inclusion in the NLP world. In:
Proceedings of the 58th Annual Meeting of the Association for
Computational Linguistics. ACL; 2020. p. 6282-6293.
https://doi.org/10.18653/v1/2020.acl-main.560

42\. Bender E M, Gebru T, McMillan-Major A, Shmitchell S. On the dangers
of stochastic parrots: can language models be too big? In: Proceedings
of the 2021 ACM Conference on Fairness, Accountability, and Transparency
(FAccT \'21). ACM; 2021. p. 610-623.
https://doi.org/10.1145/3442188.3445922

43\. Hong L, Page S E. Groups of diverse problem solvers can outperform
groups of high-ability problem solvers. Proc Natl Acad Sci USA.
2004;101(46):16385-16389. https://doi.org/10.1073/pnas.0403723101

44\. Alcott B. Jevons\' paradox. Ecol Econ. 2005;54(1):9-21.
https://doi.org/10.1016/j.ecolecon.2005.03.020

45\. Katz M L, Shapiro C. Network externalities, competition, and
compatibility. Am Econ Rev. 1985;75(3):424-440.

46\. Shaffer M L. Minimum Population Sizes for Species Conservation.
BioScience. 1981;31(2):131-134. https://doi.org/10.2307/1308256

47\. Huntington S P. The Clash of Civilizations and the Remaking of
World Order. New York: Simon & Schuster, 1996.

48\. State B, Park P, Weber I, Macy M. The mesh of civilizations in the
global network of digital communication. PLoS ONE. 2015;10(5):e0122543.
https://doi.org/10.1371/journal.pone.0122543

49\. Chinchilla-Rodríguez Z, Miao L, Murray D, Robinson-García N, Costas
R, Sugimoto C R. A global comparison of scientific mobility and
collaboration according to national scientific capacities. Front Res
Metr Anal. 2018;3:17. https://doi.org/10.3389/frma.2018.00017

50\. Jones B F, Wuchty S, Uzzi B. Multi-University Research Teams:
Shifting Impact, Geography, and Stratification in Science. Science.
2008;322(5905):1259-1262. https://doi.org/10.1126/science.1158357

51\. Freeman R B, Huang W. Collaboration: Strength in diversity. Nature.
2014;513(7518):305. https://doi.org/10.1038/513305a

52\. Kerr W R. Global Talent and U.S. Immigration Policy. Harvard
Business School Working Paper No. 20-107, 2020.
https://www.hbs.edu/ris/Publication%20Files/20-107_0967f1ab-1d23-4d54-b5a1-c884234d9b31.pdf
