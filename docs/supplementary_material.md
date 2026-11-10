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
compartment counts. Rate-level projections have RMSE 0.0876 and a skill
ratio (baseline RMSE / model RMSE) of 0.77 against a historical-mean
baseline, so they do not improve on simply carrying the historical mean
forward; stock-level errors are larger (RMSE 29). Year-to-year direction
agreement is 44.8%.

![](media/image1.png){width="6.0in" height="5.1962259405074365in"}

*Supplementary Figure S1. Observed (solid) and projected (dashed)
transition rates by research macro-region, 2000-2026.*

![](media/image2.png){width="5.8in" height="4.790865048118985in"}

*Supplementary Figure S2. Cross-region abroad author-year accumulation
by origin (rows) and destination (columns); same-region cells and
Unknown destinations excluded (lower-bound proxy).*

![](media/image3.png){width="6.0in" height="3.827672790901137in"}

*Supplementary Figure S3. Observed (solid) and projected (dashed)
compartment counts by research macro-region, 2017-2023. The dotted line
marks the end of the training period (2016).*

# Supplementary Table S2. Projection accuracy by research macro-region, 2017-2023

  ---------------------------------------------------------------------------------------------------------------------------------------------
  **Group**       **RMSE**   **MAPE**   **Direction   **Alarm      **Alarm         **Alarm         **Alarm       **Alarm years  **Alarm years
                                        agreement**   Accuracy**   Sensitivity**   Specificity**   Precision**   (observed)**   (projected)**
  --------------- ---------- ---------- ------------- ------------ --------------- --------------- ------------- -------------- ---------------
  Anglosphere     14.97      159.5%     52.8%         100.0%       ---             100.0%          ---           0.00           0.00
  ex-US                                                                                                                         

  Continental     18.73      137.6%     33.3%         100.0%       ---             100.0%          ---           0.00           0.00
  Europe                                                                                                                        

  South Asia      52.11      201.3%     47.2%         100.0%       ---             100.0%          ---           0.00           0.00

  Islamic world   42.66      233.7%     25.0%         100.0%       ---             100.0%          ---           0.00           0.00

  Japan           8.16       74.8%      63.9%         100.0%       ---             100.0%          ---           0.00           0.00

  Other regions   27.84      154.9%     47.2%         100.0%       ---             100.0%          ---           0.00           0.00

  Other Western   11.57      201.9%     41.7%         100.0%       ---             100.0%          ---           0.00           0.00
  (Israel)                                                                                                                      

  China-centred   29.28      104.1%     41.7%         100.0%       ---             100.0%          ---           0.00           0.00

  United States   25.26      133.7%     50.0%         100.0%       ---             100.0%          ---           0.00           0.00
  ---------------------------------------------------------------------------------------------------------------------------------------------

*Supplementary Table S2. Projection accuracy by research macro-region,
2017-2023.*

# Supplementary Table S3. Projection accuracy by compartment, 2017-2023

  -----------------------------------------------------------------------
  **Compartment**   **RMSE**          **MAPE**          **Direction
                                                        agreement**
  ----------------- ----------------- ----------------- -----------------
  A                 4.45              256.1%            70.4%

  $D$               56.60             442.3%            7.4%

  $H_{A}$           2.09              45.7%             68.5%

  $H_{D}$           24.68             143.7%            24.1%

  $P_{A}$           12.21             30.6%             50.0%

  $P_{D}$           32.68             16.0%             48.1%
  -----------------------------------------------------------------------

*Supplementary Table S3. Projection accuracy by compartment, 2017-2023.*

