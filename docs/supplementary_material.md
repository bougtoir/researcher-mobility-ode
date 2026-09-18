AI researchers as the next coal: transition rates, minimum viable
research communities and the preservation of variety in global AI/ML

This supplement provides the country mapping, the exploratory annual
estimation layer, robustness checks on the PI proxy and on the minimum
viable scale, and detailed tables that support the main manuscript.
Values are reproduced from the same result CSVs used to generate the
main tables and figures; no numbers are hard-coded.

# S1. Country-to-macro-region mapping

Supplementary Table S1 lists every country with at least one AI/ML work
in 2022-2023 under its macro-region. The partition starts from
Huntington\'s taxonomy and is adjusted for AI/ML sample size (Latin
American, Orthodox and sub-Saharan African countries merged into Other
regions; the United States separated from the rest of the Anglosphere).
The labels are operational aggregations of publication-affiliation
patterns and carry no claim about cultural identity. The complete
machine-readable mapping, including countries with zero works, is
data/country_civilization_mapping.json in the public repository.

  -----------------------------------------------------------------------
  **Macro-region**        **Countries**           **Works**
  ----------------------- ----------------------- -----------------------
  Anglosphere ex-US       United Kingdom of Great 66221
                          Britain and Northern    
                          Ireland, Canada,        
                          Australia, Ireland, New 
                          Zealand                 

  China-centred           China, Korea, Republic  175918
                          of, Hong Kong,          
                          Singapore, Taiwan,      
                          Province of China, Viet 
                          Nam, Macao              

  Continental Europe      Germany, France, Italy, 156002
                          Spain, Netherlands,     
                          Kingdom of the,         
                          Switzerland, Poland,    
                          Sweden, Austria,        
                          Belgium, Portugal,      
                          Denmark, Greece,        
                          Norway, Czechia,        
                          Finland, Romania,       
                          Hungary, Bulgaria,      
                          Slovenia, Slovakia,     
                          Croatia, Cyprus,        
                          Luxembourg, Estonia,    
                          Lithuania, Latvia,      
                          Iceland, Malta          

  Islamic world           Indonesia, Saudi        114388
                          Arabia, $T$ürkiye,      
                          Malaysia, Iran, Islamic 
                          Republic of, Pakistan,  
                          Egypt, Iraq, United     
                          Arab Emirates,          
                          Bangladesh, Jordan,     
                          Morocco, Algeria,       
                          Tunisia, Qatar,         
                          Lebanon, Kazakhstan,    
                          Oman, Uzbekistan,       
                          Yemen, Kuwait, Bahrain, 
                          Azerbaijan, Palestine,  
                          State of, Sudan, Brunei 
                          Darussalam, Libya       

  Japan                   Japan                   16929

  Other Western (Israel)  Israel                  3847

  Other regions           Russian Federation,     46466
                          Brazil, Mexico,         
                          Nigeria, South Africa,  
                          Ukraine, Thailand,      
                          Chile, Philippines,     
                          Colombia, Argentina,    
                          Serbia, Ethiopia,       
                          Ghana, Peru, Ecuador,   
                          Kenya, Cameroon,        
                          Belarus, Tanzania,      
                          United Republic of,     
                          Mongolia, Bosnia and    
                          Herzegovina, North      
                          Macedonia, Armenia,     
                          Uganda, Uruguay         

  South Asia              India, Nepal, Sri Lanka 53745

  United States           United States of        100154
                          America                 
  -----------------------------------------------------------------------

*Supplementary Table S1. Country membership of the research
macro-regions (countries with at least one AI/ML work in 2022-2023).*

# S2. Annual estimation and projection layer (exploratory extension)

This section is an exploratory extension of the steady-state analysis:
it asks whether the fitted rates can be updated year by year, not
whether the projection forecasts stocks. The annual layer re-estimates
each transition rate for every calendar year 2000-2016 from the
reconstructed compartment state of the cohort. Rates are estimated as
transitions divided by exposure with a Laplace pseudocount and projected
with a linear trend fitted to the 2000-2016 series, regularised in two
ways: (i) projected rates are clipped to the \[0, 1\] interval (inflows
are projected on a log1p scale and clipped to be non-negative), and (ii)
where fewer than four annual observations are available or the linear
fit explains less than 10% of the variance (R² \< 0.10), the
macro-region\'s own 2000-2016 mean is carried forward instead of the
trend; and (iii) projected dropout is capped at 1.5 times its 90th
percentile over the training period. No PI-reproduction stability cap is
imposed in the annual layer; that cap applies only to the steady-state
model. Projected rates for 2017-2026 are applied to the 2016 compartment
state with a one-year time step, and the projected 2017-2023 compartment
counts are compared with the observed reconstruction. Accuracy is
reported as RMSE, MAPE, direction agreement (whether the projected and
observed year-to-year change have the same sign) and threshold-alarm
metrics (whether the projection correctly flags years in which the
observed active pool $T\  = \ D\  + \ H_{D}\  + \ P_{D}$ falls below
$M$, its group-specific minimum viable coauthor scale; Supplementary
Table S2 reports the number of observed and projected alarm years
alongside accuracy, sensitivity, specificity and precision). Stock-level
errors are larger than rate-level errors because the cohort is fixed at
2016 and cannot contain the new entrants that the projection adds; the
layer is therefore a drift-and-threshold alarm, not a population
forecast.

