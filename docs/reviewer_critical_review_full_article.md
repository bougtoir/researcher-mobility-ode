# 査読者視点 批判的レビュー：Research Policy full-article manuscript

**対象原稿**: `docs/manuscript_full_article.docx`
**検証リビジョン**: `devin/1786331050-reviewer-audit` → `devin/researcher-mobility-ode-full-article`（以後 `12024caf` まで）
**レビュー観点**: ストーリー・フロー、伏線回収、データと主張の整合性、再現性、図表・文献の整合性

---

## 1. 実施した検証

- **公開リポ再現性**: `git clone --depth=1 https://github.com/bougtoir/researcher-mobility-ode` 後に `bash reproduce.sh` を実行。`results/`、図表、docx/pptx/md/zip が再生成され、原稿掲載数値と一致した。
- **機械的整合性**: `docs/manuscript_full_article.md` 内の Figure/Table 初出を抽出。Figure 1–9、Table 1–12 ともに初出順に番号が増加し、orphan/phantom なし。
- **数値の動的生成**: `scripts/build_full_manuscript.py` が `results/endogenous/equilibrium_summary.csv`、`results/point_of_no_return.csv`、`results/annual/*.csv`、`results/policy_counterfactuals/counterfactuals.csv` 等を読み込み、本文・表・図を生成。ハードコードされた数値は確認されなかった。
- **年度移行率スクリプトの修正圧妥当性**: `annual_rates_projection_report.py` における I_total NaN 処理、右打ち切り (right censoring) 対応、訓練期 (2000-2016) 全体の first-compartment inflow 合計、dashed/solid 描画分離、fig_dir 引数追加を確認。
- **Methods テキスト整合**: 修正後の docx/md で「dropout cap = 1.5 × 90th percentile」「inflow apportionment = training-period first-compartment distribution」と記述され、コードと一致。
- **PNR 略号統一**: docx/markdown ともに "point of no return (PNR)" は Abstract と Introduction の各初出のみ 2 回で、あとは "PNR" に統一された。

---

## 2. 修正済みの再現性・整合性バグ

| # | 問題 | 修正内容 | 影響 |
|---|---|---|---|
| 1 | `annual_rates_projection_report.py` で zero-inflow 年を outer-merge 後 `dropna()` していたため、I_total 平均が過大評価されていた | `rate_table["I_total"] = rate_table["I_total"].fillna(0.0).astype(float)` を追加 | projected inflow が training 全期間の実測分布に基づくようになり、一部文明圏で低下・収束する傾向が正しく反映された |
| 2 | `build_annual_exits` で各著者の最終観測年も離脱 (exit) としてカウントしていた | `year != last_year` の条件を追加して右打ち切りを除外 | 2023 年などの d=1.0 異常値が消え、離脱率が現実的な水準になった |
| 3 | `project_population` で初年度 compartment 配分を 1 年目だけで計算していた | 訓練期 (2000-2016) 全体の first-compartment inflow を合計して share を計算 | 複数年度にわたる流入パターンが正しく反映され、プロジェクト期の compartment 配分が安定的になった |
| 4 | `plot_annual_rates` で observed・projected を区別せず一本の実線で描いていた | observed を `-`、projected を `--`、同一色で重ね描きし凡例を整理 | Figure 5 で 2016 年を境に実線と破線が切り替わる |
| 5 | `build_full_manuscript.py --output-dir` 使用時に annual 図が `docs/figures` に固定出力されていた | `plot_annual_rates/interciv_heatmap/projection_by_compartment` に `fig_dir` 引数を追加し、`build_annual_figures` から渡す | 任意 output dir で再現可能 |
| 6 | Methods の記述がコードと不一致（90th percentile・2016 distribution） | 「1.5 times the 90th percentile」「training-period first-compartment distribution」に修正 | コードと本文が一致 |

---

## 3. レビュー指摘 A–H への対応

