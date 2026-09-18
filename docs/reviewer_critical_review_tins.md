# Technology in Society 投稿前 査読者視点レビュー（第 2 回・最新ビルド対象）

**対象原稿**: `docs/manuscript_full_article.docx` / `manuscript_full_article_blinded.docx`（コミット 9292862 でのビルド、本文 6,780 語、Fig. 9・Table 8）
**対象ジャーナル**: *Technology in Society*（Elsevier）
**前史**: Research Policy desk reject（RESPOL-D-26-02845）。理由: (a) RQ が理論的ギャップから導出されていない、(b) 仮説のメカニズムが理論化されていない。
**手順**: 通読 → 数値を `results/*.csv` に照合 → 5 領域で評価 → 致命度・修正効果・実行可能性で順位付け。

第 1 回レビューで指摘した点（P1 の準トートロジー、P3 前半の構造性、variety 未測定、ε 感度）は原稿本文に反映済みなので、本レビューは **通読で新たに見つかった問題** を中心に書く。

---

## 0. 結論

desk reject 理由 (a)(b) には §2 の再構築で正面から答えており、TinS の editor レベルは通る見込み。しかし **査読者が数表を突き合わせると矛盾に見える箇所が 3 つ**あり（§1-A, 1-B, 1-C）、これらは major revision 要因になり得る。いずれも **追加解析なし・記述修正のみで対応可能**なので、投稿前に直すことを強く推奨する。

---

## 1. 原稿（新規性・論理・結果と結論の整合）

### A. 「どの系も閾値を超えている」と Supplementary S2 の観測アラーム 5 年が矛盾して見える（致命度: 高／修正: 容易）

- Abstract・§5.1・§5.5・§7 は「All equilibrium active pools exceed M」「no system is currently below its threshold」と書く。
- 一方 Supplementary Table S2 では Other Western の **観測**アラーム年が 5（2017–2023 の 7 年中）で、投影アラームは 0（sensitivity 0%）。
- 理由は本文にある通り「2016 で閉じたコホートの観測ストックは新規参入を含まないため単調減少する」ためで、均衡 T（新規参入込み）が M を超えることと矛盾はしない。だが読者は「観測では 5 年間閾値割れ、モデルは超過、と言っているのか」と読む。
- **対応案**: §5.6 に 1 文追加 —「観測アラームは閉コホートの減衰による人工物であり、均衡 T の閾値判定とは対象が異なる。年次層のアラーム指標は新規参入を含む再構築ができるまで参考値とする」。または S2 からアラーム列を落とし、accuracy/direction のみ載せる。

### B. Table 1 の PI 数・hit 数がコホートの過半を占める（致命度: 高／修正: 容易〜中）

- Anglosphere ex-US: PIs 43,628 / Authors 64,122（68%）、Hit authors 35,822（56%）。Japan: PIs 58%、Hit 31%。
- 「PI = 最初の last-author 論文（単著含む）」「hit = 年内上位 10%（最初の 8 年内）」という定義では、≥2 論文のフィルタと相まって過半が PI かつ 3 割以上が hit になる。査読者は「PI が過半なら PI-driven recruitment という network externality の描像は何を意味するのか」「M = k×c̄ の k（distinct PI group 数）はこの PI 定義でどう数えたのか」と問う。
- **対応案**: (1) §3.2 に「PI は"独立したラストオーサー経験がある著者"の広い操作定義であり、テニュア PI ではない」と明記し、k は年あたり distinct last-author 数の中央値である旨を §4.3 で再確認する。(2) 可能なら Table 1 に「PI share」「hit share」列を出して定義の帰結を隠さない。(3) 感度として「last-author 論文 ≥3 本」等の厳しい PI 定義で T/M 順位が変わらないか（追加解析、高優先）。

### C. 均衡 T が観測 active 数の 2–3 倍（致命度: 中／修正: 容易）