Supplementary Figure S1 plots observed 2000-2016 and projected 2017-2026
transition rates by macro-region, Supplementary Figure S2 the
accumulated cross-region abroad author-years by origin and destination
(a lower-bound proxy for inter-regional pipelines, used as the host
distribution of the talent-concentration scenario in the main text), and
Supplementary Figure S3 compares the 2017-2023 projection with observed
compartment counts. Rate-level projections have RMSE 0.0892 and a skill
ratio (baseline RMSE / model RMSE) of 0.99 against a historical-mean
baseline, so they do not improve on simply carrying the historical mean
forward; stock-level errors are larger (RMSE 10,190). Year-to-year
direction agreement is 21.6%. The observed compartment series of the
closed cohort falls below $M$ in 5 macro-region-years (Other Western
(Israel); Supplementary Table S2), whereas the projection flags 0. These
observed alarms are an artefact of cohort closure, not evidence that the
system is below its threshold: the observed series excludes everyone who
entered after 2016, so it declines by construction, while the
equilibrium $T$ of the main text includes continuing entry. The alarm
metrics are reported for completeness only.

![](media/image1.png){width="6.0in" height="5.1962259405074365in"}

*Supplementary Figure S1. Observed (solid) and projected (dashed)
transition rates by research macro-region, 2000-2026.*

![](media/image2.png){width="5.8in" height="4.703937007874016in"}

*Supplementary Figure S2. Cross-region abroad author-year accumulation
by origin (rows) and destination (columns); same-region cells and
Unknown destinations excluded (lower-bound proxy).*

![](media/image3.png){width="6.0in" height="3.8268711723534556in"}

*Supplementary Figure S3. Observed (solid) and projected (dashed)
compartment counts by research macro-region, 2017-2023. The dotted line
marks the end of the training period (2016).*

# Supplementary Table S2. Projection accuracy by research macro-region, 2017-2023

  ---------------------------------------------------------------------------------------------------------------------------------------------
  **Group**       **RMSE**   **MAPE**   **Direction   **Alarm      **Alarm         **Alarm         **Alarm       **Alarm years  **Alarm years
                                        agreement**   Accuracy**   Sensitivity**   Specificity**   Precision**   (observed)**   (projected)**
  --------------- ---------- ---------- ------------- ------------ --------------- --------------- ------------- -------------- ---------------
  Anglosphere     3544.26    86.2%      19.4%         100.0%       ---             100.0%          ---           0.00           0.00
  ex-US                                                                                                                         

  Continental     11674.84   103.1%     19.4%         100.0%       ---             100.0%          ---           0.00           0.00
  Europe                                                                                                                        

  South Asia      7915.72    188.4%     16.7%         100.0%       ---             100.0%          ---           0.00           0.00

  Islamic world   16757.46   273.0%     22.2%         100.0%       ---             100.0%          ---           0.00           0.00

  Japan           1677.63    69.9%      27.8%         100.0%       ---             100.0%          ---           0.00           0.00

  Other regions   6149.73    132.4%     16.7%         100.0%       ---             100.0%          ---           0.00           0.00

  Other Western   256.88     98.7%      27.8%         28.6%        0.0%            100.0%          ---           5.00           0.00
  (Israel)                                                                                                                      

  China-centred   18771.59   132.3%     19.4%         100.0%       ---             100.0%          ---           0.00           0.00

  United States   7013.54    77.4%      25.0%         100.0%       ---             100.0%          ---           0.00           0.00
  ---------------------------------------------------------------------------------------------------------------------------------------------

*Supplementary Table S2. Projection accuracy by research macro-region,
2017-2023.*

# Supplementary Table S3. Projection accuracy by compartment, 2017-2023

  -----------------------------------------------------------------------
  **Compartment**   **RMSE**          **MAPE**          **Direction
                                                        agreement**
  ----------------- ----------------- ----------------- -----------------
  A                 849.47            215.1%            7.4%

  $D$               19801.25          263.3%            1.9%

  $H_{A}$           394.83            50.1%             38.9%

  $H_{D}$           8094.10           171.6%            9.3%

  $P_{A}$           1744.50           36.4%             25.9%

  $P_{D}$           12709.83          37.7%             46.3%
  -----------------------------------------------------------------------

