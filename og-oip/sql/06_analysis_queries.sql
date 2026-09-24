-- Analytical queries (PostgreSQL). SYNTHETIC data. Each query is numbered for traceability (see business-analysis/requirements_traceability_matrix.md).
SET search_path TO og_oip;

-- ===================== PRODUCTION =====================
-- Q01 Total production by field
SELECT f.field_id, f.field_name, SUM(oil_production_bbl) AS oil_bbl, SUM(gas_production_mcf) AS gas_mcf, SUM(water_production_bbl) AS water_bbl
FROM fact_production p JOIN dim_well w USING (well_id) JOIN dim_field f USING (field_id)
GROUP BY f.field_id, f.field_name ORDER BY oil_bbl DESC;

-- Q02 Monthly oil by field with month-over-month change (LAG)
WITH m AS (SELECT field_id, month, oil_bbl FROM v_field_monthly_production)
SELECT field_id, month, oil_bbl, oil_bbl - LAG(oil_bbl) OVER (PARTITION BY field_id ORDER BY month) AS mom_change_bbl,
       ROUND(100.0 * (oil_bbl / NULLIF(LAG(oil_bbl) OVER (PARTITION BY field_id ORDER BY month),0) - 1), 2) AS mom_pct
FROM m ORDER BY field_id, month;

-- Q03 Top 10 wells by cumulative oil
SELECT well_id, well_name, SUM(oil_production_bbl) AS cum_oil_bbl, RANK() OVER (ORDER BY SUM(oil_production_bbl) DESC) AS rnk
FROM v_well_daily GROUP BY well_id, well_name ORDER BY rnk LIMIT 10;

-- Q04 Well rank within field by average oil rate per producing day
SELECT field_id, well_id, ROUND(AVG(oil_production_bbl),1) AS avg_oil_rate_bbl_d,
       DENSE_RANK() OVER (PARTITION BY field_id ORDER BY AVG(oil_production_bbl) DESC) AS rank_in_field
FROM v_well_daily GROUP BY field_id, well_id ORDER BY field_id, rank_in_field;

-- Q05 Production loss versus simulated potential by field
SELECT field_id, SUM(potential_bbl) AS potential_bbl, SUM(loss_bbl) AS loss_bbl, ROUND(100.0*SUM(loss_bbl)/SUM(potential_bbl),2) AS loss_pct
FROM v_field_monthly_production GROUP BY field_id ORDER BY loss_bbl DESC;

-- Q06 Wells with highest loss percentage (at least 300 producing days)
SELECT well_id, well_name, COUNT(*) AS days, ROUND(100.0*SUM(production_loss_bbl)/SUM(potential_production_bbl),2) AS loss_pct
FROM v_well_daily GROUP BY well_id, well_name HAVING COUNT(*) >= 300 ORDER BY loss_pct DESC LIMIT 10;

-- Q07 Water cut trend by field and year (volume-weighted)
SELECT field_id, EXTRACT(YEAR FROM date)::int AS year, ROUND(100.0*SUM(water_production_bbl)/NULLIF(SUM(water_production_bbl+oil_production_bbl),0),2) AS water_cut_pct
FROM v_well_daily GROUP BY field_id, EXTRACT(YEAR FROM date) ORDER BY field_id, year;

-- Q08 Rolling 30-day average of daily field oil (window frame)
WITH d AS (SELECT field_id, date, SUM(oil_production_bbl) AS oil FROM v_well_daily GROUP BY field_id, date)
SELECT field_id, date, ROUND(AVG(oil) OVER (PARTITION BY field_id ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW),1) AS oil_30d_avg
FROM d ORDER BY field_id, date;

-- Q09 Wells with water cut above 60% in the last 30 days of data
SELECT well_id, well_name, ROUND(AVG(water_cut_pct),1) AS avg_water_cut_pct
FROM v_well_daily WHERE date > (SELECT MAX(date) FROM fact_production) - 30
GROUP BY well_id, well_name HAVING AVG(water_cut_pct) > 60 ORDER BY avg_water_cut_pct DESC;