- Japan: T_eq = 29,332 vs Active 2020–2023 = 11,846。US: 147,067 vs 58,969。
- 均衡は「現行率が永続した場合の漸近値」で、観測 active は閉コホートの 2020–23 スナップショットなので一致しなくてよいが、本文はこの差を説明していない。「model-implied stocks rather than a census」（§3.2）の 1 文では不足。
- **対応案**: §4.4 か §5.1 に「均衡 T は開放系の漸近値であり、閉コホートの観測 active 数を上回る。相対比較（T/M、順位）が主張の対象で、絶対値は比較しない」を明記。

### D. Other Western ≒ Israel（致命度: 中／修正: 容易）

- S1 によれば Other Western の 2022–2023 AI/ML works 3,847 件はすべて Israel（100%）で、他の構成国は 0 件。最も閾値に近い系として Abstract・Highlights に 3 回登場するのに、本文では正体が分からない。
- **対応案**: §3.1 または §5.1 で「Other Western is in practice a single national system (Israel, 100% of 2022–2023 works)」と明示し、「小規模だが高影響の研究系」という解釈を添える。地政学的含意を避けたいなら表示名を「Israel & other Western」にする選択もある。

### E. P4 の支持が弱い（致命度: 中／修正: 容易）

- Table 6 の後期窓均衡は South Asia +372%、Islamic world +391% と急伸し、Japan だけ −21%。後期窓は exposure が短いので promotion 率が過大／dropout 率が過小に出やすく、成長系ほど膨らむ。
- 本文は「sensitivity exercise」と断りつつ、Conclusion と Highlights では「rates have drifted…, shrinking the margin in Japan」と結果として書く。書き分けが不揃い。
- **対応案**: Conclusion の文を「in one macro-region (Japan) the late-window rates imply a smaller margin, a point estimate that requires longer exposure to confirm」に揃える。Highlights からは P4 を外している（現状 5 本に含まれていない）ので問題なし。

### F. 理論節の残課題（致命度: 低〜中）

- §2.2 の事例列挙のうち **Lysenkoism は国家強制**であり、選択圧による収斂とは機序が異なる。本文で「differ in mechanism」と断っているが、査読者が「事例の寄せ集め」と読むリスクがある。→ 事例を「内生的選択（perceptrons, DSGE, string theory, canonical ossification）」「外生的強制（Lysenko）」「生物学的単一栽培（corn, coffee, banana）」の 3 類型に 1 文で整理すると説得力が上がる。
- §2.3 の反論（規模の経済・OSS）に対する答えが「方法の拡散は PI・学生・制度を再生産しない」の 1 点に依拠。これはモデルの binding lever が I0/PI stock であることと整合しており良いが、**OSS が I0 を高める（参入障壁を下げる）可能性**には触れていない。1 文加えると誠実。

---

## 2. 統計・モデル設計

1. **飽和モデルの ε ≈ 1e-5 で差 <0.001%**（Table 5）。「robustness check」として提示しているが、ε がデータから実質ゼロに落ちており検定になっていない。第 1 回で指摘済み・未対応。→ 固定グリッド（ε で飽和項が r P_D の 25/50/75% を削る値）での順位不変性を Supplementary に 1 表追加するのが最小対応（追加解析、高優先）。対応しない場合は Table 5 を本文から外し、§5.3 の記述を「fitted ε is negligible, so the check is weak」と正直に書く。
2. **年次層の direction agreement 21.6%** は 3 値分類のチャンス（33%）を下回る。§6.4 の「drift in rates can be detected one year ahead」は支持されない。→ この 1 文を削除または「rate-level skill 0.99 は平均回帰ベースラインに対するもので、方向予測力はない」と書き換える（記述修正、必須）。
3. **dropout の定義がコホート年齢と交絡**。2016 参入者は 2020–23 に論文が無ければ dropout、2000 参入者は 20 年生存後の判定。Laplace 平滑・右打ち切りの記述はあるが、この交絡の言及がない。→ Limitations に 1 文。
4. **r の 0.50× キャップ**。Japan のみ観測 r がそのまま使われ（0.40×）、他はキャップに張り付く。キャップが結果（特に P3 の順位）を規定していないかの感度は S7 にない。→ Limitations に「cap 0.25/0.75 での順位」を追加するのが望ましい（追加解析、中優先）。
5. **9 観測での ρ**：P1 は indicative と明記済み。問題なし。