*Supplementary Table S3. Projection accuracy by compartment, 2017-2023.*

# Supplementary Table S4. Mean observed annual transition rates by research macro-region, 2000-2016

  ------------------------------------------------------------------------------------
  **Group**       $\alpha$   $\beta$    $h_{D}$    $p_{D}$    $d$        $I_{total}$
  --------------- ---------- ---------- ---------- ---------- ---------- -------------
  Anglosphere     0.012      0.034      0.046      0.087      0.046      3771.88
  ex-US                                                                  

  China-centred   0.007      0.027      0.026      0.091      0.034      11179.47

  Continental     0.007      0.036      0.051      0.094      0.046      9935.94
  Europe                                                                 

  Islamic world   0.013      0.038      0.025      0.095      0.030      3002.53

  Japan           0.007      0.038      0.024      0.070      0.055      1882.76

  Other Western   0.015      0.033      0.059      0.068      0.044      258.65
  (Israel)                                                               

  Other regions   0.009      0.035      0.026      0.078      0.042      2955.29

  South Asia      0.009      0.033      0.027      0.082      0.028      1651.12

  United States   0.009      0.033      0.047      0.086      0.046      7929.82
  ------------------------------------------------------------------------------------

*Supplementary Table S4. Mean observed annual transition rates by
research macro-region, 2000-2016.*

# Supplementary Table S5. Top cross-region origin-destination abroad author-year pairs

  -----------------------------------------------------------------------
  **Origin**              **Destination**         **Author-years**
  ----------------------- ----------------------- -----------------------
  United States           China-centred           52689

  United States           Continental Europe      21968

  Anglosphere ex-US       China-centred           20534

  China-centred           United States           18505

  Continental Europe      Anglosphere ex-US       18156

  United States           Anglosphere ex-US       17719

  Continental Europe      United States           15459

  Anglosphere ex-US       Continental Europe      15003

  Anglosphere ex-US       United States           14422

  Continental Europe      China-centred           10535
  -----------------------------------------------------------------------

*Supplementary Table S5. Top cross-region origin-destination abroad
author-year pairs.*

# Supplementary Table S6. Bootstrap 95% confidence intervals for equilibrium $T$ and domestic PI pool $P_{D}$

  ---------------------------------------------------------------------------
  **Group**       $T$ **median** $T$ **95% CI** $P_{D}$        $P_{D}$ **95%
                                                **mean**       CI**
  --------------- -------------- -------------- -------------- --------------
  Anglosphere     67546          \[66728,       29814          \[29158,
  ex-US                          68334\]                       30486\]

  Continental     195077         \[193718,      83476          \[82421,
  Europe                         196316\]                      84527\]

  South Asia      53407          \[52402,       30277          \[29348,
                                 54515\]                       31258\]

  Islamic world   88428          \[87356,       47264          \[46155,
                                 89880\]                       48511\]

  Japan           29372          \[28932,       7387           \[7128, 7662\]
                                 29757\]                       

  Other regions   59396          \[58590,       22326          \[21715,
                                 60178\]                       22975\]

  Other Western   4829           \[4602, 5077\] 2163           \[1981, 2370\]
  (Israel)                                                     

  China-centred   303843         \[301809,      133015         \[131418,
                                 305720\]                      134567\]

  United States   146991         \[145947,      63906          \[62994,
                                 148235\]                      64906\]
  ---------------------------------------------------------------------------

*Supplementary Table S6. Bootstrap 95% confidence intervals for
equilibrium* $T$ *and domestic PI pool* $P_{D}$*.*

# Supplementary Table S7. Closest point of no return under linear versus saturating inflow

  ------------------------------------------------------------------------------------------------
  **Group**       **Linear   **Linear   **Linear      **Saturating   **Saturating   **Saturating
                  lever**    factor**   proximity**   lever**        factor**       proximity**
  --------------- ---------- ---------- ------------- -------------- -------------- --------------
  United States   $I_{0}$    0.013      0.988         $I_{0}$        0.011          0.989

  Anglosphere     $I_{0}$    0.047      0.953         $I_{0}$        0.042          0.958
  ex-US                                                                             

  Continental     $I_{0}$    0.020      0.980         $I_{0}$        0.018          0.982
  Europe                                                                            

  China-centred   $I_{0}$    0.010      0.990         $I_{0}$        0.009          0.991

  Japan           $I_{0}$    0.061      0.939         $I_{0}$        0.059          0.942

  South Asia      $I_{0}$    0.042      0.958         $I_{0}$        0.034          0.966

  Islamic world   $I_{0}$    0.025      0.975         $I_{0}$        0.021          0.979

  Other Western   $I_{0}$    0.332      0.668         $I_{0}$        0.307          0.693
  (Israel)                                                                          

  Other regions   $I_{0}$    0.035      0.965         $I_{0}$        0.031          0.969
  ------------------------------------------------------------------------------------------------

