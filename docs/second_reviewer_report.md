# Research Policy 査読者視点 第2回レビュー報告書

**対象原稿**: `docs/manuscript_full_article.docx`（および同梱 `.md`, `_blinded.docx`, `supplementary_material.docx`）  
**対象ジャーナル**: *Research Policy*（Elsevier）  
**確認リビジョン**: `bougtoir/wip` `devin/researcher-mobility-ode-full-article` @ `4a0332eb`（PR #353 マージ後）  
**レビュー日**: 2026-08-09  
**レビュー視点**: 第1回レビュー（`docs/reviewer_report_research_policy.md`）の対応後を想定し、再び査読者・編集者目線で投稿適合度を評価。

---

## 1. 総合判定

本稿は *Research Policy* のスコープ（innovation / science & technology policy / management of research）に合致するテーマを扱っており、方法論の独自性（OpenAlex 個体データ → 6コンパートメント ODE → PNR 早期警報）も明確です。データ・コードの再現性も `reproduce.sh` と公開リポ `bougtoir/researcher-mobility-ode` で担保されています。

ただし、**投稿前に必ず直すべき事項が 4 点**残っています。

1. **形式要件違反**: Abstract が 250 語を超過、3 番目の Highlight が 85 文字を超過。
2. **データ・主張の不一致**: endogenous inflow の「safety factor」表現が実装（0.50× キャップ）と乖離。
3. **方法論的未解決**: `domestic_PIs` ターゲットの PNR 計算に active-pool 閾値 `M = k × c_bar` が使われている。
4. **提出用情報の未記入**: Funding / Competing interests / Author contributions / Corresponding author が placeholder のまま。

これらを修正すれば、*Research Policy* のダブルブラインド査読にスムーズに入ります。以下、5 領域に分けて詳述します。

---

## 2. 5 領域評価

### 2.1 原稿：新規性・焦点・論理構成

| 判定 | 項目 | 所見 | 修正案 | 優先度 |
|---|---|---|---|---|
| 強み | テーマの適合 | AI/ML 研究者モビリティを「文明圏レベルの最低維持プール」で議論する点は、RP の innovation policy / STI policy 読者に訴求する。 | 現状維持。 | – |
| 強み | 論理の一貫性 | Introduction → Literature → Methods → Results → Discussion の流れは自然。 | 現状維持。 | – |
| 要修正 | Innovation studies 文脈の強化 | 2.2 節で Nelson & Winter [13]、Dosi [14]、Lundvall [15]、Malerba [16] を一括引用しているが、本文でそれぞれの概念（進化的ダイナミクス、ナショナル・イノベーション・システム、セクタール・システム）を具体例と結びつけていない。査読者は「なぜ突然この 4 文献が並ぶのか」と疑問に思う。 | 2.2 末尾に 1–2 文追加：「本稿の遷移率・PNR は、これらのマクロ的イノベーション・システム研究を個人キャリアデータと接続する試みである」と明確化。 | 高 |
| 要修正 | PNR の概念的位置づけ | PNR は生態学の minimum viable population [10] を転用した heuristic であることをもう一度強調。査読者は「deterministic に T = M を下回ると回復不能と決めつける根拠は？」と突っ込む。 | 4.3 / Discussion 6.6 で「PNR 閾値下回りは回復困難の十分条件であって必要条件ではなく、外的ショックがあれば閾値上でも崩壊しうる」と改めて明記。 | 高 |
| 要検討 | タイトルの SHIGA | Discussion 6.6 で SHIGA 頭字語を滋賀大学の研究基盤に結びつけている。国際誌では気づかれにくいが、匿名査読では不要な情報と映りかねない。 | フルバージョンでは OK。ダブルブラインド版では「a Japanese national university」に置換済みか確認。 | 中 |

### 2.2 統計設計・解析