-- Q10 Pressure change per well: first vs last 30 days
WITH b AS (SELECT MIN(date) AS d0, MAX(date) AS d1 FROM fact_production)
SELECT p.well_id,
       ROUND(AVG(pressure_psi) FILTER (WHERE p.date <  b.d0 + 30)) AS first_30d_psi,
       ROUND(AVG(pressure_psi) FILTER (WHERE p.date >  b.d1 - 30)) AS last_30d_psi
FROM fact_production p CROSS JOIN b GROUP BY p.well_id, b.d0, b.d1 HAVING COUNT(*) FILTER (WHERE p.date < b.d0 + 30) > 0 ORDER BY p.well_id;

-- Q11 Downtime hours by field and month
SELECT field_id, month, downtime_hours FROM v_field_monthly_production ORDER BY field_id, month;

-- ===================== MAINTENANCE / RELIABILITY =====================
-- Q12 MTBF, MTTR, availability by equipment type
SELECT equipment_type, COUNT(*) AS units, SUM(failures) AS failures, ROUND(AVG(availability_pct),2) AS avg_availability_pct,
       ROUND(SUM(mtbf_hours*failures)/NULLIF(SUM(failures),0)) AS mtbf_hours_weighted, ROUND(SUM(mttr_hours*failures)/NULLIF(SUM(failures),0),1) AS mttr_hours_weighted
FROM v_equipment_reliability GROUP BY equipment_type ORDER BY failures DESC;

-- Q13 Failures by failure type
SELECT e.equipment_type, m.failure_type, COUNT(*) AS failures, ROUND(AVG(downtime_hours),1) AS avg_downtime_h, ROUND(SUM(total_cost)) AS cost_usd
FROM fact_maintenance m JOIN dim_equipment e USING (equipment_id) WHERE m.maintenance_type = 'Corrective'
GROUP BY e.equipment_type, m.failure_type ORDER BY failures DESC;

-- Q14 Top 10 equipment by downtime
SELECT equipment_id, equipment_name, criticality, ROUND(total_downtime_hours) AS downtime_h, failures FROM v_equipment_reliability ORDER BY total_downtime_hours DESC LIMIT 10;

-- Q15 Maintenance cost by type and year
SELECT EXTRACT(YEAR FROM date)::int AS year, maintenance_type, COUNT(*) AS events, ROUND(SUM(total_cost)) AS cost_usd
FROM fact_maintenance GROUP BY 1,2 ORDER BY 1,2;

-- Q16 Corrective vs preventive events per equipment type
SELECT e.equipment_type,
       COUNT(*) FILTER (WHERE m.maintenance_type='Corrective') AS corrective,
       COUNT(*) FILTER (WHERE m.maintenance_type='Preventive') AS preventive,
       ROUND(COUNT(*) FILTER (WHERE m.maintenance_type='Corrective')::numeric / NULLIF(COUNT(*) FILTER (WHERE m.maintenance_type='Preventive'),0),2) AS corrective_per_preventive
FROM fact_maintenance m JOIN dim_equipment e USING (equipment_id) GROUP BY e.equipment_type ORDER BY corrective DESC;

-- Q17 Maintenance cost Pareto (cumulative share)
WITH c AS (SELECT equipment_id, SUM(total_cost) AS cost FROM fact_maintenance GROUP BY equipment_id)
SELECT equipment_id, ROUND(cost) AS cost_usd, ROUND(100.0*SUM(cost) OVER (ORDER BY cost DESC, equipment_id)/SUM(cost) OVER (),1) AS cum_share_pct
FROM c ORDER BY cost DESC;

-- Q18 Days between consecutive failures per equipment (LAG)
WITH f AS (SELECT equipment_id, date, LAG(date) OVER (PARTITION BY equipment_id ORDER BY date) AS prev_date
           FROM fact_maintenance WHERE maintenance_type='Corrective')
