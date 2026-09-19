"""End-to-end pipeline: clean -> model -> economics -> prioritise -> outputs."""
import json
from pathlib import Path
import pandas as pd
from src import data_cleaning as dc, modeling as md, profitability as pf, evaluation as ev

OUT = Path("outputs"); OUT.mkdir(exist_ok=True)
PROC = Path("data/processed"); PROC.mkdir(parents=True, exist_ok=True)

cust = dc.clean_customers(dc.load_customers())
mail = dc.clean_mailing_list(dc.load_mailing_list())
qc = {"customers": dc.check_data_quality(cust, "p1-customers"),
      "mailing_list": dc.check_data_quality(mail, "p1-mailinglist")}

model = md.fit_linear_model(cust)
insample = ev.regression_metrics(cust["Avg_Sale_Amount"], model.predict(cust))
holdout = md.holdout_evaluation(cust)
cv = md.cross_validated_r2(cust)
alts = md.compare_alternatives(cust)

scored = md.score_mailing_list(model, mail)
econ = pf.build_customer_economics(scored)
econ = pf.prioritise_customers(econ)
summary = pf.campaign_summary(econ)

sens = pf.sensitivity_grid(econ, [0.40,0.45,0.50,0.55,0.60], [5.00,6.50,8.00,10.00],
                           [0.6,0.8,1.0,1.2])

cols = ["Customer_ID","Name","Customer_Segment","City","State","ZIP","Store_Number",
        "Avg_Num_Products_Purchased","Years_as_Customer","Predicted_Sale_Amount",
        "Response_Probability","Expected_Revenue","Gross_Profit","Catalog_Cost",
        "Expected_Net_Profit","Customer_ROI","Priority","Profit_Rank"]
econ[cols].to_csv(OUT/"customer_scores.csv", index=False)
pd.DataFrame([summary]).to_csv(OUT/"campaign_summary.csv", index=False)
sens.to_csv(OUT/"sensitivity_analysis.csv", index=False)

seg = econ.groupby("Customer_Segment").agg(
    Customers=("Customer_ID","count"),
    Avg_Predicted_Sale=("Predicted_Sale_Amount","mean"),
    Avg_Response_Prob=("Response_Probability","mean"),
    Expected_Revenue=("Expected_Revenue","sum"),
    Gross_Profit=("Gross_Profit","sum"),
    Expected_Net_Profit=("Expected_Net_Profit","sum")).reset_index()
seg["Campaign_Cost"]=seg["Customers"]*pf.COST_PER_CATALOG
seg["ROI"]=seg["Expected_Net_Profit"]/seg["Campaign_Cost"]
seg.to_csv(OUT/"segment_summary.csv", index=False)

prio = econ.groupby("Priority").agg(Customers=("Customer_ID","count"),
    Expected_Revenue=("Expected_Revenue","sum"),
    Expected_Net_Profit=("Expected_Net_Profit","sum")).reset_index()
prio.to_csv(OUT/"priority_summary.csv", index=False)
econ[cols].to_csv(PROC/"mailing_list_scored.csv", index=False)
cust.to_csv(PROC/"customers_clean.csv", index=False)

hist_seg = cust.groupby("Customer_Segment").agg(
    Customers=("Customer_ID","count"),
    Mean_Sale=("Avg_Sale_Amount","mean"),
    Median_Sale=("Avg_Sale_Amount","median"),
    Mean_Products=("Avg_Num_Products_Purchased","mean")).reset_index()

resp = cust.groupby("Responded_to_Last_Catalog")["Avg_Sale_Amount"].agg(["count","mean","median"]).reset_index()
corr = cust[["Avg_Sale_Amount","Avg_Num_Products_Purchased","Years_as_Customer"]].corr()
out_outliers = int(dc.flag_outliers_iqr(cust["Avg_Sale_Amount"]).sum())

facts = {
  "qc": qc, "coefficients": model.coefficients.to_dict(),
  "insample": insample, "holdout": holdout, "cv": cv,
  "alternatives": alts.to_dict("records"), "summary": summary,
  "segment": seg.to_dict("records"), "priority": prio.to_dict("records"),
  "hist_segment": hist_seg.to_dict("records"), "response": resp.to_dict("records"),
  "corr": corr.to_dict(), "outliers_target": out_outliers,
  "target_desc": cust["Avg_Sale_Amount"].describe().to_dict(),
  "pred_desc": econ["Predicted_Sale_Amount"].describe().to_dict(),
  "prob_desc": econ["Response_Probability"].describe().to_dict(),
  "error_band": ev.financial_error_band(holdout["test"]["mae"], 250, 0.5),
  "high_cut": float(econ["Priority_Threshold_High"].iloc[0]),
  "n_negative_profit": int((econ["Expected_Net_Profit"]<=0).sum()),
  "mail_segments": mail["Customer_Segment"].value_counts().to_dict(),
  "years_desc_mail": mail["Years_as_Customer"].describe().to_dict(),
  "breakeven_rm": summary["breakeven_response_multiplier"],
}
json.dump(facts, open(OUT/"analysis_facts.json","w"), indent=2, default=str)
print(json.dumps({k:facts[k] for k in ["coefficients","insample","holdout","cv","summary","high_cut","n_negative_profit","outliers_target"]}, indent=1, default=str))
print(alts.to_string()); print(seg.to_string()); print(prio.to_string()); print(hist_seg.to_string()); print(resp.to_string())
print(corr.to_string()); print(facts["prob_desc"]); print(facts["target_desc"]); print(facts["mail_segments"])
