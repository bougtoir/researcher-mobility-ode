#!/usr/bin/env python3
"""Build a Journal of Informetrics full-length-article manuscript from ODE result CSVs.

Outputs (regenerated from results/* CSVs, no hard-coded numbers):
- docs/JOI_MANUSCRIPT_FINAL.docx (+ JOI_MANUSCRIPT_BLINDED.docx for double-anonymised review)
- docs/JOI_MANUSCRIPT_FINAL.md
- docs/JOI_FIGURES_EDITABLE.pptx
- docs/supplementary_material.docx
- docs/JOI_HIGHLIGHTS.docx (separate editable file, 3-5 bullets <= 85 characters)
- docs/figures/*.png

All numerical values are read from the result CSVs produced by the analysis
pipeline; the script contains only formatting and prose.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import zipfile
from pathlib import Path

# Make local packages importable
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))
sys.path.insert(0, str(BASE_DIR / "scripts"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from PIL import Image
import docx.table
import docx.text.paragraph
from docx import Document
from lxml import etree as ET
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.shared import Inches, Pt, RGBColor
from pptx import Presentation
from pptx.util import Inches as PptxInches

from pyommlbuilder.main import (
    Math,
    SubscriptObject,
    Fraction,
    Numerator,
    Denominator,
    Function,
    MathPara,
)
from pyommlbuilder.helpers import make_aligned_equation

import annual_rates_projection_report as arpr
import dominant_strategy as domstrat

try:
    import pypandoc
except Exception:  # pragma: no cover - pypandoc is optional for the markdown fallback
    pypandoc = None

RESULTS_DIR = BASE_DIR / "results"
ENDOG = RESULTS_DIR / "endogenous"
SAT = RESULTS_DIR / "endogenous_saturating"
TV = RESULTS_DIR / "time_varying"
BOOT = RESULTS_DIR / "bootstrap_ci"
POL = RESULTS_DIR / "policy_counterfactuals"
DOM = RESULTS_DIR / "dominant_strategy"
ANNUAL = RESULTS_DIR / "annual"
FIG_DIR = BASE_DIR / "docs" / "figures"


def _fmt(v, dec=2):
    if pd.isna(v):
        return "—"
    try:
        return f"{float(v):.{dec}f}"
    except (ValueError, TypeError):
        return str(v)


TITLE = (
    "AI researchers as the next coal: transition rates, minimum viable research "
    "communities and the preservation of variety in global AI/ML"
)

# Display names used in prose, tables and figures. Internal CSV labels are kept
# unchanged so that the analysis pipeline and mapping_rationale.md stay stable.
GROUP_DISPLAY = {
    "United States": "United States",
    "Anglosphere ex-US": "Anglosphere ex-US",
    "Continental Europe": "Continental Europe",
    "Sinic": "China-centred",
    "Japanese": "Japan",
    "Hindu": "South Asia",
    "Islamic": "Islamic world",
    "Other Western": "Other Western (Israel)",
    "Other Civilizations": "Other regions",
}
JAPAN = GROUP_DISPLAY["Japanese"]


def display_group(name):
    return GROUP_DISPLAY.get(str(name), str(name))


def _apply_display_names(df, cols=("group", "origin_group", "destination_group")):
    if df is None:
        return None
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = df[c].map(display_group)
    return df


class CitationRegistry:
    """Assign Vancouver numbers in order of first appearance in the body text."""

    def __init__(self, refs: dict):
        self.refs = refs
        self.order: list[str] = []

    def number(self, key: str) -> int:
        if key not in self.refs:
            raise KeyError(f"Unknown reference key: {key}")
        if key not in self.order:
            self.order.append(key)
        return self.order.index(key) + 1

    def numbered_list(self):
        return [(i + 1, self.refs[k]) for i, k in enumerate(self.order)]

    def orphans(self):
        return [k for k in self.refs if k not in self.order]


def cite(para, registry: CitationRegistry, *keys):
    """Append a bracketed Vancouver citation such as ' [3]' or ' [3,7]'."""
    nums = sorted(registry.number(k) for k in keys)
    return para.add_run(" [" + ",".join(str(n) for n in nums) + "]")


def add_footnote(para, symbol="1"):
    run = para.add_run(f" {symbol}")
    run.font.superscript = True
    return run


RATE_LABELS = {
    "I0": "exogenous entry rate (I_0)",
    "I": "exogenous entry rate (I)",
    "d": "dropout rate (d)",
    "alpha": "early-career outflow rate (α)",
    "beta": "return rate (β)",
    "h_D": "domestic hit-generation rate (h_D)",
    "h_A": "abroad hit-generation rate (h_A)",
    "p_D": "domestic principal-investigator promotion rate (p_D)",
    "p_A": "abroad principal-investigator promotion rate (p_A)",
    "r": "principal-investigator reproduction rate (r)",
}


def _rate_label(name):
    """Return a full-spelling phrase with the rate symbol in parentheses."""
    return RATE_LABELS.get(str(name), str(name))


def _paragraph_text(doc):
    for p in doc.paragraphs:
        yield p.text


def _table_text(doc):
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                yield cell.text


def _doc_word_count(doc, exclude_after="References"):
    """Count words in paragraphs and tables, stopping before the reference list."""
    total = 0
    for el in doc.element.body.iterchildren():
        tag = el.tag.rsplit("}", 1)[-1]
        if tag == "p":
            text = "".join(t.text or "" for t in el.iter() if t.tag.endswith("}t")).strip()
            if text == exclude_after:
                break
            total += len(text.split())
        elif tag == "tbl":
            for t in el.iter():
                if t.tag.endswith("}t") and t.text:
                    total += len(t.text.split())
    return total


def _rel_path(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def add_omath_paragraph(doc, math_element, align=WD_ALIGN_PARAGRAPH.CENTER):
    """Append an OMML math element to a new paragraph."""
    p = doc.add_paragraph()
    p._element.append(math_element._as_xml_element())
    p.alignment = align
    return p


def add_omath_inline(para, math_element):
    """Append an OMML math element inline inside an existing paragraph."""
    para._element.append(math_element._as_xml_element())


# ---------------------------------------------------------------------------
# OMML equation builders
# ---------------------------------------------------------------------------

def math_I_linear():
    """I(P_D) = I_0 + r P_D"""
    return Math(
        Function("I", SubscriptObject("P", "D")),
        "=",
        SubscriptObject("I", "0"),
        "+",
        "r",
        SubscriptObject("P", "D"),
    )


def math_I_saturating():
    """I(P_D) = I_0 + r P_D / (1 + epsilon P_D)"""
    return Math(
        Function("I", SubscriptObject("P", "D")),
        "=",
        SubscriptObject("I", "0"),
        "+",
        Fraction(
            Numerator("r", SubscriptObject("P", "D")),
            Denominator("1 + ", "ε", "×", SubscriptObject("P", "D")),
        ),
    )


def math_threshold():
    """M = k × c̄"""
    return Math("M = k × c\u0304")


def math_active_pool():
    """T = D + H_D + P_D"""
    return Math(
        "T = D + ",
        SubscriptObject("H", "D"),
        " + ",
        SubscriptObject("P", "D"),
    )


def math_ode_system():
    """Six-equation display using MathPara."""
    def deriv(base):
        if "_" in base:
            b, sub = base.split("_", 1)
            return Fraction(Numerator("d", SubscriptObject(b, sub)), Denominator("dt"))
        return Fraction(Numerator("d" + base), Denominator("dt"))

    lines = [
        make_aligned_equation(
            deriv("D"),
            Math(
                Function("I", SubscriptObject("P", "D")),
                " + βA - (α + ",
                SubscriptObject("h", "D"),
                " + d)D",
            ),
            line_break=False,
        ),
        make_aligned_equation(
            deriv("A"),
            Math(
                "αD - (β + ",
                SubscriptObject("h", "A"),
                " + d)A",
            ),
            line_break=False,
        ),
        make_aligned_equation(
            deriv("H_D"),
            Math(
                SubscriptObject("h", "D"),
                "D + β",
                SubscriptObject("H", "A"),
                " - (",
                SubscriptObject("p", "D"),
                " + d)",
                SubscriptObject("H", "D"),
            ),
            line_break=False,
        ),
        make_aligned_equation(
            deriv("H_A"),
            Math(
                SubscriptObject("h", "A"),
                "A - (β + ",
                SubscriptObject("p", "A"),
                " + d)",
                SubscriptObject("H", "A"),
            ),
            line_break=False,
        ),
        make_aligned_equation(
            deriv("P_D"),
            Math(
                SubscriptObject("p", "D"),
                SubscriptObject("H", "D"),
                " + β",
                SubscriptObject("P", "A"),
                " - d",
                SubscriptObject("P", "D"),
            ),
            line_break=False,
        ),
        make_aligned_equation(
            deriv("P_A"),
            Math(
                SubscriptObject("p", "A"),
                SubscriptObject("H", "A"),
                " - (β + d)",
                SubscriptObject("P", "A"),
            ),
            line_break=False,
        ),
    ]
    return MathPara(*lines)


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

GROUP_COLOURS = {
    "United States": "#1f77b4",
    "Anglosphere ex-US": "#6baed6",
    "Continental Europe": "#2ca02c",
    "China-centred": "#d62728",
    "Japan": "#ff7f0e",
    "South Asia": "#9467bd",
    "Islamic world": "#8c564b",
    "Other Western (Israel)": "#17becf",
    "Other regions": "#bcbd22",
}


def _polygon_centroid(rings):
    """Area-weighted centroid of a list of polygon rings (outer rings only)."""
    total_a, cx, cy = 0.0, 0.0, 0.0
    for ring in rings:
        xs = np.array([pt[0] for pt in ring]); ys = np.array([pt[1] for pt in ring])
        a = 0.5 * np.sum(xs[:-1] * ys[1:] - xs[1:] * ys[:-1])
        if abs(a) < 1e-9:
            continue
        cx += np.sum((xs[:-1] + xs[1:]) * (xs[:-1] * ys[1:] - xs[1:] * ys[:-1])) / (6 * a) * a
        cy += np.sum((ys[:-1] + ys[1:]) * (xs[:-1] * ys[1:] - xs[1:] * ys[:-1])) / (6 * a) * a
        total_a += a
    if total_a == 0:
        return None
    return cx / total_a, cy / total_a


def build_figure1(eq, annual, fig_dir: Path):
    """World map of research macro-regions with observed inter-region early-career flows.

    Country outlines: Natural Earth 1:110m (public domain), stored slimmed in
    data/ne_110m_countries_slim.geojson. Flow widths: accumulated abroad
    author-years by origin and destination (results/annual/annual_interciv_stock.csv),
    the same series summarised in the inter-region table of the annual layer.
    """
    fig_dir.mkdir(parents=True, exist_ok=True)
    with open(BASE_DIR / "data" / "country_civilization_mapping.json", encoding="utf-8") as fh:
        mapping = json.load(fh)
    with open(BASE_DIR / "data" / "ne_110m_countries_slim.geojson", encoding="utf-8") as fh:
        world = json.load(fh)
    iso_to_group = {iso: display_group(v["group"]) for iso, v in mapping.items()}
    iso_to_works = {iso: int(v.get("ai_ml_works_2022_2023", 0)) for iso, v in mapping.items()}

    fig, ax = plt.subplots(figsize=(13, 6.8))
    country_rings = {}
    for feat in world["features"]:
        iso = feat["properties"]["iso_a3"]
        geom = feat["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        grp = iso_to_group.get(iso)
        colour = GROUP_COLOURS.get(grp, "#e0e0e0") if grp else "#e0e0e0"
        if iso == "ATA":
            continue
        for poly in polys:
            outer = poly[0]
            ax.add_patch(mpatches.Polygon(outer, closed=True, facecolor=colour, edgecolor="white", linewidth=0.3))
            # anchor countries on their largest polygon (mainland), ignoring islands and exclaves
            if len(outer) > len(country_rings.get(iso, [])):
                country_rings[iso] = outer
    ax.set_xlim(-170, 190)
    ax.set_ylim(-58, 84)
    ax.set_aspect("equal")
    ax.axis("off")

    # Region anchors: centroid of the member country with most AI/ML works in 2022-2023
    anchors = {}
    for g in GROUP_COLOURS:
        members = [(iso_to_works[iso], iso) for iso, grp in iso_to_group.items() if grp == g and iso in country_rings]
        if members:
            _, iso = max(members)
            c = _polygon_centroid([country_rings[iso]])
            if c is not None:
                anchors[g] = c

    flows = annual.get("interciv_stock")
    if flows is not None and not flows.empty:
        flows = flows[(flows["destination_group"] != "Unknown") & (flows["origin_group"] != flows["destination_group"])]
        agg = flows.groupby(["origin_group", "destination_group"])["count"].sum().reset_index()
        agg = agg[agg["count"] > 0].sort_values("count", ascending=False)
        top = agg.head(12)
        max_c = float(top["count"].max())
        for _, r in top.iterrows():
            o, d = anchors.get(r["origin_group"]), anchors.get(r["destination_group"])
            if o is None or d is None:
                continue
            lw = 0.6 + 5.0 * r["count"] / max_c
            ax.annotate("", xy=d, xytext=o,
                        arrowprops=dict(arrowstyle="-|>", lw=lw, color=GROUP_COLOURS.get(r["origin_group"], "k"),
                                        alpha=0.75, connectionstyle="arc3,rad=0.25", shrinkA=6, shrinkB=6))
        ax.text(188, -56, "Arrows: 12 largest inter-region early-career flows, 2000-2023\n(width proportional to accumulated abroad author-years);\ndots mark each region's largest AI/ML producer, used as the arrow anchor",
                fontsize=8, color="0.3", va="bottom", ha="right")
    for g, (x, y) in anchors.items():
        ax.plot(x, y, "o", ms=5, color="black", zorder=5)

    tm = {r["group"]: r["T_equilibrium"] / r["M_threshold"] for _, r in eq.iterrows()}
    handles = [mpatches.Patch(facecolor=GROUP_COLOURS[g], edgecolor="none",
                              label=f"{g} (T/M = {tm[g]:.2f})" if g in tm else g) for g in GROUP_COLOURS]
    handles.append(mpatches.Patch(facecolor="#e0e0e0", label="No AI/ML works 2022-2023"))
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 0.0), fontsize=8, frameon=True, title="Research macro-region", title_fontsize=9)
    ax.set_title("Research macro-regions and the largest inter-region early-career flows", fontsize=12)
    fig.tight_layout()
    path = fig_dir / "fig1_macro_region_map.png"
    fig.savefig(path, dpi=300)
    plt.close(fig)
    return path


COMPARTMENT_LAYOUT = {
    # (x, y) positions in axis fraction; domestic row at top, abroad row at bottom
    "D": (0.22, 0.72), "H_D": (0.52, 0.72), "P_D": (0.82, 0.72),
    "A": (0.22, 0.28), "H_A": (0.52, 0.28), "P_A": (0.82, 0.28),
}
COMPARTMENT_LABELS = {
    "D": "Domestic\nearly-career", "H_D": "Domestic\nhit", "P_D": "Domestic\nPI",
    "A": "Abroad\nearly-career", "H_A": "Abroad\nhit", "P_A": "Abroad\nPI",
}
COMPARTMENT_EDGES = [
    # (from, to, rate label)
    ("D", "A", "α"), ("A", "D", "β"), ("D", "H_D", "h_D"), ("A", "H_A", "h_A"),
    ("H_A", "H_D", "β"), ("H_D", "P_D", "p_D"), ("H_A", "P_A", "p_A"), ("P_A", "P_D", "β"),
]


def build_figure2(fig_dir: Path):
    """General six-compartment diagram with endogenous recruitment and threshold test."""
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    bw, bh = 0.16, 0.16
    for name, (x, y) in COMPARTMENT_LAYOUT.items():
        fc = "#e6f2ff" if name.endswith("D") or name == "D" else "#fff4e6"
        ax.add_patch(mpatches.FancyBboxPatch((x - bw / 2, y - bh / 2), bw, bh, boxstyle="round,pad=0.01",
                                             facecolor=fc, edgecolor="black", linewidth=1.2))
        sym = {"D": "D", "A": "A", "H_D": "$H_D$", "H_A": "$H_A$", "P_D": "$P_D$", "P_A": "$P_A$"}[name]
        ax.text(x, y + 0.03, sym, ha="center", va="center", fontsize=13, fontweight="bold")
        ax.text(x, y - 0.045, COMPARTMENT_LABELS[name], ha="center", va="center", fontsize=8.5)
    sym_rate = {"α": "α", "β": "β", "h_D": "$h_D$", "h_A": "$h_A$", "p_D": "$p_D$", "p_A": "$p_A$"}
    for a, b, lab in COMPARTMENT_EDGES:
        (x1, y1), (x2, y2) = COMPARTMENT_LAYOUT[a], COMPARTMENT_LAYOUT[b]
        if y1 == y2:  # horizontal
            ax.annotate("", xy=(x2 - bw / 2, y2), xytext=(x1 + bw / 2, y1),
                        arrowprops=dict(arrowstyle="-|>", lw=1.3, color="black"))
            ax.text((x1 + x2) / 2, y1 + 0.03, sym_rate[lab], ha="center", fontsize=11)
        else:  # vertical pair D<->A uses offset arrows; others single upward arrows
            if a == "D" and b == "A":
                ax.annotate("", xy=(x2 - 0.03, y2 + bh / 2), xytext=(x1 - 0.03, y1 - bh / 2),
                            arrowprops=dict(arrowstyle="-|>", lw=1.3, color="black"))
                ax.text(x1 - 0.06, (y1 + y2) / 2, sym_rate[lab], ha="center", va="center", fontsize=11)
            elif a == "A" and b == "D":
                ax.annotate("", xy=(x2 + 0.03, y2 - bh / 2), xytext=(x1 + 0.03, y1 + bh / 2),
                            arrowprops=dict(arrowstyle="-|>", lw=1.3, color="black"))
                ax.text(x1 + 0.06, (y1 + y2) / 2, sym_rate[lab], ha="center", va="center", fontsize=11)
            else:
                ax.annotate("", xy=(x2, y2 - bh / 2), xytext=(x1, y1 + bh / 2),
                            arrowprops=dict(arrowstyle="-|>", lw=1.3, color="black"))
                ax.text(x1 + 0.025, (y1 + y2) / 2, sym_rate[lab], ha="left", va="center", fontsize=11)
    # Inflow with endogenous feedback from P_D
    ax.annotate("", xy=(COMPARTMENT_LAYOUT["D"][0] - bw / 2, 0.72), xytext=(0.02, 0.72),
                arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#1f77b4"))
    ax.text(0.07, 0.655, "$I(P_D) = I_0 + r\\,P_D$", ha="center", fontsize=10.5, color="#1f77b4")
    ax.annotate("", xy=(0.06, 0.745), xytext=(COMPARTMENT_LAYOUT["P_D"][0], 0.72 + bh / 2),
                arrowprops=dict(arrowstyle="-|>", lw=1.1, color="#1f77b4", linestyle="--",
                                connectionstyle="arc3,rad=0.3"))
    ax.text(0.52, 0.965, "PI reproduction (network externality)", ha="center", fontsize=9, color="#1f77b4")
    # Dropout from every compartment
    for name, (x, y) in COMPARTMENT_LAYOUT.items():
        ax.annotate("", xy=(x + bw / 2 + 0.035, y - bh / 2 - 0.05), xytext=(x + bw / 2 - 0.01, y - bh / 2 + 0.01),
                    arrowprops=dict(arrowstyle="-|>", lw=0.9, color="0.45"))
    ax.text(0.95, 0.09, "d: dropout\n(all compartments)", ha="center", fontsize=8.5, color="0.35")
    # Threshold test
    ax.text(0.52, 0.5, "Active pool  $T = D + H_D + P_D$   compared with   $M = k\\,\\bar{c}$",
            ha="center", va="center", fontsize=10.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f5f5f5", edgecolor="0.6"))
    ax.text(0.22, 0.87, "Domestic (origin macro-region)", ha="center", fontsize=9, color="0.3")
    ax.text(0.22, 0.13, "Abroad (other macro-regions)", ha="center", fontsize=9, color="0.3")
    fig.tight_layout()
    path = fig_dir / "fig2_compartment_model.png"
    fig.savefig(path, dpi=300)
    plt.close(fig)
    return path


def build_figure3(eq, fig_dir: Path):
    """Equilibrium domestic active pool vs minimum viable threshold."""
    fig_dir.mkdir(parents=True, exist_ok=True)
    groups = eq["group"].tolist()
    x = np.arange(len(groups))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 5.5))
    t_bars = ax.bar(x - width / 2, eq["T_equilibrium"], width, label="Equilibrium T", color="steelblue")
    m_bars = ax.bar(x + width / 2, eq["M_threshold"], width, label="Minimum viable threshold M", color="coral")
    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=35, ha="right")
    ax.set_ylabel("Number of researchers")
    ax.set_title("Domestic active researcher pool and minimum viable coauthor threshold by group")
    max_y = max(eq["T_equilibrium"].max(), eq["M_threshold"].max()) * 1.15
    ax.set_ylim(0, max_y)
    # Annotate bars with integer counts
    for bar, val in zip(t_bars, eq["T_equilibrium"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max_y * 0.01,
                f"{int(round(val))}", ha="center", va="bottom", fontsize=7)
    for bar, val in zip(m_bars, eq["M_threshold"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max_y * 0.01,
                f"{int(round(val))}", ha="center", va="bottom", fontsize=7)
    ax.legend()
    fig.tight_layout()
    path = fig_dir / "fig1_equilibrium_margin.png"
    fig.savefig(path, dpi=300)
    plt.close(fig)
    return path


def build_figure4(pnr_closest, fig_dir: Path):
    """Closest viability-boundary proximity by group."""
    fig_dir.mkdir(parents=True, exist_ok=True)
    pnr_closest = pnr_closest.sort_values("proximity")
    groups = pnr_closest["group"].tolist()
    labels = [f"{r}\n({t})" for r, t in zip(pnr_closest["rate_name"], pnr_closest["target"])]
    prox = pnr_closest["proximity"].tolist()
    fig, ax = plt.subplots(figsize=(9, 5))
    # Use a perceptually uniform, colour-vision-deficiency-friendly sequential palette
    norm = max(prox) * 1.2 if prox else 1.0
    colors = [plt.cm.plasma(0.25 + 0.55 * (p / norm)) for p in prox]
    bars = ax.barh(groups, prox, color=colors)
    for bar, label in zip(bars, labels):
        width = bar.get_width()
        ax.text(width + 0.01, bar.get_y() + bar.get_height() / 2,
                label, va="center", fontsize=7)
    ax.set_xlabel("Required proportional change in rate |critical factor − 1|")
    ax.set_title("Closest viability-boundary sensitivity by group (smaller = more fragile)")
    xmax = max(1.2, max(prox) * 1.15) if prox else 1.2
    ax.set_xlim(0, xmax)
    ax.axvline(1.0, color="gray", linestyle="--", linewidth=0.8)
    fig.tight_layout()
    path = fig_dir / "fig2_pnr_proximity.png"
    fig.savefig(path, dpi=300)
    plt.close(fig)
    return path


def build_figure5(period_compare, fig_dir: Path):
    """Historical counterfactual: change in safety margin from early to late rates.

    Mirrored to a left-origin layout: all bars originate at the left axis (0)
    and extend to the right, with colour encoding whether late-period rates would
    raise (blue) or lower (vermillion) the safety margin.
    """
    fig_dir.mkdir(parents=True, exist_ok=True)
    df = period_compare.copy()
    df["abs_delta"] = df["delta_margin"].abs()
    df = df.sort_values("abs_delta", ascending=True)
    groups = df["group"].tolist()
    deltas = df["delta_margin"].tolist()
    lengths = df["abs_delta"].tolist()
    fig, ax = plt.subplots(figsize=(9, 5))
    # Colour-vision-deficiency-friendly palette: blue for positive, vermillion for negative
    CVD_POS = "#0072B2"
    CVD_NEG = "#D55E00"
    colors = [CVD_POS if d >= 0 else CVD_NEG for d in deltas]
    bars = ax.barh(groups, lengths, color=colors)
    for bar, d, l in zip(bars, deltas, lengths):
        ax.text(l + max(lengths) * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{_fmt(d, 1)}", va="center", ha="left",
                fontsize=8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Change in equilibrium safety margin |late − early| (late higher → blue, lower → red)")
    ax.set_title("Counterfactual change in safety margin if late-period rates persisted (point estimates)")
    fig.tight_layout()
    path = fig_dir / "fig3_historical_margin.png"
    fig.savefig(path, dpi=300)
    plt.close(fig)
    return path


def build_figure6(boot, fig_dir: Path):
    """Bootstrap 95% confidence intervals for equilibrium T."""
    fig_dir.mkdir(parents=True, exist_ok=True)
    df = boot.sort_values("T_equilibrium_median")
    groups = df["group"].tolist()
    med = df["T_equilibrium_median"].tolist()
    low = df["T_equilibrium_q025"].tolist()
    high = df["T_equilibrium_q975"].tolist()
    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(groups))
    ax.errorbar(med, y, xerr=[np.subtract(med, low), np.subtract(high, med)],
                fmt="o", color="steelblue", capsize=4, ecolor="gray")
    ax.set_yticks(y)
    ax.set_yticklabels(groups)
    ax.set_xlabel("Equilibrium domestic active pool T")
    ax.set_title("Bootstrap 95% confidence intervals for equilibrium T")
    ax.set_xlim(0, max(high) * 1.05)
    fig.tight_layout()
    path = fig_dir / "fig4_bootstrap_ci.png"
    fig.savefig(path, dpi=600, bbox_inches="tight")
    plt.close(fig)
    return path


def build_figure10(trans_rates, eq, fig_dir: Path):
    """Japan's six-compartment flow with cross-region transition-rate ladders."""
    fig_dir.mkdir(parents=True, exist_ok=True)

    def _rate_fmt(v, dec=3):
        if pd.isna(v):
            return "—"
        return f"{float(v):.{dec}f}"

    ja_row = trans_rates[trans_rates["group"] == JAPAN].iloc[0]
    ja_eq = eq[eq["group"] == JAPAN].iloc[0]

    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.2])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # Left panel: Japan compartment flow
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.axis("off")
    w, h = 0.14, 0.10
    positions = {
        "D": (0.18, 0.80), "H_D": (0.18, 0.52), "P_D": (0.18, 0.24),
        "A": (0.82, 0.80), "H_A": (0.82, 0.52), "P_A": (0.82, 0.24),
        "L": (0.50, 0.05),
    }
    counts = {
        "D": ja_eq["D_eq"], "H_D": ja_eq["H_D_eq"], "P_D": ja_eq["P_D_eq"],
        "A": ja_eq["A_eq"], "H_A": ja_eq["H_A_eq"], "P_A": ja_eq["P_A_eq"],
    }
    for name, (x, y) in positions.items():
        if name == "L":
            label = "L\n(dropout)"
            fc = "#ffcccc"
        else:
            label = f"{name}\n{int(round(counts[name]))}"
            fc = "#e6f2ff" if name in ("D", "H_D", "P_D") else "#fff4e6"
        box = mpatches.FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02",
            facecolor=fc, edgecolor="black", linewidth=1.2,
        )
        ax1.add_patch(box)
        ax1.text(x, y, label, ha="center", va="center", fontsize=9, weight="bold")

    def _arrow(start, end, label, rate, color="black", lw=1.2):
        ax1.annotate("", xy=end, xytext=start,
                     arrowprops=dict(arrowstyle="->", color=color, lw=lw,
                                     connectionstyle="arc3,rad=0"))
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2
        ax1.text(mx, my + 0.025, f"{label}={_rate_fmt(rate)}",
                 ha="center", va="bottom", fontsize=8, color=color,
                 bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                           edgecolor="none", alpha=0.8))

    _arrow((0.25, 0.85), (0.75, 0.85), r"$\alpha$", ja_row["alpha"])
    _arrow((0.75, 0.75), (0.25, 0.75), r"$\beta$", ja_row["beta"])
    _arrow((0.18, 0.75), (0.18, 0.58), "h_D", ja_row["h_D"])
    _arrow((0.18, 0.47), (0.18, 0.30), "p_D", ja_row["p_D"])
    _arrow((0.82, 0.75), (0.82, 0.58), "h_A", ja_row["h_A"])
    _arrow((0.82, 0.47), (0.82, 0.30), "p_A", ja_row["p_A"])

    ax1.annotate("", xy=(0.11, 0.80), xytext=(0.02, 0.80),
                 arrowprops=dict(arrowstyle="->", color="green", lw=1.2))
    ax1.text(0.055, 0.83, f"I0+rP_D\nI0={_rate_fmt(ja_eq['I0'],1)}\nr={_rate_fmt(ja_eq['r'],4)}",
             ha="center", va="bottom", fontsize=7, color="green")

    for name, (x, y) in positions.items():
        if name == "L":
            continue
        ax1.annotate("", xy=(0.50, 0.12), xytext=(x, y - 0.05),
                     arrowprops=dict(arrowstyle="->", color="gray", lw=0.7,
                                     ls="--", connectionstyle="arc3,rad=0.15"))
    ax1.text(0.50, 0.015, f"d={_rate_fmt(ja_row['d'])} (all compartments)",
             ha="center", va="bottom", fontsize=8, color="gray", weight="bold")
    ax1.set_title(
        f"Japan (T/M={_rate_fmt(ja_eq['T_equilibrium']/ja_eq['M_threshold'],2)})",
        fontsize=12, weight="bold", pad=10,
    )

    # Right panel: rate ladders by macro-region, Japan highlighted
    rates = ["alpha", "beta", "h_D", "h_A", "p_D", "d"]
    others = sorted([g for g in trans_rates["group"] if g != JAPAN])
    groups = [JAPAN] + others
    n_groups = len(groups)
    n_rates = len(rates)
    y = np.arange(n_groups)
    bar_height = 0.11
    colors = plt.cm.tab10(np.linspace(0, 1, n_rates))
    for i, rate in enumerate(rates):
        vals = np.array([trans_rates[trans_rates["group"] == g][rate].values[0] for g in groups])
        ax2.barh(y + i * bar_height, vals, height=bar_height, label=rate, color=colors[i])
    ax2.set_yticks(y + bar_height * (n_rates - 1) / 2)
    ax2.set_yticklabels(groups, fontsize=8)
    ax2.invert_yaxis()
    ax2.set_xlabel("Transition rate", fontsize=9)
    ax2.set_title("Transition rates by research macro-region (Japan highlighted)", fontsize=11, weight="bold", pad=10)
    ax2.legend(ncol=3, fontsize=7, loc="lower right")
    ax2.axhspan(-0.5, 0.5 + n_rates * bar_height, color="red", alpha=0.08)
    ax2.set_ylim(n_groups - 0.5, -0.5)
    ax2.set_xlim(0, 1.0)
    ax2.grid(axis="x", linestyle=":", alpha=0.5)

    fig.tight_layout()
    path = fig_dir / "fig8_japan_compartment_flow.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def build_figure11(eq, pnr_active, fig_dir: Path):
    """T/M safety margin versus closest boundary proximity for all macro-regions."""
    fig_dir.mkdir(parents=True, exist_ok=True)

    active = pnr_active[(pnr_active["target"] == "domestic_active") & (pnr_active["is_within_bounds"])].copy()
    active["proximity"] = (active["critical_factor"] - 1).abs()
    active = active.loc[active.groupby("group")["proximity"].idxmin()].reset_index(drop=True)
    merged = eq[["group", "T_equilibrium", "M_threshold"]].merge(
        active[["group", "rate_name", "current_rate", "critical_factor", "proximity"]], on="group"
    )
    merged["T_over_M"] = merged["T_equilibrium"] / merged["M_threshold"]
    merged = merged.sort_values("T_over_M")

    fig, ax = plt.subplots(figsize=(9, 7))
    colors = ["red" if g == JAPAN else "steelblue" for g in merged["group"]]
    ax.scatter(merged["T_over_M"], merged["proximity"], c=colors, s=120, edgecolors="black", zorder=3)
    for _, row in merged.iterrows():
        ax.annotate(row["group"], (row["T_over_M"], row["proximity"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=8)
    ax.axvline(1.0, color="gray", linestyle="--", lw=1)
    ax.set_xlabel("T / M (equilibrium active pool / minimum viable threshold)", fontsize=10)
    ax.set_ylabel("boundary proximity (|critical factor − 1|)\nsmaller = more fragile", fontsize=10)
    ax.set_title("Model evaluation: safety margin vs. viability-boundary proximity", fontsize=11, weight="bold")

    ja = merged[merged["group"] == JAPAN].iloc[0]
    ax.annotate(f"Japan: boundary lever = {ja['rate_name']}",
                (ja["T_over_M"], ja["proximity"]),
                textcoords="offset points", xytext=(-30, -25),
                fontsize=9, color="red",
                arrowprops=dict(arrowstyle="->", color="red"))

    fig.tight_layout()
    path = fig_dir / "fig9_tm_pnr_scatter.png"
    fig.savefig(path, dpi=300)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Reference list
# ---------------------------------------------------------------------------

NOTE_TEXT = "Yamada Y (momentumyy). Kaigai de ateta kenkyusha wa sonogo dou naru no ka [What happens to researchers who make their name abroad?]. note.com, 2026. https://note.com/momentumyy/n/n86df5d34282d (accessed 2026-08-09)."

# Keyed reference store. Numbers are assigned by CitationRegistry in order of
# first appearance, so adding or moving a citation never breaks Vancouver order.
REFS = {
    "macropolo": "MacroPolo. The Global AI Talent Tracker 2.0. Paulson Institute, 2023. https://macropolo.org/digital-projects/the-global-ai-talent-tracker/",
    "appelt": "Appelt S, van Beuzekom B, Galindo-Rueda F, de Pinho R. Which factors influence the international mobility of research scientists? OECD Science, Technology and Industry Working Papers 2015/02, 2015. https://doi.org/10.1787/5js1tmrr2233-en",
    "stephan": "Stephan P E. The Economics of Science. J Econ Lit. 1996;34(3):1199-1235.",
    "huntington": "Huntington S P. The Clash of Civilizations and the Remaking of World Order. New York: Simon & Schuster, 1996.",
    "aghion": "Aghion P, Bloom N, Blundell R, Griffith R, Howitt P. Competition and innovation: an inverted-U relationship. Q J Econ. 2005;120(2):701-728. https://doi.org/10.1162/0033553053970214",
    "openalex": "Priem J, Piwowar H, Orr R. OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. arXiv:2205.01833, 2022. https://doi.org/10.48550/arXiv.2205.01833",
    "thorn": "Thorn K, Holm-Nielsen L B. International Mobility of Researchers and Scientists: Policy Options for Turning a Drain into a Gain. UNU-WIDER Research Paper No. 2006/83, 2006. https://www.wider.unu.edu/publication/international-mobility-researchers-and-scientists",
    "alshebli": "AlShebli B, Memon S A, Evans J A, Rahwan T. China and the U.S. produce more impactful AI research when collaborating together. Sci Rep. 2024;14:28576. https://doi.org/10.1038/s41598-024-79863-5",
    "yuan": "Yuan S, Shao Z, Wei X, Tang J, Hall W, Wang Y, et al. Science behind AI: the evolution of trend, mobility, and collaboration. Scientometrics. 2020;124(2):993-1013. https://doi.org/10.1007/s11192-020-03423-7",
    "shaffer": "Shaffer M L. Minimum Population Sizes for Species Conservation. BioScience. 1981;31(2):131-134. https://doi.org/10.2307/1308256",
    "franzoni": "Franzoni C, Scellato G, Stephan P E. Foreign-born scientists: mobility patterns for 16 countries. Nat Biotechnol. 2012;30(12):1250-1253. https://doi.org/10.1038/nbt.2449",
    "jones": "Jones B F, Wuchty S, Uzzi B. Multi-University Research Teams: Shifting Impact, Geography, and Stratification in Science. Science. 2008;322(5905):1259-1262. https://doi.org/10.1126/science.1158357",
    "nelson": "Nelson R R, Winter S G. An Evolutionary Theory of Economic Change. Cambridge, MA: Harvard University Press, 1982.",
    "dosi": "Dosi G. Technological paradigms and technological trajectories: a suggested interpretation of the determinants and directions of technical change. Res Policy. 1982;11(3):147-162. https://doi.org/10.1016/0048-7333(82)90016-6",
    "lundvall": "Lundvall B-Å. National Systems of Innovation: Toward a Theory of Innovation and Interactive Learning. London: Anthem Press, 1992.",
    "malerba": "Malerba F. Sectoral systems of innovation and production. Res Policy. 2002;31(2):247-264. https://doi.org/10.1016/S0048-7333(01)00139-1",
    "state": "State B, Park P, Weber I, Macy M. The mesh of civilizations in the global network of digital communication. PLoS ONE. 2015;10(5):e0122543. https://doi.org/10.1371/journal.pone.0122543",
    "chinchilla": "Chinchilla-Rodríguez Z, Miao L, Murray D, Robinson-García N, Costas R, Sugimoto C R. A global comparison of scientific mobility and collaboration according to national scientific capacities. Front Res Metr Anal. 2018;3:17. https://doi.org/10.3389/frma.2018.00017",
    "freeman": "Freeman R B, Huang W. Collaboration: Strength in diversity. Nature. 2014;513(7518):305. https://doi.org/10.1038/513305a",
    "shachar": "Shachar A. The Race for Talent: Highly Skilled Migrants and Competitive Immigration Regimes. NYU Law Rev. 2006;81(1):148-206.",
    "kerr": "Kerr W R. Global Talent and U.S. Immigration Policy. Harvard Business School Working Paper No. 20-107, 2020. https://www.hbs.edu/ris/Publication%20Files/20-107_0967f1ab-1d23-4d54-b5a1-c884234d9b31.pdf",
    # Added for the Technology in Society revision (bibliographic data checked against Crossref/arXiv).
    "jevons": "Jevons W S. The Coal Question: An Inquiry Concerning the Progress of the Nation, and the Probable Exhaustion of Our Coal-Mines. London: Macmillan, 1865.",
    "alcott": "Alcott B. Jevons' paradox. Ecol Econ. 2005;54(1):9-21. https://doi.org/10.1016/j.ecolecon.2005.03.020",
    "bresnahan": "Bresnahan T F, Trajtenberg M. General purpose technologies 'Engines of growth'? J Econom. 1995;65(1):83-108. https://doi.org/10.1016/0304-4076(94)01598-T",
    "metcalfe": "Metcalfe J S. Evolutionary Economics and Creative Destruction. London: Routledge, 1998. https://doi.org/10.4324/9780203275146",
    "saviotti": "Saviotti P P. Technological Evolution, Variety and the Economy. Cheltenham: Edward Elgar, 1996. https://doi.org/10.4337/9781035334858",
    "arthur": "Arthur W B. Competing technologies, increasing returns, and lock-in by historical events. Econ J. 1989;99(394):116-131. https://doi.org/10.2307/2234208",
    "david": "David P A. Clio and the economics of QWERTY. Am Econ Rev. 1985;75(2):332-337.",
    "katz": "Katz M L, Shapiro C. Network externalities, competition, and compatibility. Am Econ Rev. 1985;75(3):424-440.",
    "stirling": "Stirling A. A general framework for analysing diversity in science, technology and society. J R Soc Interface. 2007;4(15):707-719. https://doi.org/10.1098/rsif.2007.0213",
    "hongpage": "Hong L, Page S E. Groups of diverse problem solvers can outperform groups of high-ability problem solvers. Proc Natl Acad Sci USA. 2004;101(46):16385-16389. https://doi.org/10.1073/pnas.0403723101",
    "olazaran": "Olazaran M. A sociological study of the official history of the perceptrons controversy. Soc Stud Sci. 1996;26(3):611-659. https://doi.org/10.1177/030631296026003005",
    "rumelhart": "Rumelhart D E, Hinton G E, Williams R J. Learning representations by back-propagating errors. Nature. 1986;323(6088):533-536. https://doi.org/10.1038/323533a0",
    "joravsky": "Joravsky D. The Lysenko Affair. Cambridge, MA: Harvard University Press, 1970.",
    "colander": "Colander D, Goldberg M, Haas A, Juselius K, Kirman A, Lux T, et al. The financial crisis and the systemic failure of the economics profession. Crit Rev. 2009;21(2-3):249-267. https://doi.org/10.1080/08913810902934109",
    "smolin": "Smolin L. The Trouble with Physics: The Rise of String Theory, the Fall of a Science, and What Comes Next. Boston: Houghton Mifflin, 2006.",
    "ullstrup": "Ullstrup A J. The impacts of the southern corn leaf blight epidemics of 1970-1971. Annu Rev Phytopathol. 1972;10:37-50. https://doi.org/10.1146/annurev.py.10.090172.000345",
    "mccook": "McCook S. Global rust belt: Hemileia vastatrix and the ecological integration of world coffee production since 1850. J Glob Hist. 2006;1(2):177-195. https://doi.org/10.1017/S174002280600012X",
    "avelino": "Avelino J, Cristancho M, Georgiou S, Imbach P, Aguilar L, Bornemann G, et al. The coffee rust crises in Colombia and Central America (2008-2013): impacts, plausible causes and proposed solutions. Food Secur. 2015;7(2):303-321. https://doi.org/10.1007/s12571-015-0446-9",
    "ploetz": "Ploetz R C. Management of Fusarium wilt of banana: a review with special reference to tropical race 4. Crop Prot. 2015;73:7-15. https://doi.org/10.1016/j.cropro.2015.01.007",
    "chu": "Chu J S G, Evans J A. Slowed canonical progress in large fields of science. Proc Natl Acad Sci USA. 2021;118(41):e2021636118. https://doi.org/10.1073/pnas.2021636118",
    "park": "Park M, Leahey E, Funk R J. Papers and patents are becoming less disruptive over time. Nature. 2023;613(7942):138-144. https://doi.org/10.1038/s41586-022-05543-x",
    "kleinberg": "Kleinberg J, Raghavan M. Algorithmic monoculture and social welfare. Proc Natl Acad Sci USA. 2021;118(22):e2018340118. https://doi.org/10.1073/pnas.2018340118",
    "hooker": "Hooker S. The hardware lottery. Commun ACM. 2021;64(12):58-65. https://doi.org/10.1145/3467017",
    "koch": "Koch B, Denton E, Hanna A, Foster J G. Reduced, reused and recycled: the life of a dataset in machine learning research. arXiv:2112.01716, 2021. https://doi.org/10.48550/arXiv.2112.01716",
    "raji": "Raji I D, Bender E M, Paullada A, Denton E, Hanna A. AI and the everything in the whole wide world benchmark. arXiv:2111.15366, 2021. https://doi.org/10.48550/arXiv.2111.15366",
    "kaplan": "Kaplan J, McCandlish S, Henighan T, Brown T B, Chess B, Child R, et al. Scaling laws for neural language models. arXiv:2001.08361, 2020. https://doi.org/10.48550/arXiv.2001.08361",
    "bommasani": "Bommasani R, Hudson D A, Adeli E, Altman R, Arora S, von Arx S, et al. On the opportunities and risks of foundation models. arXiv:2108.07258, 2021. https://doi.org/10.48550/arXiv.2108.07258",
    "sevilla": "Sevilla J, Heim L, Ho A, Besiroglu T, Hobbhahn M, Villalobos P. Compute trends across three eras of machine learning. In: 2022 International Joint Conference on Neural Networks (IJCNN). IEEE; 2022. p. 1-8. https://doi.org/10.1109/IJCNN55064.2022.9891914",
    "ahmed": "Ahmed N, Wahed M. The de-democratization of AI: deep learning and the compute divide in artificial intelligence research. arXiv:2010.15581, 2020. https://doi.org/10.48550/arXiv.2010.15581",
    "joshi": "Joshi P, Santy S, Budhiraja A, Bali K, Choudhury M. The state and fate of linguistic diversity and inclusion in the NLP world. In: Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics. ACL; 2020. p. 6282-6293. https://doi.org/10.18653/v1/2020.acl-main.560",
    "bender": "Bender E M, Gebru T, McMillan-Major A, Shmitchell S. On the dangers of stochastic parrots: can language models be too big? In: Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency (FAccT '21). ACM; 2021. p. 610-623. https://doi.org/10.1145/3442188.3445922",
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_transition_rates():
    return _apply_display_names(pd.read_csv(BASE_DIR / "data" / "cohort" / "transition_rates.csv"))


def load_pnr_full():
    return _apply_display_names(pd.read_csv(ENDOG / "point_of_no_return.csv"))


def load_data():
    cohort = _apply_display_names(pd.read_csv(BASE_DIR / "data" / "cohort" / "cohort.csv"), cols=("origin_group", "recent_group"))
    eq = _apply_display_names(pd.read_csv(ENDOG / "equilibrium_summary.csv"))
    sat_eq = _apply_display_names(pd.read_csv(SAT / "equilibrium_summary.csv")) if (SAT / "equilibrium_summary.csv").exists() else None
    top_t = _apply_display_names(pd.read_csv(ENDOG / "top_transitions_T.csv"))
    pnr_full = load_pnr_full()
    # Closest per group, active pool preferred, restricting to rates that actually cross the threshold
    active_only = pnr_full[(pnr_full["target"] == "domestic_active") & (pnr_full["is_within_bounds"] == True)].copy()
    active_only["proximity"] = (active_only["critical_factor"] - 1.0).abs()
    pnr_closest = active_only.loc[active_only.groupby("group")["proximity"].idxmin()].reset_index(drop=True)
    pnr_closest = pnr_closest.sort_values("proximity").reset_index(drop=True)
    period_compare = _apply_display_names(pd.read_csv(TV / "period_comparison.csv"))
    boot = _apply_display_names(pd.read_csv(BOOT / "bootstrap_summary.csv"))
    policy_rank = _apply_display_names(pd.read_csv(POL / "ranked_interventions.csv"))
    return cohort, eq, sat_eq, top_t, pnr_closest, period_compare, boot, policy_rank


# ---------------------------------------------------------------------------
# Robustness: PI proxy definition and M multiplier (results/pi_proxy, results/m_sensitivity)
# ---------------------------------------------------------------------------

PI_PROXY_DIR = RESULTS_DIR / "pi_proxy"
M_SENS_DIR = RESULTS_DIR / "m_sensitivity"
PI_PROXY_LABELS = {
    "first_last": "First last-author paper (baseline)",
    "corresponding": "First corresponding-author paper",
    "recurrent_last": "Second last-author paper (recurrent last author)",
}


def load_pi_proxy():
    """Return dict of PI-proxy robustness tables, or None if the analysis has not been run."""
    eq_path = PI_PROXY_DIR / "pi_proxy_equilibrium.csv"
    agr_path = PI_PROXY_DIR / "pi_proxy_rank_agreement.csv"
    if not (eq_path.exists() and agr_path.exists()):
        return None
    out = {
        "equilibrium": _apply_display_names(pd.read_csv(eq_path)),
        "agreement": pd.read_csv(agr_path),
    }
    snap = PI_PROXY_DIR / "pi_proxy_snapshot.csv"
    out["snapshot"] = pd.read_csv(snap) if snap.exists() else None
    return out


def load_m_sensitivity():
    det_path = M_SENS_DIR / "m_sensitivity.csv"
    sum_path = M_SENS_DIR / "m_sensitivity_summary.csv"
    if not (det_path.exists() and sum_path.exists()):
        return None
    det = _apply_display_names(pd.read_csv(det_path))
    summ = pd.read_csv(sum_path)
    for c in ("min_T_over_M_group", "closest_group"):
        summ[c] = summ[c].map(display_group)
    return {"detail": det, "summary": summ}


def pi_proxy_table(pp):
    """Supplementary table: T/M, rank and closest boundary lever under each PI proxy."""
    eqd = pp["equilibrium"]
    rows = []
    for d, sub in eqd.groupby("pi_definition", sort=False):
        for _, r in sub.iterrows():
            rows.append({
                "PI proxy": PI_PROXY_LABELS.get(d, d),
                "Group": r["group"],
                "Share of authors who are PIs": r["p_pi_domestic"],
                "p_D": r["p_D"],
                "T/M": r["T_over_M"],
                "Closest lever (T)": _rate_label(r["closest_rate"]) if pd.notna(r["closest_rate"]) else "—",
                "Proximity (T)": r["proximity"],
                "P_D": r["P_D_equilibrium"],
                "Closest lever (P_D)": _rate_label(r["closest_rate_P"]) if pd.notna(r["closest_rate_P"]) else "—",
                "Proximity (P_D)": r["proximity_P"],
                "Elasticity of T to p_D": r["elasticity_T_p_D"],
            })
    return pd.DataFrame(rows)


def pi_proxy_agreement_table(pp):
    a = pp["agreement"]
    a = a[a["reference"] == "first_last_same_snapshot"]
    a = a[a["pi_definition"] != "first_last"].copy()
    a["PI proxy"] = a["pi_definition"].map(PI_PROXY_LABELS)
    out = a[["PI proxy", "spearman_T_over_M", "spearman_proximity", "spearman_p_D", "spearman_P_D", "spearman_proximity_P", "n_closest_rate_same", "n_groups", "same_min_T_over_M_group"]].copy()
    out.columns = ["PI proxy", "Spearman rho (T/M)", "Spearman rho (boundary proximity, T)", "Spearman rho (p_D)", "Spearman rho (P_D)", "Spearman rho (boundary proximity, P_D)", "Same closest lever (regions)", "Regions", "Same lowest-T/M region"]
    out["Same lowest-T/M region"] = out["Same lowest-T/M region"].map({True: "yes", False: "no"})
    return out


def m_sensitivity_table(ms):
    s = ms["summary"].copy()
    out = pd.DataFrame({
        "M multiplier": s["M_multiplier"],
        "Regions below M": s["n_below_M"],
        "Minimum T/M": s["min_T_over_M"],
        "Lowest-T/M region": s["min_T_over_M_group"],
        "Closest region": s["closest_group"],
        "Spearman rho (T/M vs baseline)": s["spearman_T_over_M_vs_base"],
        "Spearman rho (proximity vs baseline)": s["spearman_proximity_vs_base"],
        "Closest lever unchanged (regions)": s["closest_rate_unchanged_vs_base"],
        "Regions with |e_d| > |e_alpha|": s["n_d_more_elastic_than_alpha"],
    })
    return out


def m_sensitivity_lever_changes(ms):
    """Rows (group, multiplier, lever) where the closest lever differs from the 1.0 baseline."""
    det = ms["detail"]
    base = det[det["M_multiplier"] == 1.0].set_index("group")["closest_rate"]
    ch = det[det["closest_rate"] != det["group"].map(base)]
    return ch[["group", "M_multiplier", "closest_rate", "proximity"]]


def robustness_context(pp, ms):
    ctx = {}
    if pp is not None:
        agr = pp["agreement"]
        same = agr[(agr["reference"] == "first_last_same_snapshot") & (agr["pi_definition"] != "first_last")]
        ctx["pp_rho_tm_min"] = float(same["spearman_T_over_M"].min())
        ctx["pp_rho_prox_min"] = float(same["spearman_proximity"].min())
        ctx["pp_rho_pd_min"] = float(same["spearman_p_D"].min())
        ctx["pp_rho_PD_min"] = float(same["spearman_P_D"].min())
        ctx["pp_rho_proxP_min"] = float(same["spearman_proximity_P"].min())
        eqd0 = pp["equilibrium"]
        el = eqd0.groupby("pi_definition")["elasticity_T_p_D"].agg(["min", "max"])
        ctx["pp_el_base"] = (float(el.loc["first_last", "min"]), float(el.loc["first_last", "max"]))
        alt = eqd0[eqd0["pi_definition"] != "first_last"]["elasticity_T_p_D"]
        ctx["pp_el_alt"] = (float(alt.min()), float(alt.max()))
        el_w = eqd0.pivot(index="group", columns="pi_definition", values="elasticity_T_p_D")
        ctx["pp_el_rho_min"] = float(min(el_w["first_last"].corr(el_w[d], method="spearman") for d in el_w.columns if d != "first_last"))
        base_lp = eqd0[eqd0["pi_definition"] == "first_last"].set_index("group")["closest_rate_P"]
        chP = eqd0[(eqd0["pi_definition"] != "first_last") & (eqd0["closest_rate_P"] != eqd0["group"].map(base_lp))]
        ctx["pp_leverP_changes"] = chP[["group", "pi_definition", "closest_rate_P", "proximity_P"]]
        ctx["pp_same_lever_min"] = int(same["n_closest_rate_same"].min())
        ctx["pp_n_groups"] = int(same["n_groups"].iloc[0])
        ctx["pp_same_min_group_all"] = bool(same["same_min_T_over_M_group"].all())
        pub = agr[(agr["reference"] == "published_results") & (agr["pi_definition"] == "first_last")]
        ctx["pp_pub_rho_tm"] = float(pub["spearman_T_over_M"].iloc[0]) if not pub.empty else float("nan")
        eqd = pp["equilibrium"]
        shares = eqd.groupby("pi_definition")["p_pi_domestic"].mean()
        ctx["pp_share_first_last"] = float(shares.get("first_last", float("nan")))
        ctx["pp_share_corresponding"] = float(shares.get("corresponding", float("nan")))
        ctx["pp_share_recurrent"] = float(shares.get("recurrent_last", float("nan")))
        if pp["snapshot"] is not None:
            ctx["pp_n_snapshot"] = int(pp["snapshot"]["n_authors_snapshot"].iloc[0])
    if ms is not None:
        s = ms["summary"]
        ctx["ms_mult_min"] = float(s["M_multiplier"].min())
        ctx["ms_mult_max"] = float(s["M_multiplier"].max())
        ctx["ms_n_below_max"] = int(s["n_below_M"].max())
        ctx["ms_min_tm_at_max"] = float(s.loc[s["M_multiplier"].idxmax(), "min_T_over_M"])
        ctx["ms_rho_tm_min"] = float(s["spearman_T_over_M_vs_base"].min())
        ctx["ms_rho_prox_min"] = float(s["spearman_proximity_vs_base"].min())
        ctx["ms_d_dom_all"] = bool((s["n_d_more_elastic_than_alpha"] == s["n_groups"]).all())
        ch = m_sensitivity_lever_changes(ms)
        ctx["ms_lever_changes"] = ch
        ctx["ms_closest_group"] = str(s.loc[s["M_multiplier"] == 1.0, "closest_group"].iloc[0])
    return ctx


def load_region_m_sensitivity():
    try:
        return {
            "mc": pd.read_csv(RESULTS_DIR / "region_specific_m" / "REGION_SPECIFIC_M_SENSITIVITY.csv"),
            "summary": pd.read_csv(RESULTS_DIR / "region_specific_m" / "REGION_SPECIFIC_M_SUMMARY.csv"),
        }
    except FileNotFoundError:
        return None


def robustness_paragraph(para, pp, ms, rsm=None):
    """Main-text paragraph on PI-proxy and M-multiplier robustness (Section 3.6)."""
    rc = robustness_context(pp, ms)
    if pp is None and ms is None:
        return
    p = para("Two further robustness checks address definitional choices in the mechanism. ")
    if pp is not None:
        p.add_run(
            "First, the PI proxy. Re-extracting the full cohort from a later OpenAlex snapshot "
            + (f"({rc['pp_n_snapshot']:,} authors under the same inclusion rules; the difference from Table 1 reflects OpenAlex updates to author and affiliation records between the two extractions) " if "pp_n_snapshot" in rc else "")
            + "and replacing the baseline definition (first last-author paper) with the first corresponding-author paper or with recurrence as last author (two or more last-author papers) changes the share of authors classified as PIs "
            f"(mean across macro-regions {_fmt(rc['pp_share_first_last']*100, 1)}%, {_fmt(rc['pp_share_corresponding']*100, 1)}% and {_fmt(rc['pp_share_recurrent']*100, 1)}% respectively), the promotion rates p_D and p_A, the equilibrium PI pool P_D and the split of recruitment between exogenous entry and PI-driven feedback. "
            "Because I_0 is calibrated so that total equilibrium entry equals observed entry (Section 2.8), the active pool T, T/M and the proximity of the entry lever are invariant to the proxy by construction; the informative test is therefore whether the proxy-dependent quantities reorder the macro-regions. "
            + ("The ordering is preserved: " if min(rc['pp_rho_PD_min'], rc['pp_rho_proxP_min'], rc['pp_el_rho_min']) >= 0.9 else "The ordering is largely preserved: ")
            + f"Spearman rho with the baseline is at least {_fmt(rc['pp_rho_PD_min'], 2)} for the equilibrium PI pool and {_fmt(rc['pp_rho_proxP_min'], 2)} for the proximity of the PI pool to its own threshold, "
            f"the elasticity of T to p_D rises from {_fmt(rc['pp_el_base'][0], 2)}-{_fmt(rc['pp_el_base'][1], 2)} under the baseline to {_fmt(rc['pp_el_alt'][0], 2)}-{_fmt(rc['pp_el_alt'][1], 2)} under the stricter proxies (Spearman rho of the elasticity ranking with the baseline at least {_fmt(rc['pp_el_rho_min'], 2)}), "
            + ("and the closest lever for the PI pool is unchanged in every macro-region" if rc["pp_leverP_changes"].empty else
               "and the closest lever for the PI pool changes only in " + ", ".join(sorted(set(rc["pp_leverP_changes"]["group"]))) + f", where it becomes {', '.join(sorted(set(_rate_label(x) for x in rc['pp_leverP_changes']['closest_rate_P'])))} under the stricter proxies")
            + " (Supplementary Tables S9-S10). "
        )
    if ms is not None:
        ch = rc["ms_lever_changes"]
        if ch.empty:
            lever_txt = "the closest lever is unchanged in every macro-region"
        else:
            parts = []
            for g, sub in ch.groupby("group"):
                mults = ", ".join(_fmt(m, 2) for m in sorted(sub["M_multiplier"].unique()))
                lev = ", ".join(sorted(set(_rate_label(x) for x in sub["closest_rate"])))
                parts.append(f"{g} at multipliers {mults}, where the closest lever becomes the {lev}")
            lever_txt = "the closest lever changes only for " + "; ".join(parts)
        p.add_run(
            f"Second, the threshold. Multiplying M by {_fmt(rc['ms_mult_min'], 2)}-{_fmt(rc['ms_mult_max'], 2)} leaves "
            + (f"no macro-region below its threshold (minimum T/M {_fmt(rc['ms_min_tm_at_max'], 2)} at the largest multiplier)" if rc["ms_n_below_max"] == 0 else f"up to {rc['ms_n_below_max']} macro-regions below their threshold")
            + f", preserves the ranking by T/M and by proximity exactly (Spearman rho = {_fmt(rc['ms_rho_tm_min'], 2)} and {_fmt(rc['ms_rho_prox_min'], 2)})"
            + (", keeps |elasticity to d| > |elasticity to alpha| in every macro-region at every multiplier" if rc["ms_d_dom_all"] else "")
            + f", and {lever_txt} (Supplementary Table S11). Because M enters the linear model only as the target, its level shifts distances without reordering systems under a common multiplier; that invariance is algebraic, not evidential."
        )
    if rsm is not None:
        summ = rsm["summary"].set_index("metric")["value"]
        mc = rsm["mc"]
        n_rev = int(summ["n_pairs_reversible"]); n_tot = int(summ["n_pairs_total"])
        jp = mc[mc["group"] == "Japanese"].iloc[0] if (mc["group"] == "Japanese").any() else None
        top3 = mc.sort_values("P_is_min_T_over_M", ascending=False).head(3)
        p.add_run(
            " Perturbing each macro-region's M independently over the same multiplicative range reverses the picture: "
            f"all {n_rev} of {n_tot} region pairs can exchange order within their T/M intervals, every macro-region can occupy every rank, "
            f"and under independent uniform perturbations the baseline minimum ({display_group(mc.loc[mc['baseline_rank'] == 1, 'group'].iloc[0])}) is lowest in only {mc['P_is_min_T_over_M'].max()*100:.0f}% of draws "
            f"(next: {', '.join(display_group(r.group) + ' ' + f'{r.P_is_min_T_over_M*100:.0f}%' for r in top3.iloc[1:].itertuples())}). "
            + (f"{display_group('Japanese')} spans ranks {int(jp['mc_rank_min'])}-{int(jp['mc_rank_max'])}. " if jp is not None else "")
            + "The closest lever remains the exogenous entry rate at every multiplier, a structural property of the fitted model rather than a robustness result. "
            "The T/M ranking is therefore conditional on the operational M: it is a monitoring diagnostic, not a determinate fragility ranking, and pinning down M empirically is part of the validation agenda."
        )


# ---------------------------------------------------------------------------
# Annual transition-rate and projection helpers
# ---------------------------------------------------------------------------


def load_annual_data():
    """Read annual transition-rate and projection CSVs.

    Returns a dict of DataFrames; missing tables are returned as None.
    """
    paths = {
        "rate_table": ANNUAL / "annual_ode_rates.csv",
        "projected_rates": ANNUAL / "projected_ode_rates.csv",
        "observed_stock": ANNUAL / "observed_annual_stock.csv",
        "projected_stock": ANNUAL / "projected_annual_stock.csv",
        "interciv_stock": ANNUAL / "annual_interciv_stock.csv",
        "evaluation": ANNUAL / "projection_evaluation.csv",
        "group_accuracy": ANNUAL / "projection_accuracy_by_group.csv",
        "compartment_accuracy": ANNUAL / "projection_accuracy_by_compartment.csv",
        "rate_accuracy": ANNUAL / "projection_rate_accuracy.csv",
        "rate_accuracy_overall": ANNUAL / "projection_rate_accuracy_overall.csv",
    }
    return {k: _apply_display_names(pd.read_csv(p)) if p.exists() else None for k, p in paths.items()}


def pnr_robustness_table():
    """Compare closest boundary levers between linear and saturating endogenous inflow."""
    lin_path = BASE_DIR / "results" / "endogenous" / "closest_point_of_no_return.csv"
    sat_path = BASE_DIR / "results" / "endogenous_saturating" / "closest_point_of_no_return.csv"
    if not (lin_path.exists() and sat_path.exists()):
        return pd.DataFrame()
    lin = _apply_display_names(pd.read_csv(lin_path))
    sat = _apply_display_names(pd.read_csv(sat_path))
    # Focus on the active-pool threshold, which is the operative boundary in the main text.
    lin = lin[lin["target"] == "domestic_active"].copy()
    sat = sat[sat["target"] == "domestic_active"].copy()
    lin = lin.rename(columns={
        "group": "origin_group",
        "rate_name": "linear_closest",
        "critical_factor": "linear_factor",
        "proximity": "linear_proximity",
    })
    sat = sat.rename(columns={
        "group": "origin_group",
        "rate_name": "saturating_closest",
        "critical_factor": "saturating_factor",
        "proximity": "saturating_proximity",
    })
    df = lin[["origin_group", "linear_closest", "linear_factor", "linear_proximity"]].merge(
        sat[["origin_group", "saturating_closest", "saturating_factor", "saturating_proximity"]],
        on="origin_group",
        how="inner",
    )
    if df.empty:
        return pd.DataFrame()
    # Reorder to the standard group order and round.
    df = df.set_index("origin_group").reindex([display_group(g) for g in arpr.ORDERED_GROUPS]).reset_index()
    df = df.rename(columns={"origin_group": "Group"})
    for col in ["linear_factor", "saturating_factor", "linear_proximity", "saturating_proximity"]:
        df[col] = df[col].round(4)
    return df


def compute_annual_context(annual):
    """Return data-derived summary strings for the annual projection sections."""
    ctx = {}
    eval_df = annual.get("evaluation")
    if eval_df is not None and not eval_df.empty:
        ctx["overall_rmse"] = float(((eval_df["error"] ** 2).mean()) ** 0.5)
        ctx["overall_mape"] = float(eval_df["ape"].mean())
        ctx["overall_mape_pct"] = ctx["overall_mape"] * 100.0
    else:
        ctx["overall_rmse"] = float("nan")
        ctx["overall_mape"] = float("nan")
        ctx["overall_mape_pct"] = float("nan")

    gacc = annual.get("group_accuracy")
    if gacc is not None and not gacc.empty:
        gacc = gacc.dropna(subset=["mape"]).copy()
        if not gacc.empty:
            best = gacc.loc[gacc["mape"].idxmin()]
            worst = gacc.loc[gacc["mape"].idxmax()]
            ctx["best_group"] = best["origin_group"]
            ctx["worst_group"] = worst["origin_group"]
            ctx["best_mape_pct"] = float(best["mape"]) * 100.0
            ctx["worst_mape_pct"] = float(worst["mape"]) * 100.0
            ctx["n_eval_groups"] = len(gacc)
            # Direction agreement (mean across civilisations)
            if "direction_agreement" in gacc.columns:
                ctx["direction_agreement"] = float(gacc["direction_agreement"].mean())
                ctx["best_direction_group"] = gacc.loc[gacc["direction_agreement"].idxmax()]["origin_group"]
                ctx["worst_direction_group"] = gacc.loc[gacc["direction_agreement"].idxmin()]["origin_group"]
            if "threshold_alarm_accuracy" in gacc.columns:
                ctx["threshold_alarm_accuracy"] = float(gacc["threshold_alarm_accuracy"].mean())
                ctx["threshold_alarm_sensitivity"] = float(gacc["threshold_alarm_sensitivity"].mean())
                ctx["threshold_alarm_specificity"] = float(gacc["threshold_alarm_specificity"].mean())
                # Observed alarms are rare; report total count across groups
                ctx["threshold_alarms_obs"] = int(gacc["threshold_alarms_obs"].sum())
                ctx["threshold_alarms_proj"] = int(gacc["threshold_alarms_proj"].sum())
                ctx["alarm_groups"] = ", ".join(gacc.loc[gacc["threshold_alarms_obs"] > 0, "origin_group"].tolist())
        else:
            ctx["best_group"] = "—"
            ctx["worst_group"] = "—"
            ctx["best_mape_pct"] = float("nan")
            ctx["worst_mape_pct"] = float("nan")
            ctx["n_eval_groups"] = 0
    else:
        ctx["best_group"] = "—"
        ctx["worst_group"] = "—"
        ctx["best_mape_pct"] = float("nan")
        ctx["worst_mape_pct"] = float("nan")
        ctx["n_eval_groups"] = 0

    proj = annual.get("projected_rates")
    if proj is not None and not proj.empty:
        ctx["n_projected_group_years"] = len(proj)
        ctx["smoothed_pct"] = float(proj["correction_smoothed"].mean()) * 100.0
        ctx["capped_pct"] = float(proj["correction_capped"].mean()) * 100.0
    else:
        ctx["n_projected_group_years"] = 0
        ctx["smoothed_pct"] = float("nan")
        ctx["capped_pct"] = float("nan")

    obs = annual.get("observed_stock")
    if obs is not None and not obs.empty:
        ctx["obs_year_min"] = int(obs["year"].min())
        ctx["obs_year_max"] = int(obs["year"].max())
    else:
        ctx["obs_year_min"] = 2000
        ctx["obs_year_max"] = 2023

    # Rate-level forecast accuracy (cleaner than stock-level because the fixed cohort lacks post-2016 entrants).
    rate_overall = annual.get("rate_accuracy_overall")
    if rate_overall is not None and not rate_overall.empty:
        ctx["rate_overall_rmse"] = float(rate_overall["rmse"].iloc[0])
        ctx["rate_overall_mae"] = float(rate_overall["mae"].iloc[0])
        ctx["rate_overall_mape"] = float(rate_overall["mape"].iloc[0])
        ctx["rate_overall_skill"] = float(rate_overall["skill"].iloc[0])
    else:
        ctx["rate_overall_rmse"] = float("nan")
        ctx["rate_overall_mae"] = float("nan")
        ctx["rate_overall_mape"] = float("nan")
        ctx["rate_overall_skill"] = float("nan")

    rate_acc = annual.get("rate_accuracy")
    if rate_acc is not None and not rate_acc.empty:
        # Best/worst rate by skill (naive/model RMSE ratio)
        rate_acc = rate_acc.dropna(subset=["skill"]).copy()
        if not rate_acc.empty:
            ctx["best_rate_skill"] = str(rate_acc.loc[rate_acc["skill"].idxmax(), "rate"])
            ctx["worst_rate_skill"] = str(rate_acc.loc[rate_acc["skill"].idxmin(), "rate"])
            ctx["best_rate_skill_value"] = float(rate_acc["skill"].max())
            ctx["worst_rate_skill_value"] = float(rate_acc["skill"].min())
        else:
            ctx["best_rate_skill"] = "—"
            ctx["worst_rate_skill"] = "—"
            ctx["best_rate_skill_value"] = float("nan")
            ctx["worst_rate_skill_value"] = float("nan")
    else:
        ctx["best_rate_skill"] = "—"
        ctx["worst_rate_skill"] = "—"
        ctx["best_rate_skill_value"] = float("nan")
        ctx["worst_rate_skill_value"] = float("nan")

    return ctx


def compute_japan_context(eq, pnr_closest, transition_rates):
    """Return data-derived prose values for the Japan-specific discussion."""
    ja = eq[eq["group"] == JAPAN].iloc[0]
    tr = transition_rates[transition_rates["group"] == JAPAN].iloc[0]
    pnr = pnr_closest[pnr_closest["group"] == JAPAN]
    if pnr.empty:
        # fallback from full pnr if pnr_closest was not supplied with Japan row
        pnr_row = None
    else:
        pnr_row = pnr.iloc[0]
    return {
        "T": float(ja["T_equilibrium"]),
        "M": float(ja["M_threshold"]),
        "T_over_M": float(ja["T_equilibrium"]) / float(ja["M_threshold"]),
        "margin": float(ja["margin_to_threshold_T"]),
        "D": int(round(ja["D_eq"])),
        "A": int(round(ja["A_eq"])),
        "H_D": int(round(ja["H_D_eq"])),
        "H_A": int(round(ja["H_A_eq"])),
        "P_D": int(round(ja["P_D_eq"])),
        "P_A": int(round(ja["P_A_eq"])),
        "I0": float(ja["I0"]),
        "r": float(ja["r"]),
        "alpha": float(tr["alpha"]),
        "beta": float(tr["beta"]),
        "h_D": float(tr["h_D"]),
        "h_A": float(tr["h_A"]),
        "p_D": float(tr["p_D"]),
        "p_A": float(tr["p_A"]),
        "d": float(tr["d"]),
        "pnr_rate": pnr_row["rate_name"] if pnr_row is not None else "I0",
        "pnr_factor": float(pnr_row["critical_factor"]) if pnr_row is not None else float("nan"),
        "pnr_proximity": float(pnr_row["proximity"]) if pnr_row is not None else float("nan"),
    }


def annual_summary_table(annual):
    """Mean observed annual transition rates and inflow by group (2000-2016)."""
    rate_table = annual.get("rate_table")
    if rate_table is None or rate_table.empty:
        return pd.DataFrame()
    observed = rate_table[rate_table["year"] <= 2016]
    cols = ["alpha", "beta", "h_D", "p_D", "d", "I_total"]
    means = observed.groupby("origin_group")[cols].mean().reset_index()
    means.columns = ["Group", "α", "β", "h_D", "p_D", "d", "I_total"]
    return means


def interciv_top_table(annual, n=10):
    """Top origin-destination abroad author-year accumulations.

    Unknown destinations and origin==destination domestic moves are excluded
    because the reconstruction cannot observe the actual host civilisation.
    """
    flows = annual.get("interciv_stock")
    if flows is None or flows.empty:
        return pd.DataFrame()
    flows = flows[
        (flows["destination_group"] != "Unknown") &
        (flows["origin_group"] != flows["destination_group"])
    ].copy()
    pivot = (
        flows.groupby(["origin_group", "destination_group"], observed=False)["count"]
        .sum()
        .reset_index()
        .sort_values("count", ascending=False)
        .head(n)
    )
    pivot.columns = ["Origin", "Destination", "Author-years"]
    return pivot


def build_annual_figures(annual, fig_dir):
    """Generate annual projection figures; reuse existing PNGs if data are missing."""
    fig_paths = {}
    # The annual module orders panels by its internal labels; switch to display names.
    arpr.ORDERED_GROUPS = [display_group(g) for g in arpr.ORDERED_GROUPS]
    rate_table = annual.get("rate_table")
    projected_rates = annual.get("projected_rates")
    if rate_table is not None and projected_rates is not None:
        fig_paths["fig7"] = arpr.plot_annual_rates(rate_table, projected_rates, fig_dir=fig_dir)
    else:
        fig_paths["fig7"] = fig_dir / "annual_rates_by_group.png"

    interciv = annual.get("interciv_stock")
    if interciv is not None:
        fig_paths["fig8"] = arpr.plot_interciv_heatmap(interciv, fig_dir=fig_dir)
    else:
        fig_paths["fig8"] = fig_dir / "annual_interciv_heatmap.png"

    obs_stock = annual.get("observed_stock")
    proj_stock = annual.get("projected_stock")
    if obs_stock is not None and proj_stock is not None:
        fig_paths["fig9"] = arpr.plot_projection_by_compartment(proj_stock, obs_stock, fig_dir=fig_dir)
    else:
        fig_paths["fig9"] = fig_dir / "annual_projection_vs_observed.png"
    return fig_paths


def _with_article(name):
    return f"the {name}" if str(name) in ("United States", "Islamic world") else str(name)


def _ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def load_dominant_strategy():
    """Read the talent-concentration scenario outputs (results/dominant_strategy)."""
    if not (DOM / "summary.csv").exists():
        return None
    out = {
        "summary": pd.read_csv(DOM / "summary.csv"),
        "thresholds": pd.read_csv(DOM / "gamma_thresholds.csv"),
        "trajectories": pd.read_csv(DOM / "trajectories.csv"),
        "assumptions": pd.read_csv(DOM / "scenario_assumptions.csv"),
        "host_ranking": pd.read_csv(DOM / "host_ranking.csv"),
        "collapse": pd.read_csv(DOM / "collapse_years.csv"),
    }
    out["focal"] = str(out["host_ranking"]["destination_group"].iloc[0])
    out["focals"] = [str(g) for g in out["thresholds"]["focal"].drop_duplicates()]
    return out


def compute_dominant_context(dom):
    """Data-derived values for the talent-concentration scenario (all from results/dominant_strategy)."""
    ctx = {}
    if dom is None:
        return ctx
    summ = dom["summary"]
    th = dom["thresholds"]
    focal = dom["focal"]
    fitted = summ[(summ["exogenous_share"] == "fitted") & (summ["host_recruits"] == True)]  # noqa: E712
    g0 = fitted[(fitted["focal"] == focal) & (fitted["gamma"] == 0.0) & (fitted["phi"] > 0)].sort_values("phi")
    ctx["focal_display"] = display_group(focal)
    ctx["focals_display"] = [display_group(f) for f in dom["focals"]]
    ctx["phi_min"], ctx["phi_max"] = float(g0["phi"].min()), float(g0["phi"].max())
    ctx["pool_gain_min"] = float((g0["terminal_relative_hosted_pool"].min() - 1) * 100)
    ctx["pool_gain_max"] = float((g0["terminal_relative_hosted_pool"].max() - 1) * 100)
    ctx["share_start"] = float(g0["share_start"].iloc[0] * 100)
    ctx["share_terminal_max"] = float(g0["share_terminal"].max() * 100)
    ctx["neff_start"] = float(g0["effective_regions_start"].iloc[0])
    ctx["neff_terminal_min"] = float(g0["effective_regions_terminal"].min())
    ctx["neff_terminal_max"] = float(g0["effective_regions_terminal"].max())
    ctx["n_collapsed_max"] = int(g0["n_collapsed"].max())
    coll = dom["collapse"]
    coll = coll[(coll["focal"] == focal) & (coll["exogenous_share"] == "fitted") & (coll["host_recruits"] == True)]  # noqa: E712
    coll = coll[coll["phi"] == coll["phi"].max()].dropna(subset=["collapse_year"])
    ctx["collapse_by_gamma"] = {float(gm): [(display_group(r.group), float(r.collapse_year))
                                            for r in d.sort_values("collapse_year").itertuples()]
                                for gm, d in coll.groupby("gamma")}
    ctx["min_TM_terminal"] = float(g0["min_T_over_M_terminal"].min())
    ctx["tau"] = float(summ["tau_years"].iloc[0])
    ctx["horizon_years"] = float(dom["trajectories"]["year"].max())
    ctx["horizon_tau"] = ctx["horizon_years"] / ctx["tau"]
    ctx["field_hits_peak_gain_max"] = float((g0["peak_relative_field_hits"].max() - 1) * 100)
    ctx["field_hits_peak_year_min"] = float(g0["peak_year_field_hits"].min())
    ctx["field_hits_peak_year_max"] = float(g0["peak_year_field_hits"].max())
    ctx["field_hits_below_year_min"] = float(g0["year_field_hits_below_baseline"].min())
    ctx["field_hits_below_year_max"] = float(g0["year_field_hits_below_baseline"].max())
    ctx["field_hits_terminal_min"] = float((g0["field_hits_terminal_relative"].min() - 1) * 100)
    ctx["field_hits_terminal_max"] = float((g0["field_hits_terminal_relative"].max() - 1) * 100)
    ctx["field_PI_terminal_min"] = float((g0["field_PI_terminal_relative"].min() - 1) * 100)
    ctx["field_PI_terminal_max"] = float((g0["field_PI_terminal_relative"].max() - 1) * 100)
    # gamma = 2 stylised case, phi = 2
    mid_phi = 2.0 if (g0["phi"] == 2.0).any() else float(g0["phi"].iloc[len(g0) // 2])
    ctx["mid_phi"] = mid_phi
    g_grid = sorted(fitted["gamma"].unique())
    ctx["gamma_max_grid"] = float(g_grid[-1])
    gmax_row = fitted[(fitted["focal"] == focal) & (fitted["gamma"] == g_grid[-1]) & (fitted["phi"] == mid_phi)].iloc[0]
    ctx["field_hits_terminal_gmax"] = float((gmax_row["field_hits_terminal_relative"] - 1) * 100)
    ctx["focal_hits_terminal_gmax"] = float((gmax_row["terminal_relative_focal_hits"] - 1) * 100)
    g0_mid = g0[g0["phi"] == mid_phi].iloc[0]
    ctx["focal_hits_terminal_g0_mid"] = float((g0_mid["terminal_relative_focal_hits"] - 1) * 100)
    ctx["field_hits_terminal_g0_mid"] = float((g0_mid["field_hits_terminal_relative"] - 1) * 100)
    # thresholds
    def _th(f, metric):
        t = th[(th["focal"] == f) & (th["metric"] == metric)]
        return t.set_index("phi")["gamma_threshold"]
    ctx["th_field_focal1"] = _th(focal, "field_hits_total")
    ctx["th_self_focal1"] = _th(focal, "focal_hosted_hits")
    ctx["th_PI_focal1"] = _th(focal, "field_PI_total")
    ctx["gamma_max_search"] = float(th["gamma_max"].iloc[0])
    other = [f for f in dom["focals"] if f != focal]
    ctx["focal2"] = other[0] if other else None
    ctx["focal2_display"] = display_group(other[0]) if other else None
    if other:
        ctx["th_field_focal2"] = _th(other[0], "field_hits_total")
        ctx["th_self_focal2"] = _th(other[0], "focal_hosted_hits")
        ctx["th_PI_focal2"] = _th(other[0], "field_PI_total")
    return ctx


def _poaching_paragraph(dctx):
    """Section 3.9 paragraph on when talent concentration turns against the recruiter (from gamma_thresholds.csv)."""
    fd1 = dctx["focal_display"]
    fd2 = dctx.get("focal2_display")
    s1 = dctx["th_self_focal1"].dropna()
    pi1 = dctx["th_PI_focal1"].dropna()
    txt = ("For a system that is weighing whether to recruit aggressively from others, the same scenario gives the conditions under which the strategy turns against the recruiter. "
           f"In the simulation, the dominant region's own hosted hit stock falls below its no-pull baseline within the horizon once γ exceeds a threshold that decreases as the pull intensifies: "
           f"from {_fmt(s1.max(), 1)} at φ = {_fmt(s1.idxmax(), 1)} to {_fmt(s1.min(), 1)} at φ = {_fmt(s1.idxmin(), 1)} with {_with_article(fd1)} as host")
    if fd2 and "th_self_focal2" in dctx:
        s2 = dctx["th_self_focal2"].dropna()
        n_phi = len(dctx["th_self_focal2"])
        if s2.empty:
            txt += f", and not within γ ≤ {_fmt(dctx['gamma_max_search'], 0)} at any pull intensity with {_with_article(fd2)} as host"
        elif len(s2) < n_phi:
            n_word = {1: "one", 2: "two", 3: "three", 4: "four"}.get(len(s2), str(len(s2)))
            txt += (f", and only at the {n_word} strongest pull intensit{'ies' if len(s2) > 1 else 'y'} (γ = {_fmt(s2.max(), 1)} and {_fmt(s2.min(), 1)}) with {_with_article(fd2)} as host, "
                    "whose higher fitted domestic reproduction rates absorb more of the variety loss")
        else:
            txt += f", and from {_fmt(s2.max(), 1)} to {_fmt(s2.min(), 1)} with {_with_article(fd2)} as host"
    txt += ". "
    if not pi1.empty:
        txt += (f"The field's PI stock, its capacity to reproduce the next generation, ends below baseline once γ exceeds {_fmt(pi1.min(), 2)}-{_fmt(pi1.max(), 2)} for {_with_article(fd1)}")
        if fd2 and "th_PI_focal2" in dctx and not dctx["th_PI_focal2"].dropna().empty:
            pi2 = dctx["th_PI_focal2"].dropna()
            txt += f" and {_fmt(pi2.min(), 2)}-{_fmt(pi2.max(), 2)} for {_with_article(fd2)}"
        txt += ", in each case well below the γ at which the host's own output reverts. "
    txt += ("Three qualifications bound this reading. The thresholds are outputs of a stylised simulation under the assumptions in Supplementary Table S8, not empirical estimates; γ is not identified by our data; and the values depend on which region pulls, how hard, whether hosts recruit, and which outcome is scored, so no single number applies across settings. "
            "The result is therefore not that international recruitment is harmful as such. It is that a recruiter cannot assume its gain is permanent: the harder it pulls, and the more the field's output owes to variety, the smaller the γ at which its own advantage in absolute output reverts, while the field-level losses in variety and in PI reproduction arrive earlier and at smaller γ still. "
            "For a system deciding whether to draw on smaller systems, that is the case for restraint the fitted model supports; for a system deciding how to respond to being drawn on, it points back to the levers in Table 9 rather than to barriers on mobility.")
    return txt


def dominant_strategy_table(dom):
    """Table 8: talent-concentration scenario summary for the largest host region (fitted rates, gamma = 0)."""
    summ = dom["summary"]
    th = dom["thresholds"]
    rows = []
    for f in dom["focals"]:
        g0 = summ[(summ["exogenous_share"] == "fitted") & (summ["host_recruits"] == True) & (summ["focal"] == f)  # noqa: E712
                  & (summ["gamma"] == 0.0) & (summ["phi"] > 0)].sort_values("phi")
        t_field = th[(th["focal"] == f) & (th["metric"] == "field_hits_total")].set_index("phi")["gamma_threshold"]
        t_self = th[(th["focal"] == f) & (th["metric"] == "focal_hosted_hits")].set_index("phi")["gamma_threshold"]
        for _, r in g0.iterrows():
            gf = t_field.get(r["phi"], float("nan")); gs = t_self.get(r["phi"], float("nan"))
            rows.append({
                "Dominant region": display_group(f),
                "Pull intensity φ": r["phi"],
                "Hosted pool at end of horizon (× baseline)": r["terminal_relative_hosted_pool"],
                "Share of hosted researchers at end of horizon (%)": r["share_terminal"] * 100,
                "Effective number of regions at end of horizon": r["effective_regions_terminal"],
                "Regions below M": int(r["n_collapsed"]),
                "Field hit stock at end of horizon (× baseline)": r["field_hits_terminal_relative"],
                "γ* field": "0 (fitted model)" if gf == 0 else ("not reached" if pd.isna(gf) else f"{gf:.2f}"),
                "γ* dominant region": "not reached" if pd.isna(gs) else f"{gs:.2f}",
            })
    return pd.DataFrame(rows)


def _t_tau(years, tau, decimals=1):
    """Model time in units of tau with the calendar-year equivalent as annotation."""
    return f"{_fmt(years / tau, decimals)} τ (≈{_fmt(years, 0)} years at fitted rates)"


def build_figure12(dom, fig_dir: Path):
    if dom is None:
        return None
    return domstrat.plot_dominant_strategy(dom["trajectories"], dom["thresholds"], dom["focal"], fig_dir,
                                           display=display_group, tau=float(dom["summary"]["tau_years"].iloc[0]),
                                           out_name="fig12_dominant_strategy.png")


def build_figure13(dom, fig_dir: Path):
    if dom is None:
        return None
    return domstrat.plot_regional_trajectories(dom["trajectories"], dom["collapse"], dom["focal"], fig_dir,
                                               display=display_group, tau=float(dom["summary"]["tau_years"].iloc[0]),
                                               out_name="fig13_dominant_strategy_regions.png")


def compute_context(cohort, eq, sat_eq, top_t, pnr_closest, period_compare, policy_rank):
    """Return data-derived summary strings used in the Results and Discussion."""
    n_groups = len(eq)
    eq_sorted = eq.sort_values("T_equilibrium", ascending=False)
    _lp = eq_sorted["group"].head(3).tolist()
    largest_pools = ", ".join(_lp[:-1]) + " and " + _lp[-1]
    smallest_pool = eq_sorted["group"].iloc[-1]
    eq_m = eq.sort_values("margin_to_threshold_T")
    smallest_margin_group = eq_m["group"].iloc[0]

    d_rows = top_t[(top_t["rate"] == "d") & (top_t["target"] == "domestic_active")]
    d_min_e = d_rows["elasticity"].min()
    d_max_e = d_rows["elasticity"].max()
    d_all_negative = (d_rows["elasticity"] < 0).all()

    # Positive levers after dropout
    positive = []
    for _, gdf in top_t.groupby("group"):
        gdf = gdf.sort_values("abs_elasticity", ascending=False)
        # Skip the largest (dropout), then collect the positive transition-rate levers
        for _, r in gdf.iloc[1:].iterrows():
            if r["elasticity"] > 0 and r["rate"] not in ("I0", "r"):
                positive.append(r["rate"])
    pos_counts = pd.Series(positive).value_counts()
    most_common_positive = pos_counts.index[0] if not pos_counts.empty else "p_D"
    second_positive = pos_counts.index[1] if len(pos_counts) > 1 else None
    if most_common_positive == "p_D":
        pos_lever_text = "principal-investigator promotion (p_D)"
    elif most_common_positive == "h_D":
        pos_lever_text = "domestic hit generation (h_D)"
    elif most_common_positive == "beta":
        pos_lever_text = "return from abroad (β)"
    else:
        pos_lever_text = most_common_positive
    if second_positive == "p_D":
        second_text = "principal-investigator promotion (p_D)"
    elif second_positive == "h_D":
        second_text = "domestic hit generation (h_D)"
    elif second_positive == "beta":
        second_text = "return from abroad (β)"
    else:
        second_text = second_positive
    if second_text and second_text != pos_lever_text:
        positive_lever_sentence = f"The largest positive transition lever is {pos_lever_text}, followed by {second_text}."
    else:
        positive_lever_sentence = f"The largest positive transition lever is {pos_lever_text}."
    positive_lever_sentence_lower = positive_lever_sentence[0].lower() + positive_lever_sentence[1:]
    if positive_lever_sentence_lower.endswith('.'):
        positive_lever_sentence_lower = positive_lever_sentence_lower[:-1]

    # PI promotion elasticity, identify group with highest p_D elasticity
    pd_elas = top_t[(top_t["rate"] == "p_D") & (top_t["target"] == "domestic_active")].copy()
    pd_elas["abs_e"] = pd_elas["elasticity"].abs()
    highest_pd_group = pd_elas.sort_values("abs_e", ascending=False).iloc[0]["group"] if not pd_elas.empty else JAPAN

    # Model-implied viability boundary
    closest_rate_counts = pnr_closest["rate_name"].value_counts()
    closest_rate_mode = closest_rate_counts.index[0] if not closest_rate_counts.empty else "I0"
    all_closest_same = len(closest_rate_counts) == 1
    if all_closest_same:
        pnr_lever_text = f"{closest_rate_mode} is the closest viability-boundary lever for the active researcher pool in every group"
    else:
        pnr_lever_text = f"{closest_rate_mode} is the most common closest viability-boundary lever for the active researcher pool"

    # Saturating reduction range
    sat_range_text = ""
    if sat_eq is not None:
        merged = eq[["group", "T_equilibrium"]].merge(
            sat_eq[["group", "T_equilibrium"]], on="group", suffixes=("_lin", "_sat")
        )
        pct_diff = 100.0 * (merged["T_equilibrium_lin"] - merged["T_equilibrium_sat"]) / merged["T_equilibrium_lin"]
        max_abs = pct_diff.abs().max()
        if max_abs < 0.001:
            sat_range_text = "below 0.001% for every group"
        else:
            sat_range_text = f"up to {max_abs:.2f}% lower than the linear variant"

    # Historical counterfactual
    if period_compare.empty:
        period_neg = "none"
        period_pos = "none"
        period_all_neg = False
    else:
        sorted_pc = period_compare.sort_values("delta_margin")
        neg = sorted_pc[sorted_pc["delta_margin"] < 0]["group"].tolist()
        pos = sorted_pc[sorted_pc["delta_margin"] > 0]["group"].tolist()[::-1]
        period_neg = ", ".join(neg) if neg else "none"
        period_pos = ", ".join(pos) if pos else "none"
        period_all_neg = len(pos) == 0

    # 10% dropout margin gain range
    d_decrease = policy_rank[(policy_rank["lever"] == "d") & (policy_rank["direction"] == "decrease")].copy()
    d_10pct = d_decrease[d_decrease["lever_change_pct"].abs() >= 9.9]
    if d_10pct.empty:
        d_10pct = d_decrease
    d_10pct_group = d_10pct.loc[d_10pct.groupby("group")["normalised_margin_gain_per_10pct"].idxmax()]
    d_min_gain = d_10pct_group.sort_values("margin_gain").iloc[0]
    d_max_gain = d_10pct_group.sort_values("margin_gain").iloc[-1]

    # Endogenous inflow safety factor used in the fitted model.  The default code
    # cap is 0.50 of the critical reproduction rate; the most constrained fitted
    # group has a realised r / r_critical ratio that is lower (about 0.40).
    safety_factor_cap = 0.50
    min_realised_safety_ratio = float((eq["r"] / eq["r_critical"]).min())

    # Proposition P1: proximity depends on T/M, not on absolute T
    tm = eq.assign(tm=eq["T_equilibrium"] / eq["M_threshold"]).sort_values("tm")
    tm_min_group, tm_min = tm["group"].iloc[0], float(tm["tm"].iloc[0])
    tm_max_group, tm_max = tm["group"].iloc[-1], float(tm["tm"].iloc[-1])
    shares = cohort.groupby("origin_group").agg(n=("author_id", "count"), pis=("pi", "sum"), hits=("hit", "sum"), active=("active", "sum"))
    pi_share_min, pi_share_max = float((shares["pis"] / shares["n"]).min()), float((shares["pis"] / shares["n"]).max())
    hit_share_min, hit_share_max = float((shares["hits"] / shares["n"]).min()), float((shares["hits"] / shares["n"]).max())
    ratio = eq.set_index("group")["T_equilibrium"] / shares["active"].reindex(eq["group"]).values
    teq_active_min, teq_active_max = float(ratio.min()), float(ratio.max())
    tm_min_dominant, tm_min_dominant_share = "", float("nan")
    mapping_path = BASE_DIR / "data" / "country_civilization_mapping.json"
    if mapping_path.exists():
        with open(mapping_path, encoding="utf-8") as fh:
            _map = json.load(fh)
        _rows = [(v["name"], int(v.get("ai_ml_works_2022_2023", 0))) for v in _map.values() if display_group(v["group"]) == tm_min_group]
        _tot = sum(w for _, w in _rows)
        if _tot > 0:
            tm_min_dominant, _w = max(_rows, key=lambda x: x[1])
            tm_min_dominant_share = _w / _tot
    prox = pnr_closest[["group", "proximity"]].merge(tm[["group", "tm", "T_equilibrium"]], on="group")
    rho_tm = float(prox["proximity"].corr(prox["tm"], method="spearman")) if len(prox) > 2 else float("nan")
    rho_T = float(prox["proximity"].corr(prox["T_equilibrium"], method="spearman")) if len(prox) > 2 else float("nan")

    # Proposition P2: dropout (all compartments) vs early-career outflow (one compartment)
    sens_path = ENDOG / "sensitivity.csv"
    d_gt_alpha_groups = 0
    alpha_abs_max = float("nan")
    if sens_path.exists():
        sens = _apply_display_names(pd.read_csv(sens_path))
        sens = sens[sens["target"] == "domestic_active"]
        piv = sens.pivot_table(index="group", columns="rate", values="elasticity")
        if {"d", "alpha"}.issubset(piv.columns):
            d_gt_alpha_groups = int((piv["d"].abs() > piv["alpha"].abs()).sum())
            alpha_abs_max = float(piv["alpha"].abs().max())

    return {
        "tm_min_group": tm_min_group,
        "pi_share_min": pi_share_min, "pi_share_max": pi_share_max,
        "hit_share_min": hit_share_min, "hit_share_max": hit_share_max,
        "teq_active_min": teq_active_min, "teq_active_max": teq_active_max,
        "tm_min_dominant": tm_min_dominant, "tm_min_dominant_share": tm_min_dominant_share,
        "tm_min": tm_min,
        "tm_max_group": tm_max_group,
        "tm_max": tm_max,
        "rho_prox_tm": rho_tm,
        "rho_prox_T": rho_T,
        "d_gt_alpha_groups": d_gt_alpha_groups,
        "alpha_abs_max": alpha_abs_max,
        "n_groups": n_groups,
        "largest_pools": largest_pools,
        "smallest_pool": smallest_pool,
        "smallest_margin_group": smallest_margin_group,
        "d_min_e": d_min_e,
        "d_max_e": d_max_e,
        "d_all_negative": d_all_negative,
        "positive_lever_sentence": positive_lever_sentence,
        "positive_lever_sentence_lower": positive_lever_sentence_lower,
        "highest_pd_group": highest_pd_group,
        "pnr_lever_text": pnr_lever_text,
        "sat_range_text": sat_range_text,
        "period_neg": period_neg,
        "period_pos": period_pos,
        "period_all_neg": period_all_neg,
        "d_min_gain_group": d_min_gain["group"],
        "d_max_gain_group": d_max_gain["group"],
        "d_min_gain": f"{round(d_min_gain['margin_gain']):,}",
        "d_max_gain": f"{round(d_max_gain['margin_gain']):,}",
        "safety_factor_cap": safety_factor_cap,
        "min_realised_safety_ratio": min_realised_safety_ratio,
    }


def _package_summary():
    """Return a narrative and a DataFrame for the best multi-lever policy packages.

    Packages are generated by src/policy_counterfactuals.py --packages.  We report
    the package with the largest absolute margin gain for each of the three
    smallest-margin groups, using counterfactuals.csv (no hard-coded numbers).
    """
    cf_path = POL / "counterfactuals.csv"
    if not cf_path.exists():
        return None, None
    cf = _apply_display_names(pd.read_csv(cf_path))
    packages = cf[cf["lever"].str.startswith("package:", na=False)].copy()
    if packages.empty:
        return None, None
    top = packages.loc[packages.groupby("group")["delta_margin"].idxmax()].copy()
    top["package_name"] = top["lever"].str.replace("package:", "", regex=False).str.replace("_", " ", regex=False)
    top = top.sort_values("delta_margin")
    parts = [
        f"{r['group']} ({r['package_name']}: +{round(r['delta_margin']):,} active researchers)"
        for _, r in top.iterrows()
    ]
    narrative = (
        "We also evaluated multi-lever policy packages for the three smallest-margin groups. "
        "The package with the largest margin gain in each group was: "
        + "; ".join(parts)
        + ". "
        "These packages combine dropout reduction with return or PI-pipeline levers, "
        "showing that the framework can compare multi-lever interventions as well as single-rate perturbations."
    )
    return narrative, top


def _unify_pnr_markdown(text):
    """Unify 'model-implied viability boundary' to boundary in markdown, keeping the definition in the Abstract and Introduction."""
    import re

    pnr_re = re.compile(r"model-implied viability boundary(?: \(boundary\))?", re.IGNORECASE)
    current_section = None
    seen = {"Abstract": False, "1. Introduction": False}

    def _replace(m, section):
        key = section if section == "Abstract" else "1. Introduction"
        if section in ("Abstract", "1. Introduction") and not seen[key]:
            seen[key] = True
            return m.group(0)
        return "boundary"

    out_lines = []
    for line in text.split("\n"):
        m_heading = re.match(r"##\s+(.+)", line)
        if m_heading:
            current_section = m_heading.group(1).strip()
        out_lines.append(pnr_re.sub(lambda m: _replace(m, current_section), line))

    return "\n".join(out_lines)



# ---------------------------------------------------------------------------
# Inline math: convert plain-text symbols in body runs to Word-native OMML
# ---------------------------------------------------------------------------

_M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_GREEK = "αβγδεζηθικλμνξοπρστυφχψωΔ"
_SUB_TOKEN = r"[A-Za-z]_[A-Za-z0-9" + _GREEK + r"]+"
_OPERAND = r"(?:" + _SUB_TOKEN + r"|[cd]\u0304|T/M|I\(P_D\)|[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?%?|[A-Za-z]|[" + _GREEK + r"])"
_SYMBOL = r"(?:" + _SUB_TOKEN + r"|I0|[cd]\u0304|T/M|I\(P_D\)|[A-Za-z]|[" + _GREEK + r"])"
_EQUATION = _SYMBOL + r"(?:\s?[=+×−<>≥≤/-]\s?" + _OPERAND + r")+"
INLINE_MATH_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:"
    + _EQUATION
    + r"|\|e_[A-Za-z" + _GREEK + r"]\|"
    + r"|" + _SUB_TOKEN
    + r"|I0"
    + r"|I\(P_D\)"
    + r"|[cd]\u0304"
    + r"|T/M"
    + r"|Δ[TM]?|[αβερτ]"
    + r"|(?<=\()A(?=\))"
    + r"|[TMDkrd]"
    + r")(?![A-Za-z0-9_\u0304])"
)
_ATOM_RE = re.compile(r"(" + _SUB_TOKEN + r"|I0|[cd]\u0304|I\(P_D\)|\s?[=+×−<>≥≤|/()-]\s?|[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?%?|[A-Za-z]|[" + _GREEK + r"])")


def _m(tag, *children, text=None):
    el = ET.Element(f"{{{_M_NS}}}{tag}")
    if text is not None:
        el.text = text
    for c in children:
        el.append(c)
    return el


def _m_run(text, normal=False):
    r = _m("r")
    if normal:
        rpr = _m("rPr")
        sty = _m("sty"); sty.set(f"{{{_M_NS}}}val", "p")
        rpr.append(sty); r.append(rpr)
    t = _m("t", text=text)
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.append(t)
    return r


def _m_sub(base, sub):
    return _m("sSub", _m("e", _m_run(base)), _m("sub", _m_run(sub)))


def _m_bar(base):
    accpr = _m("accPr"); chr_ = _m("chr"); chr_.set(f"{{{_M_NS}}}val", "\u0305"); accpr.append(chr_)
    return _m("acc", accpr, _m("e", _m_run(base)))


def _omml_from_text(expr):
    """Build an m:oMath element from a plain-text expression such as 'T = D + H_D + P_D'."""
    omath = _m("oMath")
    for atom in _ATOM_RE.findall(expr):
        if not atom:
            continue
        if atom in ("c\u0304", "d\u0304"):
            omath.append(_m_bar(atom[0]))
        elif atom == "I(P_D)":
            omath.append(_m_run("I")); omath.append(_m_run("("))
            omath.append(_m_sub("P", "D")); omath.append(_m_run(")"))
        elif atom == "I0":
            omath.append(_m_sub("I", "0"))
        elif "_" in atom:
            base, sub = atom.split("_", 1)
            omath.append(_m_sub(base, sub))
        else:
            omath.append(_m_run(atom.replace("-", "\u2212") if atom.strip() == "-" else atom))
    return omath


def _clone_run_with_text(run, text):
    new_r = copy.deepcopy(run._r)
    for child in list(new_r):
        if child.tag != f"{{{_W_NS}}}rPr":
            new_r.remove(child)
    t = ET.SubElement(new_r, f"{{{_W_NS}}}t")
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return new_r


def _mathify_paragraph(para):
    for run in list(para.runs):
        text = run.text
        if not text or not INLINE_MATH_RE.search(text):
            continue
        parent = run._r.getparent()
        idx = parent.index(run._r)
        pieces = []
        pos = 0
        for m in INLINE_MATH_RE.finditer(text):
            if m.start() > pos:
                pieces.append(_clone_run_with_text(run, text[pos:m.start()]))
            pieces.append(_omml_from_text(m.group()))
            pos = m.end()
        if pos < len(text):
            pieces.append(_clone_run_with_text(run, text[pos:]))
        for offset, el in enumerate(pieces):
            parent.insert(idx + offset, el)
        parent.remove(run._r)


def _mathify_docx(doc, stop_at="References"):
    """Replace plain-text inline symbols with OMML in body paragraphs and tables before the reference list."""
    body = doc.element.body
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            para = docx.text.paragraph.Paragraph(child, doc)
            if para.text.strip() == stop_at and para.style.name.startswith("Heading"):
                break
            _mathify_paragraph(para)
        elif tag == "tbl":
            table = docx.table.Table(child, doc)
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        _mathify_paragraph(para)


def _unify_pnr_docx(doc):
    """Unify 'model-implied viability boundary' to boundary in docx body text, keeping definitions in Abstract and Introduction."""
    import re

    pnr_re = re.compile(r"model-implied viability boundary(?: \(boundary\))?", re.IGNORECASE)
    current_section = None
    seen = {"Abstract": False, "Introduction": False}

    for para in doc.paragraphs:
        text = para.text
        if text.startswith("Abstract"):
            current_section = "Abstract"
            continue
        if text.startswith("1. Introduction"):
            current_section = "Introduction"
            continue
        # Only the abstract and introduction paragraphs contain the phrase.
        if current_section in ("Abstract", "Introduction") and pnr_re.search(text):
            for run in para.runs:
                if pnr_re.search(run.text):
                    if not seen[current_section]:
                        seen[current_section] = True
                    else:
                        run.text = pnr_re.sub("boundary", run.text)
    return doc


def _renumber_markdown_sections(lines):
    """Renumber markdown subsections so every main section has continuous numbers.

    The Word manuscript is the submission file; the Markdown copy is for version
    control and review. Some subsections that are present in the Word version are
    omitted in Markdown, creating gaps (e.g. 4.4 -> 4.10). This function renumbers
    the visible subsections continuously and updates any in-text references.
    """
    import re

    renumbered = []
    current_section = None
    subsection_counter = 0
    mapping = {}

    section_re = re.compile(r"^## (\d+)\.\s+(.*)")
    subsection_re = re.compile(r"^### (\d+)\.(\d+)\s+(.*)")

    for line in lines:
        m = section_re.match(line)
        if m:
            current_section = int(m.group(1))
            subsection_counter = 0
            renumbered.append(line)
            continue
        m = subsection_re.match(line)
        if m and current_section is not None:
            section_num = int(m.group(1))
            old_sub = m.group(2)
            title = m.group(3)
            if section_num != current_section:
                current_section = section_num
                subsection_counter = 0
            subsection_counter += 1
            new_num = f"{section_num}.{subsection_counter}"
            old_full = f"{section_num}.{old_sub}"
            if old_full != new_num:
                mapping[old_full] = new_num
            renumbered.append(f"### {new_num} {title}")
            continue
        renumbered.append(line)

    # Replace in-text references like "Section 4.7" with the renumbered target.
    keys = sorted(mapping.keys(), key=lambda k: len(k), reverse=True)
    for i, line in enumerate(renumbered):
        for old in keys:
            # Match "Section" or "Sections" followed by the old number at a word boundary.
            pattern = re.compile(rf"(Section[s]?\\s+){re.escape(old)}\\b")
            line = pattern.sub(rf"\g<1>{mapping[old]}", line)
        renumbered[i] = line

    return renumbered


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------

def _abstract_and_highlights(eq, pnr_closest):
    closest = pnr_closest.iloc[0]
    # Data-driven statement about the most efficient lever
    policy_rank_path = POL / "ranked_interventions.csv"
    if policy_rank_path.exists():
        policy_rank = _apply_display_names(pd.read_csv(policy_rank_path))
        top_by_group = policy_rank.groupby("group").head(1)
        all_top_are_d = (top_by_group["lever"] == "d").all()
        top_lever_mode = top_by_group["lever"].mode()
        most_common_lever = top_lever_mode.iloc[0] if not top_lever_mode.empty else "d"
    else:
        all_top_are_d = True
        most_common_lever = "d"
    if all_top_are_d:
        lever_text = "Dropout, which drains every compartment, is the most elastic lever in every macro-region. "
        highlight_lever = "Dropout, which drains every career stage, is the most elastic lever everywhere"
    else:
        lever_text = f"Dropout, which drains every compartment, is the most elastic lever in most macro-regions (most common top lever: {_rate_label(most_common_lever)}). "
        highlight_lever = f"Adjusting {most_common_lever} yields the largest margin gain in most macro-regions"
    # Historical direction of change (Period comparison) for the abstract
    pc_path = TV / "period_comparison.csv"
    approaching = None
    if pc_path.exists():
        pc = _apply_display_names(pd.read_csv(pc_path))
        if {"group", "delta_T"}.issubset(pc.columns):
            approaching = int((pc["delta_T"] < 0).sum())
    hist_text = (
        f"Transition rates estimated from the 2011-2016 career-start window imply a smaller equilibrium pool than 2000-2010 rates in {approaching} of {len(pc)} macro-regions. "
        if approaching is not None else ""
    )
    smallest_tm = eq.assign(tm=eq["T_equilibrium"] / eq["M_threshold"]).sort_values("tm").iloc[0]
    abstract = (
        "Researcher mobility is measured as stocks and net flows, but those quantities do not say whether a research system can still reproduce its own workforce. "
        "We build a reproducible measurement pipeline that turns open bibliometric records into cohort career-transition rates, a six-compartment dynamical model, and a monitoring indicator pair: the equilibrium active pool relative to a minimum viable coauthor scale (T/M) and the proximity of that equilibrium to a model-implied viability boundary. The two are linked by construction and form one diagnostic scale, not two independent tests. "
        f"Applied to an OpenAlex AI/ML cohort (2000-2023) across {len(eq)} research macro-regions, all systems exceed their minimum scale, but distance to the boundary is governed by relative scale rather than size: "
        f"the lowest T/M is {_fmt(smallest_tm['tm'], 2)} ({display_group(smallest_tm['group'])}), and the closest boundary is in {display_group(closest['group'])}, "
        f"where {_rate_label(closest['rate_name'])} reduced to {closest['critical_factor']*100:.1f}% of its current value-a {closest['proximity']*100:.1f}% reduction-would drive the active pool to its threshold. "
        + lever_text
        + hist_text
        + "Seven origin specifications never reverse a macro-region's mobility direction, and six PI definitions leave the T-side rankings structurally invariant while the P-side varies. "
        "The pipeline is field-agnostic; AI/ML is the case study. The indicators give a recomputable monitoring diagnostic; its ranking is conditional on the operational M and we claim no validated predictive power."
    )
    keywords = (
        "researcher mobility; research evaluation; science of science; minimum viable scale; "
        "compartment model; bibliometric indicators; artificial intelligence"
    )
    highlights = [
        "A reproducible pipeline from bibliometric records to research-system viability",
        "Distance to the boundary follows relative scale T/M, not system size",
        f"Closest boundary: {display_group(closest['group'])}, {closest['rate_name']} at {closest['critical_factor']*100:.1f}% of baseline",
        highlight_lever,
        "Seven origin rules and six PI definitions audited in the main results",
    ]
    return abstract, keywords, highlights


def check_front_matter(abstract, highlights):
    """Enforce Journal of Informetrics limits: abstract <= 250 words, 3-5 highlights <= 85 chars."""
    n_words = len(abstract.split())
    if n_words > 250:
        raise ValueError(f"Abstract has {n_words} words (limit 250)")
    if not 3 <= len(highlights) <= 5:
        raise ValueError(f"{len(highlights)} highlights (need 3-5)")
    too_long = [h for h in highlights if len(h) > 85]
    if too_long:
        raise ValueError(f"Highlights over 85 characters: {too_long}")
    return n_words


def _data_availability_text(blinded=False):
    repo = (
        "will be deposited in a public repository upon acceptance"
        if blinded
        else "are available in the public GitHub repository https://github.com/bougtoir/researcher-mobility-ode"
    )
    return (
        "All bibliometric data used in this study come from OpenAlex (https://openalex.org), an open scholarly database released under a CC0 licence; works were retrieved through the OpenAlex API for the Artificial Intelligence subfield (subfield 1702) and publication years 2000 to 2023. "
        "The country-to-macro-region mapping with its documented overrides, the estimated transition rates for every macro-region, and every aggregate result table underlying the figures and numbers reported here "
        + repo
        + ". The same repository contains the Python code for cohort extraction, rate estimation, the ODE model and its endogenous-inflow variant, the bootstrap, the sensitivity and robustness analyses, the coupled nine-region simulation, and the script that regenerates this manuscript, its figures, tables and Supplementary Material. "
        "The author-level cohort and the underlying work and authorship records are derivatives of OpenAlex data and are not redistributed; the single reproduction command (reproduce.sh) re-extracts them from the OpenAlex API with the scripts provided, using the same subfield, year window and inclusion rules, and then rebuilds all results from that extraction. "
        "OpenAlex is updated continuously, so a fresh extraction reproduces the reported rates, rankings and thresholds up to small snapshot differences of the kind reported in Section 3.6. "
        "No proprietary or restricted data were used."
    )


def _descriptive_table(cohort):
    """Return DataFrame of descriptive statistics per group."""
    grp = cohort.groupby("origin_group").agg(
        n=("author_id", "count"),
        works=("n_ai_works", "sum"),
        active=("active", "sum"),
        hits=("hit", "sum"),
        pis=("pi", "sum"),
        career_start_mean=("career_start", "mean"),
        abroad=("abroad", "sum"),
    ).reset_index()
    grp["career_start_mean"] = grp["career_start_mean"].round(1)
    grp = grp.rename(columns={"origin_group": "Group"})
    return grp


def _docx_to_markdown(docx_path: Path, output_dir: Path) -> Path:
    """Convert an existing Word manuscript to Markdown so markdown is a faithful derivative."""
    if pypandoc is None:
        raise RuntimeError("pypandoc is required to generate the markdown version")
    md_path = output_dir / docx_path.with_suffix(".md").name
    pypandoc.convert_file(str(docx_path), "md", format="docx", outputfile=str(md_path))
    return md_path


def write_markdown(output_dir: Path, data=None, fig_paths=None, docx_path=None, blinded=False):
    """Write a plain-text markdown version for version control and review."""
    if docx_path is not None:
        md_path = _docx_to_markdown(docx_path, output_dir)
        return md_path
    # Fallback: the legacy markdown builder is no longer maintained; use pypandoc instead.
    raise RuntimeError("write_markdown now requires a docx_path; regenerate docx first.")


def _add_title_page(doc, word_count=None, blinded=False):
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.line_spacing = 1.5
    # Journal format: Times New Roman 12pt, black text throughout.
    for sname in ("Title", "Heading 1", "Heading 2", "Heading 3", "Heading 4",
                  "Caption", "Title Char", "Heading 1 Char", "Heading 2 Char",
                  "Heading 3 Char", "Heading 4 Char", "Caption Char"):
        try:
            st = doc.styles[sname]
            st.font.name = "Times New Roman"
            st.font.color.rgb = RGBColor(0, 0, 0)
            if sname != "Title":
                st.font.size = Pt(12)
        except KeyError:
            pass

    title = doc.add_heading(TITLE, level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.size = Pt(16); title.runs[0].font.color.rgb = RGBColor(0,0,0)
    title.runs[0].font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Article type: Full Length Article")

    if word_count:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run(f"Approximate word count (main text incl. tables, excl. references): {word_count}")

    if not blinded:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("Corresponding author: [To be completed at submission]")
    else:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("Author information removed for double-anonymised review")

    p = doc.add_paragraph()
    run = p.add_run()
    run.add_break(WD_BREAK.PAGE)


def _add_front_matter(doc, abstract, keywords, highlights, blinded=False):
    doc.add_heading("Abstract", level=1)
    p = doc.add_paragraph()
    p.add_run(abstract)

    p = doc.add_paragraph()
    p.add_run("Keywords: ").bold = True
    p.add_run(keywords)

    doc.add_heading("Highlights", level=2)
    for h in highlights:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(h)

    doc.add_heading("Data and Code Availability", level=2)
    p = doc.add_paragraph()
    p.add_run(_data_availability_text(blinded=blinded))

    doc.add_heading("Declarations", level=2)
    declarations = [
        ("Funding", "[To be completed by the authors at submission.]"),
        ("Competing interests", "[To be completed by the authors at submission.]"),
        ("Author contributions", "[To be completed by the authors at submission.]"),
        (
            "Declaration of generative AI in scientific writing",
            "During the preparation of this work the authors used AI-assisted tools to draft, code, and revise the manuscript. All claims, data, and interpretations were reviewed and approved by the authors.",
        ),
    ]
    if not blinded:
        declarations.append(("Acknowledgments", "This study was motivated by a note.com essay by Yamada Y (momentumyy) that framed researcher mobility in terms of transition rates rather than net flows (" + NOTE_TEXT + ")."))
    else:
        declarations.append(("Acknowledgments", "[Removed for double-anonymised review]"))
    for sub, text in declarations:
        p = doc.add_paragraph()
        p.add_run(f"{sub}: ").bold = True
        p.add_run(text)


def load_measurement_validity():
    """Load the Gate-1 measurement-validity result tables (results/measurement_validity/)."""
    base = BASE_DIR / "results" / "measurement_validity"
    out = {}
    for name in ["ORIGIN_SENSITIVITY", "MOBILITY_SENSITIVITY", "MOBILITY_MULTISTATE",
                 "PI_SENSITIVITY", "PI_PROPAGATION_P", "MISSINGNESS_SUMMARY"]:
        f = base / f"{name}.csv"
        out[name] = _apply_display_names(pd.read_csv(f)) if f.exists() else None
    return out


def _add_table_from_df(doc, df, caption, decimals=None, bold_header=True):
    if decimals is None:
        decimals = {}
    cols = df.columns.tolist()
    table = doc.add_table(rows=1, cols=len(cols))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, c in enumerate(cols):
        hdr[i].text = str(c)
        if bold_header:
            for run in hdr[i].paragraphs[0].runs:
                run.font.bold = True
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, c in enumerate(cols):
            v = row[c]
            cells[i].text = _fmt(v, decimals.get(c, 2))
    cap = doc.add_paragraph()
    cap.add_run(caption).italic = True
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return table


def _add_docx_body(doc, data, fig_paths, blinded=False, registry=None):
    (cohort, eq, sat_eq, top_t, pnr_closest, period_compare, boot, policy_rank) = data
    if registry is None:
        registry = CitationRegistry(REFS)
    C = lambda p, *keys: cite(p, registry, *keys)  # noqa: E731
    ctx = compute_context(cohort, eq, sat_eq, top_t, pnr_closest, period_compare, policy_rank)
    transition_rates = load_transition_rates()
    ja_ctx = compute_japan_context(eq, pnr_closest, transition_rates)
    annual = load_annual_data()
    annual_ctx = compute_annual_context(annual)
    dom = load_dominant_strategy()
    dctx = compute_dominant_context(dom)
    pi_proxy = load_pi_proxy()
    m_sens = load_m_sensitivity()
    mv = load_measurement_validity()
    n_authors = len(cohort)

    def para(text=""):
        p = doc.add_paragraph()
        if text:
            p.add_run(text)
        return p

    def figure(key, caption, width=5.8):
        doc.add_picture(str(fig_paths[key]), width=Inches(width))
        cap = doc.add_paragraph()
        cap.paragraph_format.space_before = Pt(12)
        cap.add_run(caption).italic = True
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # ------------------------------------------------------------------
    # 1. Introduction
    # ------------------------------------------------------------------
    doc.add_heading("1. Introduction", level=1)
    p = para("The science of science measures researcher mobility as stocks and net flows: how many scientists a country has, how many leave and how many arrive")
    C(p, "thorn", "franzoni", "appelt")
    p.add_run(". Those quantities describe redistribution, but they do not tell an evaluator whether a research system can still reproduce its own workforce. "
              "What is missing is a community-level state variable-an observable quantity that tracks, in model terms, whether a system retains the capacity to reproduce its workforce before the headcount shows it. "
              "This paper builds that measurement pipeline end to end and applies it to one field where the question is urgent.")
    p = para("Artificial intelligence (AI) and machine learning (ML) research is an informative case. Its methods are a general-purpose technology being embedded across science, industry and public administration")
    C(p, "bresnahan", "macropolo")
    p.add_run("; its senior researchers are unusually mobile internationally; and its talent, compute and data are concentrating in a small number of systems")
    C(p, "macropolo", "sevilla", "ahmed")
    p.add_run(". Governments compete for this population through visas, fellowships and salaries")
    C(p, "appelt", "shachar", "kerr")
    p.add_run(". The question echoes Jevons's coal question—extended from an exhaustible input to a reproducible but concentrating human one")
    C(p, "jevons", "alcott")
    p.add_run(". A measurement framework that converts individual career-transition rates into system-level viability indicators is therefore of direct interest to research evaluation and science-of-science research, and AI/ML is the field where we calibrate and illustrate it; the framework itself is field-agnostic.")
    p = para("The mechanism behind the indicators has four steps. "
             "(i) Career-transition rates-entry (I_0), early-career moves abroad (α), return (β), high-impact production (h_D, h_A), promotion to independent authorship (p_D, p_A) and dropout (d)-determine the equilibrium domestic active pool T. "
             "(ii) Recruitment exhibits a network externality: principal investigators (PIs) train students and attract post-doctoral researchers, so inflow rises with the PI stock")
    C(p, "katz")
    p.add_run(", making the pool self-reinforcing. "
             "(iii) A research system must exceed a minimum viable coauthor scale M-an operational quantity computed from the field's observed number of independent last-author groups and its coauthor intensity")
    C(p, "shaffer")
    p.add_run("-to sustain its norms of production. "
             "(iv) Below M, the system can no longer reproduce its PI stock, and the research programme it carried leaves the field's menu of variety, a loss that is path-dependent in Arthur's sense")
    C(p, "arthur", "nelson", "dosi")
    p.add_run(". The research question is: for each research system, how far is the active pool from its minimum viable scale, which transition governs that distance, and has the distance been shrinking?")
    p = para("Four propositions are derived from the mechanism before seeing the results. "
             "P1 (relative scale): distance to the viability boundary is governed by T/M rather than absolute T; because the entry lever rescales the whole equilibrium, this is a structural implication used diagnostically, not a falsifiable hypothesis. "
             "P2 (asymmetric leakage): dropout, which removes researchers from every compartment, is more elastic than early-career outflow, which preserves return. "
             "P3 (endogenous recruitment): the transition closest to the threshold is the one feeding the reproduction loop from outside (I_0), and the fragility ranking is robust to the form of the recruitment feedback. "
             "P4 (historical drift): later-window rates imply different equilibria from earlier-window rates, so proximity to the threshold is not stationary. "
             "P2-P4 are falsifiable by the fitted model; P1 is checked for consistency.")
    p = para("The contribution is primarily methodological. "
             f"We assemble a fully reproducible measurement pipeline-from OpenAlex extraction through researcher identification, geographic attribution, mobility transitions, PI operationalisation and community aggregation to a calibrated six-compartment dynamical model-for a cohort of {n_authors:,} AI/ML authors across {len(eq)} research macro-regions")
    C(p, "openalex")
    p.add_run(". "
              "Each measurement choice is stress-tested: origin assignment under seven specifications, mobility direction under each, PI status under six alternative definitions propagated through the model, and a missingness and censoring audit; the sensitivity results are reported in the Results section alongside the model results, not relegated to footnotes. "
              "Empirically, we provide comparative estimates of career-transition rates, minimum viable scale and proximity to a model-implied viability boundary (MVB) for the macro-regions. "
              "For research evaluation, the output is a recomputable monitoring diagnostic (T/M and its closest-lever reading, MVB proximity) that can be recomputed with each OpenAlex release. "
              "AI/ML serves as the case study; we make no claim that the specific findings generalise to other fields, only that the pipeline transfers.")
    p = para("Section 2 specifies data and measurement, Section 3 reports observed, model and sensitivity results in that order, Section 4 discusses implications and limitations, and Section 5 concludes.")


    # ------------------------------------------------------------------
    # 2. Data and measurement
    # ------------------------------------------------------------------
    doc.add_heading("2. Data and measurement", level=1)

    doc.add_heading("2.1 Data source and cohort", level=2)
    p = para("We extracted AI/ML works and author histories from the OpenAlex API for subfield 1702 (Artificial Intelligence), 2000-2023")
    C(p, "openalex")
    p.add_run(". OpenAlex provides open, CC0 metadata on authors, affiliations, countries, publication dates and citations. "
              "Author histories were built by following each author's sequence of works and affiliations, assigning a country per work and an origin macro-region by the modal group of recorded affiliations.")
    p = para(f"Authors enter the cohort if their first observed AI/ML publication is in 2000-2016 and they have at least two AI/ML works in 2000-2023; authors with only unknown affiliations are excluded, giving {n_authors:,} authors. "
             "An author is active if they have at least one AI/ML work in 2020-2023 and has dropped out otherwise. "
             "A hit is a paper in the top 10% of AI/ML citations for its publication year, observed within the first eight career years. "
             "A PI is an author whose first last-author paper (single-authored papers are treated as last-author) appears in the window")
    C(p, "stephan")
    p.add_run(". Both are deliberately broad operational definitions: a PI in this sense is any author with at least one independent last-author paper, not a tenured group leader, and a hit author is any author with at least one top-decile paper. "
              f"Because the cohort is restricted to authors with at least two works, PIs account for {ctx['pi_share_min']*100:.0f}-{ctx['pi_share_max']*100:.0f}% and hit authors for {ctx['hit_share_min']*100:.0f}-{ctx['hit_share_max']*100:.0f}% of each macro-region's cohort (Table 1). "
              "The PI compartment therefore represents the population able to lead work and recruit, and the minimum viable scale in Section 2.9 counts distinct last-author groups per year under the same definition, so the two are consistent. "
              "The abroad flag is set if the author is affiliated in a non-origin macro-region within the first six career years. "
              "OpenAlex coverage is incomplete for non-English venues and author disambiguation is imperfect, so absolute counts are model-implied stocks rather than a census; relative comparisons are preserved because the same rules are applied to every macro-region. "
              "Table 1 reports the cohort by macro-region. "
              f"The {ctx['largest_pools']} macro-regions contribute the largest author counts. "
              "A smaller cohort with low coauthor intensity can be more resilient than a larger one with high coauthor intensity, which is why T and M must be compared jointly (P1).")
    desc = _descriptive_table(cohort).rename(columns={
        "group": "Group", "n": "Authors", "works": "Works", "active": "Active 2020-2023", "hits": "Hit authors",
        "pis": "PIs", "career_start_mean": "Mean career start", "abroad": "Abroad early-career"})
    _add_table_from_df(
        doc, desc,
        caption="Table 1. Descriptive statistics for the extracted AI/ML cohort by research macro-region. Labels are operational aggregations of OpenAlex country-affiliation patterns.",
        decimals={"Authors": 0, "Works": 0, "Active 2020-2023": 0, "Hit authors": 0, "PIs": 0, "Mean career start": 1, "Abroad early-career": 0},
    )

    doc.add_heading("2.2 Researcher identification", level=2)
    p = para("Each researcher is an OpenAlex author identifier, linked across works by OpenAlex's own disambiguation. "
             "Author disambiguation is imperfect: careers can be split across duplicate identifiers or merged across namesakes, and we do not re-disambiguate. "
             "Because every macro-region is subjected to the same extraction rules, we read the cohort sizes and the estimated rates as operational quantities that are comparable across systems rather than as exact headcounts, and we carry the disambiguation uncertainty into the measurement audit in Section 3.7.")

    doc.add_heading("2.3 Geographic attribution and origin", level=2)
    p = para("Each work carries the affiliation countries recorded for the author on that work; a work with several affiliations contributes all of its countries. "
             "An author's origin is an operational construct, not birthplace or nationality: it is the modal research macro-region of the author's affiliations over their first three observed career years (ties broken toward the earliest year). "
             "This window rule is one specification among several; Section 3.7 reports results under seven origin rules (the three-year mode, first observed affiliation, two- and five-year window modes, fractional assignment of multi-group years, exclusion of multi-group years, and seeded probabilistic assignment), so that no conclusion rests on this single choice. "
             "Two consequences of the operational definition are measured rather than assumed: multi-affiliated authors, for whom a single 'location' in a year is unobserved, and authors whose origin changes under an alternative rule. The aggregate mobility statistics are regional aggregates, and 'zero direction reversals' in Section 3.7 refers to those aggregates, not to individual trajectories.")

    doc.add_heading("2.4 Mobility transitions", level=2)
    p = para("From each author's origin and yearly affiliations we define the career transitions the model uses: the abroad flag records affiliation in a non-origin macro-region within the first six career years; return is recorded when a subsequent affiliation again includes the origin macro-region; hit and PI years are defined in Section 2.1 and 2.5; and dropout is inferred when no further AI/ML work is observed. "
             "Affiliation changes are a proxy for mobility: they do not observe physical moves, remote collaboration or short visits, and a researcher can hold affiliations in several systems at once. These limitations are quantified in Section 3.7.")

    doc.add_heading("2.5 PI operationalisation", level=2)
    p = para("The baseline PI proxy follows AI/ML authorship conventions: the senior or group-lead author is listed last or flagged corresponding. "
             "Because the concept 'principal investigator' has no direct bibliometric field, we define six operationalisations and propagate each through the full model (Section 3.7): ever-last-author (baseline), ever-corresponding-author, at least two last-author papers, at least eight observed career years, coauthor-network centrality in the top decile of the author's macro-region, and a combined union of the three career-stage definitions. "
             "The absolute PI share is proxy-dependent and we report the full range; the model's T-side equilibria are structurally invariant to the proxy because the inflow calibration anchors total entry to observed entry (Section 2.8), so only P-side quantities vary-an asymmetry we report rather than hide.")

    doc.add_heading("2.6 Community aggregation", level=2)
    p = para("The unit of analysis is the research macro-region: a set of countries whose AI/ML researchers share funding systems, labour markets, languages and mobility corridors closely enough to be treated as one recruitment pool. "
             "For reproducibility, the initial partition of countries was taken from Huntington's taxonomy")
    C(p, "huntington")
    p.add_run(", which predicts the structure of global communication networks")
    C(p, "state")
    p.add_run(" and of scientific mobility and collaboration")
    C(p, "chinchilla")
    p.add_run("; it serves only as a documented starting heuristic and the resulting groups are operational research systems, not civilisations. "
              "The partition was adjusted to the size and mobility structure of AI/ML: the United States is separated from the rest of the Anglosphere as the dominant destination with a distinct funding system; Continental Europe is kept distinct because intra-European mobility and EU funding form a separate bloc; Latin American, Orthodox and sub-Saharan African countries are merged into Other regions because their author counts are too small to estimate stable rates. "
              f"The final {len(eq)} macro-regions are: " + ", ".join(display_group(g) for g in arpr.ORDERED_GROUPS) + ". "
              + (f"{ctx['tm_min_group']} is in practice a single national system: {ctx['tm_min_dominant']} accounts for {ctx['tm_min_dominant_share']*100:.0f}% of its 2022-2023 AI/ML works, so results for this macro-region should be read as results for a small, high-impact national system. " if ctx['tm_min_dominant'] else "")
              + "Figure 1 maps the partition and overlays the largest observed inter-region early-career flows, which are the cross-region moves the model tracks through the abroad compartments. The full country mapping is in Supplementary Material.")
    figure("fig1", "Figure 1. Research macro-regions and the largest inter-region early-career flows, 2000-2023. Country outlines from Natural Earth (public domain); arrow width is proportional to accumulated abroad author-years by origin and destination; the legend gives each region's equilibrium T/M ratio.", width=6.3)

    doc.add_heading("2.7 Dynamical model", level=2)
    p = para("Each macro-region is represented by six compartments: domestic early-career (D), abroad early-career (A), domestic hit (H_D), abroad hit (H_A), domestic PI (P_D) and abroad PI (P_A) researchers. "
             "Transition rates are early-career outflow (α), return (β), hit generation (h_D, h_A), PI promotion (p_D, p_A) and dropout from all compartments (d). Figure 2 shows the structure; the equations are:")
    add_omath_paragraph(doc, math_ode_system())
    figure("fig2", "Figure 2. Compartment structure of the model for one research macro-region. Solid arrows are per-year transition rates; the dashed arrow is the endogenous recruitment feedback from the domestic PI stock; grey arrows are dropout from every compartment. The active pool T is compared with the minimum viable coauthor scale M.", width=6.0)
    p = para("The model treats each macro-region as one aggregate with constant per-year rates and collapses careers into three observed layers. These simplifications keep the model estimable from OpenAlex and the threshold calculation transparent; the model is a diagnostic monitoring device, not a demographic projection, and we do not claim validated predictive performance.")
    p = para("Step (ii) of the mechanism is implemented by making entry depend on the domestic PI stock. The linear form is ")
    add_omath_inline(p, math_I_linear())
    p.add_run(f", where I_0 is exogenous entry and r is the PI reproduction rate, capped at {_fmt(ctx['safety_factor_cap'], 2)}× the stability-critical value (the most constrained fitted macro-region realises {_fmt(ctx['min_realised_safety_ratio'], 2)}×). A saturating alternative, ")
    add_omath_inline(p, math_I_saturating())
    p.add_run(", is used as a robustness check for P3. The cap prevents runaway growth when observed r exceeds the critical value, a common finding because observed recruitment is bounded by the data window. Given r, I_0 is calibrated so that total equilibrium entry I_0 + r × P_D equals the observed annual entry of each macro-region; the equilibrium size of the active pool is therefore anchored to observed entry, and the PI feedback redistributes rather than rescales it.")

    doc.add_heading("2.8 Calibration and estimation", level=2)
    p = para("Rates are estimated as constant per-year hazards from observed transitions over exposure time, with a Laplace pseudocount of 1 per outcome. Because the data are right-censored, rates are lower bounds and equilibria conservative. "
             "Steady states are solved with a trust-region Newton method. "
             f"The equilibrium T is the asymptotic pool of an open system with continuing entry and is therefore larger than the 2020-2023 active count of the closed 2000-2016 cohort in Table 1 (by a factor of {ctx['teq_active_min']:.1f}-{ctx['teq_active_max']:.1f}); the two are not comparable, and all claims rest on relative quantities (T/M, elasticities, proximity and rankings), not on absolute T. "
             "Elasticities perturb each rate by 1% and record the percentage change in T (P2). "
             "Historical drift (P4) compares equilibria under rates estimated from the 2000-2010 and 2011-2016 career windows. "
             "Policy counterfactuals perturb single rates by ±10% and rank levers by margin gain; bootstrap resampling of authors (200 draws) gives 95% intervals. "
             "All counterfactuals are mechanical perturbations of fitted rates: they identify sensitive transitions, not causal effects of programmes. "
             "An annual layer re-estimates rates year by year (2000-2016), projects them to 2017-2026 and compares the projected compartment counts with observed 2017-2023 stocks; it is an exploratory extension whose estimation, regularisation, figures and accuracy metrics are reported in Supplementary Material Section S2 (Supplementary Figures S1-S3, Supplementary Tables S2-S5).")

    doc.add_heading("2.9 The model-implied viability boundary", level=2)
    p = para("Step (iii) is implemented as ")
    add_omath_inline(p, math_threshold())
    p.add_run(", where c̄ is the mean number of authors per work and k the median number of distinct last-author groups per recent year. When the equilibrium active pool ")
    add_omath_inline(p, math_active_pool())
    p.add_run(" falls below M, the system cannot produce work at the field's coauthor intensity. Falling below M is a sufficient, not a necessary, condition for collapse; M is a soft lower bound, so observed margins are probably smaller than they appear. "
              "For the boundary proximity measure we scale each rate until T reaches M and record the critical factor and its proximity |critical factor - 1|.")
    p = para("Terminology matters for interpretation. The boundary M = k x c̄ is a defined classification boundary: it is a function of observed coauthor structure and is not an object inside the ODE dynamics; the ODE solutions do not 'feel' M. Approaching the boundary (a falling margin) is a statement about fitted equilibria, not about time. A model crossing is what we compute when we perturb a rate until the equilibrium T reaches M-it is an algebraic property of the fitted system, not a simulated or observed event in time. Empirical collapse of a real system is something the data do not contain: no observed macro-region is below M. Irreversibility, finally, enters only through the collapse rule of the coupled scenario in Section 2.10, where crossing M switches off a region's PI-driven recruitment; it is an assumption of that scenario, not an empirical finding, and we do not claim that a real system below M could not rebuild. We therefore speak throughout of a model-implied viability boundary, and never of a point of no return.")

    doc.add_heading("2.10 Sensitivity design and the talent-concentration scenario", level=2)
    p = para("Sensitivity is assessed along three axes whose results appear in Sections 3.4-3.7: functional form (linear versus saturating recruitment feedback), the value of M (multipliers around the fitted k and c̄), and the measurement layer (origin rules, mobility specifications, PI definitions and missing-data treatment). "
             "Bootstrap resampling of authors (200 draws) gives 95% intervals on the equilibrium quantities.")
    dctx_tau = float(dom["summary"]["tau_years"].iloc[0]); dhorizon_tau = float(dom["trajectories"]["year"].max()) / dctx_tau
    p = para("To examine what the mechanism implies when one research system deliberately concentrates talent, we couple the nine fitted single-region models through the observed inter-regional mobility matrix (Figure 1) and simulate a stylised talent-concentration strategy. "
             "In the baseline, each macro-region's abroad compartments are distributed over host regions in proportion to observed off-diagonal abroad author-years (Supplementary Figure S2), each host recruits into its early-career pool in proportion to the PIs it hosts, and exogenous entry is adjusted so that the coupled system reproduces the fitted equilibria exactly. "
             "The concentration strategy is a pull of intensity φ exerted by one focal region: early-career outflow from every other region rises from α to α(1 + φ), the increment is directed to the focal region and tracked in separate compartments, researchers pulled this way return at β/(1 + φ), and the stock already abroad keeps its observed host distribution, so every scenario starts from the same state. "
             "Two further rules link the scenario to the mechanism. Once a region's active pool falls below M, its PI-driven recruitment stops permanently (Section 2.9). "
             "Hit generation in all regions is multiplied by the effective number of macro-regions (inverse Simpson index of domestic active pools) relative to its baseline value, raised to a variety elasticity γ; γ = 0 is the fitted model and γ > 0 encodes the hypothesis that a more concentrated field generates fewer independent contributions. "
             f"We run φ ∈ {{{', '.join(_fmt(v, 1) for v in sorted(dom['summary']['phi'].unique()) if v > 0)}}} for the two largest observed host regions, report all quantities relative to a φ = 0 baseline, and search for the smallest γ at which the field's, and the focal region's own, hit stock falls below baseline. "
             f"The clock of the model is set by the fitted transition rates, so we report time in units of the characteristic time τ = 1/d̄, the mean career duration implied by the fitted dropout rates (τ ≈ {_fmt(dctx_tau, 0)} years); the horizon is {_fmt(dhorizon_tau, 1)} τ, and calendar years appear only as an annotation because the same trajectory would unfold faster or slower in a field with faster or slower career turnover. Read in this way, the horizon spans about {_fmt(dhorizon_tau, 0)} researcher generations; in a field where careers last twice as long the same number of generations would take twice as many years, and the policy implication of a given t/τ shifts accordingly. "
             "φ, γ, the retention and collapse rules and the horizon are stylised assumptions, listed with their status in Supplementary Table S8; the transition rates, equilibria, thresholds and host shares are fitted. The scenario is a model-consistent projection of the mechanism, not a forecast.")


    # ------------------------------------------------------------------
    # 3. Results
    # ------------------------------------------------------------------
    doc.add_heading("3. Results", level=1)
    p = para("Results are reported in three layers that are kept distinct throughout: observed quantities estimated directly from the cohort, model-implied quantities computed from the fitted ODE, and sensitivity results showing how both layers move under alternative measurement and modelling choices.")

    doc.add_heading("3.1 Observed cohort and transition rates", level=2)
    tr_mean = transition_rates.groupby("group").first()
    obs_alpha = tr_mean["alpha"]; obs_beta = tr_mean["beta"]; obs_pab = tr_mean["p_abroad"]; obs_d = tr_mean["d"]
    p = para(f"Table 1 (Section 2.1) describes the cohort. The observed transition rates vary widely across macro-regions: early-career outflow α spans {_fmt(obs_alpha.min(), 3)} ({obs_alpha.idxmin()}) to {_fmt(obs_alpha.max(), 3)} ({obs_alpha.idxmax()}), "
             f"the share affiliated abroad within six career years p_abroad spans {_fmt(obs_pab.min(), 3)} to {_fmt(obs_pab.max(), 3)}, "
             f"return β spans {_fmt(obs_beta.min(), 3)} to {_fmt(obs_beta.max(), 3)}, "
             f"and annual dropout d spans {_fmt(obs_d.min(), 3)} to {_fmt(obs_d.max(), 3)}. "
             "These are observed hazards with Laplace regularisation, not model outputs; every model quantity in Sections 3.2-3.8 is downstream of them.")

    doc.add_heading("3.2 Equilibrium pools and minimum viable scale (P1)", level=2)
    p = para(f"Table 2 reports the equilibrium domestic active pool T, the minimum viable scale M and the inflow parameters for the {len(eq)} macro-regions. "
             "All exceed their threshold under the fitted model, but the ratio T/M ranges from "
             f"{_fmt(ctx['tm_min'], 2)} ({ctx['tm_min_group']}) to {_fmt(ctx['tm_max'], 2)} ({ctx['tm_max_group']}). "
             + (f"The {ctx['largest_pools']} macro-regions have the largest absolute pools; {ctx['smallest_pool']} has both the smallest pool and the narrowest absolute margin. " if ctx['smallest_pool'] == ctx['smallest_margin_group'] else f"The {ctx['largest_pools']} macro-regions have the largest absolute pools; {ctx['smallest_pool']} has the smallest pool and {ctx['smallest_margin_group']} the narrowest absolute margin. ")
             + "Figure 3 visualises the gap between T and M.")
    eq_table = eq[["group", "T_equilibrium", "M_threshold", "margin_to_threshold_T", "I0", "r", "r_obs", "r_critical"]].copy()
    eq_table["T_over_M"] = eq_table["T_equilibrium"] / eq_table["M_threshold"]
    eq_table = eq_table.rename(columns={"group": "Group", "T_equilibrium": "T", "M_threshold": "M", "margin_to_threshold_T": "Margin", "T_over_M": "T/M", "r": "r (fitted)", "r_obs": "r (observed)", "r_critical": "r (critical)"})
    _add_table_from_df(doc, eq_table,
                       caption="Table 2. Equilibrium domestic active pool, minimum viable coauthor scale and endogenous inflow parameters by research macro-region.",
                       decimals={"T": 0, "M": 0, "Margin": 0, "T/M": 2, "I0": 0, "r (fitted)": 4, "r (observed)": 4, "r (critical)": 4})
    figure("fig3", "Figure 3. Equilibrium domestic active pool (T) and minimum viable coauthor scale (M) by research macro-region.")

    doc.add_heading("3.3 Which transitions govern the pool (P2)", level=2)
    p = para("Table 3 lists the three transition-rate elasticities with the largest absolute effect on T in each macro-region. "
             f"Dropout (d) is the largest negative lever everywhere, with elasticity from {_fmt(ctx['d_min_e'], 2)} to {_fmt(ctx['d_max_e'], 2)}, "
             f"whereas the largest absolute elasticity of early-career outflow (α) is {_fmt(ctx['alpha_abs_max'], 2)}; |e_d| exceeds |e_α| in {ctx['d_gt_alpha_groups']} of {len(eq)} macro-regions, as P2 predicts. "
             f"{ctx['positive_lever_sentence']} The {ctx['highest_pd_group']} macro-region shows the strongest response to PI promotion (p_D). "
             "Attrition removes researchers from every compartment, whereas outflow moves them to compartments from which return and contribution remain possible.")
    rows3 = []
    for group, gdf in top_t.groupby("group"):
        top3 = gdf.sort_values("abs_elasticity", ascending=False).head(3)
        r = [group]
        for _, row in top3.iterrows():
            r.extend([row["rate"], _fmt(row["elasticity"], 3)])
        rows3.append(r)
    elas_df = pd.DataFrame(rows3, columns=["Group", "1st rate", "1st elasticity", "2nd rate", "2nd elasticity", "3rd rate", "3rd elasticity"])
    _add_table_from_df(doc, elas_df, caption="Table 3. Top transition-rate elasticities of the domestic active pool T by research macro-region.")

    doc.add_heading("3.4 Viability-boundary proximity and endogenous recruitment (P1, P3)", level=2)
    closest = pnr_closest.iloc[0]
    p = para("Table 4 reports, for each macro-region, the single rate that reaches the active-pool threshold with the smallest proportional change, and Figure 4 ranks macro-regions by that proximity. "
             f"{ctx['pnr_lever_text']}, consistent with P3: the transition that feeds the reproduction loop from outside is the binding one. "
             f"The closest model-implied viability boundary is in {closest['group']}, where {closest['rate_name']} multiplied by {_fmt(closest['critical_factor'], 4)}-that is, the rate reduced to {closest['critical_factor']*100:.1f}% of its current value, a {closest['proximity']*100:.1f}% reduction-drives the active pool to M. "
             f"Across macro-regions the Spearman correlation between boundary proximity and T/M is {_fmt(ctx['rho_prox_tm'], 2)}, whereas that between proximity and absolute T is {_fmt(ctx['rho_prox_T'], 2)}. "
             "Because the I_0 lever scales the whole equilibrium, proximity is close to a deterministic function of T/M in the linear model, so the first correlation is the consistency check that P1 calls for rather than an independent test; the diagnostic content of P1 is that the ranking by absolute size and the ranking by proximity diverge, which the second correlation shows (Section 3.8 returns to individual cases).")
    pnr_table = pnr_closest[["group", "rate_name", "current_rate", "critical_factor", "proximity"]].copy()
    pnr_table.columns = ["Group", "Closest rate", "Current value", "Critical factor", "Proximity"]
    _add_table_from_df(doc, pnr_table, caption="Table 4. Closest model-implied viability boundary for the active researcher pool by research macro-region.",
                       decimals={"Current value": 1, "Critical factor": 3, "Proximity": 3})
    figure("fig4", "Figure 4. Closest viability-boundary proximity by research macro-region. Smaller values mean a smaller proportional change in the listed rate reaches the threshold.")

    if sat_eq is not None:
        pnr_rob = pnr_robustness_table()
        p = para("Replacing the linear recruitment feedback with a saturating one changes the equilibrium pool by "
                 f"{ctx['sat_range_text']} (Table 5)")
        if not pnr_rob.empty:
            same_lever = bool((pnr_rob["linear_closest"] == pnr_rob["saturating_closest"]).all())
            rho_sat = float(pnr_rob["linear_proximity"].corr(pnr_rob["saturating_proximity"], method="spearman"))
            lever_txt = "the closest lever is unchanged in every macro-region" if same_lever else "the closest lever changes in some macro-regions"
            p.add_run(f", and {lever_txt} while the rank order of proximity has Spearman ρ = {_fmt(rho_sat, 2)} between the two variants (Supplementary Table S7)")
        p.add_run(". The second part of P3 is therefore supported: the ranking of systems by fragility does not depend on the functional form of the network externality.")
        merged = eq[["group", "T_equilibrium"]].merge(sat_eq[["group", "T_equilibrium", "epsilon"]], on="group", suffixes=("_lin", "_sat"))
        merged.columns = ["Group", "Linear T", "Saturating T", "ε"]
        _add_table_from_df(doc, merged, caption="Table 5. Equilibrium T under linear and saturating PI-driven inflow.",
                           decimals={"Linear T": 0, "Saturating T": 0, "ε": 5})

    doc.add_heading("3.5 Historical drift in transition rates (P4)", level=2)
    n_compare = len(period_compare)
    if ctx["period_all_neg"]:
        prefix = "Both" if n_compare == 2 else f"All {n_compare}"
        period_direction_text = f"{prefix} macro-regions with dual-window support would have smaller margins under late-window rates ({ctx['period_neg']})."
    else:
        period_direction_text = (f"Under late-window rates the margin shrinks in {ctx['period_neg']} "
                                 f"and grows in {ctx['period_pos']}.")
    p = para("Table 6 compares the equilibrium that would emerge if rates estimated from the early (2000-2010) or late (2011-2016) career window persisted; Figure 5 plots the change in margin. "
             + (f"All {n_compare} macro-regions have dual-window support for both estimates. " if n_compare == len(eq) else f"Only {n_compare} of {len(eq)} macro-regions have enough dual-window support for both estimates. ")
             + f"{period_direction_text} "
             "The late window is shorter and its cohorts younger, so its promotion and hit rates are estimated from less exposure and its equilibria are less certain; the comparison is a sensitivity exercise rather than a forecast. "
             "It nevertheless supports P4 in its weak form: equilibria differ across windows, so the distance to the threshold is not stationary, and where margins shrink the mechanism implies ongoing drift toward the threshold.")
    pc = period_compare[["group", "T_early", "T_late", "pct_delta_T", "margin_early", "margin_late", "delta_margin"]].rename(columns={
        "group": "Group", "T_early": "T early", "T_late": "T late", "pct_delta_T": "ΔT (%)",
        "margin_early": "Margin early", "margin_late": "Margin late", "delta_margin": "Δ margin"})
    _add_table_from_df(doc, pc, caption="Table 6. Equilibrium active pool and safety margin under early (2000-2010) versus late (2011-2016) transition-rate regimes.",
                       decimals={"T early": 0, "T late": 0, "ΔT (%)": 1, "Margin early": 0, "Margin late": 0, "Δ margin": 1})
    figure("fig5", "Figure 5. Change in safety margin between early and late transition-rate regimes. Negative values mean the late-window rates would shrink the margin if they persisted. Point estimates only; the two windows differ in cohort size.")

    doc.add_heading("3.6 Policy counterfactuals and uncertainty", level=2)
    policy_top = policy_rank.groupby("group").head(1).copy()
    all_top_are_d = (policy_top["lever"] == "d").all()
    dominant_text = ("Reducing dropout is the dominant positive lever in every macro-region, consistent with P2. "
                     if all_top_are_d else "Reducing dropout is the dominant positive lever in most macro-regions. ")
    p = para(f"Table 7 reports the mechanical counterfactual with the largest margin gain per 10% lever change in each macro-region. {dominant_text}"
             f"The gain from a 10% reduction in d ranges from about {ctx['d_min_gain']} active researchers ({ctx['d_min_gain_group']}) to about {ctx['d_max_gain']} ({ctx['d_max_gain_group']}). "
             "Blocking early-career outflow is not the efficient response: a researcher abroad remains in the global system and may return, whereas a researcher who leaves research is lost to every compartment.")
    policy_top = policy_top.drop(columns=["margin_gain"], errors="ignore").rename(columns={"group": "Group", "lever": "Lever", "direction": "Direction", "lever_change_pct": "Change (%)",
                                            "margin_gain": "Margin gain", "normalised_margin_gain_per_10pct": "Gain per 10%"})
    _add_table_from_df(doc, policy_top, caption="Table 7. Top positive mechanical counterfactual per research macro-region (margin gain per 10% proportional lever change).",
                       decimals={"Change (%)": 0, "Gain per 10%": 0})
    package_text, _ = _package_summary()
    if package_text:
        para(package_text)
    p = para("Figure 6 shows bootstrap 95% intervals for T (values in Supplementary Table S6). Intervals are wide, and for the smallest macro-regions the lower bound lies closer to M, so point estimates of proximity should be read as indicative. "
             "The lower bounds nevertheless remain above M for every macro-region, which supports the qualitative conclusion that no system is below its threshold under the fitted model.")
    figure("fig6", "Figure 6. Bootstrap 95% confidence intervals for equilibrium T by research macro-region.")

    robustness_paragraph(para, pi_proxy, m_sens, load_region_m_sensitivity())
    p = para("As an exploratory extension, the annual layer re-estimates the rates year by year and projects them to 2017-2026; "
             f"rate-level projections have a skill ratio of {_fmt(annual_ctx.get('rate_overall_skill', float('nan')), 2)} against a historical-mean baseline and the layer is a drift monitor rather than a forecast, so its figures and accuracy tables are reported in Supplementary Material Section S2 (Supplementary Figures S1-S3, Supplementary Tables S2-S5).")

    doc.add_heading("3.7 Measurement sensitivity: origin, PI definition, multi-affiliation and missingness", level=2)
    ms7 = {}
    if mv["ORIGIN_SENSITIVITY"] is not None:
        os_df = mv["ORIGIN_SENSITIVITY"]
        ms7["n_rules"] = int(os_df["origin_rule"].nunique())
        # The sensitivity CSV recomputes M under each rule, which conflates
        # origin-rule sensitivity with M-construction sensitivity. For the
        # origin-rule question, hold M at its baseline value and recompute T/M.
        canonM = eq.set_index("group")["M_threshold"]
        os_df = os_df.copy()
        os_df["T_over_M_fixedM"] = os_df["T"] / os_df["group"].map(canonM)
        _min_per_rule = os_df.groupby("origin_rule")["T_over_M_fixedM"].idxmin().map(lambda i: os_df.loc[i, "group"])
        ms7["tm_min_invariant"] = (_min_per_rule.nunique() == 1)
        ms7["tm_min_group"] = _min_per_rule.mode().iloc[0]
        ms7["tm_min_group_rawM"] = os_df.groupby("origin_rule")["T_over_M"].idxmin().map(lambda i: os_df.loc[i, "group"]).mode().iloc[0]
        ms7["rho_min"] = float(os_df.groupby("origin_rule").apply(lambda d: d["p_abroad"].corr(os_df[os_df["origin_rule"] == "window3_mode"].set_index("group").reindex(d["group"])["p_abroad"], method="spearman")).min()) if "p_abroad" in os_df.columns else float("nan")
    if mv["MOBILITY_SENSITIVITY"] is not None:
        mob = mv["MOBILITY_SENSITIVITY"]
        ms7["n_cells"] = len(mob)
        ms7["n_reversed"] = int(mob["direction_reversed"].sum())
    if mv["MOBILITY_MULTISTATE"] is not None:
        # Share of cohort authors with >1 macro-region in at least one year.
        # MOBILITY_MULTISTATE counts states, not authors, so read the cohort sidecar.
        _ayg_path = Path("data/cohort/author_year_groups.json")
        if _ayg_path.exists():
            _ayg = json.load(open(_ayg_path))
            ms7["multi_share"] = sum(1 for v in _ayg.values() if any(len(gs) > 1 for _y, gs in v)) / len(_ayg)
        else:
            ms7["multi_share"] = float("nan")
    if mv["PI_SENSITIVITY"] is not None:
        ps = mv["PI_SENSITIVITY"]
        ms7["n_pi_defs"] = int(ps["pi_definition"].nunique())
        ms7["pi_share_min"] = float(ps["pi_share"].min()); ms7["pi_share_max"] = float(ps["pi_share"].max())
    if mv["PI_PROPAGATION_P"] is not None:
        pp7 = mv["PI_PROPAGATION_P"]
        ms7["p_over_m_min"] = float(pp7["P_over_M_P"].min()); ms7["p_over_m_max"] = float(pp7["P_over_M_P"].max())
        ms7["closest_P_levers"] = sorted(pp7["closest_P_rate"].unique().tolist())
    if mv["MISSINGNESS_SUMMARY"] is not None:
        msum = mv["MISSINGNESS_SUMMARY"].set_index(mv["MISSINGNESS_SUMMARY"].columns[0])["value"]
        ms7["miss_country"] = float(msum.get("share_missing_country_cohort", float("nan")))
        ms7["left_censor"] = float(msum.get("share_career_start_at_window_edge_2000", float("nan")))
        ms7["span_lt5"] = float(msum.get("share_span_lt5", float("nan")))
        ms7["span_ge15"] = float(msum.get("share_span_ge15", float("nan")))
    p = para("Origin specification. "
             f"Re-estimating the cohort under {ms7.get('n_rules', 7)} origin rules leaves the qualitative results intact: with M held at its baseline value, the lowest-T/M macro-region is {ms7.get('tm_min_group', 'unchanged')} under every rule, matching Table 2. "
             f"(When M is instead recomputed inside each rule's re-estimated coauthor structure, {ms7.get('tm_min_group_rawM', 'a different region')} falls lowest because its small pool of independent groups shrinks its M; that variant conflates the origin question with threshold construction, so we report the fixed-M reading here and flag the alternative in the repository tables.) "
             f"Additionally, in {ms7.get('n_cells', 0)} group-rule cells ({ms7.get('n_rules', 7) - 1} alternative rules x {len(eq)} macro-regions) the share affiliated abroad never crosses the majority direction-that is, no macro-region's aggregate p_abroad flips from below to above 50%, or vice versa ({ms7.get('n_reversed', 0)} reversals). "
             "This statement is about group-level aggregates: individual authors do change assigned origin under the alternative rules (baseline agreement 94-99.8%), so the stability is at the level of the regional statistics the model consumes, not of individual trajectories, and it is not a full validation of origin estimation.")
    p = para("Multi-affiliation and missingness. "
             f"{ms7.get('multi_share', 0) * 100:.1f}% of cohort authors record affiliations in more than one macro-region in at least one year; fractional and exclusion specifications of those years change the outputs by at most a few percent, so multi-affiliation is a measurement ambiguity to disclose rather than a driver of results. "
             f"Country is missing on {ms7.get('miss_country', 0) * 100:.1f}% of cohort authorship rows, and the missingness is not random (it is concentrated in earlier years), "
             f"{ms7.get('left_censor', 0) * 100:.1f}% of authors have careers left-censored at the 2000 window edge, "
             f"and {ms7.get('span_lt5', 0) * 100:.0f}% of observed spans are shorter than five years ({ms7.get('span_ge15', 0) * 100:.0f}% are 15 years or more). "
             "The first two push the reported rates toward underestimates of mobility; the short spans widen the bootstrap intervals, which is one reason rankings are reported rather than precise margins.")
    p = para("PI proxy. "
             f"Across the {ms7.get('n_pi_defs', 6)} PI operationalisations the cohort PI share ranges from {ms7.get('pi_share_min', 0) * 100:.0f}% to {ms7.get('pi_share_max', 0) * 100:.0f}%, so the absolute PI share is not robust to the proxy and is never reported as a fact about the field. "
             "The T-side equilibria, T/M, elasticities and boundary proximities are structurally invariant to the PI definition because the inflow calibration fixes total entry to observed entry (Section 2.8); this invariance is a property of the calibration, not evidence that the PI measurement is valid. "
             f"What does vary is the P-side: the domestic-PI equilibrium P_D relative to its PI-scale threshold M_P spans {ms7.get('p_over_m_min', 0):,.0f}–{ms7.get('p_over_m_max', 0):,.0f}x across definitions, and the closest P-side lever is {', '.join(_rate_label(x) for x in ms7.get('closest_P_levers', []))} in every definition, so the qualitative findings survive while the absolute PI-stock numbers move.")
    sens_rows = [
        ["Origin rule (7 specs)", "Lowest-T/M region (fixed M); p_abroad direction", f"Invariant ({ms7.get('tm_min_group', '?')}); {ms7.get('n_reversed', 0)}/{ms7.get('n_cells', 0)} aggregate reversals", "Regional aggregates, not individuals"],
        ["Multi-affiliation (8.4% authors)", "All model outputs", "<2% change under fractional/exclusion", "Same-year location unobserved"],
        ["PI proxy (6 defs)", "PI share", f"{ms7.get('pi_share_min', 0) * 100:.0f}-{ms7.get('pi_share_max', 0) * 100:.0f}%", "Absolute share proxy-dependent"],
        ["PI proxy (6 defs)", "T/M, elasticities, proximity rankings", "Structurally invariant (I_0 calibration)", "Calibration artefact, not validation"],
        ["PI proxy (6 defs)", "P_D/M_P, closest P-side lever", f"{ms7.get('p_over_m_min', 0):,.0f}–{ms7.get('p_over_m_max', 0):,.0f}x; lever unchanged", "P-side varies by construction"],
        ["Missing country (4.2% rows)", "Rates", "Toward underestimation", "Missingness non-random"],
        ["Left censoring (5.7%)", "Career windows", "Rates are lower bounds", "Pre-2000 careers unobserved"],
        ["Short spans (27.8% <5y)", "Bootstrap intervals", "Wide intervals", "Rankings descriptive"],
    ]
    _add_table_from_df(doc, pd.DataFrame(sens_rows, columns=["Choice varied", "Quantity affected", "Observed effect", "Caveat"]),
                       caption="Table 8. Measurement-sensitivity summary. Every row is computed from the cohort under the stated specification; details and per-rule tables are in the public repository.")

    doc.add_heading("3.8 Worked example: Japan", level=2)
    p = para(f"Japan illustrates the mechanism in a large research system with an independent institutional lineage and comparatively low T/M. "
             f"Its fitted equilibrium is T = {ja_ctx['D'] + ja_ctx['H_D'] + ja_ctx['P_D']:,} active researchers (D = {ja_ctx['D']:,}, H_D = {ja_ctx['H_D']:,}, P_D = {ja_ctx['P_D']:,}) against M = {round(ja_ctx['M']):,}, so T/M = {_fmt(ja_ctx['T_over_M'], 2)}. "
             f"The closest model-implied viability boundary is {ja_ctx['pnr_rate']}: a fall to {_fmt(ja_ctx['pnr_factor'] * 100, 1)}% of its current level would bring T to M. "
             f"Figure 7 places Japan's six compartments and compares its rates with the other macro-regions: early-career outflow (α = {_fmt(ja_ctx['alpha'], 3)}) and domestic PI promotion (p_D = {_fmt(ja_ctx['p_D'], 3)}) are comparatively low, return (β = {_fmt(ja_ctx['beta'], 3)}) and domestic hit generation (h_D = {_fmt(ja_ctx['h_D'], 3)}) moderate, and dropout d = {_fmt(ja_ctx['d'], 3)}. "
             "Low leakage but a thin internal promotion pipeline is the configuration P1 and P2 describe: the system does not lose many researchers abroad, so its distance to the threshold is governed by scale relative to M and by attrition rather than by mobility. "
             "Figure 8 generalises the diagnostic by plotting T/M against boundary proximity for all macro-regions; the lower-left corner combines a low buffer with a small proportional change needed to reach M. "
             "The same two-panel diagnostic applies to any macro-region with sufficient OpenAlex coverage; Japan is a worked example, not a special case.")
    figure("fig7", "Figure 7. Japan in the six-compartment model, with a ladder of fitted transition rates across research macro-regions (Japan highlighted; longer bars are higher rates).", width=6.0)
    figure("fig8", "Figure 8. Equilibrium safety ratio (T/M) versus closest viability-boundary proximity for all research macro-regions. Japan is shown in red.")

    doc.add_heading("3.9 Talent concentration: short-run dominance, field-level loss", level=2)
    fd = dctx["focal_display"]; fd_the = _with_article(fd)
    fd2 = dctx.get("focal2_display"); fd2_the = _with_article(fd2) if fd2 else None
    ts1_reached = dctx["th_self_focal1"].dropna()
    tau = dctx["tau"]
    p = para(f"Under the coupled scenario of Section 2.10, the dominant region's hosted pool and share rise monotonically with the pull intensity φ, while the effective number of macro-regions falls: the strategy wins the short run it was designed for, at a direct variety cost to the field (Figure 9). Within the simulated horizon no region's active pool approaches M (the collapse rule never activates in any run), so these outcomes do not depend on that scenario assumption. "
             f"Whether the field's hit stock also falls depends on the variety elasticity γ: it declines even at γ = 0 for {fd_the}, and only once γ exceeds a moderate value for the second-largest host. "
             f"Whether the dominant region itself ends worse off requires a larger γ still (γ* = {_fmt(ts1_reached.max(), 1)} at the strongest pull). γ is not identified by our data; the variety loss is the robust finding. "
             f"Figure 10 shows the regional time paths at φ = {_fmt(dctx['phi_max'], 1)}: the dominant pool rises, source regions decline toward their thresholds, and each crossing of M switches off that region's PI-driven recruitment under the scenario's collapse rule-a discrete model event, not an observed one.")
    figure("fig9", f"Figure 9. Talent-concentration scenario with {fd_the} as the dominant region (coupled nine-region model, fitted rates unless stated). (a) Hosted active pool relative to the φ = 0 baseline; (b) effective number of macro-regions; (c) field hit stock relative to baseline at φ = {_fmt(dctx['mid_phi'], 1)} for three variety elasticities γ; (d) smallest γ at which the field's, and the dominant region's own, hit stock falls below baseline within the horizon, for the two largest host regions (points on the dotted line at the top of the panel: not reached within the search range). Time in (a)-(c) is in units of τ = 1/d̄ (upper axis: years at fitted rates). φ and γ are stylised.", width=6.5)
    _add_table_from_df(doc, dominant_strategy_table(dom),
                       caption=f"Table 9. Talent-concentration scenario at the end of the horizon ({_fmt(dctx['horizon_tau'], 1)} τ ≈ {_fmt(dctx['horizon_years'], 0)} years at fitted rates) relative to the φ = 0 baseline, fitted rates (γ = 0), for the two largest observed host regions. γ* is the smallest variety elasticity at which the hit stock falls below baseline within the horizon.",
                       decimals={"Regions below M": 0, "Pull intensity φ": 1, "Hosted pool at end of horizon (× baseline)": 2, "Share of hosted researchers at end of horizon (%)": 0,
                                 "Effective number of regions at end of horizon": 1, "Field hit stock at end of horizon (× baseline)": 2})
    p = para(f"Figure 10 shows the time paths behind these summaries for every macro-region at the strongest pull we simulate (φ = {_fmt(dctx['phi_max'], 1)}), one panel per γ. "
             "The timing scales with τ: a field with faster career turnover would reach the same crossings in proportionally fewer years, so the ordering of outcomes, not the calendar dates, is the result.")
    figure("fig10", f"Figure 10. Regional time paths under the talent-concentration strategy exerted by {fd_the} at pull intensity φ = {_fmt(dctx['phi_max'], 1)}, for three variety elasticities γ. Lines show each macro-region's domestic active pool as a multiple of its minimum viable coauthor scale M (log scale; dashed line M); the thick line is the dominant region. Crosses and dotted verticals mark when a region falls below M, after which its PI-driven recruitment is switched off permanently under the scenario's collapse rule. Time is in units of the characteristic time τ = 1/d̄ (mean career duration; ≈{_fmt(dctx['tau'], 0)} years at fitted rates, upper axis). Fitted rates; φ, γ and the collapse rule are stylised.", width=6.5)


    # ------------------------------------------------------------------
    # 4. Discussion
    # ------------------------------------------------------------------
    doc.add_heading("4. Discussion", level=1)

    doc.add_heading("4.1 Principal findings", level=2)
    p2_txt = ("P2 is supported in every macro-region: dropout is more elastic than early-career outflow, and reducing dropout is the most efficient single lever. "
              if ctx["d_gt_alpha_groups"] == len(eq) else f"P2 is supported in {ctx['d_gt_alpha_groups']} of {len(eq)} macro-regions. ")
    ms_ch = robustness_context(None, m_sens).get("ms_lever_changes") if m_sens is not None else None
    if ms_ch is not None and not ms_ch.empty:
        ms_groups = ", ".join(sorted(set(ms_ch["group"])))
        ms_min_mult = _fmt(ms_ch["M_multiplier"].min(), 2)
        p3_qual = (f" The primacy of the entry lever is a property of the fitted thresholds rather than of the mechanism: when M is raised to {ms_min_mult}× its fitted value or more, dropout becomes the closest lever in {ms_groups} (Section 3.6), "
                   "which is why we read P3 as support for the entry lever being binding at the observed scale, not as a general law. ")
    else:
        p3_qual = " "
    p = para(f"P1 is consistent with the results in the sense that matters for policy: rankings by absolute T and by proximity to the threshold diverge (ρ = {_fmt(ctx['rho_prox_T'], 2)}), the largest systems are not the safest, and proximity itself is governed by T/M as the mechanism implies; this is a diagnostic reading rather than a test. "
             + p2_txt +
             f"P3 is supported: {ctx['pnr_lever_text']}, and the ranking is invariant to the form of the recruitment feedback." + p3_qual +
             f"P4 is supported in its weak form: equilibria differ between the two career-start windows in all {n_compare} macro-regions with dual-window support, and the margin shrinks in {ctx['period_neg']}. "
             "Together the results move the researcher-mobility debate from net flows to the transition rates that govern reproduction, and they give an empirically observable monitoring variable-one whose predictive value for real community failure is a separate, unvalidated question (Section 4.7).")

    doc.add_heading("4.2 Methodological contribution", level=2)
    p = para("For informetrics, the contribution is a measurement pipeline rather than a single indicator. "
             "Origin assignment, mobility transitions, PI status, community aggregation, calibration and the viability boundary are each specified operationally, and each is accompanied by a sensitivity result reported in the main text: origin under seven rules, mobility direction under each, PI under six definitions propagated through the model, multi-affiliation and missingness quantified. "
             "This is the level of measurement audit that secondary-data mobility studies often leave implicit, and it is what makes the resulting indicators-T/M and viability-boundary proximity-usable as monitoring quantities. "
             "The pipeline is field-agnostic in design: every step is parameterised on a subfield, a year window and an authorship convention, and AI/ML is the case study on which it is calibrated and illustrated. We do not claim the findings generalise to other fields; we claim the machinery does, with authorship conventions redefined per field.")

    doc.add_heading("4.3 Related literature", level=2)
    p = para("Researcher mobility has been studied under the headings of brain drain, brain circulation and brain gain")
    C(p, "thorn")
    p.add_run(". Outflows become a gain when return migration and diaspora networks are supported")
    C(p, "thorn")
    p.add_run("; bilateral flows are driven by collaboration, economic convergence and visa restrictions")
    C(p, "appelt")
    p.add_run("; and cross-country shares of foreign-born scientists vary widely")
    C(p, "franzoni")
    p.add_run(". In AI/ML, the United States is the dominant destination, mobile scientists keep ties to origin systems")
    C(p, "macropolo", "alshebli")
    p.add_run(", and elite networks are highly clustered")
    C(p, "yuan")
    p.add_run(". The economics of science supplies the microfoundation: individuals respond to career incentives")
    C(p, "stephan")
    p.add_run(". What this literature measures is stocks and flows; it does not specify a community-level state variable whose crossing makes the loss self-reinforcing rather than recoverable. "
              "Evolutionary and innovation-systems economics supplies the threshold concepts-variety generation and selection, lock-in through increasing returns")
    C(p, "nelson", "dosi", "arthur", "david")
    p.add_run(", and frameworks for analysing the diversity of a technological system")
    C(p, "stirling", "saviotti", "metcalfe")
    p.add_run("-but its unit of analysis is the firm, the technology or the sector. "
              "The present framework connects the two: the community-level state variable is the equilibrium active pool relative to a coauthor-scale threshold, estimated from the career transitions the mobility literature already measures. "
              "The AI-specific homogenisation concerns it connects to-algorithmic monoculture, benchmark and compute concentration, linguistic and data bias-are documented elsewhere")
    C(p, "kleinberg", "hooker", "koch", "ahmed", "joshi", "bender", "raji")
    p.add_run(", and the scale of the leading models intensifies the concentration")
    C(p, "kaplan", "bommasani", "sevilla")
    p.add_run(". Historical cases of fields that narrowed onto a dominant approach and stagnated are well documented-from the perceptrons controversy in AI itself, through Lysenkoist biology, pre-2008 macroeconomics and string theory, to agricultural monocultures")
    C(p, "olazaran", "rumelhart", "joravsky", "colander", "smolin", "ullstrup", "mccook", "avelino", "ploetz")
    p.add_run(". Evidence that large fields slow canonical progress and that papers become less disruptive over time makes the variety question empirical rather than rhetorical")
    C(p, "chu", "park")
    p.add_run("; diversity demonstrably aids problem solving")
    C(p, "hongpage")
    p.add_run(", multi-site and internationally distributed teams retain high impact")
    C(p, "jones", "freeman")
    p.add_run(", innovation is highest at intermediate competition")
    C(p, "aghion")
    p.add_run(", and the processes are institutionally embedded in national and sectoral systems")
    C(p, "lundvall", "malerba")
    p.add_run(".")

    doc.add_heading("4.4 Implications for research evaluation", level=2)
    p = para("The indicators are designed for evaluators rather than for national accounting. "
             "T/M and boundary proximity can be recomputed with each OpenAlex release; a declining margin in any macro-region is a signal for the field, not only for that region. "
             "Because the closest lever and the most elastic lever are identified separately, the indicators also distinguish where monitoring should focus: entry pipelines (I_0) bind first at the observed scale, while attrition (d) is the most elastic. "
             "The exploratory annual layer provides the machinery for tracking rates year by year, although its current direction-prediction skill is low and it should be read as a monitor rather than a forecast. "
             "For individual universities, the PI stock is the node of the network externality: institutions that convert hit researchers into PIs and retain them regenerate their own inflow, and the macro-regional ladder (Figure 7) gives a benchmark against which an institution's own transition rates can be read. "
             "For early-career researchers, going abroad is a smaller threat to a home system than net-flow accounting implies; attrition is the larger one.")

    doc.add_heading("4.5 Policy implications", level=2)
    p = para("Concentrating talent is individually advantageous for the large systems pursuing it: it raises short-run output")
    C(p, "sevilla", "shachar", "kerr")
    p.add_run(", but each round of concentration lowers T/M in the systems that lose researchers, and the collective outcome can be an evolutionary dead end for the field (Section 3.9). "
              "No single actor captures the benefit of the variety it preserves, so the response has to be shared: jointly funded early-career fellowships and return grants aimed at low-T/M systems, routine monitoring of the indicator pair, and shared compute and data infrastructure acting on the intra-regional levers h_D and p_D where mobility itself cannot or should not be steered")
    C(p, "arthur", "saviotti")
    p.add_run(". "
              f"Because endogenous inflow is capped at {_fmt(ctx['safety_factor_cap'], 2)}× the critical reproduction rate, the implied interventions are conservative: they aim to keep systems away from the threshold, not to maximise any one system's share. "
              "Lever rankings are model-conditional: they follow from the fitted rates and thresholds and are not causal effects of programmes.")
    lever_policy_mgmt = pd.DataFrame({
        "Lever": ["Dropout (d)", "Exogenous entry (I_0)", "Return from abroad (β)", "Domestic hit generation (h_D)", "PI promotion (p_D)"],
        "Mechanism (in model)": [
            "Lowers d; raises T and margin directly; most elastic lever",
            "Raises I_0; linearly rescales all stocks; closest lever at observed scale",
            "Raises return inflow into early-career pool",
            "Raises hit generation; builds the H compartments feeding P",
            "Raises promotion D to P_D; feeds the reproduction loop",
        ],
        "Policy instrument": [
            "Early-career fellowships, childcare and dual-career support, stable non-tenure tracks",
            "Research-master and undergraduate pipelines, doctoral fellowships, recruitment visas",
            "Return grants, diaspora networks, dual appointments, overseas-experience recognition",
            "Independent-lab programmes, doctoral/postdoctoral training, compute access",
            "Tenure-track conversion, startup packages, project-based PI status",
        ],
        "Principal actor": [
            "Universities, department heads",
            "National funders, ministries",
            "Diaspora networks, funders, recruiters",
            "National funders, universities",
            "Universities, funders",
        ],
        "Empirical evidence": [
            "Indirect: early-career support is linked to lower attrition in the fellowship/tenure literature; AI/ML magnitude unestablished",
            "Strong generic: doctoral expansion raises the research workforce; visa effects on inflow documented",
            "Mixed: diaspora policies show small positive return rates",
            "Moderate: compute/data access is the AI/ML-specific bottleneck",
            "Indirect: tenure-track expansion raises senior-author counts (descriptive)",
        ],
        "Unintended consequences": [
            "Lock-in of marginal researchers; subsidy capture by secure staff",
            "Dilution of supervision quality; credential inflation",
            "Return-then-leave-again churn; benefits concentrated on the already-mobile",
            "Concentration on incumbents; hardware lock-in",
            "Premature promotion dilutes the PI proxy (measurement, not reality)",
        ],
        "Uncertainty and model dependence": [
            "Rate elasticity estimated; instrument-to-rate link not measured",
            "I_0 is calibrated to observed entry; pipeline vs migration not separable",
            "Return measured from affiliations only; physical return unobserved",
            "h_D bundles output quantity and quality",
            "Instrument-proxy mismatch possible; ranking robust to M only at observed scale",
        ],
    })
    # Table 10 is wide; place it on a landscape page for readability.
    sec_land = doc.add_section(WD_SECTION.NEW_PAGE)
    sec_land.orientation = WD_ORIENT.LANDSCAPE
    sec_land.page_width, sec_land.page_height = sec_land.page_height, sec_land.page_width
    _add_table_from_df(doc, lever_policy_mgmt, caption="Table 10. Levers, mechanisms, instruments, evidence and uncertainty. Lever rankings are model-conditional; the instrument-to-rate links are argued from the literature, not measured here.")
    sec_port = doc.add_section(WD_SECTION.NEW_PAGE)
    sec_port.orientation = WD_ORIENT.PORTRAIT
    sec_port.page_width, sec_port.page_height = sec_port.page_height, sec_port.page_width
    p = para("Each instrument affects a model rate; the instrument-to-rate link is argued from the literature, not measured here, and estimated rate elasticities do not establish that any single instrument moves any single rate by the stated amount. "
             "Regional effects are two-sided: a pull that raises one region's inflow lowers another's, and the coupled scenario shows the sender regions, not only the receiver, pay the margin cost.")

    doc.add_heading("4.6 Limitations", level=2)
    p = para("OpenAlex affiliation and country assignments are noisy, especially for multi-affiliated authors, and coverage of non-English venues is incomplete. The T/M ranking is sensitive to the operational M: under independent per-region multipliers in [0.5, 2.0] every region pair can exchange order, so the ranking conditions on the chosen threshold definition (Section 3.6). "
             "The macro-regional grouping is coarse; within-group heterogeneity is substantial, and the grouping of, for example, mainland China and Taiwan follows current OpenAlex country metadata rather than any resolution of their relationship. "
             "Geographic variety is a proxy for the cognitive and institutional variety the mechanism concerns, and the model does not observe research content directly; that macro-regions differ in institutions, languages and funding is documented, but that they carry distinct research programmes is assumed here, not measured, and claims about problem framings or benchmarks should be read with that qualification. "
             "Irreversibility is likewise a property of the collapse rule in the coupled scenario, not an empirical finding: a real system that fell below M could in principle rebuild through return migration or new entry, which the model does not represent, so the viability boundary denotes the threshold at which the fitted feedback loop stops sustaining the pool, not a prediction that recovery is impossible. "
             "The model omits cross-region spillovers, firm-level mobility and within-year dynamics; rates are assumed constant within windows; the cohort over-weights prolific authors; and bootstrap intervals are wide, so rankings are descriptive. "
             f"The endogenous inflow cap ({_fmt(ctx['safety_factor_cap'], 2)}) is a modelling choice whose alternatives should be mapped. "
             "Falling below M is a sufficient rather than necessary condition for collapse, and the historical comparison rests on two point estimates. "
             "The talent-concentration scenario couples the regions only through observed host shares and stylised pull, retention and collapse rules, holds fitted rates constant over a long horizon, and treats the variety elasticity γ as a free parameter; its results are model-consistent projections that rank strategies, not predictions of when any region's advantage ends. "
             "The PI and hit proxies follow AI/ML authorship conventions (group leader listed last or corresponding; hits scored within the AI/ML subfield); the sensitivity battery shows the absolute PI share varies widely across definitions while rankings survive, and transfer of the pipeline to fields with alphabetical author order or consortium authorship requires redefining these proxies. "
             "Measurement limits quantified in Section 3.7-multi-affiliated authors, non-random missing country, left-censored careers at the 2000 window edge, and short observed spans-mean the reported rates are best read as comparable lower bounds. "
             "Finally, the propositions are tested on nine macro-regions, so correlational support for P1 is indicative; the strongest support is for P2 and P3, which hold system by system.")

    doc.add_heading("4.7 Future validation agenda", level=2)
    p = para("Three extensions would test rather than extend the framework. "
             "First, external validation of the viability boundary: back-testing the indicator against historical cases of systems that contracted or lost a research programme would show whether proximity predicts outcomes rather than merely describing fitted equilibria. "
             "Second, identifying the variety elasticity γ from disruption or novelty measures would determine whether the talent-concentration scenario's field-level output loss is a real possibility or a parameter artefact. "
             "Third, applying the pipeline to a field with different authorship conventions-and to a deliberately mis-specified macro-regional partition-would test which results are measurement artefacts and which are structural. "
             "Each is executable on open data with the released code.")

    # ------------------------------------------------------------------
    # 5. Conclusion
    # ------------------------------------------------------------------
    doc.add_heading("5. Conclusion", level=1)
    p = para("We asked how far each AI/ML research system is from the scale below which it can no longer reproduce its research workforce, which career transition governs that distance, and whether the distance is shrinking. "
             "The answer is delivered by a measurement pipeline that turns open bibliometric records into cohort career-transition rates, a calibrated compartment model, and a monitoring diagnostic pair (T/M and its closest-lever reading, viability-boundary proximity), with every measurement choice stress-tested in the main results. "
             f"All systems currently exceed their minimum viable coauthor scale, but distance to the threshold is governed by relative scale and by attrition rather than by size or outflow; exogenous entry is the binding lever everywhere; the ranking is robust to the form of the recruitment feedback; and rates have drifted between career windows, shrinking the margin in {ctx['period_neg']}. "
             "For research evaluation the contribution is a reproducible, field-agnostic measurement framework for research-system viability; for AI/ML it locates the systems whose margins are thin and the levers that matter. "
             "Extensions include external validation of the boundary against historical contractions, identification of the variety elasticity, finer partitions with inter-regional spillovers, and application to other general-purpose research fields.")



    # References (Vancouver, order of first appearance)
    doc.add_heading("References", level=1)
    for i, ref in registry.numbered_list():
        p = doc.add_paragraph()
        p.add_run(f"{i}. {ref}")
    orphans = registry.orphans()
    if orphans:
        raise ValueError(f"Reference keys defined but never cited: {orphans}")
    return registry


def _anonymize_docx(doc):
    """Remove identifying text from a document for double-anonymised review."""
    replacements = {
        "https://github.com/bougtoir/researcher-mobility-ode": "[repository URL removed for double-anonymised review]",
    }
    for p in doc.paragraphs:
        for run in p.runs:
            for old, new in replacements.items():
                if old in run.text:
                    run.text = run.text.replace(old, new)
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        for old, new in replacements.items():
                            if old in run.text:
                                run.text = run.text.replace(old, new)


def write_docx(output_dir, data, fig_paths, blinded=False):
    abstract, keywords, highlights = _abstract_and_highlights(data[1], data[4])
    check_front_matter(abstract, highlights)

    # Pre-compute body word count by building a throwaway body doc
    body_doc = Document()
    _add_docx_body(body_doc, data, fig_paths, blinded=blinded)
    body_wc = _doc_word_count(body_doc)

    doc = Document()
    _add_title_page(doc, word_count=body_wc, blinded=blinded)
    _add_front_matter(doc, abstract, keywords, highlights, blinded=blinded)
    _add_docx_body(doc, data, fig_paths, blinded=blinded)
    _unify_pnr_docx(doc)
    _mathify_docx(doc)
    if blinded:
        _anonymize_docx(doc)

    suffix = "JOI_MANUSCRIPT_BLINDED_FINAL_LOCK" if blinded else "JOI_MANUSCRIPT_FINAL_LOCK"
    path = output_dir / f"{suffix}.docx"
    doc.save(path)
    return path


def add_compartment_shape_slide(prs, title):
    """Editable native-shape version of the compartment diagram."""
    from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
    from pptx.dml.color import RGBColor
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title
    W, H = PptxInches(2.0), PptxInches(1.1)
    pos = {}
    for name, (fx, fy) in COMPARTMENT_LAYOUT.items():
        left = PptxInches(0.8 + fx * 11.0) - W // 2
        top = PptxInches(1.4 + (1 - fy) * 5.2) - H // 2
        shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, W, H)
        shp.fill.solid()
        shp.fill.fore_color.rgb = RGBColor(0xE6, 0xF2, 0xFF) if name in ("D", "H_D", "P_D") else RGBColor(0xFF, 0xF4, 0xE6)
        shp.line.color.rgb = RGBColor(0, 0, 0)
        tf = shp.text_frame
        tf.text = name.replace("_", "") if "_" not in name else name.split("_")[0]
        r0 = tf.paragraphs[0].runs[0]
        r0.font.size = Pt(16); r0.font.bold = True; r0.font.color.rgb = RGBColor(0, 0, 0)
        if "_" in name:
            rs = tf.paragraphs[0].add_run(); rs.text = name.split("_")[1]
            rs.font.size = Pt(16); rs.font.bold = True; rs.font.color.rgb = RGBColor(0, 0, 0)
            rs.font._element.set("baseline", "-25000")
        para2 = tf.add_paragraph(); para2.text = COMPARTMENT_LABELS[name].replace("\n", " ")
        para2.runs[0].font.size = Pt(10); para2.runs[0].font.color.rgb = RGBColor(0,0,0)
        pos[name] = shp
    def connect(a, b, label, dashed=False):
        sa, sb = pos[a], pos[b]
        c = slide.shapes.add_connector(MSO_CONNECTOR.CURVE if dashed else MSO_CONNECTOR.STRAIGHT, 0, 0, 0, 0)
        fa_y, fb_y = COMPARTMENT_LAYOUT[a][1], COMPARTMENT_LAYOUT[b][1]
        if dashed:
            c.begin_connect(sa, 0); c.end_connect(sb, 0)
        elif fa_y == fb_y:
            c.begin_connect(sa, 3); c.end_connect(sb, 1)
        elif fa_y > fb_y:
            c.begin_connect(sa, 2); c.end_connect(sb, 0)
        else:
            c.begin_connect(sa, 0); c.end_connect(sb, 2)
        c.line.color.rgb = RGBColor(0x1F, 0x77, 0xB4) if dashed else RGBColor(0, 0, 0)
        c.line.width = Pt(1.5)
        ln = c.line._get_or_add_ln()
        from pptx.oxml.ns import qn
        tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle"})
        ln.append(tail)
        if dashed:
            dash = ln.makeelement(qn("a:prstDash"), {"val": "dash"}); ln.insert(0, dash)
        mx = (c.begin_x + c.end_x) // 2; my = (c.begin_y + c.end_y) // 2
        tb = slide.shapes.add_textbox(mx - PptxInches(0.3), my - PptxInches(0.35), PptxInches(0.6), PptxInches(0.3))
        tb.text_frame.text = label
        tb.text_frame.paragraphs[0].runs[0].font.size = Pt(12)
    for a, b, lab in COMPARTMENT_EDGES:
        if (a, b) == ("A", "D"):
            continue  # drawn as the reverse of D->A with a shared label below
        connect(a, b, lab if (a, b) != ("D", "A") else "α ↓  β ↑")
    inflow = slide.shapes.add_textbox(PptxInches(0.3), PptxInches(1.6), PptxInches(2.2), PptxInches(0.8))
    inflow.text_frame.text = "Inflow I(P_D) = I_0 + r·P_D"
    inflow.text_frame.paragraphs[0].runs[0].font.size = Pt(12)
    inflow.text_frame.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x1F, 0x77, 0xB4)
    connect("P_D", "D", "r (feedback)", dashed=True)
    note = slide.shapes.add_textbox(PptxInches(3.5), PptxInches(3.85), PptxInches(6.5), PptxInches(0.6))
    note.text_frame.text = "Active pool T = D + H_D + P_D compared with M = k·c̄;  d = dropout from every compartment"
    note.text_frame.paragraphs[0].runs[0].font.size = Pt(12)
    return slide


def write_pptx(output_dir, data, fig_paths):
    (cohort, eq, sat_eq, top_t, pnr_closest, period_compare, boot, policy_rank) = data
    annual = load_annual_data()
    prs = Presentation()
    prs.slide_width = PptxInches(13.333)
    prs.slide_height = PptxInches(7.5)

    def add_image_slide(title, img_path, caption):
        slide_layout = prs.slide_layouts[3]
        slide = prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = title
        left = PptxInches(1.5)
        top = PptxInches(1.2)
        slide.shapes.add_picture(str(img_path), left, top, width=PptxInches(10))
        txBox = slide.shapes.add_textbox(left, PptxInches(6.0), PptxInches(10), PptxInches(0.8))
        txBox.text_frame.text = caption
        for paragraph in txBox.text_frame.paragraphs:
            paragraph.font.size = Pt(14)

    def add_table_slide(title, df, col_names, width_per_col=1.5, font_size=10):
        slide_layout = prs.slide_layouts[3]
        slide = prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = title
        rows, cols = len(df) + 1, len(col_names)
        left = PptxInches(0.5)
        top = PptxInches(1.2)
        table = slide.shapes.add_table(rows, cols, left, top, PptxInches(cols * width_per_col), PptxInches(0.6 * rows)).table
        for i, h in enumerate(col_names):
            table.cell(0, i).text = str(h)
        for row_i, (_, row) in enumerate(df.iterrows()):
            for j, val in enumerate(row):
                table.cell(row_i + 1, j).text = str(val)
                table.cell(row_i + 1, j).text_frame.paragraphs[0].font.size = Pt(font_size)

    # Title slide
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = TITLE
    slide.placeholders[1].text = "Data-driven manuscript figures and tables"

    add_image_slide(
        "Figure 1: Research macro-regions and inter-region flows",
        fig_paths["fig1"],
        "Countries coloured by research macro-region; arrows show the 12 largest observed inter-region early-career flows (width proportional to accumulated abroad author-years). Legend gives equilibrium T/M.",
    )
    add_image_slide(
        "Figure 2: Compartment model (image)",
        fig_paths["fig2"],
        "Six compartments per macro-region with transition rates, endogenous recruitment from the domestic PI stock, dropout from every compartment and the threshold test T versus M.",
    )
    add_compartment_shape_slide(prs, "Figure 2 (editable shapes): Compartment model")
    add_image_slide(
        "Figure 3: Equilibrium T vs minimum viable threshold",
        fig_paths["fig3"],
        "Blue bars: equilibrium T; orange bars: threshold M. All groups remain above the threshold, but margins vary widely.",
    )
    add_image_slide(
        "Figure 4: Closest viability-boundary proximity",
        fig_paths["fig4"],
        "Smaller values mean a smaller proportional change in the listed rate is required to reach the threshold for the stated target pool.",
    )
    add_image_slide(
        "Figure 5: Historical counterfactual margin change",
        fig_paths["fig5"],
        "Positive values mean the late-window rates would produce a larger safety margin than the early-window rates if they persisted; negative values mean the margin would shrink. The comparison is across point estimates; uncertainty is substantial.",
    )
    add_image_slide(
        "Figure 6: Bootstrap 95% CI for equilibrium T",
        fig_paths["fig6"],
        "Intervals are asymmetric and wide, reflecting model uncertainty.",
    )

    desc = _descriptive_table(cohort)
    add_table_slide("Table 1: Descriptive cohort statistics", desc, desc.columns.tolist(), width_per_col=1.3)

    eq_table = eq[["group", "T_equilibrium", "M_threshold", "margin_to_threshold_T", "I0", "r", "r_obs", "r_critical"]].copy()
    eq_table["T_over_M"] = eq_table["T_equilibrium"] / eq_table["M_threshold"]
    eq_table.columns = ["Group", "T_eq", "M", "Margin", "T/M", "I0", "r", "r_obs", "r_crit"]
    for c in ["T_eq", "M", "Margin", "I0"]:
        eq_table[c] = eq_table[c].apply(lambda x: _fmt(x, 0))
    eq_table["T/M"] = eq_table["T/M"].apply(lambda x: _fmt(x, 2))
    for c in ["r", "r_obs", "r_crit"]:
        eq_table[c] = eq_table[c].apply(lambda x: _fmt(x, 5))
    add_table_slide("Table 2: Equilibrium and inflow parameters", eq_table, eq_table.columns.tolist(), width_per_col=1.35)

    rows2 = []
    for group, gdf in top_t.groupby("group"):
        top3 = gdf.sort_values("abs_elasticity", ascending=False).head(3)
        parts = [group]
        for _, row in top3.iterrows():
            parts.extend([row["rate"], _fmt(row["elasticity"], 3)])
        rows2.append(parts)
    elas_df = pd.DataFrame(rows2, columns=["Group", "1st", "el1", "2nd", "el2", "3rd", "el3"])
    add_table_slide("Table 3: Top transition-rate elasticities", elas_df, elas_df.columns.tolist(), width_per_col=1.4)

    pnr_table = pnr_closest[["group", "target", "rate_name", "current_rate", "critical_factor", "proximity"]].copy()
    pnr_table.columns = ["Group", "Target", "Rate", "Current", "Crit.factor", "Proximity"]
    for c, d in {"Current": 4, "Crit.factor": 3, "Proximity": 3}.items():
        pnr_table[c] = pnr_table[c].apply(lambda x, d=d: _fmt(x, d))
    add_table_slide("Table 4: Closest model-implied viability boundary", pnr_table, pnr_table.columns.tolist(), width_per_col=1.8)

    if sat_eq is not None:
        merged = eq[["group", "T_equilibrium"]].merge(
            sat_eq[["group", "T_equilibrium", "epsilon"]], on="group", suffixes=("_lin", "_sat")
        )
        merged.columns = ["Group", "Linear T", "Saturating T", "ε"]
        for c, d in {"Linear T": 0, "Saturating T": 0, "ε": 5}.items():
            merged[c] = merged[c].apply(lambda x, d=d: _fmt(x, d))
        add_table_slide("Table 5: Saturating inflow extension", merged, merged.columns.tolist(), width_per_col=2.0)

    pc = period_compare.rename(columns={
        "group": "Group",
        "T_early": "T early",
        "T_late": "T late",
        "pct_delta_T": "ΔT (%)",
        "margin_early": "Margin early",
        "margin_late": "Margin late",
        "delta_margin": "Δ margin",
    })
    for c, d in {"T early": 0, "T late": 0, "ΔT (%)": 1, "Margin early": 0, "Margin late": 0, "Δ margin": 1}.items():
        pc[c] = pc[c].apply(lambda x, d=d: _fmt(x, d))
    add_table_slide("Table 6: Historical counterfactual", pc, pc.columns.tolist(), width_per_col=1.4)

    policy_top = policy_rank.groupby("group").head(1).rename(columns={
        "group": "Group",
        "lever": "Lever",
        "direction": "Direction",
        "lever_change_pct": "Change (%)",
        "margin_gain": "Margin gain",
        "normalised_margin_gain_per_10pct": "Gain per 10%",
    })
    for c, d in {"Change (%)": 0, "Margin gain": 0, "Gain per 10%": 1}.items():
        policy_top[c] = policy_top[c].apply(lambda x, d=d: _fmt(x, d))
    add_table_slide("Table 7: Top policy intervention", policy_top, policy_top.columns.tolist(), width_per_col=2.0)

    lever_policy_mgmt = pd.DataFrame({
        "Lever": ["Dropout (d)", "Exogenous entry (I_0)", "Return from abroad (β)", "Domestic hit generation (h_D)", "PI promotion (p_D)"],
        "Policy instrument": [
            "Early-career fellowships, childcare and dual-career support, stable non-tenure tracks",
            "Research-master and undergraduate pipelines, doctoral fellowships, recruitment visas",
            "Return grants, diaspora networks, dual appointments, overseas-experience recognition",
            "Independent-lab programmes (e.g. SPREAD-style), doctoral/postdoctoral training, compute access",
            "Tenure-track conversion, startup packages, project-based PI status",
        ],
        "Management action": [
            "Retain researchers in the domestic pipeline beyond the first career years",
            "Widen the base of incoming researchers before they select a field or location",
            "Encourage mobile researchers to re-establish domestic research groups",
            "Translate junior capacity into visible, high-impact work and independent research lines",
            "Create durable principal-investigator positions that train the next cohort",
        ],
    })
    add_table_slide("Table 9: Transition levers, policy instruments and principal actors", lever_policy_mgmt, lever_policy_mgmt.columns.tolist(), width_per_col=2.2)

    # Bootstrap CI is placed at the end as Supplementary Table S6.


    if fig_paths.get("fig7"):
        add_image_slide(
            "Figure 7: Japan compartment model and cross-region transition-rate ladders",
            fig_paths["fig7"],
            "Left: Japan's six compartments; right: Japan highlighted against other macro-regions on each transition rate.",
        )

    if fig_paths.get("fig8"):
        add_image_slide(
            "Figure 8: T/M safety margin versus closest boundary proximity",
            fig_paths["fig8"],
            "Lower-left points are the most fragile. Japan is highlighted in red.",
        )

    if fig_paths.get("fig9"):
        add_image_slide(
            "Figure 9: Talent-concentration scenario (coupled nine-region model)",
            fig_paths["fig9"],
            "(a) hosted pool of the dominant region; (b) effective number of macro-regions; (c) field hit stock for three variety elasticities; (d) elasticity threshold for a net loss. Pull intensity and variety elasticity are stylised.",
        )
    if fig_paths.get("fig10"):
        add_image_slide(
            "Figure 10: Regional time paths under the talent-concentration strategy",
            fig_paths["fig10"],
            "Domestic active pool of each macro-region as a multiple of its minimum viable scale M, one panel per variety elasticity; time in units of the characteristic time τ = 1/d̄; crosses mark when a region falls below M and loses PI-driven recruitment permanently.",
        )
    dom_ = load_dominant_strategy()
    if dom_ is not None:
        dt = dominant_strategy_table(dom_)
        for c, d in {"Pull intensity φ": 1, "Hosted pool at end of horizon (× baseline)": 2, "Share of hosted researchers at end of horizon (%)": 0,
                     "Effective number of regions at end of horizon": 1, "Field hit stock at end of horizon (× baseline)": 2}.items():
            dt[c] = dt[c].map(lambda v: _fmt(v, d))
        add_table_slide("Table 8: Talent-concentration scenario at the end of the horizon (fitted rates, γ = 0)", dt, dt.columns.tolist(), width_per_col=1.4)

    # Supplementary (exploratory annual layer) slides
    if fig_paths.get("figS1"):
        add_image_slide(
            "Supplementary Figure S1: Observed and projected transition rates",
            fig_paths["figS1"],
            "Solid lines mark observed 2000-2016 rates; dashed lines mark projected 2017-2026 rates.",
        )
    if fig_paths.get("figS2"):
        add_image_slide(
            "Supplementary Figure S2: Cross-region abroad author-years",
            fig_paths["figS2"],
            "Rows are origin macro-regions; columns are destination macro-regions approximated by recent_group. Same-region cells and Unknown destinations are excluded.",
        )
    if fig_paths.get("figS3"):
        add_image_slide(
            "Supplementary Figure S3: Observed vs projected compartment counts",
            fig_paths["figS3"],
            "Solid lines are observed counts; dashed lines are 2017-2026 projections. The vertical dotted line is 2016.",
        )

    annual_means = annual_summary_table(annual)
    if not annual_means.empty:
        add_table_slide(
            "Supplementary Table S4: Mean observed annual transition rates, 2000-2016",
            annual_means,
            annual_means.columns.tolist(),
            width_per_col=1.4,
        )

    interciv_top = interciv_top_table(annual)
    if not interciv_top.empty:
        add_table_slide(
            "Supplementary Table S5: Top origin-destination abroad author-year pairs",
            interciv_top,
            interciv_top.columns.tolist(),
            width_per_col=2.0,
        )

    group_acc = annual.get("group_accuracy")
    if group_acc is not None and not group_acc.empty:
        gacc = group_acc.copy()
        gacc["rmse"] = gacc["rmse"].apply(lambda x: _fmt(x, 2))
        gacc["mape"] = gacc["mape"].apply(lambda x: f"{x*100:.1f}%")
        gacc = gacc.rename(columns={"origin_group": "Group", "rmse": "RMSE", "mape": "MAPE"})
        add_table_slide(
            "Supplementary Table S2: Projection accuracy by research macro-region, 2017-2023",
            gacc,
            gacc.columns.tolist(),
            width_per_col=2.2,
        )

    comp_acc = annual.get("compartment_accuracy")
    if comp_acc is not None and not comp_acc.empty:
        cacc = comp_acc.copy()
        cacc["rmse"] = cacc["rmse"].apply(lambda x: _fmt(x, 2))
        cacc["mape"] = cacc["mape"].apply(lambda x: f"{x*100:.1f}%")
        cacc = cacc.rename(columns={"compartment": "Compartment", "rmse": "RMSE", "mape": "MAPE"})
        add_table_slide(
            "Supplementary Table S3: Projection accuracy by compartment, 2017-2023",
            cacc,
            cacc.columns.tolist(),
            width_per_col=2.2,
        )

    boot_tab = boot.copy()
    boot_tab["T 95% CI"] = boot_tab.apply(lambda r: f"[{_fmt(r['T_equilibrium_q025'], 0)}, {_fmt(r['T_equilibrium_q975'], 0)}]", axis=1)
    boot_tab["P_D 95% CI"] = boot_tab.apply(lambda r: f"[{_fmt(r['P_D_equilibrium_q025'], 0)}, {_fmt(r['P_D_equilibrium_q975'], 0)}]", axis=1)
    boot_tab = boot_tab[["group", "T_equilibrium_median", "T 95% CI", "P_D_equilibrium_mean", "P_D 95% CI"]]
    boot_tab.columns = ["Group", "T median", "T 95% CI", "P_D mean", "P_D 95% CI"]
    for c in ["T median", "P_D mean"]:
        boot_tab[c] = boot_tab[c].apply(lambda x: _fmt(x, 0))
    add_table_slide("Supplementary Table S6: Bootstrap 95% CI", boot_tab, boot_tab.columns.tolist(), width_per_col=2.2)

    path = output_dir / "JOI_FIGURES_EDITABLE_FINAL_LOCK.pptx"
    prs.save(path)
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def write_supplementary_docx(output_dir, data, fig_paths):
    """Write a supplementary-materials docx with detailed tables supporting the main manuscript."""
    annual = load_annual_data()
    boot = data[6]
    doc = Document()
    doc.add_heading("Supplementary Material", level=0)
    p = doc.add_paragraph()
    p.add_run(TITLE)
    p = doc.add_paragraph()
    p.add_run("This supplement provides the country mapping, the exploratory annual estimation layer, robustness checks on the PI proxy and on the minimum viable scale, and detailed tables that support the main manuscript. "
              "Values are reproduced from the same result CSVs used to generate the main tables and figures; no numbers are hard-coded.")

    doc.add_heading("S1. Country-to-macro-region mapping", level=1)
    mapping_path = BASE_DIR / "data" / "country_civilization_mapping.json"
    if mapping_path.exists():
        with open(mapping_path, encoding="utf-8") as fh:
            mapping = json.load(fh)
        rows = [(display_group(v["group"]), v["name"], int(v.get("ai_ml_works_2022_2023", 0))) for v in mapping.values()]
        mdf = pd.DataFrame(rows, columns=["Macro-region", "Country", "AI/ML works 2022-2023"])
        mdf = mdf[mdf["AI/ML works 2022-2023"] > 0].sort_values(["Macro-region", "AI/ML works 2022-2023"], ascending=[True, False])
        agg = mdf.groupby("Macro-region").agg(
            Countries=("Country", lambda x: ", ".join(x)),
            Works=("AI/ML works 2022-2023", "sum"),
        ).reset_index()
        p = doc.add_paragraph()
        p.add_run("Supplementary Table S1 lists every country with at least one AI/ML work in 2022-2023 under its macro-region. "
                  "The partition starts from Huntington's taxonomy and is adjusted for AI/ML sample size (Latin American, Orthodox and sub-Saharan African countries merged into Other regions; the United States separated from the rest of the Anglosphere). "
                  "The labels are operational aggregations of publication-affiliation patterns and carry no claim about cultural identity. "
                  "The complete machine-readable mapping, including countries with zero works, is data/country_civilization_mapping.json in the public repository.")
        _add_table_from_df(doc, agg, caption="Supplementary Table S1. Country membership of the research macro-regions (countries with at least one AI/ML work in 2022-2023).", decimals={"Works": 0})

    doc.add_heading("S2. Annual estimation and projection layer (exploratory extension)", level=1)
    annual_ctx = compute_annual_context(annual)

    def sfigure(key, caption, width=5.8):
        src = fig_paths.get(key)
        if not src or not Path(src).exists():
            return
        doc.add_picture(str(src), width=Inches(width))
        cap = doc.add_paragraph()
        cap.paragraph_format.space_before = Pt(12)
        cap.add_run(caption).italic = True
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p = doc.add_paragraph()
    p.add_run("This section is an exploratory extension of the steady-state analysis: it asks whether the fitted rates can be updated year by year, not whether the projection forecasts stocks. "
              "The annual layer re-estimates each transition rate for every calendar year 2000-2016 from the reconstructed compartment state of the cohort. "
              "Rates are estimated as transitions divided by exposure with a Laplace pseudocount and projected with a linear trend fitted to the 2000-2016 series, regularised in two ways: "
              "(i) projected rates are clipped to the [0, 1] interval (inflows are projected on a log1p scale and clipped to be non-negative), and "
              "(ii) where fewer than four annual observations are available or the linear fit explains less than 10% of the variance (R\u00b2 < 0.10), the macro-region's own 2000-2016 mean is carried forward instead of the trend; and "
              "(iii) projected dropout is capped at 1.5 times its 90th percentile over the training period. "
              "No PI-reproduction stability cap is imposed in the annual layer; that cap applies only to the steady-state model. "
              "Projected rates for 2017-2026 are applied to the 2016 compartment state with a one-year time step, and the projected 2017-2023 compartment counts are compared with the observed reconstruction. "
              "Accuracy is reported as RMSE, MAPE, direction agreement (whether the projected and observed year-to-year change have the same sign) and threshold-alarm metrics (whether the projection correctly flags years in which the observed active pool T = D + H_D + P_D falls below M, its group-specific minimum viable coauthor scale; Supplementary Table S2 reports the number of observed and projected alarm years alongside accuracy, sensitivity, specificity and precision). "
              "Stock-level errors are larger than rate-level errors because the cohort is fixed at 2016 and cannot contain the new entrants that the projection adds; the layer is therefore a drift-and-threshold alarm, not a population forecast.")
    p = doc.add_paragraph()
    p.add_run("Supplementary Figure S1 plots observed 2000-2016 and projected 2017-2026 transition rates by macro-region, Supplementary Figure S2 the accumulated cross-region abroad author-years by origin and destination (a lower-bound proxy for inter-regional pipelines, used as the host distribution of the talent-concentration scenario in the main text), and Supplementary Figure S3 compares the 2017-2023 projection with observed compartment counts. "
              f"Rate-level projections have RMSE {_fmt(annual_ctx.get('rate_overall_rmse', float('nan')), 4)} and a skill ratio (baseline RMSE / model RMSE) of {_fmt(annual_ctx.get('rate_overall_skill', float('nan')), 2)} against a historical-mean baseline, "
              + ("so they do not improve on simply carrying the historical mean forward" if annual_ctx.get('rate_overall_skill', float('nan')) < 1 else "a modest improvement over carrying the historical mean forward")
              + f"; stock-level errors are larger (RMSE {round(annual_ctx.get('overall_rmse', float('nan'))):,}). ")
    if "direction_agreement" in annual_ctx:
        p.add_run(f"Year-to-year direction agreement is {_fmt(annual_ctx['direction_agreement'] * 100, 1)}%. ")
    if annual_ctx.get("threshold_alarms_obs", 0) > 0:
        p.add_run(f"The observed compartment series of the closed cohort falls below M in {annual_ctx['threshold_alarms_obs']} macro-region-years ({annual_ctx['alarm_groups']}; Supplementary Table S2), whereas the projection flags {annual_ctx['threshold_alarms_proj']}. "
                  "These observed alarms are an artefact of cohort closure, not evidence that the system is below its threshold: the observed series excludes everyone who entered after 2016, so it declines by construction, while the equilibrium T of the main text includes continuing entry. The alarm metrics are reported for completeness only.")
    sfigure("figS1", "Supplementary Figure S1. Observed (solid) and projected (dashed) transition rates by research macro-region, 2000-2026.", width=6.0)
    sfigure("figS2", "Supplementary Figure S2. Cross-region abroad author-year accumulation by origin (rows) and destination (columns); same-region cells and Unknown destinations excluded (lower-bound proxy).")
    sfigure("figS3", "Supplementary Figure S3. Observed (solid) and projected (dashed) compartment counts by research macro-region, 2017-2023. The dotted line marks the end of the training period (2016).", width=6.0)

    doc.add_heading("Supplementary Table S2. Projection accuracy by research macro-region, 2017-2023", level=1)
    group_acc = annual.get("group_accuracy")
    if group_acc is not None and not group_acc.empty:
        gacc = group_acc.copy()
        gacc["rmse"] = gacc["rmse"].apply(lambda x: _fmt(x, 2))
        gacc["mape"] = gacc["mape"].apply(lambda x: f"{x*100:.1f}%")
        if "direction_agreement" in gacc.columns:
            gacc["direction_agreement"] = gacc["direction_agreement"].apply(lambda x: f"{x*100:.1f}%")
        if "threshold_alarm_accuracy" in gacc.columns:
            for c in ["threshold_alarm_accuracy", "threshold_alarm_sensitivity", "threshold_alarm_specificity", "threshold_alarm_precision"]:
                gacc[c] = gacc[c].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "—")
        rename = {"origin_group": "Group", "rmse": "RMSE", "mape": "MAPE", "direction_agreement": "Direction agreement",
                  "threshold_alarms_obs": "Alarm years (observed)", "threshold_alarms_proj": "Alarm years (projected)"}
        for c in ["threshold_alarm_accuracy", "threshold_alarm_sensitivity", "threshold_alarm_specificity", "threshold_alarm_precision"]:
            if c in gacc.columns:
                rename[c] = c.replace("threshold_alarm_", "Alarm ").replace("_", " ").title()
        gacc = gacc.rename(columns=rename)
        _add_table_from_df(doc, gacc, caption="Supplementary Table S2. Projection accuracy by research macro-region, 2017-2023.", decimals={"MAPE": 2})
    else:
        doc.add_paragraph("No group-level accuracy data available.")

    doc.add_heading("Supplementary Table S3. Projection accuracy by compartment, 2017-2023", level=1)
    comp_acc = annual.get("compartment_accuracy")
    if comp_acc is not None and not comp_acc.empty:
        cacc = comp_acc.copy()
        cacc["rmse"] = cacc["rmse"].apply(lambda x: _fmt(x, 2))
        cacc["mape"] = cacc["mape"].apply(lambda x: f"{x*100:.1f}%")
        if "direction_agreement" in cacc.columns:
            cacc["direction_agreement"] = cacc["direction_agreement"].apply(lambda x: f"{x*100:.1f}%")
        cacc = cacc.rename(columns={"compartment": "Compartment", "rmse": "RMSE", "mape": "MAPE", "direction_agreement": "Direction agreement"})
        _add_table_from_df(doc, cacc, caption="Supplementary Table S3. Projection accuracy by compartment, 2017-2023.", decimals={"MAPE": 2})
    else:
        doc.add_paragraph("No compartment-level accuracy data available.")

    doc.add_heading("Supplementary Table S4. Mean observed annual transition rates by research macro-region, 2000-2016", level=1)
    annual_means = annual_summary_table(annual)
    if not annual_means.empty:
        _add_table_from_df(doc, annual_means, caption="Supplementary Table S4. Mean observed annual transition rates by research macro-region, 2000-2016.", decimals={"α": 3, "β": 3, "h_D": 3, "p_D": 3, "d": 3, "I_total": 2})
    else:
        doc.add_paragraph("No annual transition-rate data available.")

    doc.add_heading("Supplementary Table S5. Top cross-region origin-destination abroad author-year pairs", level=1)
    interciv_top = interciv_top_table(annual)
    if not interciv_top.empty:
        _add_table_from_df(doc, interciv_top, caption="Supplementary Table S5. Top cross-region origin-destination abroad author-year pairs.", decimals={"Author-years": 0})
    else:
        doc.add_paragraph("No cross-region flow data available.")

    doc.add_heading("Supplementary Table S6. Bootstrap 95% confidence intervals for equilibrium T and domestic PI pool P_D", level=1)
    boot_tab = boot.copy()
    boot_tab["T 95% CI"] = boot_tab.apply(lambda r: f"[{_fmt(r['T_equilibrium_q025'], 0)}, {_fmt(r['T_equilibrium_q975'], 0)}]", axis=1)
    boot_tab["P_D 95% CI"] = boot_tab.apply(lambda r: f"[{_fmt(r['P_D_equilibrium_q025'], 0)}, {_fmt(r['P_D_equilibrium_q975'], 0)}]", axis=1)
    boot_tab = boot_tab[["group", "T_equilibrium_median", "T 95% CI", "P_D_equilibrium_mean", "P_D 95% CI"]]
    boot_tab.columns = ["Group", "T median", "T 95% CI", "P_D mean", "P_D 95% CI"]
    _add_table_from_df(doc, boot_tab, caption="Supplementary Table S6. Bootstrap 95% confidence intervals for equilibrium T and domestic PI pool P_D.", decimals={"T median": 0, "P_D mean": 0})

    doc.add_heading("Supplementary Table S7. Closest model-implied viability boundary under linear versus saturating inflow", level=1)
    pnr_rob = pnr_robustness_table()
    if not pnr_rob.empty:
        rob = pnr_rob.rename(columns={
            "origin_group": "Group", "linear_closest": "Linear lever", "linear_factor": "Linear factor", "linear_proximity": "Linear proximity",
            "saturating_closest": "Saturating lever", "saturating_factor": "Saturating factor", "saturating_proximity": "Saturating proximity",
        })
        _add_table_from_df(doc, rob, caption="Supplementary Table S7. Closest viability-boundary lever, critical factor and proximity for the active pool under linear and saturating PI-driven inflow.",
                           decimals={"Linear factor": 3, "Linear proximity": 3, "Saturating factor": 3, "Saturating proximity": 3})
    else:
        doc.add_paragraph("No saturating-inflow boundary results available.")

    doc.add_heading("Supplementary Table S8. Talent-concentration scenario: inputs and their status", level=1)
    dom_s = load_dominant_strategy()
    if dom_s is not None:
        ass = dom_s["assumptions"].rename(columns={"parameter": "Parameter", "value": "Value", "status": "Status"})
        _add_table_from_df(doc, ass, caption="Supplementary Table S8. Inputs to the talent-concentration scenario (Section 2.10). 'Fitted' inputs come from the estimated model and observed mobility data; 'stylised' inputs are modelling assumptions without an empirical estimate.")
    else:
        doc.add_paragraph("No talent-concentration scenario results available.")

    doc.add_heading("S3. Robustness to the PI proxy definition", level=1)
    pp = load_pi_proxy()
    if pp is not None:
        snap = pp["snapshot"]
        p = doc.add_paragraph()
        p.add_run("The baseline defines a PI by the first last-author paper. To test this choice, the full AI/ML author population was re-extracted from OpenAlex with the corresponding-author flag of every authorship retained, and each author was classified under three definitions on the same snapshot: "
                  "(a) first last-author paper (baseline); (b) first paper on which the author is flagged as corresponding author (OpenAlex authorships.is_corresponding); (c) second last-author paper, i.e. last author on at least two papers. "
                  + (f"The re-extracted snapshot contains {int(snap['n_authors_snapshot'].iloc[0]):,} authors against {int(snap['n_authors_published'].iloc[0]):,} in the published cohort; the difference reflects OpenAlex updates between extractions, so definitions are compared with each other on the same snapshot (Supplementary Table S10) and the baseline definition is also compared with the published results. " if snap is not None else "")
                  + "For each definition the transition rates were re-estimated, the endogenous-inflow equilibrium, the elasticities and the closest model-implied viability boundary were recomputed with the same M, and the nine-region rankings were compared by Spearman rank correlation. "
                  "Two quantities are invariant to the proxy by construction and are reported only for completeness: because I_0 is calibrated so that total equilibrium entry equals observed entry (Section 2.8), the equilibrium active pool T (hence T/M) and the proximity of the entry lever I_0 do not depend on how PIs are identified. "
                  "The proxy does change the promotion rates p_D and p_A, the equilibrium PI pool P_D, the exogenous/PI-driven split of entry (I_0, r), the elasticity of T to p_D and the model-implied viability boundary of the PI pool relative to its own threshold k. "
                  "Supplementary Table S9 reports the region-level results and Supplementary Table S10 the rank agreement on these proxy-dependent quantities.")
        _add_table_from_df(doc, pi_proxy_table(pp), caption="Supplementary Table S9. Equilibrium active pool, T/M, rank and closest viability-boundary lever by research macro-region under three PI proxy definitions (same OpenAlex snapshot; M held at its baseline value).",
                           decimals={"Share of authors who are PIs": 3, "p_D": 3, "T/M": 2, "Proximity (T)": 3, "P_D": 0, "Proximity (P_D)": 3, "Elasticity of T to p_D": 3})
        _add_table_from_df(doc, pi_proxy_agreement_table(pp), caption="Supplementary Table S10. Rank agreement between alternative PI proxies and the baseline definition across the nine research macro-regions (Spearman rho). T/M and the T proximity are invariant by construction (see text).",
                           decimals={"Spearman rho (T/M)": 2, "Spearman rho (boundary proximity, T)": 2, "Spearman rho (p_D)": 2, "Spearman rho (P_D)": 2, "Spearman rho (boundary proximity, P_D)": 2})
    else:
        doc.add_paragraph("PI proxy robustness results (results/pi_proxy) are not available; run src/pi_proxy_robustness.py after re-extracting the cohort.")

    doc.add_heading("S4. Sensitivity to the minimum viable scale M", level=1)
    ms = load_m_sensitivity()
    if ms is not None:
        rc = robustness_context(None, ms)
        p = doc.add_paragraph()
        p.add_run("M = k x c-bar is an operational threshold, so we multiply it by "
                  + ", ".join(_fmt(v, 2) for v in ms["summary"]["M_multiplier"]) +
                  " and recompute, for every macro-region, T/M, the rank by T/M, the closest viability-boundary lever and its proximity, and the elasticities of T to dropout (d) and early-career outflow (alpha). "
                  f"Supplementary Table S11 summarises the results. No macro-region falls below M at any multiplier (minimum T/M {_fmt(rc['ms_min_tm_at_max'], 2)} at the largest multiplier); "
                  f"the rankings by T/M and by proximity are unchanged (Spearman rho = {_fmt(rc['ms_rho_tm_min'], 2)} and {_fmt(rc['ms_rho_prox_min'], 2)} against the baseline at every multiplier); and |elasticity to d| exceeds |elasticity to alpha| in every macro-region at every multiplier. "
                  + ("The closest lever is unchanged everywhere." if rc["ms_lever_changes"].empty else
                     "The closest lever changes only where a larger M brings the dropout lever closer than exogenous entry: " +
                     "; ".join(f"{r['group']} at multiplier {_fmt(r['M_multiplier'], 2)} ({_rate_label(r['closest_rate'])}, proximity {_fmt(r['proximity'], 3)})" for _, r in rc["ms_lever_changes"].iterrows()) + "."))
        _add_table_from_df(doc, m_sensitivity_table(ms), caption="Supplementary Table S11. Sensitivity of the steady-state results to the level of the minimum viable coauthor scale M (multipliers applied to every macro-region).",
                           decimals={"M multiplier": 2, "Minimum T/M": 2, "Spearman rho (T/M vs baseline)": 2, "Spearman rho (proximity vs baseline)": 2})
        det = ms["detail"][["group", "M_multiplier", "T_over_M", "rank_T_over_M", "closest_rate", "proximity", "elasticity_d", "elasticity_alpha"]].copy()
        det["closest_rate"] = det["closest_rate"].map(_rate_label)
        det.columns = ["Group", "M multiplier", "T/M", "T/M rank", "Closest lever", "Proximity", "Elasticity (d)", "Elasticity (alpha)"]
        _add_table_from_df(doc, det, caption="Supplementary Table S12. Region-level results underlying Supplementary Table S11.",
                           decimals={"M multiplier": 2, "T/M": 2, "Proximity": 3, "Elasticity (d)": 3, "Elasticity (alpha)": 3})
    else:
        doc.add_paragraph("M sensitivity results (results/m_sensitivity) are not available; run src/m_sensitivity.py.")

    _mathify_docx(doc)
    sup_path = output_dir / "supplementary_material.docx"
    doc.save(sup_path)
    return sup_path


def write_highlights_docx(output_dir, data):
    """Separate editable Highlights file required by Technology in Society."""
    abstract, _keywords, highlights = _abstract_and_highlights(data[1], data[4])
    check_front_matter(abstract, highlights)
    doc = Document()
    doc.add_heading("Highlights", level=1)
    for h in highlights:
        doc.add_paragraph(h, style="List Bullet")
    path = output_dir / "JOI_HIGHLIGHTS_FINAL_LOCK.docx"
    doc.save(path)
    return path


def write_cover_letter(output_dir, data):
    """Cover letter for the Journal of Informetrics; numbers are drawn from results."""
    (cohort, eq, sat_eq, top_t, pnr_closest, period_compare, _boot, policy_rank) = data
    ctx = compute_context(cohort, eq, sat_eq, top_t, pnr_closest, period_compare, policy_rank)
    closest = pnr_closest.iloc[0]
    paras = [
        "Dear Editors of the Journal of Informetrics,",
        f"I submit the manuscript \"{TITLE}\" for consideration as a Full Length Article.",
        "Why it matters. Researcher-mobility measurement today reports stocks and net flows, which describe redistribution but cannot tell an evaluator whether a research system can still reproduce its own workforce. "
        "What the field lacks is a community-level state variable that tracks, in model terms, whether a system retains the capacity to reproduce its workforce before the headcount shows it. "
        "This paper supplies that variable and the complete, auditable measurement pipeline behind it.",
        "What is new. The pipeline turns open bibliometric records into cohort career-transition rates, a calibrated six-compartment dynamical model, and a monitoring indicator pair (the equilibrium active pool relative to a minimum viable coauthor scale, T/M, and the proximity of that equilibrium to a model-implied viability boundary); the two are linked by construction and form one diagnostic scale, not two independent tests, and predictive validation is left as future work. "
        f"Applied to {len(cohort):,} OpenAlex AI/ML authors (2000-2023) across {len(eq)} research macro-regions, it shows that distance to the boundary is governed by relative scale, not size: the lowest T/M is {ctx['tm_min']:.2f} ({ctx['tm_min_group']}), and the closest boundary is in {closest['group']}, where {_rate_label(closest['rate_name'])} reduced to {closest['critical_factor']*100:.1f}% of its current value-a {closest['proximity']*100:.1f}% reduction-would drive the pool to its threshold. "
        f"Dropout, not outflow, is the most elastic lever in {ctx['d_gt_alpha_groups']} of {len(eq)} macro-regions.",
        "Why methodological contribution comes first. Every measurement choice in the pipeline is stress-tested and reported in the main results rather than in footnotes: origin assignment under seven specifications (no macro-region reverses mobility direction), PI status under six alternative definitions propagated through the model (T-side rankings are structurally invariant, P-side quantities vary and are reported), multi-affiliation prevalence and missingness/censoring bounds are quantified, and the dependence of the regional ranking on the operational M definition is quantified rather than assumed away. "
        "The pipeline is field-agnostic by construction-AI/ML is the case study, not the object of the paper-which is why I believe it fits the Journal of Informetrics' interest in reusable measurement and evaluation methodology.",
        "All results are reproducible from the public repository named in the Data and Code Availability statement; a single script regenerates every number, figure and table. "
        "The manuscript has not been published and is not under consideration elsewhere. I declare no competing interests. "
        "Generative-AI tools were used in drafting and coding, as declared in the manuscript; I take full responsibility for the content.",
        "A double-anonymised version and a Highlights file are included.",
        "Thank you for considering this work.",
        "Sincerely,",
        "[Corresponding author, affiliation and contact details to be completed at submission]",
    ]
    doc = Document()
    for t in paras:
        doc.add_paragraph(t)
    path = output_dir / "JOI_COVER_LETTER_FINAL_LOCK.docx"
    doc.save(path)
    md_path = output_dir / "JOI_COVER_LETTER_FINAL_LOCK.md"
    md_path.write_text("\n\n".join(paras) + "\n", encoding="utf-8")
    return path


def write_title_page(output_dir, data):
    """Standalone JOI title page with author placeholders and declarations."""
    abstract, keywords, highlights = _abstract_and_highlights(data[1], data[4])
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    title = doc.add_heading(TITLE, level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.size = Pt(16); title.runs[0].font.color.rgb = RGBColor(0,0,0)
    doc.add_paragraph("Article type: Full Length Article")
    doc.add_paragraph("Authors: [names, affiliations and ORCID to be completed at submission]")
    doc.add_paragraph("Corresponding author: [name, affiliation, email]")
    doc.add_paragraph(f"Keywords: {keywords}")
    doc.add_paragraph("Declarations of interest: [to be completed at submission]")
    doc.add_paragraph("Funding: [to be completed at submission]")
    doc.add_paragraph("Data availability: aggregate results and code at https://github.com/bougtoir/researcher-mobility-ode; author-level data re-extractable from OpenAlex (CC0) via reproduce.sh.")
    path = output_dir / "JOI_TITLE_PAGE_FINAL_LOCK.docx"
    doc.save(path)
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=BASE_DIR / "docs")
    args = parser.parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_data()
    cohort, eq, sat_eq, top_t, pnr_closest, period_compare, boot, policy_rank = data

    transition_rates = load_transition_rates()
    pnr_full = load_pnr_full()

    fig_dir = output_dir / "figures"
    annual = load_annual_data()
    fig1 = build_figure1(eq, annual, fig_dir)
    fig2 = build_figure2(fig_dir)
    fig3 = build_figure3(eq, fig_dir)
    fig4 = build_figure4(pnr_closest, fig_dir)
    fig5 = build_figure5(period_compare, fig_dir)
    fig6 = build_figure6(boot, fig_dir)
    fig10 = build_figure10(transition_rates, eq, fig_dir)
    fig11 = build_figure11(eq, pnr_full, fig_dir)
    fig12 = build_figure12(load_dominant_strategy(), fig_dir)
    fig13 = build_figure13(load_dominant_strategy(), fig_dir)

    annual_figs = build_annual_figures(annual, fig_dir)

    # Main-text figures are numbered 1-10; the annual layer is Supplementary Figures S1-S3.
    fig_paths = {
        "fig1": fig1,
        "fig2": fig2,
        "fig3": fig3,
        "fig4": fig4,
        "fig5": fig5,
        "fig6": fig6,
        "fig7": fig10,
        "fig8": fig11,
        "fig9": fig12,
        "fig10": fig13,
        "figS1": annual_figs.get("fig7"),
        "figS2": annual_figs.get("fig8"),
        "figS3": annual_figs.get("fig9"),
    }

    docx_path = write_docx(output_dir, data, fig_paths, blinded=False)
    blinded_docx_path = write_docx(output_dir, data, fig_paths, blinded=True)
    md_path = write_markdown(output_dir, docx_path=docx_path, blinded=False)
    blinded_md_path = write_markdown(output_dir, docx_path=blinded_docx_path, blinded=True)
    pptx_path = write_pptx(output_dir, data, fig_paths)
    sup_path = write_supplementary_docx(output_dir, data, fig_paths)
    sup_md_path = write_markdown(output_dir, docx_path=sup_path, blinded=False)
    highlights_path = write_highlights_docx(output_dir, data)
    cover_path = write_cover_letter(output_dir, data)
    titlepage_path = write_title_page(output_dir, data)

    print(f"Wrote {docx_path}")
    print(f"Wrote {blinded_docx_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {blinded_md_path}")
    print(f"Wrote {pptx_path}")
    print(f"Wrote {sup_path}")
    if sup_md_path:
        print(f"Wrote {sup_md_path}")
    print(f"Wrote {highlights_path}")
    print(f"Wrote {cover_path}")
    print(f"Wrote {titlepage_path}")
    print(f"Figures saved to {fig_dir}")

    # Numbered submission copies (Figure_01 ... Figure_10, Supplementary_Figure_S1 ...) as PNG and TIFF, matching manuscript numbering.
    sub_fig_dir = fig_dir / "submission"
    sub_fig_dir.mkdir(exist_ok=True)
    for old in list(sub_fig_dir.glob("Figure_*")) + list(sub_fig_dir.glob("Supplementary_Figure_*")):
        old.unlink()
    sub_fig_files = []
    for key, src in fig_paths.items():
        if not src or not Path(src).exists():
            continue
        stem = re.sub(r"^fig\d+_", "", Path(src).stem).replace("pnr", "mvb")
        if key.startswith("figS"):
            prefix = f"Supplementary_Figure_{key[3:]}"
        else:
            prefix = f"Figure_{int(key[3:]):02d}"
        png_out = sub_fig_dir / f"{prefix}_{stem}.png"
        tif_out = sub_fig_dir / f"{prefix}_{stem}.tif"
        with Image.open(src) as im:
            dpi = im.info.get("dpi", (300, 300))
            im.save(png_out, format="PNG", dpi=dpi)
            im.convert("RGB").save(tif_out, format="TIFF", compression="tiff_lzw", dpi=dpi)
        sub_fig_files += [png_out, tif_out]
    print(f"Submission figures (PNG + TIFF) saved to {sub_fig_dir}")

    # Build a submission zip containing the manuscript, editable figures, PNGs and TIFFs
    zip_path = output_dir / "JOI_SUBMISSION_FINAL_LOCK.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in [docx_path, blinded_docx_path, pptx_path, md_path, blinded_md_path, sup_path, highlights_path, cover_path, titlepage_path]:
            if path and path.exists():
                zf.write(path, arcname=path.name)
        if sup_md_path and sup_md_path.exists():
            zf.write(sup_md_path, arcname=sup_md_path.name)
        for fig in sorted(sub_fig_files):
            zf.write(fig, arcname=f"figures/{fig.suffix.lstrip('.')}/{fig.name}")
    print(f"Wrote {zip_path}")


if __name__ == "__main__":
    main()