*Supplementary Table S7. Closest point-of-no-return lever, critical
factor and proximity for the active pool under linear and saturating
PI-driven inflow.*

# Supplementary Table S8. Talent-concentration scenario: inputs and their status

  --------------------------------------------------------------------------------------------
  **Parameter**           **Value**                                    **Status**
  ----------------------- -------------------------------------------- -----------------------
  phi_grid                0.0,0.5,1.0,2.0,4.0,8.0                      stylised

  gamma_grid              0.0,1.0,2.0                                  stylised

  horizon_years           100.00                                       stylised

  tau_years               24.31                                        fitted (1 / mean $d$)

  horizon_in_tau          4.11                                         derived

  pull_rule               additional outflow alpha_i phi from $D_{i}$  stylised
                          to separate compartments hosted by the focal 
                          region (i != focal); pre-existing abroad     
                          stock keeps observed host shares W           

  retention_rule          beta_i/(1+phi) for researchers pulled to the stylised
                          focal region                                 

  host_recruitment_rule   each host recruits $r_{j}$ x hosted abroad   stylised
                          PIs; I0_j reduced so the fitted equilibrium  
                          is unchanged                                 

  collapse_rule           $r_{i}$ -\> 0 permanently once               stylised
                          $T_{i}\  < \ M_{i}$ (integrator terminal     
                          event at the crossing)                       

  variety_rule            $h_{D}$, $h_{A}$ scaled by                   stylised
                          ($N_{eff}/N_{eff0}$)\^gamma; gamma = 0 is    
                          the fitted model                             

  initial_state           baseline equilibrium from                    fitted
                          results/endogenous/equilibrium_summary.csv   

  transition_rates        data/cohort/transition_rates.csv             fitted

  recruitment_split       $I_{0}$, $r$ from                            fitted / stylised
                          results/endogenous/equilibrium_summary.csv   
                          (exogenous_share=fitted); 0.25 as            
                          sensitivity                                  

  host_shares             results/annual/annual_interciv_stock.csv,    fitted
                          all years, off-diagonal                      
  --------------------------------------------------------------------------------------------

*Supplementary Table S8. Inputs to the talent-concentration scenario
(Section 4.5). \'Fitted\' inputs come from the estimated model and
observed mobility data; \'stylised\' inputs are modelling assumptions
without an empirical estimate.*

# S3. Robustness to the PI proxy definition