# Supplementary Table S4. Mean observed annual transition rates by research macro-region, 2000-2016

  ------------------------------------------------------------------------------------
  **Group**       $\alpha$   $\beta$    $h_{D}$    $p_{D}$    $d$        $I_{total}$
  --------------- ---------- ---------- ---------- ---------- ---------- -------------
  Anglosphere     0.063      0.110      0.136      0.171      0.018      13.65
  ex-US                                                                  

  China-centred   0.028      0.101      0.078      0.139      0.010      25.65

  Continental     0.043      0.088      0.105      0.195      0.010      24.65
  Europe                                                                 

  Islamic world   0.060      0.165      0.088      0.176      0.009      14.47

  Japan           0.041      0.174      0.094      0.166      0.021      12.06

  Other Western   0.063      0.099      0.134      0.109      0.015      9.82
  (Israel)                                                               

  Other regions   0.047      0.159      0.087      0.149      0.019      13.71

  South Asia      0.063      0.190      0.086      0.194      0.007      12.12

  United States   0.042      0.082      0.136      0.160      0.012      23.29
  ------------------------------------------------------------------------------------

*Supplementary Table S4. Mean observed annual transition rates by
research macro-region, 2000-2016.*

# Supplementary Table S5. Top cross-region origin-destination abroad author-year pairs

  -----------------------------------------------------------------------
  **Origin**              **Destination**         **Author-years**
  ----------------------- ----------------------- -----------------------
  United States           China-centred           326

  Continental Europe      United States           221

  United States           Anglosphere ex-US       176

  Anglosphere ex-US       Continental Europe      170

  Continental Europe      Anglosphere ex-US       167

  China-centred           United States           159

  China-centred           Anglosphere ex-US       157

  Anglosphere ex-US       China-centred           152

  Japan                   China-centred           152

  United States           Other Western (Israel)  146
  -----------------------------------------------------------------------

*Supplementary Table S5. Top cross-region origin-destination abroad
author-year pairs.*

# Supplementary Table S6. Bootstrap 95% confidence intervals for equilibrium $T$ and domestic PI pool $P_{D}$

  ---------------------------------------------------------------------------
  **Group**       $T$ **median** $T$ **95% CI** $P_{D}$        $P_{D}$ **95%
                                                **mean**       CI**
  --------------- -------------- -------------- -------------- --------------
  Anglosphere     57460          \[56692,       25801          \[25154,
  ex-US                          58061\]                       26345\]

  Continental     172433         \[171191,      75531          \[74446,
  Europe                         173627\]                      76593\]

  South Asia      50534          \[49394,       28261          \[27346,
                                 51488\]                       29182\]

  Islamic world   73447          \[72351,       36927          \[35927,
                                 74502\]                       37819\]

  Japan           26382          \[25978,       6420           \[6161, 6728\]
                                 26816\]                       

  Other regions   56514          \[55876,       19287          \[18809,
                                 57346\]                       19861\]

  Other Western   4238           \[4003, 4460\] 1865           \[1681, 2054\]
  (Israel)                                                     

  China-centred   279924         \[278113,      128708         \[127109,
                                 282145\]                      130687\]

  United States   120403         \[119426,      52998          \[52252,
                                 121245\]                      53680\]
  ---------------------------------------------------------------------------

*Supplementary Table S6. Bootstrap 95% confidence intervals for
equilibrium* $T$ *and domestic PI pool* $P_{D}$*.*

# Supplementary Table S7. Closest model-implied viability boundary under linear versus saturating inflow

  ------------------------------------------------------------------------------------------------
  **Group**       **Linear   **Linear   **Linear      **Saturating   **Saturating   **Saturating
                  lever**    factor**   proximity**   lever**        factor**       proximity**
  --------------- ---------- ---------- ------------- -------------- -------------- --------------
  United States   $I_{0}$    0.004      0.996         $I_{0}$        0.003          0.997

  Anglosphere     $I_{0}$    0.005      0.995         $I_{0}$        0.004          0.996
  ex-US                                                                             

  Continental     $I_{0}$    0.003      0.997         $I_{0}$        0.003          0.997
  Europe                                                                            

  China-centred   $I_{0}$    0.003      0.998         $I_{0}$        0.002          0.998

  Japan           $I_{0}$    0.003      0.997         $I_{0}$        0.003          0.997

  South Asia      $I_{0}$    0.003      0.997         $I_{0}$        0.003          0.997

  Islamic world   $I_{0}$    0.004      0.996         $I_{0}$        0.003          0.997

  Other Western   $I_{0}$    0.004      0.996         $I_{0}$        0.004          0.996
  (Israel)                                                                          

  Other regions   $I_{0}$    0.003      0.997         $I_{0}$        0.003          0.997
  ------------------------------------------------------------------------------------------------

