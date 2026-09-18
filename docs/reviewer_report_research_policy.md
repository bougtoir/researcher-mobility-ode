# Research Policy 査読者視点レビュー & ジャーナル適合度向上案

**対象原稿**: `docs/manuscript_full_article.docx`（および同梱の `manuscript_full_article.md`）  
**対象ジャーナル**: *Research Policy*（Elsevier）  
**レビュー観点**: ストーリー・フロー、データ－主張整合性、再現性、Research Policy スコープ／形式適合度  
**確認リビジョン**: `devin/researcher-mobility-ode-full-article` @ `c21bbc81`、PR #353 マージ済

---

## 1. 総合評価

### 1.1 ジャーナル適合度の基本判定

*Research Policy* は「innovation, technology, R&D, science, and the management of research and knowledge」を扱い、政策・管理実務者も読者層に含むトップジャーナルです。本稿の「AI/ML 研究者の遷移率から PNR（point of no return）を定量化し、文明圏レベルで早期介入の優先度を示す」という貢献は、RP の「science & technology policy」「innovation policy」スコープに**合致します**。ただし、以下 2 点が投稿前に致命的になりうるリスクです。

1. **docx と md の乖離**：同じ `reproduce.sh` から生成されるはずの `manuscript_full_article.docx` と `manuscript_full_article.md` が、Methods/Results/Discussion の章構成・引用文献・文字数で大きく異なっています。
2. **文字数超過**：docx（投稿原稿）の「main text incl. tables, excl. references」が **11,120 語**と、RP の Research Article 上限（8,000–10,000 語）を超過しています。

これらを修正すれば、double-blind 対応と併せて **minor revision で通りうる原稿**になります。

### 1.2 強み（査読者が評価するポイント）

- **オリジナリティ**：生態学の minimum viable population 概念を研究者集団の「最低維持可能共著者プール」に翻訳し、遷移率の感応度・PNR・政策レバーを結びつけた点は新規性があります。
- **再現性の設計**：`reproduce.sh` 一括実行、`results/` CSV からの動的原稿生成、公開リポ `bougtoir/researcher-mobility-ode` がある点は Data/Code Availability 要件を満たします。
- **主張の慎重さ**：「機械的反実仮想（mechanical perturbation）」「早期警報（early-warning）」「方向性指標」として因果効果を主張しない姿勢は適切です。
- **日本特化の動機付け**：Figure 8/9 と 6.5 節で日本の脆弱性を具体的に議論し、SPREAD 等の政策レバーと接続している点は、一般論に陥らない好材料です。

---

## 2. 投稿前に必ず対応すべき事項