The baseline defines a PI by the first last-author paper. To test this
choice, the full AI/ML author population was re-extracted from OpenAlex
with the corresponding-author flag of every authorship retained, and
each author was classified under three definitions on the same snapshot:
(a) first last-author paper (baseline); (b) first paper on which the
author is flagged as corresponding author (OpenAlex
authorships.is_corresponding); (c) second last-author paper, i.e. last
author on at least two papers. The re-extracted snapshot contains
719,173 authors against 723,647 in the published cohort; the difference
reflects OpenAlex updates between extractions, so definitions are
compared with each other on the same snapshot (Supplementary Table S10)
and the baseline definition is also compared with the published results.
For each definition the transition rates were re-estimated, the
endogenous-inflow equilibrium, the elasticities and the closest point of
no return were recomputed with the same $M$, and the nine-region
rankings were compared by Spearman rank correlation. Two quantities are
invariant to the proxy by construction and are reported only for
completeness: because $I_{0}$ is calibrated so that total equilibrium
entry equals observed entry (Section 4.2), the equilibrium active pool
$T$ (hence $T/M$) and the proximity of the entry lever $I_{0}$ do not
depend on how PIs are identified. The proxy does change the promotion
rates $p_{D}$ and $p_{A}$, the equilibrium PI pool $P_{D}$, the
exogenous/PI-driven split of entry ($I_{0}$, $r$), the elasticity of $T$
to $p_{D}$ and the point of no return of the PI pool relative to its own
threshold $k$. Supplementary Table S9 reports the region-level results
and Supplementary Table S10 the rank agreement on these proxy-dependent
quantities.

  -----------------------------------------------------------------------------------------------------------------------------------------------------------
  **PI proxy**           **Group**       **Share   $p_{D}$   $T/M$   **Closest     **Proximity   $P_{D}$   **Closest lever   **Proximity       **Elasticity
                                         of                          lever         (**$T$**)**             (**$P_{D}$**)**   (**$P_{D}$**)**   of** $T$
                                         authors                     (**$T$**)**                                                               **to** $p_{D}$
                                         who are                                                                                               
                                         PIs**                                                                                                 
  ---------------------- --------------- --------- --------- ------- ------------- ------------- --------- ----------------- ----------------- --------------
  First last-author      Anglosphere     0.667     0.073     21.57   exogenous     0.954         30773     exogenous entry   0.980             0.338
  paper (baseline)       ex-US                                       entry rate                            rate ($I_{0}$)                      
                                                                     ($I_{0}$)                                                                 

  First last-author      Continental     0.666     0.073     49.68   exogenous     0.980         83975     exogenous entry   0.991             0.355
  paper (baseline)       Europe                                      entry rate                            rate ($I_{0}$)                      
                                                                     ($I_{0}$)                                                                 

  First last-author      South Asia      0.734     0.088     23.93   exogenous     0.958         30608     exogenous entry   0.982             0.211
  paper (baseline)                                                   entry rate                            rate ($I_{0}$)                      
                                                                     ($I_{0}$)                                                                 

  First last-author      Islamic world   0.744     0.091     39.33   exogenous     0.975         47906     exogenous entry   0.988             0.220
  paper (baseline)                                                   entry rate                            rate ($I_{0}$)                      
                                                                     ($I_{0}$)                                                                 

  First last-author      Japan           0.618     0.064     16.88   exogenous     0.941         7642      exogenous entry   0.945             0.265
  paper (baseline)                                                   entry rate                            rate ($I_{0}$)                      
                                                                     ($I_{0}$)                                                                 

  First last-author      Other regions   0.672     0.074     28.67   exogenous     0.965         22513     exogenous entry   0.978             0.315
  paper (baseline)                                                   entry rate                            rate ($I_{0}$)                      
                                                                     ($I_{0}$)                                                                 

  First last-author      Other Western   0.597     0.060     2.94    exogenous     0.660         2099      exogenous entry   0.823             0.355
  paper (baseline)       (Israel)                                    entry rate                            rate ($I_{0}$)                      
                                                                     ($I_{0}$)                                                                 

  First last-author      China-centred   0.707     0.082     96.96   exogenous     0.990         136375    exogenous entry   0.995             0.256
  paper (baseline)                                                   entry rate                            rate ($I_{0}$)                      
                                                                     ($I_{0}$)                                                                 

  First last-author      United States   0.662     0.072     80.16   exogenous     0.988         64884     exogenous entry   0.995             0.356
  paper (baseline)                                                   entry rate                            rate ($I_{0}$)                      
                                                                     ($I_{0}$)                                                                 

  First                  Anglosphere     0.515     0.048     21.57   exogenous     0.954         26050     exogenous entry   0.976             0.428
  corresponding-author   ex-US                                       entry rate                            rate ($I_{0}$)                      
  paper                                                              ($I_{0}$)                                                                 

  First                  Continental     0.544     0.052     49.68   exogenous     0.980         73375     exogenous entry   0.989             0.430
  corresponding-author   Europe                                      entry rate                            rate ($I_{0}$)                      
  paper                                                              ($I_{0}$)                                                                 

  First                  South Asia      0.549     0.053     23.93   exogenous     0.958         26708     exogenous entry   0.980             0.305
  corresponding-author                                               entry rate                            rate ($I_{0}$)                      
  paper                                                              ($I_{0}$)                                                                 

  First                  Islamic world   0.543     0.052     39.33   exogenous     0.975         41082     exogenous entry   0.986             0.322
  corresponding-author                                               entry rate                            rate ($I_{0}$)                      
  paper                                                              ($I_{0}$)                                                                 

  First                  Japan           0.451     0.040     16.88   exogenous     0.941         6083      exogenous entry   0.930             0.513
  corresponding-author                                               entry rate                            rate ($I_{0}$)                      
  paper                                                              ($I_{0}$)                                                                 

  First                  Other regions   0.514     0.048     28.67   exogenous     0.965         19126     exogenous entry   0.974             0.405
  corresponding-author                                               entry rate                            rate ($I_{0}$)                      
  paper                                                              ($I_{0}$)                                                                 

  First                  Other Western   0.482     0.044     2.94    exogenous     0.660         1824      dropout rate      0.728             0.427
  corresponding-author   (Israel)                                    entry rate                            ($d$)                               
  paper                                                              ($I_{0}$)                                                                 

  First                  China-centred   0.559     0.055     96.96   exogenous     0.990         120427    exogenous entry   0.995             0.337
  corresponding-author                                               entry rate                            rate ($I_{0}$)                      
  paper                                                              ($I_{0}$)                                                                 

  First                  United States   0.461     0.041     80.16   exogenous     0.988         50906     exogenous entry   0.993             0.482
  corresponding-author                                               entry rate                            rate ($I_{0}$)                      
  paper                                                              ($I_{0}$)                                                                 

  Second last-author     Anglosphere     0.472     0.043     21.57   exogenous     0.954         24564     exogenous entry   0.975             0.456
  paper (recurrent last  ex-US                                       entry rate                            rate ($I_{0}$)                      
  author)                                                            ($I_{0}$)                                                                 

  Second last-author     Continental     0.481     0.044     49.68   exogenous     0.980         67407     exogenous entry   0.988             0.472
  paper (recurrent last  Europe                                      entry rate                            rate ($I_{0}$)                      
  author)                                                            ($I_{0}$)                                                                 

  Second last-author     South Asia      0.536     0.051     23.93   exogenous     0.958         26351     exogenous entry   0.980             0.314
  paper (recurrent last                                              entry rate                            rate ($I_{0}$)                      
  author)                                                            ($I_{0}$)                                                                 

  Second last-author     Islamic world   0.535     0.051     39.33   exogenous     0.975         40550     exogenous entry   0.986             0.332
  paper (recurrent last                                              entry rate                            rate ($I_{0}$)                      
  author)                                                            ($I_{0}$)                                                                 

  Second last-author     Japan           0.460     0.041     16.88   exogenous     0.941         6151      exogenous entry   0.931             0.478
  paper (recurrent last                                              entry rate                            rate ($I_{0}$)                      
  author)                                                            ($I_{0}$)                                                                 

  Second last-author     Other regions   0.471     0.042     28.67   exogenous     0.965         17994     exogenous entry   0.973             0.437
  paper (recurrent last                                              entry rate                            rate ($I_{0}$)                      
  author)                                                            ($I_{0}$)                                                                 

  Second last-author     Other Western   0.440     0.039     2.94    exogenous     0.660         1731      dropout rate      0.680             0.447
  paper (recurrent last  (Israel)                                    entry rate                            ($d$)                               
  author)                                                            ($I_{0}$)                                                                 

  Second last-author     China-centred   0.479     0.044     96.96   exogenous     0.990         110377    exogenous entry   0.994             0.388
  paper (recurrent last                                              entry rate                            rate ($I_{0}$)                      
  author)                                                            ($I_{0}$)                                                                 

  Second last-author     United States   0.460     0.041     80.16   exogenous     0.988         50768     exogenous entry   0.993             0.484
  paper (recurrent last                                              entry rate                            rate ($I_{0}$)                      
  author)                                                            ($I_{0}$)                                                                 
  -----------------------------------------------------------------------------------------------------------------------------------------------------------

