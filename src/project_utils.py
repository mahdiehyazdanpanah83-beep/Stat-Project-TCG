"""Reusable helpers for the TCGA-BRCA statistics project.

All paths are resolved relative to the repository; no machine-specific paths.
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd


def project_root(start=None):
    here = Path(start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "data").is_dir() and ((candidate / "notebooks").exists() or (candidate / "src").exists()):
            return candidate
    # Notebook launched from the notebooks directory in a fresh clone.
    if here.name == "notebooks" and (here.parent / "data").exists():
        return here.parent
    raise FileNotFoundError("Project root not found. Run this notebook inside the cloned repository.")


def find_column(df, candidates, required=True, label="column"):
    """Find a column by ordered exact names, then case-insensitive exact names."""
    lower = {str(c).lower(): c for c in df.columns}
    for name in candidates:
        if name in df.columns:
            return name
        if name.lower() in lower:
            return lower[name.lower()]
    if required:
        raise KeyError(f"Could not identify {label}. Available columns include: {list(df.columns[:60])}")
    return None


def patient_id_from_series(series):
    """Map TCGA sample/case barcodes to the 12-character patient barcode."""
    raw = series.astype("string").str.upper().str.strip()
    extracted = raw.str.extract(r"(TCGA-[A-Z0-9]{2}-[A-Z0-9]{4})", expand=False)
    # Do not silently treat arbitrary non-TCGA strings as valid patient IDs.
    return extracted


def normalize_age(series):
    x = pd.to_numeric(series, errors="coerce")
    med = x.median()
    # GDC age_at_index is ordinarily in years; some sources encode days.
    if pd.notna(med) and med > 120:
        x = x / 365.25
    return x


def simplify_stage(value):
    if pd.isna(value):
        return np.nan
    s = str(value).upper().replace("STAGE", "").strip()
    # Exclude unknown/not reported values rather than classifying them as early.
    if any(token in s for token in ["NOT REPORTED", "NOT AVAILABLE", "UNKNOWN", "N/A", "[DISCREPANCY"]):
        return np.nan
    if "IV" in s or "III" in s:
        return "Advanced"
    if "II" in s or "I" in s:
        return "Early"
    return np.nan


def clean_stage(value):
    """Convert blank and explicit missing-stage placeholders to NaN; retain other labels."""
    if pd.isna(value):
        return np.nan
    value = str(value).strip()
    normalized = value.upper().replace("_", " ").strip()
    missing_tokens = {"", "--", "-", "NOT REPORTED", "NOT AVAILABLE", "UNKNOWN", "N/A", "NA", "NULL", "NAN"}
    if normalized in missing_tokens:
        return np.nan
    return value


def consensus_stage_group(values):
    """Return a binary stage group only when all valid records agree on the group."""
    groups = set()
    for value in values:
        if pd.isna(value):
            continue
        group = simplify_stage(value)
        if pd.notna(group) and group in {"Early", "Advanced"}:
            groups.add(group)
    if len(groups) == 1:
        return next(iter(groups))
    # No usable stage, or conflicting Early/Advanced records.
    return np.nan


def mode_or_nan(series):
    s = series.dropna()
    if s.empty:
        return np.nan
    modes = s.mode()
    return modes.iloc[0] if len(modes) else np.nan


def save_figure(fig, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=300, bbox_inches="tight")