---

## 3. 図表

- Fig. 5–7（年次層）は本文の主張（P1–P4）を直接支持しない。§5.6 の結論が「forecast ではない」なら **Supplementary へ移動**し、本文は Fig. 1–4, 8, 9 の 6 点に絞ると読みやすい（任意→中優先に引き上げ）。
- Table 5 は情報量がほぼゼロ（全行同値）。Supplementary S7 と統合を推奨。
- Table 2 の「r」「r (observed)」「r (critical)」の 3 列は、脚注なしでは r と r(observed) の違いが読めない。キャプションに「r = value used (capped at 0.50× r critical)」を追加。
- Table 6 の Δ margin が小数第 1 位（10466.2）で人数らしくない。整数化。
- Fig. 6（cross-region heatmap）は本文で 1 文しか参照されない。Supplementary 候補。
- 図表は全て英語・インライン・初出順・pptx 同梱を確認。

---

## 4. 再現性

- 全数値は `results/*.csv` → `build_full_manuscript.py`。Abstract/Highlights/Cover letter も同経路。
- `reproduce.sh` をクリーン環境で完走済み（bootstrap 200 draws が数時間）。**README に所要時間と `--n-boot` を下げた短縮手順**を書くと第三者再現の実効性が上がる（任意）。
- Supplementary S2 の手法記述は今回実装と一致させた（クリップ／R²<0.10 で平均置換／dropout 上限／PI 安定キャップなし）。
- 参考文献 7, 8, 10 に DOI がない（Franzoni 2012: 10.1038/nbt.2449、Stephan 1996 JEL、Dosi 1982: 10.1016/0048-7333(82)90016-6）。Crossref で確認のうえ追加を推奨。
- 抽出コホート SQLite は「on request」。TinS は Data Availability の記載があれば可だが、OpenAlex は CC0 なので派生集計を公開リポに置く方が強い（任意）。

---

## 5. 主張の強さ

- 「irreversible」は Abstract に 1 回、本文では「difficult to reverse」に緩めてある。Abstract も「potentially irreversible」に揃えると安全。
- Highlights 3 本目「Closest PNR: Other Western, via 67% change in I0」は、他の 8 系の critical factor が 0.01–0.06（つまり I0 を 94–99% 削らないと閾値に届かない）であることと合わせて読むと、「現状どの系も遠い」という含意になる。**危機を示す結果ではなく早期警戒指標の提示**であることを Abstract 最終文で明確にしているのは良い。Highlights は事実記述なので問題なし。
- 「Who benefits」節は各アクターをモデル出力に接地しており、規範的主張の暴走はない。
- 「AI/ML が既に袋小路」とは主張していない（§2.2 末尾）。

---

## 6. 追加：人材集中シナリオ（§4.5 / §5.8 / Fig. 12 / Table 8）

- **強み**：適合済みの 9 系モデルを観測ホスト行列で結合しただけの γ = 0 で、field の実効地域数が全設定で低下する（頑健）。ドミナント地域の相対優位と field の縮小を分けて書き、「相対優位を維持できるから合理的」と読めないように §6.5 で評価スケールを field/社会/人類に固定している。
- **弱み・査読で突かれる点**：(1) γ（variety 弾性）は本データで識別されない自由パラメータであり、field 産出の低下が γ = 0 で出るのは最大ホスト（China-centred）の国内 hit 率が低いという適合値に依存する（第 2 ホスト United States では γ > 0.8–3.9 が必要）。本文でその依存を明示した。(2) 引き抜き強度 φ・帰還率の φ 依存・M 割れ後の永久停止は様式化。(3) 遷移率は horizon 全体で固定。時間軸は特性時間 τ = 1/d̄（適合離脱率から出る平均キャリア期間）で無次元化し、暦年換算は副軸・括弧内の注釈に留めた。「n 年後に衰退する」という普遍的な暦年主張はしておらず、覇権の対価が τ の数倍で field に現れるという相対表現に統一。国家の存続期間・覇権期間は識別しないと明記。いずれも §4.5・§6.6 Limitations と Supplementary Table S8 に記載済み。(4) 実装上、φ で増えた流出は別コンパートメントで追跡し既存在外ストックは観測ホスト比率 W を保つため、全 φ が同一初期状態から出発する。M 割れは積分器の terminal event で正確な交差時刻に適用。
- **推奨**：査読者に「γ を測れ」と言われる可能性が高い。トピック多様性（OpenAlex topics）と hit 率の地域パネル回帰で γ の粗い推定を試みることを次回改稿の第一候補にする。

