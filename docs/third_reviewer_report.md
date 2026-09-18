# Research Policy 査読者視点 第3回レビュー報告書

**対象原稿**: `docs/manuscript_full_article.docx`（および同梱 `.md`, `_blinded.docx`, `supplementary_material.docx`）  
**対象ジャーナル**: *Research Policy*（Elsevier）  
**確認リビジョン**: `bougtoir/wip` `devin/researcher-mobility-ode-full-article` @ `d1d1a807`  
**レビュー日**: 2026-08-09  
**レビュー視点**: 第2回レビュー（`docs/second_reviewer_report.md`）の全項目対応後を想定し、改めて査読者・編集者目線で投稿適合度を評価。

---

## 1. 総合判定

第2回レビューで挙げられた **A1–A4 / C1–C2** は原則として対応済みです。

- A1（Abstract 250 語以内）、A2（Highlights 85 文字以下）：確認時点で Abstract 231 語、Highlights 最大 70 文字。
- A3（endogenous inflow safety factor の表現）：「capped at 0.50× r_critical; the most constrained group (Japanese) realises 0.40×」に修正。
- A4（PI-pool PNR 閾値）：`src/ode_model_endogenous.py` で `M_threshold_P = k`（distinct last-author groups）を使用。
- C1（一部図表の Supplementary 化）：年次平均率テーブル・上位 OD ペアは Supplementary Table 3/4 へ移動。
- C2（MAPE 解釈補強）：方向一致率 21.6%、閾値超過警報精度 92.1%（sensitivity 0.0%, specificity 100.0%）を本文に追加。

さらに今回の対応で以下を追加修正しました。

- 年次遷移確率の Laplace smoothing を `+0.5/destination` から `+1/destination` に統一し、`cohort_extraction.py` の `prior=1` と整合。
- Data and Code Availability の「full-work local snapshot」という不正確な表現を削除し、公開リポに同梱されている「pre-extracted cohort and stratified sample of works」と正確に記述。
- 公開リポ `bougtoir/researcher-mobility-ode` をクリーン clone して `bash reproduce.sh` を完走し、原稿・図表・結果 CSV が同一に再生成されることを確認。

**総合判定**: 形式・再現性・データ整合性は *Research Policy* のダブルブラインド査読に耐えうるレベル。残るのは主に **A5（Funding/COI/Author contributions 等の提出情報）** と、査読者が突いてくる可能性の高いいくつかの解釈的問題です。投稿前にこれらを対応すれば、採択可能性は相当高いです。

---

## 2. 5 領域評価

### 2.1 原稿：新規性・焦点・論理構成

| 判定 | 項目 | 所見 | 修正案 | 優先度 |
|---|---|---|---|---|
| 強み | テーマの適合 | AI/ML 研究者モビリティを「文明圏レベルの最低維持プール」で議論する点は、RP の innovation policy / STI policy 読者に訴求する。 | 現状維持。 | – |
| 強み | フレームワークの具体性 | 6 コンパートメント ODE、PNR、endogenous inflow、safety factor、年次投影と、モデル構成が明確。 | 現状維持。 | – |
| 要修正 | Innovation studies 文脈の接続 | 2.2 節で Nelson & Winter [13]、Dosi [14]、Lundvall [15]、Malerba [16] を一括引用しているが、本文でそれぞれの概念（進化的ダイナミクス、ナショナル・イノベーション・システム、セクタール・システム）を具体例と結びつけていない。査読者は「なぜ突然この 4 文献が並ぶのか」と疑問に思う。 | 2.2 末尾に 1–2 文追加：「本稿の遷移率・PNR は、これらのマクロ的イノベーション・システム研究を個人キャリアデータと接続する試みである」と明確化。 | 高 |
| 要修正 | PNR の概念的位置づけ | PNR は生態学の minimum viable population [10] を転用した heuristic であることをもう一度強調。査読者は「deterministic に T = M を下回ると回復不能と決めつける根拠は？」と突っ込む。 | 4.3 / Discussion 6.6 で「PNR 閾値下回りは回復困難の十分条件であって必要条件ではなく、外的ショックがあれば閾値上でも崩壊しうる」と改めて明記。 | 高 |
| 要検討 | SHIGA 頭字語（匿名査読版） | Discussion 6.6 で SHIGA を「滋賀大学の研究基盤」に結びつけている。国際誌では気づかれにくいが、匿名査読では不要な情報と映りかねない。 | フルバージョンでは OK。`blinded` 版では「a Japanese national university」または institution withholding に置換することを提案。 | 中 |

