# Risk Register

> All operational data in this project are synthetic. PetroNexa Energy is a FICTIONAL company; stakeholders and roles are illustrative assumptions.

Likelihood/Impact use L/M/H (qualitative judgement of the author, not measured).

| ID | Risk | L | I | Mitigation | Owner (assumed) |
|---|---|---|---|---|---|
| R-01 | Users mistake synthetic results for real operations | M | H | Notices on every output and chart; fictional names | Analyst |
| R-02 | KPI definitions differ between tools | M | H | Single KPI dictionary; SQL, DAX and Python use the same formulas | Data Steward |
| R-03 | Silent data loss in cleaning | L | H | Quarantine files; cleaning log with counts; validation of processed data | Data Steward |
| R-04 | Imputation biases results | M | M | Flags in dq_flag; imputed share reported; conservative methods | Analyst |
| R-05 | Forecast/ML over-trusted | M | H | Backtests, time-based splits, stated baselines and limits; ranking not auto-action | Planning |
| R-06 | Simulated relationships mistaken for discovered ones | M | H | Methodology document lists every simulated relationship; association wording | Analyst |
| R-07 | BSEE column mapping incorrect | M | M | Explicit caveat; verification step against BSEE dictionary before publication | Analyst |
| R-08 | Redistribution of real data violates terms | M | M | README asks to check publisher terms | Owner |
| R-09 | SQL not validated on a live server | M | M | Schema consistency test against CSV headers; run 04-07 on PostgreSQL before release | IT |
| R-10 | Dashboard specs drift from data model | L | M | Specs generated against real column names; consistency test | BI Dev |
| R-11 | Environment differences (package versions) | L | L | requirements.txt with tested versions | Analyst |