SELECT equipment_id, ROUND(AVG(date - prev_date),1) AS avg_days_between_failures, COUNT(*) FILTER (WHERE prev_date IS NOT NULL) AS intervals
FROM f GROUP BY equipment_id HAVING COUNT(prev_date) > 0 ORDER BY avg_days_between_failures;

-- Q19 Repeat failures: same equipment failing again within 30 days
WITH f AS (SELECT equipment_id, date, LAG(date) OVER (PARTITION BY equipment_id ORDER BY date) AS prev_date FROM fact_maintenance WHERE maintenance_type='Corrective')
SELECT equipment_id, COUNT(*) AS repeat_failures_within_30d FROM f WHERE date - prev_date <= 30 GROUP BY equipment_id ORDER BY repeat_failures_within_30d DESC;

-- Q20 Monthly corrective events with 3-month moving average
WITH m AS (SELECT date_trunc('month', date)::date AS month, COUNT(*) AS failures FROM fact_maintenance WHERE maintenance_type='Corrective' GROUP BY 1)
SELECT month, failures, ROUND(AVG(failures) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),2) AS failures_3m_avg FROM m ORDER BY month;

-- Q21 Age band versus failures per unit-year
WITH e AS (SELECT r.equipment_id, r.failures, CASE WHEN (DATE '2022-01-01' - d.installation_date)/365.25 < 5 THEN '<5y'
             WHEN (DATE '2022-01-01' - d.installation_date)/365.25 < 10 THEN '5-10y' ELSE '10y+' END AS age_band
           FROM v_equipment_reliability r JOIN dim_equipment d USING (equipment_id))
SELECT age_band, COUNT(*) AS units, ROUND(SUM(failures)::numeric / COUNT(*) / 3.0, 2) AS failures_per_unit_year FROM e GROUP BY age_band ORDER BY age_band;

-- ===================== FINANCIAL =====================
-- Q22 Revenue, opex, margin by field and year
SELECT field_id, EXTRACT(YEAR FROM month)::int AS year, ROUND(SUM(revenue_usd)) AS revenue_usd, ROUND(SUM(opex_usd)) AS opex_usd, ROUND(SUM(operating_margin_usd)) AS margin_usd
FROM v_field_financial_monthly GROUP BY 1,2 ORDER BY 1,2;

-- Q23 Cost per barrel by field-month
SELECT field_id, month, ROUND(cost_per_bbl_oil_sold,2) AS cost_per_bbl FROM v_field_financial_monthly ORDER BY field_id, month;

-- Q24 Opex category share
SELECT cost_category, ROUND(SUM(cost_amount_usd)) AS usd, ROUND(100.0*SUM(cost_amount_usd)/SUM(SUM(cost_amount_usd)) OVER (),1) AS share_pct
FROM fact_operating_cost GROUP BY cost_category ORDER BY usd DESC;

-- Q25 Estimated revenue lost to production loss (realised oil price of the day)
SELECT w.field_id, ROUND(SUM(w.production_loss_bbl * s.oil_price_usd)) AS est_lost_revenue_usd
FROM v_well_daily w JOIN fact_sales s ON s.field_id = w.field_id AND s.date = w.date GROUP BY w.field_id ORDER BY 2 DESC;

-- Q26 Monthly portfolio margin with cumulative margin
WITH m AS (SELECT month, SUM(operating_margin_usd) AS margin FROM v_field_financial_monthly GROUP BY month)
SELECT month, ROUND(margin) AS margin_usd, ROUND(SUM(margin) OVER (ORDER BY month)) AS cumulative_margin_usd FROM m ORDER BY month;

-- ===================== INVENTORY / SUPPLY CHAIN =====================
-- Q27 Stockout rate by material category
SELECT m.material_category, ROUND(100.0*AVG(i.stockout_flag),2) AS stockout_rate_pct, SUM(i.stockout_flag) AS stockout_days
FROM fact_inventory i JOIN dim_material m USING (material_id) GROUP BY m.material_category ORDER BY stockout_rate_pct DESC;