| 判定 | 項目 | 所見 | 修正案 | 優先度 |
|---|---|---|---|---|
| 要修正 | **endogenous inflow safety factor の表現** | `src/ode_model_endogenous.py:197` では `r` は `safety_factor=0.5` で `r_critical` をキャップ。ところが `build_full_manuscript.py:876` は `(eq["r"] / eq["r_critical"]).min()` を `safety_factor` として取得し、4.2 節で「r is capped at 0.40× the stability-critical value」と記述。実際には日本が 0.397、他は 0.50 となる（`equilibrium_summary.csv` の `r`/`r_critical` 列を確認）。 | 4.2 節を修正：「r is capped at 0.50× r_critical; the most constrained group shows a realised ratio of 0.40×」または `compute_context()` を `r_cap` と `min_realised_ratio` に分離して記述を正確化。 | **最優先** |
| 要修正 | **PI-pool PNR の閾値** | `src/ode_model_endogenous.py:563` で `point_of_no_return(params, I0, M_threshold, rate_name, target=target)` を `target="P"`（domestic_PIs）でも `M_threshold = k × c_bar`（active-pool 閾値）を使っている。`M` は `D + H_D + P_D` 合計の閾値であり、`P_D` 単独の存続閾値ではない。 | PI-pool PNR を提示する場合は `M_PI = k`（= 年間観測された distinct last-author グループ数の中央値）を閾値として使用。提示しないなら `target="P"` の PNR 出力を抑制し、論文中では active-pool PNR のみを議論。 | **最優先** |
| 確認済 | コホート定義 | `src/cohort_extraction.py` の `MIN_WORKS=2`、`hit` は top-10% citation かつ著者位置不問、PI は last-author（単著含む）と本文記載一致。 | 現状維持。 | – |
| 確認済 | 反実仮想の mechanical 性 | 5.3 / 6.3 節で政策レバーは「遷移率を 10% 擾動させた機械的反実仮想」であり、因果効果ではないと説明。 | 現状維持。ただし政策レバーと具体政策の対応表（Table 11）をさらに充実させるとよい。 | 中 |
| 要検討 | MAPE 130.4% の扱い | Abstract でも「conservative, non-standard MAPE 130.4% (count_obs + 1)」と自覚的に提示。Supplementary Table 1/2 でグループ別・コンパートメント別の予測精度を開示。 | そのままでも許容範囲だが、もし査読者が「なぜ投影層が必要か」と問う場合、方向一致率（上昇/横ばい/下降）や閾値超過警報精度を追加。 | 中 |

### 2.3 図表

| 判定 | 項目 | 所見 | 修正案 | 優先度 |
|---|---|---|---|---|
| 確認済 | 図表引用 | Figure 1–9、Table 1–11 が本文で引用済み。orphan / phantom なし。 | 現状維持。 | – |
| 要修正 | Highlights 文字数 | 3 番目のハイライトが 101 文字（`Dropout reduction gives the largest margin gain per 10% change across all groups in the fitted model.`）。RP・Elsevier 系 Highlights は「各 85 文字以下」が標準。 | 例：「Dropout reduction yields the largest margin gain across all groups.」（62 文字）に短縮。 | **最優先** |
| 要検討 | 図表の多さ | 本文に Figure 9 + Table 11 の計 20 点。RP に明確上限はないが、査読者が情報過多と感じる可能性。 | Table 9（年次平均率）、Table 10（上位 OD ペア）、Figure 4（Bootstrap CI 棒グラフ）を Supplementary へ移すことを検討。 | 中 |
| 要修正 | Figure 3 左右反転 | ユーザ指摘で左原点に修正済み。 | 現状維持。 | – |
| 要修正 | 日本特化図の重複掲載 | ユーザ指摘で Figure 8 の再掲を削除済み。 | 現状維持。 | – |

### 2.4 再現性・Data/Code Availability

| 判定 | 項目 | 所見 | 修正案 | 優先度 |
|---|---|---|---|---|
| 強み | 再現パイプライン | `reproduce.sh` で `results/` → 図表 → 原稿まで再生成。公開リポ `bougtoir/researcher-mobility-ode` でも `bash reproduce.sh` で完走を確認。 | 現状維持。 | – |
| 強み | 数値の自動挿入 | `scripts/build_full_manuscript.py` が `results/endogenous/equilibrium_summary.csv`、`point_of_no_return.csv`、`policy_counterfactuals/ranked_interventions.csv`、`annual/projection_evaluation.csv` 等を読み込み、原稿数値を動的生成。ハードコードなし。 | 現状維持。 | – |
| 確認済 | 主要数値のトレーサビリティ | 以下の主張が results CSV と一致：<br>・コホート `n=723,647`（`data/cohort/cohort.csv`）<br>・最も近い active-pool PNR は Other Western, `I0` 0.332×（`results/endogenous/point_of_no_return.csv`）<br>・MAPE 130.4%（`results/annual/projection_evaluation.csv`）<br>・最大マージンゲインは `d`（`results/endogenous/top_transitions_T.csv`） | 現状維持。 | – |
| 要記載 | OpenAlex スナップショット日 | `Data and Code Availability` に「full-work local snapshot in August 2026」とあるが、具体的な取得日・ファイル名がない。 | `README.md` または `data/cohort/README.md` にスナップショット取得日（例：2026-08-09）と `data/` 内ファイル名を明記。 | 低 |