*Supplementary Table S7. Closest viability-boundary lever, critical
factor and proximity for the active pool under linear and saturating
PI-driven inflow.*

# Supplementary Table S8. Talent-concentration scenario: inputs and their status

  --------------------------------------------------------------------------------------------
  **Parameter**           **Value**                                    **Status**
  ----------------------- -------------------------------------------- -----------------------
  phi_grid                0.0,0.5,1.0,2.0,4.0,8.0                      stylised

  gamma_grid              0.0,1.0,2.0                                  stylised

  horizon_years           100.00                                       stylised

  tau_years               23.71                                        fitted (1 / mean $d$)

  horizon_in_tau          4.22                                         derived

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
(Section 2.10). \'Fitted\' inputs come from the estimated model and
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
623,176 authors against 623,176 in the published cohort; the difference
reflects OpenAlex updates between extractions, so definitions are
compared with each other on the same snapshot (Supplementary Table S10)
and the baseline definition is also compared with the published results.
For each definition the transition rates were re-estimated, the
endogenous-inflow equilibrium, the elasticities and the closest
model-implied viability boundary were recomputed with the same $M$, and
the nine-region rankings were compared by Spearman rank correlation. Two
quantities are invariant to the proxy by construction and are reported
only for completeness: because $I_{0}$ is calibrated so that total
equilibrium entry equals observed entry (Section 2.8), the equilibrium
active pool $T$ (hence $T/M$) and the proximity of the entry lever
$I_{0}$ do not depend on how PIs are identified. The proxy does change
the promotion rates $p_{D}$ and $p_{A}$, the equilibrium PI pool
$P_{D}$, the exogenous/PI-driven split of entry ($I_{0}$, $r$), the
elasticity of $T$ to $p_{D}$ and the model-implied viability boundary of
the PI pool relative to its own threshold $k$. Supplementary Table S9
reports the region-level results and Supplementary Table S10 the rank
agreement on these proxy-dependent quantities.

  ------------------------------------------------------------------------------------------------------------------------------------------------------------
  **PI proxy**           **Group**       **Share   $p_{D}$   $T/M$    **Closest     **Proximity   $P_{D}$   **Closest lever   **Proximity       **Elasticity
                                         of                           lever         (**$T$**)**             (**$P_{D}$**)**   (**$P_{D}$**)**   of** $T$
                                         authors                      (**$T$**)**                                                               **to** $p_{D}$
                                         who are                                                                                                
                                         PIs**                                                                                                  
  ---------------------- --------------- --------- --------- -------- ------------- ------------- --------- ----------------- ----------------- --------------
  First last-author      Anglosphere     0.675     0.075     215.76   exogenous     0.995         25809     exogenous entry   0.997             0.347
  paper (baseline)       ex-US                                        entry rate                            rate ($I_{0}$)                      
                                                                      ($I_{0}$)                                                                 

  First last-author      Continental     0.684     0.077     330.60   exogenous     0.997         75612     exogenous entry   0.998             0.357
  paper (baseline)       Europe                                       entry rate                            rate ($I_{0}$)                      
                                                                      ($I_{0}$)                                                                 

  First last-author      South Asia      0.755     0.094     311.91   exogenous     0.997         28219     exogenous entry   0.998             0.213
  paper (baseline)                                                    entry rate                            rate ($I_{0}$)                      
                                                                      ($I_{0}$)                                                                 

  First last-author      Islamic world   0.744     0.091     250.94   exogenous     0.996         36876     exogenous entry   0.997             0.240
  paper (baseline)                                                    entry rate                            rate ($I_{0}$)                      
                                                                      ($I_{0}$)                                                                 

  First last-author      Japan           0.614     0.063     292.95   exogenous     0.997         6428      exogenous entry   0.996             0.301
  paper (baseline)                                                    entry rate                            rate ($I_{0}$)                      
                                                                      ($I_{0}$)                                                                 

  First last-author      Other regions   0.696     0.079     291.60   exogenous     0.997         19285     exogenous entry   0.997             0.324
  paper (baseline)                                                    entry rate                            rate ($I_{0}$)                      
                                                                      ($I_{0}$)                                                                 

  First last-author      Other Western   0.579     0.058     238.05   exogenous     0.996         1868      exogenous entry   0.997             0.368
  paper (baseline)       (Israel)                                     entry rate                            rate ($I_{0}$)                      
                                                                      ($I_{0}$)                                                                 

  First last-author      China-centred   0.716     0.084     404.87   exogenous     0.998         128635    exogenous entry   0.998             0.253
  paper (baseline)                                                    entry rate                            rate ($I_{0}$)                      
                                                                      ($I_{0}$)                                                                 

  First last-author      United States   0.658     0.072     263.11   exogenous     0.996         52999     exogenous entry   0.997             0.374
  paper (baseline)                                                    entry rate                            rate ($I_{0}$)                      
                                                                      ($I_{0}$)                                                                 

  First                  Anglosphere     0.523     0.049     215.76   exogenous     0.995         21796     exogenous entry   0.996             0.439
  corresponding-author   ex-US                                        entry rate                            rate ($I_{0}$)                      
  paper                                                               ($I_{0}$)                                                                 

  First                  Continental     0.563     0.055     330.60   exogenous     0.997         66208     exogenous entry   0.997             0.432
  corresponding-author   Europe                                       entry rate                            rate ($I_{0}$)                      
  paper                                                               ($I_{0}$)                                                                 

  First                  South Asia      0.572     0.057     311.91   exogenous     0.997         24706     exogenous entry   0.998             0.306
  corresponding-author                                                entry rate                            rate ($I_{0}$)                      
  paper                                                               ($I_{0}$)                                                                 

  First                  Islamic world   0.549     0.053     250.94   exogenous     0.996         31481     exogenous entry   0.997             0.342
  corresponding-author                                                entry rate                            rate ($I_{0}$)                      
  paper                                                               ($I_{0}$)                                                                 

  First                  Japan           0.456     0.041     292.95   exogenous     0.997         5138      exogenous entry   0.995             0.543
  corresponding-author                                                entry rate                            rate ($I_{0}$)                      
  paper                                                               ($I_{0}$)                                                                 

  First                  Other regions   0.528     0.050     291.60   exogenous     0.997         16202     exogenous entry   0.996             0.421
  corresponding-author                                                entry rate                            rate ($I_{0}$)                      
  paper                                                               ($I_{0}$)                                                                 

  First                  Other Western   0.472     0.043     238.05   exogenous     0.996         1638      exogenous entry   0.996             0.433
  corresponding-author   (Israel)                                     entry rate                            rate ($I_{0}$)                      
  paper                                                               ($I_{0}$)                                                                 

  First                  China-centred   0.564     0.055     404.87   exogenous     0.998         113336    exogenous entry   0.998             0.336
  corresponding-author                                                entry rate                            rate ($I_{0}$)                      
  paper                                                               ($I_{0}$)                                                                 

  First                  United States   0.457     0.041     263.11   exogenous     0.996         41141     exogenous entry   0.996             0.505
  corresponding-author                                                entry rate                            rate ($I_{0}$)                      
  paper                                                               ($I_{0}$)                                                                 

  Second last-author     Anglosphere     0.495     0.046     215.76   exogenous     0.995         20970     exogenous entry   0.996             0.458
  paper (recurrent last  ex-US                                        entry rate                            rate ($I_{0}$)                      
  author)                                                             ($I_{0}$)                                                                 

  Second last-author     Continental     0.511     0.048     330.60   exogenous     0.997         61862     exogenous entry   0.997             0.468
  paper (recurrent last  Europe                                       entry rate                            rate ($I_{0}$)                      
  author)                                                             ($I_{0}$)                                                                 

  Second last-author     South Asia      0.580     0.058     311.91   exogenous     0.997         24799     exogenous entry   0.998             0.305
  paper (recurrent last                                               entry rate                            rate ($I_{0}$)                      
  author)                                                             ($I_{0}$)                                                                 

  Second last-author     Islamic world   0.547     0.053     250.94   exogenous     0.996         31196     exogenous entry   0.997             0.350
  paper (recurrent last                                               entry rate                            rate ($I_{0}$)                      
  author)                                                             ($I_{0}$)                                                                 

  Second last-author     Japan           0.468     0.042     292.95   exogenous     0.997         5216      exogenous entry   0.995             0.497
  paper (recurrent last                                               entry rate                            rate ($I_{0}$)                      
  author)                                                             ($I_{0}$)                                                                 

  Second last-author     Other regions   0.514     0.048     291.60   exogenous     0.997         15821     exogenous entry   0.996             0.436
  paper (recurrent last                                               entry rate                            rate ($I_{0}$)                      
  author)                                                             ($I_{0}$)                                                                 

  Second last-author     Other Western   0.431     0.038     238.05   exogenous     0.996         1548      exogenous entry   0.996             0.456
  paper (recurrent last  (Israel)                                     entry rate                            rate ($I_{0}$)                      
  author)                                                             ($I_{0}$)                                                                 

  Second last-author     China-centred   0.507     0.047     404.87   exogenous     0.998         106604    exogenous entry   0.998             0.374
  paper (recurrent last                                               entry rate                            rate ($I_{0}$)                      
  author)                                                             ($I_{0}$)                                                                 

  Second last-author     United States   0.472     0.043     263.11   exogenous     0.996         42079     exogenous entry   0.997             0.495
  paper (recurrent last                                               entry rate                            rate ($I_{0}$)                      
  author)                                                             ($I_{0}$)                                                                 
  ------------------------------------------------------------------------------------------------------------------------------------------------------------