---

## 優先度付き対応リスト

**最優先（投稿前に必須・記述修正のみ）**
1. §5.6 に観測アラームが閉コホートの人工物である旨を追記（または S2 からアラーム列を除去）— §1-A
2. §3.2/§4.3 で PI・hit の広い操作定義と k の数え方を明示 — §1-B
3. §4.4/§5.1 に「均衡 T は開放系の漸近値で観測 active と一致しない」を追記 — §1-C
4. §6.4「detected one year ahead」を削除／書き換え — §2-2
5. Other Western ≒ Israel を本文で明示 — §1-D

**高優先（追加解析を伴う；未実施なら Limitations で明示）**
- 厳しい PI 定義での T/M 順位感度 — §1-B(3)
- 飽和 ε の固定グリッド感度 — §2-1
- variety の直接指標（トピック／ベンチマーク多様性）— 第 1 回から継続

**中優先（記述・構成）**
- Conclusion の P4 文を sensitivity 表現に揃える — §1-E
- §2.2 事例を 3 類型に整理、OSS が I0 を高め得る点を 1 文 — §1-F
- dropout とコホート年齢の交絡を Limitations に — §2-3
- r キャップ感度を Limitations に — §2-4
- Fig. 5–7・Table 5・Fig. 6 の Supplementary 移動 — §3
- Table 2 キャプション（r の定義）、Table 6 Δ margin の整数化 — §3

**任意**
- 参考文献 7, 8, 10 の DOI 追加
- README に短縮再現手順
- Abstract の「irreversible」→「potentially irreversible」

---

# 第 3 回レビュー（頑健性補強後ビルド：ブランチ `devin/1789691565-tins-robustness`）

**対象**: 本文 Fig. 1–10・Table 1–9、Supplementary S1–S4・Table S1–S12・Fig. S1–S3。数値は `results/pi_proxy/`, `results/m_sensitivity/`, `results/annual/` に照合。

## 1. 今回対応した点と査読者視点での残課題

### A. PI proxy 頑健性（第 2 回 §1-B(3)、高優先 → 対応済み）
- OpenAlex 2000–2023 AI/ML 全母集団を再抽出（3,454,766 works・10,387,948 authorships、719,173 著者）し、SQLite（`works` / `author_works` / `authorships`、`is_corresponding`・著者順・国コード・年を保持）に永続化。3 定義（first last-author／first corresponding／recurrent last-author ≥2）を **同一スナップショット**で比較。
- **結果の読み方に注意が必要**: 均衡 T・T/M・I0 レバーの PNR 近接度は 3 定義で完全一致する。これは I0 を「均衡総流入 = 観測年間流入」で較正しているため、T が PI 定義に**構成上**依存しないからである（T_eq(f) = f·T_obs）。第 1 稿では「順位が頑健」と書いていたが、これは検定になっていない。本文 §5.5 と Supplementary S3 で「T/M と I0 近接度は構成上不変」と明記し、**PI 定義に依存する量**（p_D・p_A、均衡 P_D、I0/r の分配、T の p_D 弾性、PI プールの自閾値 k に対する PNR）で順位一致を示す形に改めた。Spearman ρ: P_D ≥ 0.98、PI プール近接度 1.00、p_D 弾性 ≥ 0.73（0.21–0.36 → 0.30–0.51 に上昇）、PI プールの最近接レバーは Other Western (Israel) のみ I0 → d に変化。
- 残課題（中）: PI 定義を厳しくすると PI シェアが 67% → 48% に落ちるが、それでも約半数が PI。第 2 回 §1-B の「広い操作定義」注記は維持が必要。§4.2 に I0 較正の 1 文を追加した。