### 2.5 主張の強さ

| 判定 | 項目 | 所見 | 修正案 | 優先度 |
|---|---|---|---|---|
| 要修正 | 因果表現の抑制 | Abstract/Introduction では「policy scenarios that preserve civilisational diversity」とやや強めの言い回し。実際には機械的反実仮想。 | 6.3 節冒頭に 1 文追加：「本稿の数値は政策の因果効果ではなく、有限データ内で優先的に監視すべきレバーを特定する指標である。」 | 高 |
| 要修正 | 日本文明圏の一般化 | 5.9 / 6.5 節が日本に大きく割かれている。RP はグローバル読者向け。 | 「日本は最小文明圏の一つの illustrative case である」と冒頭で明示し、他文明圏への一般化可能性を一言述べる。 | 中 |
| 要検討 | 文明圏ラベル | 「Hindu」等の Huntington ラベルが否定的に受け取られる可能性。ユーザーと「名称変更の議論」が未決。 | Introduction の脚注で「文化・制度的共変量の操作化であり、規範的判断ではない」と明記。将来の名称変更は別途検討。 | 中 |
| 確認済 | 数理モデルの限界 | 4.5 / 6.6 節で定常状態の heuristic 性、右打ち切り、cross-civilisation spillover 無視等を開示。 | 現状維持。 | – |

---

## 3. 優先度別アクションマトリックス

### A. 投稿前に必ず対応（desk-reject / major revision リスク）

| # | 項目 | 修正箇所 | 修正内容 | 実装工数 |
|---|---|---|---|---|
| A1 | Abstract 250 語以内 | `build_full_manuscript.py:1076` 付近 | 現在 267 語（docx）/ 280 語（md）を 1–2 文削り 250 語以内に。特に「equivalent to a 67% proportional reduction」等を 1 語に縮約。 | 小 |
| A2 | Highlights 85 文字以内 | `build_full_manuscript.py:1093` 付近 | 3 番目の bullet を 85 文字以下に短縮。PNR 略語も定義済みなので可。 | 小 |
| A3 | safety factor 表現の訂正 | `build_full_manuscript.py:1519` 付近 `ctx['safety_factor']` | 「capped at 0.50× r_critical; the Japanese group has the lowest realised ratio 0.40×」と正確化。`compute_context()` を `r_cap=0.50` と `min_realised_safety_ratio` に分離。 | 中 |
| A4 | PI-pool PNR 閾値の修正 | `src/ode_model_endogenous.py:548–563` | `target="P"` の場合、`M_threshold` を `k`（PI グループ数）にするか、PI-pool PNR 計算を停止して active-pool PNR のみ使用。 | 中 |
| A5 | 提出用情報の完成 | `build_full_manuscript.py` タイトルページ / Declarations | Funding, Competing interests, Author contributions, Corresponding author を placeholder から実値へ。blinded 版でも「[Removed for peer review]」ではなく「[To be completed at submission]」を避ける。 | 小（ユーザー入力必要） |

### B. 高優先（採択可能性を大きく高める）

| # | 項目 | 修正箇所 | 修正内容 |
|---|---|---|---|
| B1 | Innovation studies 文脈の接続 | `docs/manuscript_full_article.docx` 2.2 節 | Nelson & Winter / Dosi / Lundvall / Malerba を「セクタール・イノベーション・システム / 進化的経済学」の文脈で引用し、本稿の「遷移率・PNR」と結びつける一文を追加。 |
| B2 | 政策含意の独立性強化 | 6.3 節 | 「Policy implications」小節を独立させ、各レバー（`d`, `I0`, `h_D`, `p_D`）に対応する政策主体（研究助成機関、大学、R&D マネージャー）を Table 11 より明確に記述。 |
| B3 | 因果表現のさらなる抑制 | 6.3 節冒頭 | 「本数値は因果効果ではなく、監視・優先順位付け指標である」を追加。 |

### C. 中優先