*Supplementary Table S9. Equilibrium active pool,* $T/M$*, rank and
closest viability-boundary lever by research macro-region under three PI
proxy definitions (same OpenAlex snapshot;* $M$ *held at its baseline
value).*

  -----------------------------------------------------------------------------------------------------------------------------------------------------
  **PI proxy**           **Spearman rho  **Spearman rho **Spearman rho    **Spearman rho    **Spearman rho **Same        **Regions**   **Same
                         (**$T/M$**)**   (boundary      (**$p_{D}$**)**   (**$P_{D}$**)**   (boundary      closest lever               lowest-**$T/M$
                                         proximity,**                                       proximity,**   (regions)**                 **region**
                                         $T$**)**                                           $P_{D}$**)**                               
  ---------------------- --------------- -------------- ----------------- ----------------- -------------- ------------- ------------- ----------------
  First                  1.00            1.00           0.87              1.00              1.00           9.00          9.00          yes
  corresponding-author                                                                                                                 
  paper                                                                                                                                

  Second last-author     1.00            1.00           0.95              1.00              1.00           9.00          9.00          yes
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
macro-region, $T/M$, the rank by $T/M$, the closest viability-boundary
lever and its proximity, and the elasticities of $T$ to dropout ($d$)
and early-career outflow (alpha). Supplementary Table S11 summarises the
results. No macro-region falls below $M$ at any multiplier (minimum
$T/M$ 107.88 at the largest multiplier); the rankings by $T/M$ and by
proximity are unchanged (Spearman rho = 1.00 and 1.00 against the
baseline at every multiplier); and \|elasticity to $d$\| exceeds
\|elasticity to alpha\| in every macro-region at every multiplier. The
closest lever is unchanged everywhere.

  ---------------------------------------------------------------------------------------------------------------------------------------------
  $M$              **Regions   **Minimum**   **Lowest-**$T/M$   **Closest     **Spearman    **Spearman    **Closest     **Regions with**
  **multiplier**   below** $M$ $T/M$         **region**         region**      rho (**$T/M$  rho           lever         $|e_{d}|$ **\>
                                                                              **vs          (proximity vs unchanged     \|**$e_{alpha}$**\|**
                                                                              baseline)**   baseline)**   (regions)**   
  ---------------- ----------- ------------- ------------------ ------------- ------------- ------------- ------------- -----------------------
  0.50             0.00        431.52        Anglosphere ex-US  Anglosphere   1.00          1.00          9.00          9.00
                                                                ex-US                                                   

  0.75             0.00        287.68        Anglosphere ex-US  Anglosphere   1.00          1.00          9.00          9.00
                                                                ex-US                                                   

  1.00             0.00        215.76        Anglosphere ex-US  Anglosphere   1.00          1.00          9.00          9.00
                                                                ex-US                                                   

  1.25             0.00        172.61        Anglosphere ex-US  Anglosphere   1.00          1.00          9.00          9.00
                                                                ex-US                                                   

  1.50             0.00        143.84        Anglosphere ex-US  Anglosphere   1.00          1.00          9.00          9.00
                                                                ex-US                                                   

  2.00             0.00        107.88        Anglosphere ex-US  Anglosphere   1.00          1.00          9.00          9.00
                                                                ex-US                                                   
  ---------------------------------------------------------------------------------------------------------------------------------------------