### 2.2 統計設計・解析

| 判定 | 項目 | 所見 | 修正案 | 優先度 |
|---|---|---|---|---|
| 強み | コホート定義の整合性 | `src/cohort_extraction.py` の `MIN_WORKS=2`、hit は top-10% citation かつ著者位置不問、PI は last-author（単著含む）と本文記載一致。 | 現状維持。 | – |
| 強み | Laplace smoothing の統一 | コホート推定 `prior=1` と年次投影 `+1/destination` が統一された。 | 現状維持。 | – |
| 強み | 反実仮想の mechanical 性 | 政策レバーは「遷移率を 10% 擾動させた機械的反実仮想」であり、因果効果ではないと説明。 | 現状維持。ただし政策レバーと具体政策の対応表（Table 9）をさらに議論本文で言及するとよい。 | 中 |
| 要検討 | MAPE 129.0% の扱い | Abstract でも「conservative, non-standard MAPE 129.0% (count_obs + 1)」と自覚的に提示。Supplementary Table 1/2 でグループ別・コンパートメント別の予測精度を開示。 | そのままでも許容範囲だが、もし査読者が「なぜ投影層が必要か」と問う場合、方向一致率 21.6% の低さを補う表現を追加。 | 中 |
| 要検討 | 年次投影の方向一致率 21.6% | 方向一致率が低い。これは「 small compartments / sparse transitions 」を早期警戒では捉えにくいことを示唆。 | 6.4 節で「年次投影は人口予測ではなく、閾値超過の binary 警報を目的とする」と補強。 | 中 |
| 確認済 | 主要数値のトレーサビリティ | コホート `n=723,647`、closest PNR Other Western `I0=0.332×`、最大マージンゲイン `d`、MAPE 129.0% は `results/` CSV から再現可能。 | 現状維持。 | – |

### 2.3 図表

| 判定 | 項目 | 所見 | 修正案 | 優先度 |
|---|---|---|---|---|
| 確認済 | 図表引用 | Figure 1–9、Table 1–9 が本文で引用済み。orphan / phantom なし。 | 現状維持。 | – |
| 確認済 | Highlights 文字数 | 最大 70 文字。 | 現状維持。 | – |
| 要検討 | 図表の多さ | 本文に Figure 9 + Table 9 の計 18 点。RP に明確上限はないが、査読者が情報過多と感じる可能性。 | Table 8（Bootstrap CI 表）と Figure 4（同内容の棒グラフ）が重複。Table 8 を Supplementary へ移し、Figure 4 のみ本文に残すことを検討。 | 中 |
| 確認済 | Figure 3 左右反転 | 左原点に修正済み。 | 現状維持。 | – |
| 確認済 | 日本特化図の重複掲載 | Figure 8 は 1 度のみ掲載。 | 現状維持。 | – |

### 2.4 再現性・Data/Code Availability

| 判定 | 項目 | 所見 | 修正案 | 優先度 |
|---|---|---|---|---|
| 強み | 再現パイプライン | `reproduce.sh` で `results/` → 図表 → 原稿まで再生成。公開リポ `bougtoir/researcher-mobility-ode` でも `bash reproduce.sh` で完走を確認。 | 現状維持。 | – |
| 強み | 数値の自動挿入 | `scripts/build_full_manuscript.py` が `results/` CSV を読み込み、原稿数値を動的生成。ハードコードなし。 | 現状維持。 | – |
| 強み | Data Availability の正確化 | 「full-work local snapshot」という誤解を招く表現を削除。pre-extracted cohort + stratified sample と記述。 | 現状維持。 | – |
| 要記載 | 全 SQLite snapshot の取り扱い | 6.0 GB の `cohort.db` は GitHub サイズ制限のため公開リポに含まれない。 | Data Availability に「full SQLite snapshot is available from the authors on request」を 1 行追加。 | 低 |

