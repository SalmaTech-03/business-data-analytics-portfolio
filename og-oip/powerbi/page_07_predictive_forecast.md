# Page 7 - Predictive Maintenance & Forecast

> Synthetic data (fictional PetroNexa Energy). Specification only; no .pbix is provided.

**Audience:** Reliability Engineer, Planning Analyst

## Layout
| Visual | Fields / measures |
|---|---|
| Bar: failure risk score by equipment (Top 15) | ml_latest_equipment_risk[equipment_name], [Latest Failure Risk] |
| Card: [High Risk Units (>=0.5)] | display threshold, not the model threshold |
| Table: model metrics | ml_model_metrics_test: model, roc_auc, pr_auc, precision, recall, f1 |
| Line: 30-day forecast | forecast_next_30d[date], [Forecast Oil (bbl/d)] with last actuals from fact_production |
| Table: forecast backtest | forecast_backtest_summary: model, MAE, RMSE, MAPE_pct, mean_bias |
| Text box | Sensor relationships are simulated; metrics apply to synthetic data only. ARIMA not included. |

## Filters
Equipment type, Field

## Insight questions
1. Which units deserve inspection first? 2. How accurate are baseline forecasts?