### B. M 感度（対応済み）
- M × 0.5–2.0 で閾値割れ 0 系、T/M・近接度順位は完全保存（ρ = 1.00）、|e_d| > |e_α| は全系・全倍率で成立。最近接レバーは Other Western (Israel) で 1.25 倍以上のとき I0 → d。M は線形モデルでは target にしか入らないため、順位不変は構成上の性質でもある点を本文に記した。

### C. Annual monitoring の Supplementary 移動（第 2 回 §3、対応済み）
- 本文からは 2 文の参照のみ（exploratory extension）。Fig. S1–S3、Table S2 相当は S2 節へ。本文図は 10 点に減り、check_manuscript で図表初出順・全引用を確認。

### D. 記述修正（対応済み）
- M 初出「operational minimum viable coauthor scale」、P1 を structural implication / diagnostic に、Conclusion「can reduce total output after a transient gain」、表示名「Other Western (Israel)」、Huntington 出発点の短縮。

### E. 他分野への転用（新規・Limitations に追加）
- PI・hit proxy は AI/ML の著者順慣行（group leader が last / corresponding）に依存。アルファベット順（数学・経済・HEP）や consortium authorship の分野では `is_last_author` / `pi_years_by_definition` / `is_top10` の修正が必須である旨を Limitations・README・コードコメントに明記。

## 2. 再現性
- `reproduce.sh` に `pi_proxy_robustness.py` と `m_sensitivity.py` を追加。`FULL=1` で全母集団再抽出→`data/cohort/pi_proxy/` を再生成。通常経路は公開リポにコミットした `data/cohort/pi_proxy/cohort.csv`（82 MB）から再現可能。SQLite 本体（4.2 GB）は gitignore（API 再取得で再生成可）。

## 3. 未対応（次回改稿候補）
- 飽和 ε の固定グリッド感度（第 2 回 §2-1）、r キャップ感度（§2-4）、γ の直接推定（§6）。いずれも Limitations で明示済み。

---

# 第 4 回レビュー（投稿前最終：ブランチ `devin/1789705114-tins-final-polish`）

**対象**: 本文 Fig. 1–10・Table 1–9、Supplementary Table S1–S12・Fig. S1–S3、highlights、cover letter。数値は `results/endogenous/`, `results/dominant_strategy/gamma_thresholds.csv`, `results/pi_proxy/`, `results/m_sensitivity/` に照合。TinS 投稿規定（Abstract ≤ 250 語、Highlights 3–5 点・各 ≤ 85 字、double-anonymized、編集可能ファイル）は `check_front_matter` で強制。

## 1. 原稿（新規性・論理・方法・結論整合）