| # | 項目 | 問題の所在 | 根拠 | 修正案 |
|---|---|---|---|---|
| **M1** | **docx / md / 原稿生成パイプラインの統一** | `scripts/build_full_manuscript.py` 内の `write_markdown()`（`build_full_manuscript.py:1091` 付近）と `write_docx()`（`build_full_manuscript.py:2789` 付近）が**別々の原稿テキスト**を出力している。 | docx では Methods が 4.1–4.11、Results が 5.1–5.10、Discussion が 6.1–6.7、7.1 Future work まで存在するのに対し、md では Methods が 4.1–4.6（再整備後）、Results が 5.1–5.9、Discussion が 6.1–6.4。さらに md 内に「Section 4.11」（`manuscript_full_article.md:239` 及び `:321`）への参照があるが、md には 4.11 が存在しない。 | **① 単一ソース化**：docx / md / pptx を同じセクションリストから生成する。または② md を「docx の忠実な Markdown 版」として後処理で出力し、両者が食い違わないようにする。当面は **docx を唯一の投稿原稿**とし、md は `wip` 作業用または削除。 |
| **M2** | **文字数超過** | タイトルページに「Approximate word count (main text incl. tables, excl. references): 11120」と記載（`manuscript_full_article.docx` 冒頭）。 | RP Research Article は「up to 8–10,000 words」。本稿は上限を 11% 超過。 | 1,500 語程度削減。候補：① Methods 4.5–4.8（Historical counterfactual design / Bootstrap uncertainty / Robustness checks / Relationship to existing indicators）を Supplementary Material へ；② Results 5.5「Synthesis」を Discussion 6.1 と統合；③ 表内の重複説明をキャプションに集約；④ 日本特化節を必要最小限に。 |
| **M3** | **匿名査読（double-blind）対応** | docx には「Corresponding author: [To be completed / removed for double-blind review]」（冒頭）、Acknowledgments に `note.com` エッセイと氏名・URL（`manuscript_full_article.docx` 冒頭）、Discussion に「research base at Shiga University」(`manuscript_full_article.md:369` 付近 / docx 6.5 節) と特定可能な記述がある。 | RP は全論文 double-blind。編集者は unblinded version も必要だが、査読者に送られる version からは著者・所属を消す。 | `build_full_manuscript.py` に `--blinded` オプションを追加。匿名版では Acknowledgments 全文を「[removed for peer review]」に、Shiga University 言及は「a Japanese national university」に置換、Corresponding author 行を削除。full version では通常通り記載。 |
| **M4** | **未引用参考文献の整理** | `manuscript_full_article.md` の References（`:391` 以下）では `[6]`, `[11]`–`[15]` が本文から引用されていない。docx では 15 文献すべて引用されている模様だが、md では未引用。 | Vancouver スタイル（RP は Vancouver 系）では、reference list に掲載する文献は本文で必ず引用。 | md/docx 統合時に整合。重要な文献は Introduction/Literature Review に引用し、不要な文献は削除。 |

---

## 3. 高優先：ジャーナル適合度を高める提案

| # | 項目 | 問題の所在 | 根拠 | 修正案 |
|---|---|---|---|---|
| **H1** | **Innovation Studies 文脈との接続強化** | Introduction と Literature Review が「研究者モビリティ」「AI 文献」中心で、RP の中核である *innovation systems*、*evolutionary economics*、*sectoral systems of innovation* の言葉や先行研究が薄い。 | RP Editorial Strategy は、innovation studies や S&T policy の文献と対話することを重視し、純粋経済学・管理学向け論文は desk-reject されるリスクがある。 | 既に reference list にある Freeman & Huang (2013)[13]、Franzoni et al. (2012)[11]、Jones et al. (2008)[12]、Kerr (2020)[15]、Shachar (2006)[14] 等を Introduction/Literature Review（2.1/2.2）で引用。さらに Dosi、Nelson & Winter、Lundvall、Malerba、Pavitt 等のセクターシステム・ナショナル・イノベーション・システムの議論を 2.4 節で引用し、「本稿の遷移率・PNR 枠組みは、それらのマクロ的文脈を個人キャリアデータと接続するもの」と位置づける。 |
| **H2** | **Policy / Management Implications の独立節化** | Discussion 6.3「Policy implications and early warning」は存在するが、介入対象（政策立案者、研究助成機関、大学研究部門、R&D マネージャー）と政策手段の対応が埋もれている。 | RP は「All RP papers are expected to yield findings that have implications for policy or management」と明記。 | Discussion に **6.3 Policy implications** と **6.4 Management implications** を分離。表形式で各遷移率（`d`, `I0`, `α`, `β`, `h_D`, `p_D`）に対応する「政策手段」「実務主体」「測定可能な KPI」を示す。例：`d` 低減 → 子育て支援/デュアルキャリア/任期制研究員ポジション → 女性・若手の継続率。 |
| **H3** | **MAPE 162% の提示方法** | Results 5.7/Table 11/12 で「MAPE 162%」を大きく報告。本文は「early-warning 指標であって精密予測ではない」と説明しているが、数値だけ見ると予測性能が非常に悪い印象を与える。 | 査読者は「なぜこの予測層が必要か」と問う。 | Table 11/12 を Supplementary Material に移し、本文には「観測値とプロジェクト値の時系列プロット（Figure 7）と RMSE のみ」を残す。または、方向予測の正答率（上昇/横ばい/下降の sign test）や閾値超過検出率を追加し、early-warning としての有用性を定量化する。 |
| **H4** | **Section 参照と図表番号の完全整合** | md 内の「Section 4.11」`(:239, :321)`、docx 内の「Sections 4.1-4.4」「Section 4.11」など、セクション番号がハードコードされている。 | 章番号を変更すると参照が全部壊れる。 | 原稿生成スクリプト内でセクション番号を動的変数にし、交叉参照も自動挿入する（例：`{section_correction_pressures}`）。docx では `python-docx` の bookmark/cross-reference、md ではテンプレート変数を使う。 |