| 指摘 | 内容 | 対応 |
|---|---|---|
| **A** | Markdown セクション番号の不連続 | `scripts/build_full_manuscript.py` の `write_markdown()` 末尾で `_renumber_markdown_sections()` を呼び、全 main section を 4.1–4.6、5.1–5.9、6.1–6.7 の連番に再整備。docx はもともと連続 |
| **B** | MAPE 42.5% の解釈 | Abstract、Results 5.7、Discussion 6.4 に「保守的・非標準的 MAPE（count_obs + 1 で計算）」「small compartments / zero-observed cells」「directional early-warning indicator, not precise count forecast」と明記 |
| **C** | RQ4「policy packages」と single-lever counterfactual のギャップ | `results/policy_counterfactuals/counterfactuals.csv` から `package:*` 行を読み込む `_package_summary()` を追加。Results 5.3・Discussion 6.1 に「single-lever and multi-lever scenarios」として統合し、日本・Other Civilizations・Other Western の最良 2 レバー package 例を表に追加 |
| **D** | Abstract の因果表現 | `A simulated reduction in dropout yields the largest margin gain per unit proportional change in every group in the fitted model` と「in the fitted model」を明記。Discussion 6.1 終盤・Conclusion で「mechanical perturbation」「not causal estimates」を強調 |
| **E** | Inter-civilisation flow の proxy/lower-bound | Figure 6 キャプションを「Inter-civilisation abroad author-year accumulation ... (lower-bound proxy; year-to-year destination switches within a spell abroad are not observed)」に変更。Methods 4.10・Discussion 6.7 でも proxy であることを補足 |
| **F** | Hindu グループ命名 | 名称はそのまま、Introduction で「India and nearby South Asian countries (Hindu)」と定義を明記。他地域名の変更はユーザー相談の上 |
| **G** | Figure 4（bootstrap CI）の視認性 | `savefig(..., dpi=600, bbox_inches='tight')` に変更し印刷品質を確保 |
| **H** | PNR 略号統一 | Abstract と Introduction でそれぞれ 1 度ずつ「point of no return (PNR)」を定義し、それ以降は「PNR」に統一。docx 側も `_unify_pnr_docx()` で同様に処理 |

### 追加対応

- **中国・台湾に関する文明圏境界の言及**: Discussion 6.7（Limitations）に「歴史を踏まえた文明圏の境界線が、こんにちの価値観や政治領域の境界線と必ずしも一致しない」ことを、Sinic グループ（mainland China/Taiwan）の例としてニュートラルに追加。さらに「アイディアの多様性が歴史的文明圏境界に依拠するか、今日的価値観・政治領域の境界に依拠するかは本研究では判定できない」と明示。

---

## 4. 総合評価

### 4.1 強み

- **再現性**: 公開リポ `bougtoir/researcher-mobility-ode` をクリーン clone して `bash reproduce.sh` 一括実行可能。全数値は `results/` CSV から動的生成され、捏造・ハードコードなし。
- **整合性**: 修正後の annual projection は observed/projected 分離、右打ち切り処理、訓練期 first-compartment 配分を反映し、コードと本文が一致。
- **主張の慎重さ**: 因果を主張せず「mechanical perturbation」「early warning」「scenario tool」として位置づける。
- **ストーリー回収**: Intro の 5 RQs と 4 Hs が Results/Discussion/Conclusion で原則的に回収。特に「早期介入 → 文明圏多様性維持」という目標が Conclusion で結ばれている。
- **SHIGA 導入**: タイトルは「Sustaining Heterogeneity through Interventions in Global AI/ML Researcher Mobility: A Transition-Rate Framework」、Discussion 6.5 で初出としてフル表記+（SHIGA）を導入し、滋賀大学との関連を明記。それ以降は「SHIGA」のみ。

### 4.2 主要な弱み（残件）

- `manuscript_full_article.md` は docx 提出を前提とした補助ファイルであり、連番化は実施済みだが、最終投稿時は docx を規定ファイルとする。
- MAPE 42.5% は高い値のままだが、本文で早期警報系としての位置づけを十分に説明済み。

### 4.3 投稿準備判定

**minor revision 対応完了**。指摘 A–H はすべて本文またはコードレベルで対応済み。再現性と公開リポ整合性も確認。最新版は `devin/researcher-mobility-ode-full-article`、公開ミラーは `bougtoir/researcher-mobility-ode`。

---

## 5. 検証に使用したコマンド（再現用）

```bash
git clone --depth=1 https://github.com/bougtoir/researcher-mobility-ode
cd researcher-mobility-ode
bash reproduce.sh
# 出力: docs/manuscript_full_article.docx, .md, .pptx, _submission.zip
```

主な整合性チェック:

```python
import pandas as pd
pd.read_csv("results/endogenous/equilibrium_summary.csv")[["group","T_equilibrium","M_threshold","T_over_M","margin_to_threshold_T","I0","r"]]
pd.read_csv("results/point_of_no_return.csv").query("group=='Japanese'")
pd.read_csv("results/annual/projected_ode_rates.csv").query("origin_group=='Anglosphere ex-US' & year>=2017")[["year","I_total","d"]]
```
