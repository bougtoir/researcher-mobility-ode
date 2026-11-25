#!/usr/bin/env python3
"""Regression tests for the R1 delta repairs.

Coverage:
  A. Scenario interpretation (Repair A): canonical dominant_strategy outputs
     must imply the direction stated in the manuscript - US-led concentration
     raises terminal field hit stock at gamma=0, the Sinic-centred scenario is
     already below baseline at gamma=0; gamma* is a terminal-value criterion.
  B. PPTX table mapping (Repair B): _equilibrium_table_pptx produces an
     explicit column-name mapping, is invariant to input column order, fails
     on missing columns, and every rendered PPTX table cell reconciles with
     canonical CSVs.

Run: python scripts/pptx_table_regression.py [--pptx docs/JOI_R1_FIGURES_EDITABLE.pptx]
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "src"))

DOM = REPO / "results" / "dominant_strategy"
RESULTS = REPO / "results"

failures = []


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}" + (f" - {detail}" if detail else ""))
    if not cond:
        failures.append(name)


def test_scenario_interpretation():
    summ = pd.read_csv(DOM / "summary.csv")
    th = pd.read_csv(DOM / "gamma_thresholds.csv")
    g0 = summ[(summ["exogenous_share"] == "fitted") & (summ["host_recruits"] == True)  # noqa: E712
              & (summ["gamma"] == 0.0) & (summ["phi"] > 0)]
    us = g0[g0["focal"] == "United States"].set_index("phi")["field_hits_terminal_relative"]
    sn = g0[g0["focal"] == "Sinic"].set_index("phi")["field_hits_terminal_relative"]
    check("A1 US gamma=0 terminal field hit stock rises for every pull", (us > 1.0).all(),
          f"min={us.min():.4f}")
    check("A2 Sinic gamma=0 terminal field hit stock below baseline for every pull", (sn < 1.0).all(),
          f"max={sn.max():.4f} (displays 1.00 after rounding at the two weakest pulls)")
    tf_us = th[(th["focal"] == "United States") & (th["metric"] == "field_hits_total")].set_index("phi")["gamma_threshold"]
    tf_sn = th[(th["focal"] == "Sinic") & (th["metric"] == "field_hits_total")].set_index("phi")["gamma_threshold"]
    check("A3 US gamma*field not reached at weakest pull", pd.isna(tf_us.loc[0.5]))
    check("A4 US gamma*field decreases with pull", tf_us.dropna().is_monotonic_decreasing,
          str(dict(tf_us.dropna())))
    check("A5 Sinic gamma*field = 0 (already below at fitted gamma)", (tf_sn == 0).all())
    ts_us = th[(th["focal"] == "United States") & (th["metric"] == "focal_hosted_hits")].set_index("phi")["gamma_threshold"]
    ts_sn = th[(th["focal"] == "Sinic") & (th["metric"] == "focal_hosted_hits")].set_index("phi")["gamma_threshold"]
    check("A6 US gamma*dominant reached only at the strongest pull", ts_us.dropna().index.tolist() == [8.0])
    check("A7 Sinic gamma*dominant reached at every pull", len(ts_sn.dropna()) == 5)
    check("A8 gamma* is a terminal criterion (US field never dips below baseline at gamma=0)",
          g0[g0["focal"] == "United States"]["year_field_hits_below_baseline"].isna().all())
    # Manuscript direction guard: rebuilt docx must not contain the old reversal.
    md = REPO / "docs" / "JOI_R1_MANUSCRIPT.md"
    if md.exists():
        txt = md.read_text()
        bad = "declines even at $\\gamma\\  = \\ 0$\nfor the United States" in txt or "declines even at gamma = 0 for the United States" in txt
        check("A9 manuscript does not state field hit stock declines at gamma=0 for the US", not bad)


def test_equilibrium_table():
    from build_full_manuscript import _equilibrium_table_pptx, _fmt
    eq = pd.read_csv(RESULTS / "endogenous" / "equilibrium_summary.csv")
    tbl = _equilibrium_table_pptx(eq)
    # full-cell reconciliation against canonical values
    canon = eq.set_index("group")
    ok = True
    bad = []
    for _, r in tbl.iterrows():
        g = r["Group"]
        exp = {
            "T_eq": _fmt(canon.loc[g, "T_equilibrium"], 0),
            "M": _fmt(canon.loc[g, "M_threshold"], 0),
            "Margin": _fmt(canon.loc[g, "margin_to_threshold_T"], 0),
            "T/M": _fmt(canon.loc[g, "T_equilibrium"] / canon.loc[g, "M_threshold"], 2),
            "I0": _fmt(canon.loc[g, "I0"], 0),
            "r": _fmt(canon.loc[g, "r"], 5),
            "r_obs": _fmt(canon.loc[g, "r_obs"], 5),
            "r_crit": _fmt(canon.loc[g, "r_critical"], 5),
        }
        for col, want in exp.items():
            if str(r[col]) != str(want):
                ok = False
                bad.append(f"{g}.{col}: got {r[col]} want {want}")
    check("B1 Table 2 full-cell reconciliation (9 regions x 9 cols)", ok, "; ".join(bad[:4]))
    # column-order permutation invariance
    perm = eq[list(reversed(eq.columns))]
    tbl2 = _equilibrium_table_pptx(perm)
    check("B2 column-order permutation invariance", tbl2.equals(tbl))
    # missing-column failure
    try:
        _equilibrium_table_pptx(eq.drop(columns=["r_critical"]))
        check("B3 missing required column raises", False, "no error raised")
    except KeyError as e:
        check("B3 missing required column raises", "r_critical" in str(e), str(e)[:60])


def test_pptx_cells(pptx_path):
    from pptx import Presentation
    from build_full_manuscript import _fmt
    prs = Presentation(pptx_path)
    tables = {}
    for i, slide in enumerate(prs.slides):
        title = ""
        if slide.shapes.title is not None:
            title = slide.shapes.title.text
        for shape in slide.shapes:
            if shape.has_table:
                tbl = shape.table
                rows = [[c.text for c in row.cells] for row in tbl.rows]
                tables[title or f"slide{i}"] = rows
    check("B4 PPTX contains table slides", len(tables) >= 8, f"{len(tables)} tables: {list(tables)[:4]}")
    # Table 2 reconciliation cell-by-cell (header + 9 regions)
    eq = pd.read_csv(RESULTS / "endogenous" / "equilibrium_summary.csv")
    from build_full_manuscript import _equilibrium_table_pptx, _apply_display_names
    want = _equilibrium_table_pptx(_apply_display_names(eq))
    t2 = tables.get("Table 2: Equilibrium and inflow parameters")
    check("B5 Table 2 slide exists", t2 is not None)
    if t2:
        check("B6 Table 2 header matches", t2[0] == want.columns.tolist(), str(t2[0]))
        got = {r[0]: r for r in t2[1:]}
        mism = []
        for _, r in want.iterrows():
            g = r["Group"]
            if g not in got:
                mism.append(f"missing row {g}")
                continue
            for j, col in enumerate(want.columns):
                if got[g][j] != str(r[col]):
                    mism.append(f"{g}.{col}: {got[g][j]} != {r[col]}")
        check("B7 Table 2 all cells match canonical", not mism, "; ".join(mism[:4]))
    # Table 8 reconciliation vs canonical scenario outputs
    t8 = tables.get("Table 8: Talent-concentration scenario at the end of the horizon (fitted rates, γ = 0)")
    check("B8 Table 8 slide exists", t8 is not None)
    if t8:
        summ = pd.read_csv(DOM / "summary.csv")
        th = pd.read_csv(DOM / "gamma_thresholds.csv")
        mism = []
        disp = {"United States": "United States", "Sinic": "Sinic"}
        for row in t8[1:]:
            focal_label, phi = row[0], float(row[1])
            focal = {"United States": "United States", "China-centred": "Sinic"}.get(focal_label, focal_label)
            g0 = summ[(summ["focal"] == focal) & (summ["exogenous_share"] == "fitted")
                      & (summ["host_recruits"] == True) & (summ["gamma"] == 0.0) & (summ["phi"] == phi)]  # noqa: E712
            if g0.empty:
                mism.append(f"{focal_label} phi={phi}: no canonical row")
                continue
            r = g0.iloc[0]
            if row[2] != _fmt(r["terminal_relative_hosted_pool"], 2):
                mism.append(f"{focal_label}@{phi} hosted pool {row[2]} != {_fmt(r['terminal_relative_hosted_pool'], 2)}")
            if row[6] != _fmt(r["field_hits_terminal_relative"], 2):
                mism.append(f"{focal_label}@{phi} field hits {row[6]} != {_fmt(r['field_hits_terminal_relative'], 2)}")
        check("B9 Table 8 hosted-pool and field-hit cells match canonical", not mism, "; ".join(mism[:4]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pptx", default=str(REPO / "docs" / "JOI_R1_FIGURES_EDITABLE.pptx"))
    args = ap.parse_args()
    test_scenario_interpretation()
    test_equilibrium_table()
    if Path(args.pptx).exists():
        test_pptx_cells(args.pptx)
    else:
        print(f"[SKIP] PPTX not found: {args.pptx}")
    print(f"\n{len(failures)} failure(s)" + (f": {failures}" if failures else ""))
    sys.exit(1 if failures else 0)
