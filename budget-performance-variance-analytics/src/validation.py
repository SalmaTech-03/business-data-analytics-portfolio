"""
validation.py

Data validation checks for the Budget Performance & Variance
Analytics pipeline. Returns a structured, human-readable
ValidationResult rather than raising on every issue, so the caller
(run_analysis.py) can decide what to do with warnings vs. hard
failures.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from data_loading import REQUIRED_COLUMNS

VALID_QUARTERS = {"Q1", "Q2", "Q3", "Q4"}
VALID_BUDGET_STATUS = {"Efficient", "Moderate", "Inefficient"}


@dataclass
class ValidationResult:
    passed: bool
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def report(self) -> str:
        lines = ["VALIDATION RESULT: " + ("PASS" if self.passed else "FAIL")]
        if self.errors:
            lines.append("Errors:")
            lines += [f"  - {e}" for e in self.errors]
        if self.warnings:
            lines.append("Warnings:")
            lines += [f"  - {w}" for w in self.warnings]
        if not self.errors and not self.warnings:
            lines.append("No issues found.")
        return "\n".join(lines)


def validate_required_columns(df: pd.DataFrame) -> list[str]:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns
               and c.lower() not in df.columns]
    return [f"Missing required column: {c}" for c in missing]


def validate_no_duplicates(df: pd.DataFrame, id_col: str = "record_id") -> list[str]:
    errors = []
    if df.duplicated().sum() > 0:
        errors.append(f"{df.duplicated().sum()} fully duplicated rows found.")
    if id_col in df.columns and df[id_col].duplicated().sum() > 0:
        errors.append(
            f"{df[id_col].duplicated().sum()} duplicate {id_col} values found."
        )
    return errors


def validate_categorical_domains(df: pd.DataFrame) -> list[str]:
    warnings = []
    if "fiscal_quarter" in df.columns:
        bad = set(df["fiscal_quarter"].astype(str).unique()) - VALID_QUARTERS
        if bad:
            warnings.append(f"Unexpected fiscal_quarter values: {bad}")
    if "budget_status" in df.columns:
        bad = set(df["budget_status"].astype(str).unique()) - VALID_BUDGET_STATUS
        if bad:
            warnings.append(f"Unexpected budget_status values: {bad}")
    return warnings


def validate_non_negative(df: pd.DataFrame, columns: list[str]) -> list[str]:
    warnings = []
    for col in columns:
        if col in df.columns:
            n_negative = int((df[col] < 0).sum())
            if n_negative:
                warnings.append(f"{n_negative} negative values found in '{col}'.")
    return warnings


def validate_utilization_sanity(df: pd.DataFrame, extreme_ratio: float = 3.0) -> list[str]:
    """Flag (don't fail on) records where utilization is extremely far
    from 100% of allocation - useful for spotting data entry errors."""
    warnings = []
    if {"budget_allocated", "budget_utilized"}.issubset(df.columns):
        ratio = df["budget_utilized"] / df["budget_allocated"].replace(0, pd.NA)
        n_extreme = int((ratio > extreme_ratio).sum())
        if n_extreme:
            warnings.append(
                f"{n_extreme} records have Budget_Utilized > "
                f"{extreme_ratio}x Budget_Allocated."
            )
    return warnings


def run_all_validations(df: pd.DataFrame) -> ValidationResult:
    errors = []
    errors += validate_required_columns(df)
    errors += validate_no_duplicates(df)

    warnings = []
    warnings += validate_categorical_domains(df)
    warnings += validate_non_negative(
        df, ["budget_allocated", "budget_utilized", "monthly_expense",
             "revenue_forecast", "actual_revenue", "inflation_rate",
             "allocation_efficiency"]
    )
    warnings += validate_utilization_sanity(df)

    return ValidationResult(passed=(len(errors) == 0), errors=errors, warnings=warnings)


if __name__ == "__main__":
    from data_loading import load_dataset
    from data_cleaning import clean_dataset

    raw = load_dataset()
    cleaned, _ = clean_dataset(raw)
    result = run_all_validations(cleaned)
    print(result.report())