### 2.5 主張の強さ

| 判定 | 項目 | 所見 | 修正案 | 優先度 |
|---|---|---|---|---|
| 確認済 | 因果表現の抑制 | Abstract/Discussion で「政策シナリオは mechanical perturbation であり因果効果ではない」と明記。 | 現状維持。 | – |
| 要検討 | 日本文明圏の一般化 | 5.9 / 6.5 節が日本に大きく割かれている。RP はグローバル読者向け。 | 「日本は最小文明圏の一つの illustrative case である」と冒頭で明示し、他文明圏への一般化可能性を一言述べる。 | 中 |
| 要検討 | 文明圏ラベル | 「Hindu」等の Huntington ラベルが否定的に受け取られる可能性。ユーザーと「名称変更の議論」が未決。 | Introduction の脚注で「文化・制度的共変量の操作化であり、規範的判断ではなく、現在の政治国境・価値観とは必ずしも一致しない」と明記。 | 中 |
| 要検討 | 数理モデルの限界 | 定常状態の heuristic 性、右打ち切り、cross-civilisation spillover 無視等は開示されている。 | 6.7 節に「アイディアの多様性が歴史的文明圏境界に依拠するか、今日的価値観境界に依拠するかは本研究では判定できない」と追加済み。 | 中 |

---

## 3. 優先度別アクションマトリックス

### A. 投稿前に必ず対応（desk-reject / major revision リスク）

| # | 項目 | 修正箇所 | 修正内容 | 実装工数 |
|---|---|---|---|---|
| A5 | 提出用情報の完成 | `build_full_manuscript.py` タイトルページ / Declarations | Funding, Competing interests, Author contributions, Corresponding author を placeholder から実値へ。 | 小（ユーザー入力必要） |

### B. 高優先（採択可能性を大きく高める）

| # | 項目 | 修正箇所 | 修正内容 |
|---|---|---|---|
| B1 | Innovation studies 文脈の接続 | 2.2 節 | Nelson & Winter / Dosi / Lundvall / Malerba を「進化的経済学 / ナショナル・イノベーション・システム / セクタール・システム」の文脈で引用し、本稿の「遷移率・PNR」と結びつける一文を追加。 |
| B2 | PNR 概念の位置づけ強化 | 4.3 / 6.6 節 | 「閾値下回りは回復困難の十分条件であって必要条件ではなく、外的ショックがあれば閾値上でも崩壊しうる」と改めて明記。 |
| B3 | 年次投影の目的を明確化 | 5.7 / 6.4 節 | 方向一致率 21.6% の低さを補いつつ、「population forecast ではなく drift / threshold-crossing の early-warning である」と強調。 |
| B4 | 政策含意の独立性強化 | 6.3 節 | 「Policy implications」小節を独立させ、各レバー（`d`, `I0`, `h_D`, `p_D`）に対応する政策主体（研究助成機関、大学、R&D マネージャー）を Table 9 より明確に記述。 |

### C. 中優先

| # | 項目 | 修正箇所 | 修正内容 |
|---|---|---|---|
| C1 | 日本特化議論の一般化 | 5.9 / 6.5 節 | 「illustrative application to the Japanese case」と位置づけ、他文明圏への一般化可能性を付記。 |
| C2 | 文明圏ラベルの定義脚注 | Introduction / Table 1 | 「Hindu」「Sinic」等の操作的位置づけを脚注で補強。 |
| C3 | Table 8 / Figure 4 の重複整理 | `build_full_manuscript.py` | Table 8 を Supplementary へ移し、Figure 4 のみ本文に残す。 |
| C4 | 全 SQLite snapshot の取り扱い | Data and Code Availability | full SQLite snapshot は著者依頼で提供可能と 1 行追加。 |