*Supplementary Table S11. Sensitivity of the steady-state results to the
level of the minimum viable coauthor scale* $M$ *(multipliers applied to
every macro-region).*

  --------------------------------------------------------------------------------------------------------------
  **Group**       $M$              $T/M$    $T/M$      **Closest   **Proximity**   **Elasticity   **Elasticity
                  **multiplier**            **rank**   lever**                     (**$d$**)**    (alpha)**
  --------------- ---------------- -------- ---------- ----------- --------------- -------------- --------------
  Anglosphere     0.50             431.52   1.00       exogenous   0.998           -2.658         -0.235
  ex-US                                                entry rate                                 
                                                       ($I_{0}$)                                  

  Anglosphere     0.75             287.68   1.00       exogenous   0.997           -2.658         -0.235
  ex-US                                                entry rate                                 
                                                       ($I_{0}$)                                  

  Anglosphere     1.00             215.76   1.00       exogenous   0.995           -2.658         -0.235
  ex-US                                                entry rate                                 
                                                       ($I_{0}$)                                  

  Anglosphere     1.25             172.61   1.00       exogenous   0.994           -2.658         -0.235
  ex-US                                                entry rate                                 
                                                       ($I_{0}$)                                  

  Anglosphere     1.50             143.84   1.00       exogenous   0.993           -2.658         -0.235
  ex-US                                                entry rate                                 
                                                       ($I_{0}$)                                  

  Anglosphere     2.00             107.88   1.00       exogenous   0.991           -2.658         -0.235
  ex-US                                                entry rate                                 
                                                       ($I_{0}$)                                  

  Continental     0.50             661.21   8.00       exogenous   0.998           -2.647         -0.100
  Europe                                               entry rate                                 
                                                       ($I_{0}$)                                  

  Continental     0.75             440.80   8.00       exogenous   0.998           -2.647         -0.100
  Europe                                               entry rate                                 
                                                       ($I_{0}$)                                  

  Continental     1.00             330.60   8.00       exogenous   0.997           -2.647         -0.100
  Europe                                               entry rate                                 
                                                       ($I_{0}$)                                  

  Continental     1.25             264.48   8.00       exogenous   0.996           -2.647         -0.100
  Europe                                               entry rate                                 
                                                       ($I_{0}$)                                  

  Continental     1.50             220.40   8.00       exogenous   0.995           -2.647         -0.100
  Europe                                               entry rate                                 
                                                       ($I_{0}$)                                  

  Continental     2.00             165.30   8.00       exogenous   0.994           -2.647         -0.100
  Europe                                               entry rate                                 
                                                       ($I_{0}$)                                  

  South Asia      0.50             623.82   7.00       exogenous   0.998           -2.516         -0.113
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  South Asia      0.75             415.88   7.00       exogenous   0.998           -2.516         -0.113
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  South Asia      1.00             311.91   7.00       exogenous   0.997           -2.516         -0.113
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  South Asia      1.25             249.53   7.00       exogenous   0.996           -2.516         -0.113
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  South Asia      1.50             207.94   7.00       exogenous   0.995           -2.516         -0.113
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  South Asia      2.00             155.96   7.00       exogenous   0.994           -2.516         -0.113
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Islamic world   0.50             501.89   3.00       exogenous   0.998           -2.600         -0.137
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Islamic world   0.75             334.59   3.00       exogenous   0.997           -2.600         -0.137
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Islamic world   1.00             250.94   3.00       exogenous   0.996           -2.600         -0.137
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Islamic world   1.25             200.75   3.00       exogenous   0.995           -2.600         -0.137
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Islamic world   1.50             167.30   3.00       exogenous   0.994           -2.600         -0.137
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Islamic world   2.00             125.47   3.00       exogenous   0.992           -2.600         -0.137
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Japan           0.50             585.91   6.00       exogenous   0.998           -2.305         -0.117
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Japan           0.75             390.61   6.00       exogenous   0.997           -2.305         -0.117
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Japan           1.00             292.95   6.00       exogenous   0.997           -2.305         -0.117
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Japan           1.25             234.36   6.00       exogenous   0.996           -2.305         -0.117
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Japan           1.50             195.30   6.00       exogenous   0.995           -2.305         -0.117
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Japan           2.00             146.48   6.00       exogenous   0.993           -2.305         -0.117
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other regions   0.50             583.19   5.00       exogenous   0.998           -2.795         -0.094
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other regions   0.75             388.79   5.00       exogenous   0.997           -2.795         -0.094
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other regions   1.00             291.60   5.00       exogenous   0.997           -2.795         -0.094
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other regions   1.25             233.28   5.00       exogenous   0.996           -2.795         -0.094
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other regions   1.50             194.40   5.00       exogenous   0.995           -2.795         -0.094
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other regions   2.00             145.80   5.00       exogenous   0.993           -2.795         -0.094
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  Other Western   0.50             476.10   2.00       exogenous   0.998           -2.726         -0.133
  (Israel)                                             entry rate                                 
                                                       ($I_{0}$)                                  

  Other Western   0.75             317.40   2.00       exogenous   0.997           -2.726         -0.133
  (Israel)                                             entry rate                                 
                                                       ($I_{0}$)                                  

  Other Western   1.00             238.05   2.00       exogenous   0.996           -2.726         -0.133
  (Israel)                                             entry rate                                 
                                                       ($I_{0}$)                                  

  Other Western   1.25             190.44   2.00       exogenous   0.995           -2.726         -0.133
  (Israel)                                             entry rate                                 
                                                       ($I_{0}$)                                  

  Other Western   1.50             158.70   2.00       exogenous   0.994           -2.726         -0.133
  (Israel)                                             entry rate                                 
                                                       ($I_{0}$)                                  

  Other Western   2.00             119.02   2.00       exogenous   0.992           -2.726         -0.133
  (Israel)                                             entry rate                                 
                                                       ($I_{0}$)                                  

  China-centred   0.50             809.74   9.00       exogenous   0.999           -2.634         -0.041
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  China-centred   0.75             539.83   9.00       exogenous   0.998           -2.634         -0.041
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  China-centred   1.00             404.87   9.00       exogenous   0.998           -2.634         -0.041
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  China-centred   1.25             323.90   9.00       exogenous   0.997           -2.634         -0.041
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  China-centred   1.50             269.91   9.00       exogenous   0.996           -2.634         -0.041
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  China-centred   2.00             202.44   9.00       exogenous   0.995           -2.634         -0.041
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  United States   0.50             526.21   4.00       exogenous   0.998           -2.640         -0.146
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  United States   0.75             350.81   4.00       exogenous   0.997           -2.640         -0.146
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  United States   1.00             263.11   4.00       exogenous   0.996           -2.640         -0.146
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  United States   1.25             210.49   4.00       exogenous   0.995           -2.640         -0.146
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  United States   1.50             175.40   4.00       exogenous   0.994           -2.640         -0.146
                                                       entry rate                                 
                                                       ($I_{0}$)                                  

  United States   2.00             131.55   4.00       exogenous   0.992           -2.640         -0.146
                                                       entry rate                                 
                                                       ($I_{0}$)                                  
  --------------------------------------------------------------------------------------------------------------

*Supplementary Table S12. Region-level results underlying Supplementary
Table S11.*