| 指摘 | 致命度 | 修正効果 | 実行可能性 | 対応 |
|---|---|---|---|---|
| §6.5 が「引き抜きは field に損」と述べるが、引き抜き側**自身**が損をする条件（γ 閾値の φ・ホスト・指標依存）を数値で示していない。政策含意として片手落ち | 中 | 高（TinS の policy 志向に直結） | 既存 `gamma_thresholds.csv` のみで可 | **対応済み**: §6.5 に 1 段落追加。focal_hosted_hits の γ* が φ↑で低下（China-centred 4.5→1.5、US は φ=4,8 のみ 5.4/3.0）、field_PI_total の γ* はそれより十分小、の順序をビルド側で CSV から生成。「γ 未同定」「様式化仮定（Table S8）」「単一閾値ではない」「国際採用一般が有害という主張ではない」を同段落で明示 |
| §6.1 「P1 is supported」— §2.6 では P1 を診断的含意（検定対象ではない）と位置づけており矛盾 | 中 | 中 | 文言のみ | **対応済み**: 「consistent with … a diagnostic reading rather than a test」に修正 |
| §6.1 P3 「every macro-region で I0 が最近接」— §5.5 の M 感度で Other Western (Israel) は M×1.25 以上で d に切替わるのに Discussion が触れていない（言わなさすぎ） | 中 | 中 | 文言のみ（`ms_lever_changes` から生成） | **対応済み**: P3 の直後に M 感度による限定を追加し、「観測スケールでの結論、一般法則ではない」と明記 |
| §6.3 「the macro-regional ladder in Figure 10」— Fig. 10 はドミナント戦略の時間経路図で、ラダーは Fig. 7 | 低（誤参照は査読で必ず指摘） | 中 | 文言のみ | **対応済み**: Figure 7 |
| §6.4 「the gap … is growing」は 2 期比較（1 回の差分）から成長トレンドを述べており言い過ぎ | 低 | 中 | 文言のみ | **対応済み**: 「the macro-regions are not drifting in the same direction」 |
| Abstract/Conclusion の「test four propositions」— P1 は検定でないため「examine」に | 低 | 低 | 文言のみ | **対応済み** |
| §5.5 の PI proxy スナップショット 719,173 著者 vs Table 1 の 723,647 著者の不一致が未説明 | 中（数値不整合として指摘される） | 中 | 文言のみ | **対応済み**: 「later OpenAlex snapshot… difference reflects OpenAlex updates to author/affiliation records」を本文に明記。両数値は `data/cohort/cohort.csv` と `results/pi_proxy/pi_proxy_snapshot.csv` に由来 |

## 2. 統計・モデル設計
- 追加解析なし。γ の閾値は 0–6 の探索範囲内で二分法／走査により求めた**シミュレーション出力**であり、信頼区間を持たない（ブートストラップ遷移率を結合 ODE に流す感度は今後の課題）。本文でその旨を明示。
- 因果表現の点検: OpenAlex 由来の遷移率・弾性・PNR は「model diagnostics / mechanical counterfactuals」、ドミナント戦略は「simulation / model-consistent projection」と表記されていることを全文 grep で確認（「causes」「leads to」の実証部分での使用なし）。

## 3. 図表
- 本文 Fig. 1–10・Table 1–9 は全て初出順・初出段落直後にインライン、キャプション番号と一致（`check_manuscript.py` 合格）。Supplementary Fig. S1–S3・Table S1–S12 も同様。
- 新段落は既存 Fig. 9(d)・Table 8 の γ* 列を参照するのみで新規図表なし。

## 4. 再現性
- 全数値は `results/*.csv` → `build_full_manuscript.py`。新段落の数値も `compute_dominant_context()` から。
- `bash reproduce.sh`（通常経路）を本ブランチで実行し、結果 CSV・本文 md が一致することを確認（下記ログ）。公開リポ（sync ブランチ）のクリーンクローンでも再実行。

## 5. 主張の強さ・ジャーナル適合
- TinS 規定: Abstract 247 語、Highlights 5 点（最長 85 字）、Vancouver 出現順 52 文献（全件 DOI/URL で実在確認済み、Supplementary/README に記載）、blinded 版 docx、編集可能 pptx・docx、PNG+TIFF。
- 数式は全て Word ネイティブ OMML（docx→pandoc md 変換で `$…$` として現れることで確認；docx 内に生の LaTeX 文字列なし）。
- 非 ASCII 文字: 本文に CJK・全角文字なし。残るのは数学記号（α β γ φ τ ρ Δ ε ≈ ≤ × − ∈）・タイポグラフィ（– —）・参考文献の著者名の発音区別符号（Å í）のみで、いずれも TinS が許容する範囲。`check_manuscript.py` が一覧を出力し、CJK/全角が混入すれば失敗する。

## 6. 残課題（任意・次回改稿）
- 結合 ODE への遷移率ブートストラップ伝播（γ* の区間推定）。
- γ の直接推定（地域多様性と field 産出の観測関係）— データ外。
- 飽和 ε グリッド・r キャップ感度（第 2 回 §2）。

---

# 第5回レビュー（外部評価への対応：概念的限定・規範的語彙・TinS 適合）