*Supplementary Table S9. Equilibrium active pool,* $T/M$*, rank and
closest point-of-no-return lever by research macro-region under three PI
proxy definitions (same OpenAlex snapshot;* $M$ *held at its baseline
value).*

  -----------------------------------------------------------------------------------------------------------------------------------------------------
  **PI proxy**           **Spearman rho  **Spearman rho **Spearman rho    **Spearman rho    **Spearman rho **Same        **Regions**   **Same
                         (**$T/M$**)**   (PNR           (**$p_{D}$**)**   (**$P_{D}$**)**   (PNR           closest lever               lowest-**$T/M$
                                         proximity,**                                       proximity,**   (regions)**                 **region**
                                         $T$**)**                                           $P_{D}$**)**                               
  ---------------------- --------------- -------------- ----------------- ----------------- -------------- ------------- ------------- ----------------
  First                  1.00            1.00           0.73              0.98              1.00           9.00          9.00          yes
  corresponding-author                                                                                                                 
  paper                                                                                                                                

  Second last-author     1.00            1.00           0.87              0.98              1.00           9.00          9.00          yes
  paper (recurrent last                                                                                                                
  author)                                                                                                                              
  -----------------------------------------------------------------------------------------------------------------------------------------------------

*Supplementary Table S10. Rank agreement between alternative PI proxies
and the baseline definition across the nine research macro-regions
(Spearman rho).* $T/M$ *and the* $T$ *proximity are invariant by
construction (see text).*

# S4. Sensitivity to the minimum viable scale $M$