---

## 4. 中優先：品質・透明性向上

| # | 項目 | 問題の所在 | 根拠 | 修正案 |
|---|---|---|---|---|
| **C1** | **「small sample/pilot」表現の修正** | `manuscript_full_article.md:59` に「The sample is a reproducible pilot extraction; absolute counts are small...」とあるが、Table 1 では Anglosphere ex-US だけで 64,122 人・700,342 works、合計 723,647 人のコホートである。 | 主張とデータが矛盾。査読者は「パイロットなのかフルコホートなのか」と疑問に思う。 | 表現を修正：「The sample is a full AI/ML cohort extracted from the OpenAlex snapshot; absolute counts should be interpreted as model-implied stocks, not as a definitive census due to coverage and disambiguation limitations」とする。 |
| **C2** | **文明圏ラベルの扱い** | 「Hindu」等の文明圏ラベルが否定的に受け取られる可能性がある。 | RP は cross-disciplinary readership を持つため、読者によっては本質主義的ラベルと誤解される。 | Introduction で「これは地理・文化的共変量の操作化であり、規範的判断ではない」と明記。フットノートで各グループの国リストを示す。ユーザーと相談の上、将来的には「South Asian」等への変更も検討。 |
| **C3** | **Highlights / Abstract / Keywords の政策色強化** | Highlights（docx 冒頭）は方法論的な 3  bullet。Keywords に「PNR」が含まれる。 | Highlights は検索可視性とRP読者への訴求力を担う。PNR は専門外読者には通じにくい。 | Highlights を政策指向に書き換える例：  
  - "We estimate civilisation-level transition rates of AI/ML researchers from OpenAlex and identify which rate is closest to a point-of-no-return threshold."  
  - "Dropout reduction and exogenous entry are the most sensitive levers for policy intervention."  
  - "The framework can be rerun annually as an early-warning dashboard for research-policy design."  
Keywords に "science policy", "innovation systems", "researcher mobility" を含め、「PNR」は abstract で定義済みなので外しても可。 |
| **C4** | **生成AI使用の開示** | Elsevier / RP Guide for Authors に「Declaration of generative AI in scientific writing」が要件。 | 本稿の生成（Devin/LLM 支援）を開示しないと、出版倫理上の問題になりうる。 | Declarations に「The authors used AI-assisted tools to draft, code, and revise the manuscript. All claims, data, and interpretations were verified and approved by the authors.」を追加。 |
| **C5** | **図表数の適正化** | 12 tables + 9 figures = 21 の図表。RP には明確上限がないが、量が多い。 | 過多な図表は物語の流れを乱す。 | Table 5（saturating T）、Table 8（bootstrap CI）、Table 10（top OD pairs）、Table 12（projection by compartment）、Figure 4（bootstrap CI）、Figure 6（inter-civ heatmap）を Supplementary Material に移すことを検討。ただしユーザー知見「図表は本文にインライン」との整合は要相談。 |

---

## 5. 任意／小修整

