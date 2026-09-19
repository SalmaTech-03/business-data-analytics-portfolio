"""Tests for data loading, cleaning and quality checking."""

import numpy as np
import pandas as pd
import pytest

from src import data_cleaning as dc
from src import feature_engineering as fe


@pytest.fixture
def messy_frame():
    """A frame carrying the quirks found in the real source files."""
    return pd.DataFrame({
        "Customer_ID": [3, 1, 2],
        "Name": ["C Third", "A First", "B Second"],
        "Customer_Segment": ["  Credit Card Only ", "Loyalty Club Only", "Store Mailing List"],
        "ZIP": [1234, 80224, 80111],
        "Avg_Sale_Amount": [100.0, 200.0, 300.0],
        "Avg_Num_Products_Purchased": [1, 2, 3],
        "#_Years_as_Customer": [5, 3, 1],
    })


class TestStandardiseColumns:
    def test_hash_prefix_removed_from_tenure(self, messy_frame):
        """`#_Years_as_Customer` is invalid in SQL and awkward in BI tools."""
        out = dc.standardise_columns(messy_frame)
        assert "Years_as_Customer" in out.columns
        assert "#_Years_as_Customer" not in out.columns

    def test_whitespace_stripped_from_column_names(self):
        out = dc.standardise_columns(pd.DataFrame({"  Customer_ID  ": [1]}))
        assert list(out.columns) == ["Customer_ID"]

    def test_other_columns_untouched(self, messy_frame):
        out = dc.standardise_columns(messy_frame)
        assert "Avg_Sale_Amount" in out.columns


class TestCleanCustomers:
    def test_segment_whitespace_stripped(self, messy_frame):
        """Untrimmed labels would create phantom categories when encoded."""
        out = dc.clean_customers(messy_frame)
        assert set(out["Customer_Segment"]) == {
            "Credit Card Only", "Loyalty Club Only", "Store Mailing List"
        }

    def test_zip_becomes_zero_padded_string(self, messy_frame):
        """An integer ZIP silently destroys leading zeros."""
        out = dc.clean_customers(messy_frame)
        assert not pd.api.types.is_numeric_dtype(out["ZIP"])
        assert "01234" in list(out["ZIP"])

    def test_rows_sorted_by_customer_id(self, messy_frame):
        out = dc.clean_customers(messy_frame)
        assert list(out["Customer_ID"]) == [1, 2, 3]

    def test_no_rows_lost(self, messy_frame):
        assert len(dc.clean_customers(messy_frame)) == len(messy_frame)

    def test_numeric_columns_remain_numeric(self, messy_frame):
        out = dc.clean_customers(messy_frame)
        assert pd.api.types.is_numeric_dtype(out["Avg_Sale_Amount"])


class TestDataQualityChecks:
    def test_clean_frame_reports_no_issues(self, messy_frame):
        report = dc.check_data_quality(dc.clean_customers(messy_frame))
        assert report["total_missing"] == 0
        assert report["duplicate_rows"] == 0
        assert report["duplicate_ids"] == 0

    def test_missing_values_are_counted(self, messy_frame):
        messy_frame.loc[0, "Avg_Sale_Amount"] = np.nan
        report = dc.check_data_quality(messy_frame)
        assert report["total_missing"] == 1

    def test_duplicate_ids_are_detected(self, messy_frame):
        dup = pd.concat([messy_frame, messy_frame.iloc[[0]]], ignore_index=True)
        assert dc.check_data_quality(dup)["duplicate_ids"] == 1

    def test_unexpected_segment_label_is_flagged(self, messy_frame):
        messy_frame.loc[0, "Customer_Segment"] = "Platinum Tier"
        report = dc.check_data_quality(messy_frame)
        assert "Platinum Tier" in report["unexpected_segments"]

    def test_out_of_range_probabilities_are_flagged(self):
        df = pd.DataFrame({"Score_Yes": [0.5, 1.4, -0.2], "Score_No": [0.5, -0.4, 1.2]})
        assert dc.check_data_quality(df)["Score_Yes_out_of_range"] == 2

    def test_probability_pair_consistency_is_measured(self):
        df = pd.DataFrame({"Score_Yes": [0.3, 0.7], "Score_No": [0.7, 0.3]})
        assert dc.check_data_quality(df)["max_score_sum_deviation"] == pytest.approx(0.0)

    def test_non_positive_target_is_flagged(self, messy_frame):
        messy_frame.loc[0, "Avg_Sale_Amount"] = 0.0
        assert dc.check_data_quality(messy_frame)["non_positive_target"] == 1


class TestOutlierFlagging:
    def test_extreme_value_flagged(self):
        s = pd.Series([10, 11, 12, 13, 14, 15, 1000])
        assert dc.flag_outliers_iqr(s).iloc[-1]

    def test_uniform_series_has_no_outliers(self):
        assert not dc.flag_outliers_iqr(pd.Series([5.0] * 20)).any()

    def test_returns_boolean_mask_of_matching_length(self):
        s = pd.Series([1, 2, 3, 100])
        mask = dc.flag_outliers_iqr(s)
        assert len(mask) == len(s)
        assert mask.dtype == bool


class TestLoaders:
    def test_missing_customer_file_raises_with_a_useful_message(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="p1-customers"):
            dc.load_customers(tmp_path / "nope.xlsx")

    def test_missing_mailing_list_raises_with_a_useful_message(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="p1-mailinglist"):
            dc.load_mailing_list(tmp_path / "nope.xlsx")


class TestFeatureEngineering:
    """BRule-05, BRule-07: what enters the model, and how it is encoded."""

    @pytest.fixture
    def frame(self):
        return pd.DataFrame({
            "Customer_ID": [1, 2, 3, 4],
            "Name": ["A", "B", "C", "D"],
            "Avg_Num_Products_Purchased": [1, 2, 3, 4],
            "Customer_Segment": ["Credit Card Only", "Loyalty Club Only",
                                 "Loyalty Club and Credit Card", "Store Mailing List"],
        })

    def test_reference_segment_is_dropped(self, frame):
        """All four dummies would be perfectly collinear with the intercept."""
        X = fe.build_feature_matrix(frame)
        assert "Customer_Segment_Credit Card Only" not in X.columns

    def test_three_segment_indicators_remain(self, frame):
        X = fe.build_feature_matrix(frame)
        assert sum(c.startswith("Customer_Segment_") for c in X.columns) == 3

    def test_identifiers_and_names_excluded(self, frame):
        X = fe.build_feature_matrix(frame)
        assert "Customer_ID" not in X.columns
        assert "Name" not in X.columns

    def test_reference_customer_has_all_zero_indicators(self, frame):
        X = fe.build_feature_matrix(frame)
        seg_cols = [c for c in X.columns if c.startswith("Customer_Segment_")]
        assert X.loc[0, seg_cols].sum() == 0

    def test_all_values_numeric(self, frame):
        X = fe.build_feature_matrix(frame)
        assert all(pd.api.types.is_numeric_dtype(X[c]) for c in X.columns)

    def test_missing_segment_in_scoring_data_becomes_a_zero_column(self, frame):
        """A scoring set lacking a segment must still align to the training columns."""
        training_cols = list(fe.build_feature_matrix(frame).columns)
        partial = frame[frame["Customer_Segment"] == "Credit Card Only"]
        X = fe.build_feature_matrix(partial, columns=training_cols)
        assert list(X.columns) == training_cols
        assert X.shape[0] == 1

    def test_missing_required_column_raises(self):
        with pytest.raises(KeyError):
            fe.build_feature_matrix(pd.DataFrame({"Customer_Segment": ["Credit Card Only"]}))