$M\  = \ k$ x c-bar is an operational threshold, so we multiply it by
0.50, 0.75, 1.00, 1.25, 1.50, 2.00 and recompute, for every
macro-region, $T/M$, the rank by $T/M$, the closest point-of-no-return
lever and its proximity, and the elasticities of $T$ to dropout ($d$)
and early-career outflow (alpha). Supplementary Table S11 summarises the
results. No macro-region falls below $M$ at any multiplier (minimum
$T/M$ 1.51 at the largest multiplier); the rankings by $T/M$ and by
proximity are unchanged (Spearman rho = 1.00 and 1.00 against the
baseline at every multiplier); and \|elasticity to $d$\| exceeds
\|elasticity to alpha\| in every macro-region at every multiplier. The
closest lever changes only where a larger $M$ brings the dropout lever
closer than exogenous entry: Other Western (Israel) at multiplier 1.25
(dropout rate ($d$), proximity 0.533); Other Western (Israel) at
multiplier 1.50 (dropout rate ($d$), proximity 0.374); Other Western
(Israel) at multiplier 2.00 (dropout rate ($d$), proximity 0.184).

  -------------------------------------------------------------------------------------------------------------------------------------------
  $M$              **Regions   **Minimum**   **Lowest-**$T/M$   **Closest   **Spearman    **Spearman    **Closest     **Regions with**
  **multiplier**   below** $M$ $T/M$         **region**         region**    rho (**$T/M$  rho           lever         $|e_{d}|$ **\>
                                                                            **vs          (proximity vs unchanged     \|**$e_{alpha}$**\|**
                                                                            baseline)**   baseline)**   (regions)**   
  ---------------- ----------- ------------- ------------------ ----------- ------------- ------------- ------------- -----------------------
  0.50             0.00        6.03          Other Western      Other       1.00          1.00          9.00          9.00
                                             (Israel)           Western                                               
                                                                (Israel)                                              

  0.75             0.00        4.02          Other Western      Other       1.00          1.00          9.00          9.00
                                             (Israel)           Western                                               
                                                                (Israel)                                              

  1.00             0.00        3.01          Other Western      Other       1.00          1.00          9.00          9.00
                                             (Israel)           Western                                               
                                                                (Israel)                                              

  1.25             0.00        2.41          Other Western      Other       1.00          1.00          8.00          9.00
                                             (Israel)           Western                                               
                                                                (Israel)                                              

  1.50             0.00        2.01          Other Western      Other       1.00          1.00          8.00          9.00
                                             (Israel)           Western                                               
                                                                (Israel)                                              

  2.00             0.00        1.51          Other Western      Other       1.00          1.00          8.00          9.00
                                             (Israel)           Western                                               
                                                                (Israel)                                              
  -------------------------------------------------------------------------------------------------------------------------------------------

