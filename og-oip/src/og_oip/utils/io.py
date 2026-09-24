from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def read_csv(path: Path, **kw) -> pd.DataFrame:
    return pd.read_csv(path, **kw)


def write_json(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, default=str)


def read_json(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def df_to_md(df: pd.DataFrame, floatfmt: str = ",.2f", index: bool = False, max_rows: int = 50) -> str:
    """Small dependency-free markdown table renderer."""
    d = df.head(max_rows).reset_index() if index else df.head(max_rows)
    cols = [str(c) for c in d.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in d.iterrows():
        cells = []
        for v in r.values:
            if isinstance(v, float):
                cells.append("" if pd.isna(v) else format(v, floatfmt))
            else:
                cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)