### D. 任意（提出直前）

| # | 項目 | 備考 |
|---|---|---|
| D1 | 図表ファイルの分離 | Elsevier 最終提出時は個別 PNG/TIFF/EPS が必要。`docs/figures/*.png` および `manuscript_full_article_figures.pptx` を用意済み。 |
| D2 | SHIGA 頭字語の匿名化 | `blinded` 版では「a Japanese national university」または institution withholding に置換。 |
| D3 | robustness check の追加 | saturating inflow / 異なる `k` 値 / career-start window 変化で PNR ランキングが安定していることを Supplementary Table 5 等にまとめる。 |

---

## 4. 査読者が投げそうな質問と先回り回答

1. **「なぜ Huntington の文明圏を使うのか？」**  
   → Introduction と Table 1 脚注で「地理・制度的共変量の操作化であり、現在の政治国境・価値観と一致しない限界も 6.7 節で議論」と説明済み。

2. **「PNR は本当に point of no return か？」**  
   → 4.3 / 6.6 節で「閾値下回りは回復困難の十分条件であって必要条件ではない」「外的ショックがあれば閾値上でも崩壊しうる」と説明。

3. **「PI-pool PNR の閾値は active-pool と同じなのか？」**  
   → `src/ode_model_endogenous.py` で `target="P"` の場合 `M_threshold_P = k`（distinct last-author groups）を使用。

4. **「MAPE 129% では予測として成立しないのでは？」**  
   → 5.7 / Abstract で「directional drift and threshold crossing の early-warning 指標」として位置づけ。Supplementary ではグループ別・コンパートメント別精度を開示。

5. **「政策介入の因果効果を示していないのでは？」**  
   → 5.3 / 6.3 節で「mechanical perturbation, not causal estimate」と明記。Table 9 で政策レバー対応を示す。

6. **「公開リポに 6.0 GB の `cohort.db` がないのでは？」**  
   → 公開リポは再現に必要な pre-extracted `cohort.csv` と stratified sample を同梱。full SQLite snapshot はサイズ制限のため著者依頼で提供。

---

## 5. 最終推奨

**現時点で *Research Policy* へ投稿可能か？** → **A5 のみ対応すれば条件付きで可能**。

1. **A5**（Funding / COI / Author contributions / Corresponding author）は編集者が投稿前に要求するため、提出直前までに必ず完了。
2. **B1–B4** を追加すれば、innovation studies 文文脈での採択可能性が大きく上がる。
3. **C1–C4** は中優先。対応すると査読者の「なぜこの設計か」という質問を未然に防ぐ。
4. 公開リポ `bougtoir/researcher-mobility-ode` はクリーン clone から `bash reproduce.sh` で完走し、原稿・図表・結果 CSV が再生成されることを確認済み。

上記 A/B/C を実装し、`reproduce.sh` で再生成 → 公開リポ同期後、投稿準備完了とみなすことができます。

---

## 付録：主要数値の results CSV 対応チェック

| 原稿記述 | 出典 CSV / スクリプト | 確認結果 |
|---|---|---|
| `n = 723,647` コホート | `data/cohort/cohort.csv` | 一致 |
| 9 文明圏 | `results/endogenous/equilibrium_summary.csv` | 一致（`group` 列 9 行） |
| 最も近い active-pool PNR: Other Western `I0` 0.332× | `results/endogenous/point_of_no_return.csv` | 一致 |
| 最大マージンゲイン：dropout `d` | `results/endogenous/top_transitions_T.csv` | 一致 |
| MAPE 129.0% | `results/annual/projection_evaluation.csv` | 一致 |
| safety factor cap = 0.50, 最小実現比 0.40 | `src/ode_model_endogenous.py` | 一致 |
| PI-pool 閾値 `M_PI = k` | `src/ode_model_endogenous.py` | 一致 |
| 年次 Laplace smoothing `+1/destination` | `scripts/annual_rates_projection_report.py` | 一致 |