*Supplementary Table S11. Sensitivity of the steady-state results to the
level of the minimum viable coauthor scale* $M$ *(multipliers applied to
every macro-region).*

  --------------------------------------------------------------------------------------------------------------
  **Group**       $M$              $T/M$    $T/M$      **Closest   **Proximity**   **Elasticity   **Elasticity
                  **multiplier**            **rank**   lever**                     (**$d$**)**    (alpha)**
  --------------- ---------------- -------- ---------- ----------- --------------- -------------- --------------
  Anglosphere     0.50             42.43    3.00       exogenous   0.976           -2.680         -0.267
  ex-US                                                entry rate                                 
                                                       ($I_{0}$)                                  

  Anglosphere     0.75             28.28    3.00       exogenous   0.965           -2.680         -0.267
  ex-US                                                entry rate                                 
                                                       ($I_{0}$)                                  

  Anglosphere     1.00             21.21    3.00       exogenous   0.953           -2.680         -0.267
  ex-US                                                entry rate                                 
                                                       ($I_{0}$)                                  

  Anglosphere     1.25             16.97    3.00       exogenous   0.941           -2.680         -0.267
  ex-US                                                entry rate                                 
                                                       ($I_{0}$)                                  

  Anglosphere     1.50             14.14    3.00       exogenous   0.929           -2.680         -0.267
  ex-US                                                entry rate                                 
                                                       ($I_{0}$)                                  

  Anglosphere     2.00             10.61    3.00       exogenous   0.906           -2.680         -0.267
  ex-US                                                entry rate                                 
                                                       ($I_{0}$)                                  

  Continental     0.50             99.45    7.00       exogenous   0.990           -2.681         -0.134
  Europe                                               entry rate                                 
                                                       ($I_{0}$)                                  

  Continental     0.75             66.30    7.00       exogenous   0.985           -2.681         -0.134
  Europe                                               entry rate                                 
                                                       ($I_{0}$)                                  

  Continental     1.00             49.72    7.00       exogenous   0.980           -2.681         -0.134
  Europe                                               entry rate                                 
                                                       ($I_{0}$)                                  

  Continental     1.25             39.78    7.00       exogenous   0.975           -2.681         -0.134
  Europe                                               entry rate                                 
                                                       ($I_{0}$)                                  

  Continental     1.50             33.15    7.00       exogenous   0.970           -2.681         -0.134
  Europe                                               entry rate                                 
                                                       ($I_{0}$)                                  

  Continental     2.00             24.86    7.00       exogenous   0.960           -2.681         -0.134
  Europe                                               entry rate                                 
                                                       ($I_{0}$)                                  

  South Asia      0.50             47.52    4.00       exogenous   0.979           -2.535         -0.123
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  South Asia      0.75             31.68    4.00       exogenous   0.968           -2.535         -0.123
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  South Asia      1.00             23.76    4.00       exogenous   0.958           -2.535         -0.123
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  South Asia      1.25             19.01    4.00       exogenous   0.947           -2.535         -0.123
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  South Asia      1.50             15.84    4.00       exogenous   0.937           -2.535         -0.123
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  South Asia      2.00             11.88    4.00       exogenous   0.916           -2.535         -0.123
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Islamic world   0.50             78.52    6.00       exogenous   0.987           -2.579         -0.134
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Islamic world   0.75             52.35    6.00       exogenous   0.981           -2.579         -0.134
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Islamic world   1.00             39.26    6.00       exogenous   0.975           -2.579         -0.134
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Islamic world   1.25             31.41    6.00       exogenous   0.968           -2.579         -0.134
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Islamic world   1.50             26.17    6.00       exogenous   0.962           -2.579         -0.134
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Islamic world   2.00             19.63    6.00       exogenous   0.949           -2.579         -0.134
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Japan           0.50             32.72    2.00       exogenous   0.969           -2.274         -0.156
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Japan           0.75             21.82    2.00       exogenous   0.954           -2.274         -0.156
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Japan           1.00             16.36    2.00       exogenous   0.939           -2.274         -0.156
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Japan           1.25             13.09    2.00       exogenous   0.924           -2.274         -0.156
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Japan           1.50             10.91    2.00       exogenous   0.908           -2.274         -0.156
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Japan           2.00             8.18     2.00       exogenous   0.878           -2.274         -0.156
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other regions   0.50             57.38    5.00       exogenous   0.983           -2.790         -0.187
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other regions   0.75             38.25    5.00       exogenous   0.974           -2.790         -0.187
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other regions   1.00             28.69    5.00       exogenous   0.965           -2.790         -0.187
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other regions   1.25             22.95    5.00       exogenous   0.956           -2.790         -0.187
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other regions   1.50             19.13    5.00       exogenous   0.948           -2.790         -0.187
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other regions   2.00             14.34    5.00       exogenous   0.930           -2.790         -0.187
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other Western   0.50             6.03     1.00       exogenous   0.834           -2.744         -0.191
  (Israel)                                             entry rate                                 
                                                       ($I_{0}$)                                  

  Other Western   0.75             4.02     1.00       exogenous   0.751           -2.744         -0.191
  (Israel)                                             entry rate                                 
                                                       ($I_{0}$)                                  

  Other Western   1.00             3.01     1.00       exogenous   0.668           -2.744         -0.191
  (Israel)                                             entry rate                                 
                                                       ($I_{0}$)                                  

  Other Western   1.25             2.41     1.00       dropout     0.533           -2.744         -0.191
  (Israel)                                             rate ($d$)                                 

  Other Western   1.50             2.01     1.00       dropout     0.374           -2.744         -0.191
  (Israel)                                             rate ($d$)                                 

  Other Western   2.00             1.51     1.00       dropout     0.184           -2.744         -0.191
  (Israel)                                             rate ($d$)                                 

  China-centred   0.50             194.24   9.00       exogenous   0.995           -2.685         -0.063
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  China-centred   0.75             129.50   9.00       exogenous   0.992           -2.685         -0.063
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  China-centred   1.00             97.12    9.00       exogenous   0.990           -2.685         -0.063
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  China-centred   1.25             77.70    9.00       exogenous   0.987           -2.685         -0.063
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  China-centred   1.50             64.75    9.00       exogenous   0.985           -2.685         -0.063
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  China-centred   2.00             48.56    9.00       exogenous   0.979           -2.685         -0.063
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  United States   0.50             159.50   8.00       exogenous   0.994           -2.665         -0.227
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  United States   0.75             106.34   8.00       exogenous   0.991           -2.665         -0.227
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  United States   1.00             79.75    8.00       exogenous   0.987           -2.665         -0.227
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  United States   1.25             63.80    8.00       exogenous   0.984           -2.665         -0.227
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  United States   1.50             53.17    8.00       exogenous   0.981           -2.665         -0.227
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  United States   2.00             39.88    8.00       exogenous   0.975           -2.665         -0.227
                                                       entry rate                                 
                                                       ($I_{0}$)                                  
  --------------------------------------------------------------------------------------------------------------

*Supplementary Table S12. Region-level results underlying Supplementary
Table S11.*