| # | 項目 | 修正箇所 | 修正内容 |
|---|---|---|---|
| C1 | 一部図表を Supplementary へ | `build_full_manuscript.py` | Table 9 / Table 10 / Figure 4 / Figure 6 を Supplementary Material に移し、本文は要約のみにする。 |
| C2 | MAPE 解釈補強 | 5.7 節 / Supplementary | 方向一致率や閾値超過警報精度を追加し、early-warning としての有用性を補強。 |
| C3 | 日本特化議論の一般化 | 5.9 / 6.5 節 | 「illustrative application to the Japanese case」と位置づけ、他文明圏への一般化可能性を付記。 |
| C4 | 文明圏ラベルの定義脚注 | Introduction / Table 1 | 「Hindu」「Sinic」等の操作的位置づけを脚注で補強。 |

### D. 任意（提出直前）

| # | 項目 | 備考 |
|---|---|---|
| D1 | 図表ファイルの分離 | Elsevier 最終提出時は個別 PNG/TIFF/EPS が必要。`docs/figures/*.png` および `manuscript_full_article_figures.pptx` を用意済み。 |
| D2 | 未使用コードの整理 | `src/cohort_extraction.py` の `failed_batches` 分岐は現状到達しない可能性。ただし動作に影響なし。 |
| D3 | OpenAlex snapshot 取得日の明記 | `data/cohort/README.md` への 1 行追加。 |

---

## 4. 査読者が投げそうな質問と先回り回答

1. **「なぜ Huntington の文明圏を使うのか？」**  
   → Introduction と Table 1 脚注で「地理・制度的共変量の操作化であり、現在の政治国境・価値観と一致しない限界も 6.6 節で議論」と説明済み。

2. **「PNR は本当に point of no return か？」**  
   → 4.3 / 6.6 節で「閾値下回りは回復困難の十分条件であって必要条件ではない」「外的ショックがあれば閾値上でも崩壊しうる」と説明。

3. **「PI-pool PNR の閾値は active-pool と同じなのか？」**  
   → 現状は同じ `M = k × c_bar` を使っているため、修正が必要。修正後は `M_PI = k` として再計算し、結果を開示。

4. **「MAPE 130% では予測として成立しないのでは？」**  
   → 5.7 節 / Abstract で「directional drift and threshold crossing の early-warning 指標」として位置づけ。Supplementary ではグループ別・コンパートメント別精度を開示。

5. **「政策介入の因果効果を示していないのでは？」**  
   → 5.3 / 6.3 節で「mechanical perturbation, not causal estimate」と明記。Table 11 で政策レバー対応を示す。

---

## 5. 最終推奨

**現時点で *Research Policy* へ投稿可能か？** → **条件付きで可能**。ただし A1–A5 を先に修正すること。

1. **A1–A2**（Abstract/Highlights 形式要件）は最優先。ジャーナル投稿システムで文字超過で即 desk-reject される可能性がある。
2. **A3–A4**（safety factor / PI-pool PNR）は査読者が「方法が正確か」と問う核心。データ・主張の整合性を保つために修正。
3. **A5**（Funding/COI/Author contributions/Corresponding author）は編集者が投稿前に要求するため、提出直前までに必ず完了。
4. **B1–B3** を追加すれば、innovation studies 文脈での採択可能性が大きく上がる。

上記 A/B/C を実装し、`reproduce.sh` で再生成 → 公開リポ同期後、再び査読者目線レビューを行うことを推奨します。

---

## 付録：主要数値の results CSV 対応チェック

| 原稿記述 | 出典 CSV / スクリプト | 確認結果 |
|---|---|---|
| `n = 723,647` コホート | `data/cohort/cohort.csv` | 一致 |
| 9 文明圏 | `results/endogenous/equilibrium_summary.csv` | 一致（`group` 列 9 行） |
| 最も近い active-pool PNR: Other Western `I0` 0.332× | `results/endogenous/point_of_no_return.csv` | 一致 |
| 最大マージンゲイン：dropout `d` | `results/endogenous/top_transitions_T.csv` | 一致（`d` の `abs_elasticity` が最大） |
| MAPE 130.4% | `results/annual/projection_evaluation.csv` | 一致（`ev["ape"].mean()*100` = 130.4） |
| `safety_factor = 0.40` | `src/ode_model_endogenous.py` + `build_full_manuscript.py:876` | 不整合：コードの cap は 0.50、最小実現比は 0.397 |
| `domestic_PIs` PNR | `src/ode_model_endogenous.py:563` | 閾値 `M` が active-pool のまま |