外部評価（ChatGPT）が挙げた 3 つの残存査読リスクと Abstract 提案を、本文・データに照らして再評価した。

| 指摘 | 致命度 | 修正効果 | 実行可能性 | 対応 |
|---|---|---|---|---|
| 「地理的多様性 = research variety」— モデルが観測するのは research-system geography であり research programme の差ではない。§6.4 の「problem framings, benchmarks, data leave the field's menu」は観測より先に進んでいる | 中（TinS の社会理論寄りの査読者は指摘し得るが、制度・言語・技術軌道の差を論じること自体は同誌では自然） | 中 | 文言のみ | **対応済み**: §6.4 を「whatever distinct problem framings, benchmarks and data it carried … with no route back in the model」と限定。§6.6 Limitations に「macro-region が異なる制度・言語・資金を持つことは文献で裏付けられるが、異なる research programme を担うことは本研究では**仮定であって測定していない**」を追記 |
| Huntington 区分への依存 | 低（現行の「documented starting heuristic / operational research systems, not civilisations」で防御済み） | 低 | — | **維持**（ユーザー判断）。cover letter では Huntington に一切触れない（現状も言及なし）ことを確認 |
| 「irreversible / for good / dead end / point of no return」— 不可逆性は collapse rule というモデル仮定であり、実社会の Israel・日本が M を割れば永久に復活不能という経験的主張ではない | 中（規範的語彙を読む査読者） | 中 | 文言のみ | **対応済み**: Abstract・§1・§2.1・cover letter・Highlight の「irreversible」を「lasting」または「self-reinforcing rather than recoverable」に、§5.8 と §6.4 の「for good」を「under the collapse rule / with no route back in the model」に、§6.5 の「irreversible one」を「one that the model treats as irreversible」に変更。§6.6 に「不可逆性は collapse rule の性質であり経験的知見ではない。PNR は fitted feedback loop がプールを維持しなくなる閾値を指し、回復不能の予測ではない」を追記。「evolutionary dead end」（§6.2 見出し・§6.4・§7）は、field スケールでの variety 損失というメカニズム上の含意として維持（毎回「the mechanism identifies as」「at the scale of the field」で限定されている） |
| Abstract 末尾を societal technology governance に接続（「AI research capacity itself is a sociotechnical infrastructure」） | — | 中（editor が Abstract のみで TinS 適合を判断する場面） | 文言のみ | **対応済み**: Abstract 末尾を「Treating AI research capacity as a sociotechnical infrastructure rather than a national asset, …」に変更（250 語以内を `check_front_matter` で強制）。cover letter の fit 段落も同じ枕で書き換え、「tests」→「examines」 |
| タイトル「next coal」 | — | — | — | 変更なし |

数値・図表・結果 CSV に変更はなく、文言のみの改稿。機械的チェック（図表順・OMML・非 CJK・文献数）は再実行して合格を確認。

---

# 第6回レビュー（外部評価への対応：ゲーム理論用語・Conclusion の限定）

| 指摘 | 致命度 | 修正効果 | 実行可能性 | 対応 |
|---|---|---|---|---|
| 「dominant strategy」はゲーム理論では「相手の行動にかかわらず最適」という厳密な意味を持ち、本稿はそれを証明していない | 中（理論系査読者からの不要な攻撃点） | 中 | 即時（文言のみ） | §4.5・§5.8・Fig. 10 キャプション・§6.5・§7 の「dominant strategy」を「(stylised / aggressive) talent-concentration strategy」「individually advantageous」に置換。Fig. 10 の図内タイトルも `src/dominant_strategy.py` で同様に変更し再生成。結果 CSV のファイル名（`results/dominant_strategy/`）とモジュール名は互換性のため維持 |
| Conclusion「the field loses variety at once」「a dead end」が §6.6 の「地理は認知的多様性の代理」「γ 未同定」と比べて強い | 低〜中 | 中 | 即時 | 「loses macro-regional variety」「can become … an evolutionary dead end」に限定 |

数値・結果 CSV に変更はなく、Fig. 10 は図内タイトルの文言のみ変更。機械的チェックは再実行して合格。