| # | 項目 | 問題の所在 | 根拠 | 修正案 |
|---|---|---|---|---|
| **L1** | **未使用コード（dead code）の整備** | `researcher_mobility_ode/src/cohort_extraction.py:344` `if failed_batches:` ブロックは、fail-fast 化により実際には到達しないデッドコード。 | Devin Review (#353) の指摘。再抽出時の保守性・可読性を損なう。 | 再試行成功時に回復ログを記録するようにするか、到達不能な `if failed_batches:` ブロックを削除する。 |
| **L2** | **OpenAlex スナップショット情報の明示** | 本文では「OpenAlex API (subfield 1702, 2000–2023)」とあるが、実際には API 制限を避けるためスナップショット経由で取得した可能性がある。 | Data Availability を精査する査読者がバージョン・取得日を問う。 | Methods/Data Availability に「OpenAlex snapshot accessed on YYYY-MM-DD (or API calls in 2026-08)」と明記。 |
| **L3** | **日本特化議論のバランス** | 5.9/6.5 節が日本に大きく割かれている。 | RP はグローバル読者向け。過度な国別展開は「単一ケーススタディ」と誤解される。 | 5.9/6.5 を「illustrative application to the Japanese case」として明確に位置づけ、他文明圏への一般化可能性を 6.5 節の冒頭で一言述べる。 |
| **L4** | **Section 配置の順序** | `Data and Code Availability` と `Declarations` が Abstract の直後、Introduction の前にある。 | RP の標準的な原稿順序は Introduction 以降に配置するか、declaration として最後に置くことが多い。 | `Declarations`, `Acknowledgments`, `Data and Code Availability` を Conclusion 後または References 直後に移動。Your Paper Your Way であれば必須ではないが、読みやすさ向上のため推奨。 |

---

## 6. 査読者が抱きそうな具体的疑問と対応案

1. **「なぜ Huntington の文明圏？」**  
   → Introduction で「地理・制度的共変量の操作化であり、現在の国境や価値観と一致しない限界も 6.7 節で議論する」と先回り。

2. **「PNR は本当に point of no return か？決定論的ではないか？」**  
   → すでに「sufficient condition, not necessary」と説明。さらに Discussion の冒頭で「閾値下回りは回復困難の十分条件であって、上回りでも外的ショックで崩壊しうる」と強調。

3. **「T_eq は観測値より大きいが、これは何を表しているのか？」**  
   → Methods 4.4 で「定常状態のモデル含意ストックであり、コホートそのものではない」と明記。Table 1（観測コホート）と Table 2（定常状態）の違いを一文で対比。

4. **「政策介入の因果効果を示していないのでは？」**  
   → すでに「mechanical perturbation / not causal estimates」と謙虚に記載。H2 で policy implications 節を独立させ、因果推定を今後の研究として切り分ける。

5. **「MAPE 162% では早期警報として使えないのでは？」**  
   → H3 の対応：方向性指標として再設計し、閾値越え警報精度や sign test を追加。または予測精度表を Supplementary へ。

---

## 7. 最終推奨アクション

1. **即座に `build_full_manuscript.py` を単一ソース化し、docx と md を完全に一致させる**（M1）。これが最優先。
2. **docx 文字数を 10,000 語以内に圧縮**（M2）。docx を投稿用、md を下書き用に分ける場合は md の重複セクションを整理。
3. **double-blind 用と full 用の 2 バージョンを生成**（M3）。
4. **Introduction/Literature Review に innovation studies 文献を追加**（H1）。
5. **Discussion に Policy/Management implications 節を独立化**（H2）。
6. **MAPE 関連表を Supplementary か本文末尾に移し、early-warning 指標として再位置づけ**（H3）。
7. **生成AI使用、OpenAlex 取得情報、未引用文献の整理を完了**（M4, C4, M4）。

これらを実施すれば、*Research Policy* において「スコープ内、方法論的に興味深く、政策含意も明確」という first-round 印象を与えられます。