-- Q28 Inventory value on the last day by warehouse
SELECT warehouse_id, ROUND(SUM(stock_value_usd)) AS stock_value_usd FROM v_inventory_position GROUP BY warehouse_id ORDER BY 2 DESC;

-- Q29 Items at or below reorder level on the last day
SELECT material_id, material_name, warehouse_id, closing_stock, reorder_level FROM v_inventory_position WHERE at_or_below_reorder ORDER BY warehouse_id, material_id;

-- Q30 Annualised inventory turnover by category
SELECT m.material_category,
       ROUND((SUM(i.consumption*i.unit_cost) / NULLIF(AVG(i.closing_stock*i.unit_cost) * COUNT(DISTINCT i.material_id||i.warehouse_id),0)) / (COUNT(DISTINCT i.date)/365.25),2) AS turnover
FROM fact_inventory i JOIN dim_material m USING (material_id) GROUP BY m.material_category ORDER BY turnover DESC;

-- Q31 Supplier on-time delivery
SELECT supplier_id, supplier_name, pos_received, ROUND(on_time_pct,1) AS on_time_pct FROM v_supplier_performance ORDER BY on_time_pct;

-- Q32 Quoted vs actual lead time by supplier
SELECT supplier_id, supplier_name, ROUND(avg_quoted_lead_days,1) AS quoted_days, ROUND(avg_actual_lead_days,1) AS actual_days, ROUND(avg_actual_lead_days-avg_quoted_lead_days,1) AS gap_days
FROM v_supplier_performance ORDER BY gap_days DESC;

-- Q33 Excess inventory: average days of inventory above 90
SELECT material_id, warehouse_id, ROUND(AVG(closing_stock)/NULLIF(AVG(consumption),0),0) AS days_of_inventory, ROUND(AVG(closing_stock*unit_cost)) AS avg_value_usd
FROM fact_inventory GROUP BY material_id, warehouse_id HAVING AVG(closing_stock)/NULLIF(AVG(consumption),0) > 90 ORDER BY avg_value_usd DESC;

-- Q34 Open purchase orders
SELECT po_id, order_date, promised_date, material_id, supplier_id, warehouse_id, quantity, (promised_date < (SELECT MAX(date) FROM dim_date)) AS past_promised_date
FROM fact_purchase_order WHERE status = 'Open' ORDER BY promised_date;

-- Q35 Material consumed by maintenance work by category
SELECT m.material_category, SUM(mm.quantity) AS units, ROUND(SUM(mm.quantity*m.unit_cost)) AS value_usd
FROM fact_maintenance_material mm JOIN dim_material m USING (material_id) GROUP BY m.material_category ORDER BY value_usd DESC;

-- ===================== HSE =====================
-- Q36 Incidents by field and severity
SELECT field_id, severity, COUNT(*) AS incidents FROM fact_hse GROUP BY field_id, severity ORDER BY field_id, severity;

-- Q37 Lost-time incidents per 200,000 assumed exposure hours by field-year (assumption: 30 exposure hours per producing well-day)
WITH exp AS (SELECT w.field_id, EXTRACT(YEAR FROM p.date)::int AS year, COUNT(*) * 30.0 AS exposure_hours
             FROM fact_production p JOIN dim_well w USING (well_id) GROUP BY 1,2),
inc AS (SELECT field_id, EXTRACT(YEAR FROM date)::int AS year, SUM(lost_time_flag) AS lti, COUNT(*) AS incidents FROM fact_hse GROUP BY 1,2)
SELECT e.field_id, e.year, i.incidents, i.lti, ROUND(i.lti*200000/e.exposure_hours,2) AS ltir_per_200k_h
FROM exp e JOIN inc i USING (field_id, year) ORDER BY 1,2;

-- Q38 Root cause distribution
SELECT root_cause, COUNT(*) AS incidents, ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER (),1) AS share_pct FROM fact_hse GROUP BY root_cause ORDER BY incidents DESC;

-- Q39 Incidents within 3 days after a corrective event in the same field
SELECT COUNT(DISTINCT h.incident_id) AS incidents_in_window, (SELECT COUNT(*) FROM fact_hse) AS total_incidents
FROM fact_hse h JOIN dim_equipment e ON e.field_id = h.field_id
JOIN fact_maintenance m ON m.equipment_id = e.equipment_id AND m.maintenance_type = 'Corrective' AND h.date BETWEEN m.date AND m.date + 3;

-- Q40 Monthly incident trend
SELECT month, SUM(incidents) AS incidents, SUM(lost_time_incidents) AS lost_time FROM v_hse_monthly GROUP BY month ORDER BY month;

-- ===================== SENSORS / PREDICTIVE MAINTENANCE =====================
-- Q41 Latest sensor reading per equipment
SELECT DISTINCT ON (equipment_id) equipment_id, timestamp, temperature_c, vibration_mm_s, pressure_psi
FROM fact_sensor ORDER BY equipment_id, timestamp DESC;

-- Q42 Equipment-days where daily mean vibration exceeds 1.3x the equipment's median daily vibration
WITH d AS (SELECT equipment_id, timestamp::date AS day, AVG(vibration_mm_s) AS vib FROM fact_sensor GROUP BY 1,2),
b AS (SELECT equipment_id, percentile_cont(0.5) WITHIN GROUP (ORDER BY vib) AS med FROM d GROUP BY equipment_id)
SELECT d.equipment_id, COUNT(*) AS alert_days FROM d JOIN b USING (equipment_id) WHERE d.vib > 1.3*b.med GROUP BY d.equipment_id ORDER BY alert_days DESC LIMIT 15;

-- Q43 Mean vibration in the 7 days before corrective failures versus the equipment overall mean
WITH pre AS (SELECT m.equipment_id, AVG(s.vibration_mm_s) AS pre_failure_vib
             FROM fact_maintenance m JOIN fact_sensor s ON s.equipment_id = m.equipment_id AND s.timestamp >= m.date - 7 AND s.timestamp < m.date
             WHERE m.maintenance_type='Corrective' GROUP BY m.equipment_id),
overall AS (SELECT equipment_id, AVG(vibration_mm_s) AS overall_vib FROM fact_sensor GROUP BY equipment_id)
SELECT p.equipment_id, ROUND(p.pre_failure_vib,3) AS pre_failure_vib, ROUND(o.overall_vib,3) AS overall_vib, ROUND(p.pre_failure_vib/o.overall_vib,2) AS ratio
FROM pre p JOIN overall o USING (equipment_id) ORDER BY ratio DESC;

-- ===================== DATA QUALITY / GOVERNANCE =====================
-- Q44 Production rows carrying a data-quality flag
SELECT COALESCE(NULLIF(dq_flag,''),'(no flag)') AS dq_flag, COUNT(*) AS rows FROM fact_production GROUP BY 1 ORDER BY rows DESC;

-- Q45 Orphan check: production rows whose well is missing (expected 0)
SELECT COUNT(*) AS orphan_rows FROM fact_production p LEFT JOIN dim_well w USING (well_id) WHERE w.well_id IS NULL;

-- Q46 Row counts per table
SELECT 'fact_production' AS tbl, COUNT(*) FROM fact_production UNION ALL SELECT 'fact_sensor', COUNT(*) FROM fact_sensor
UNION ALL SELECT 'fact_maintenance', COUNT(*) FROM fact_maintenance UNION ALL SELECT 'fact_inventory', COUNT(*) FROM fact_inventory
UNION ALL SELECT 'fact_sales', COUNT(*) FROM fact_sales UNION ALL SELECT 'fact_operating_cost', COUNT(*) FROM fact_operating_cost
UNION ALL SELECT 'fact_purchase_order', COUNT(*) FROM fact_purchase_order UNION ALL SELECT 'fact_hse', COUNT(*) FROM fact_hse;
