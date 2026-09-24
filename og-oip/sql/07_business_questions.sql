-- Business questions answered in SQL (PostgreSQL). SYNTHETIC data; results are illustrative of the fictional PetroNexa Energy.
SET search_path TO og_oip;

-- BQ01 Which fields lose the most revenue to production loss, and what share of revenue is that?
WITH lost AS (SELECT w.field_id, SUM(w.production_loss_bbl * s.oil_price_usd) AS lost_usd
              FROM v_well_daily w JOIN fact_sales s ON s.field_id=w.field_id AND s.date=w.date GROUP BY w.field_id),
rev AS (SELECT field_id, SUM(revenue_usd) AS revenue_usd FROM fact_sales GROUP BY field_id)
SELECT l.field_id, ROUND(l.lost_usd) AS lost_usd, ROUND(100*l.lost_usd/r.revenue_usd,1) AS pct_of_revenue FROM lost l JOIN rev r USING (field_id) ORDER BY lost_usd DESC;

-- BQ02 Which equipment types drive the most downtime and cost?
SELECT equipment_type, ROUND(SUM(total_downtime_hours)) AS downtime_h, ROUND(SUM(maintenance_cost_usd)) AS cost_usd,
       ROUND(100.0*SUM(total_downtime_hours)/SUM(SUM(total_downtime_hours)) OVER (),1) AS downtime_share_pct
FROM v_equipment_reliability GROUP BY equipment_type ORDER BY downtime_h DESC;

-- BQ03 Water-management candidates: wells with water cut > 60% in the last 30 days, ranked by oil rate
SELECT well_id, well_name, ROUND(AVG(water_cut_pct),1) AS water_cut_pct, ROUND(AVG(oil_production_bbl),1) AS oil_rate_bbl_d
FROM v_well_daily WHERE date > (SELECT MAX(date) FROM fact_production) - 30 GROUP BY well_id, well_name
HAVING AVG(water_cut_pct) > 60 ORDER BY oil_rate_bbl_d DESC;

-- BQ04 Are suppliers of critical-path categories delivering late more often than average?
WITH s AS (SELECT * FROM v_supplier_performance)
SELECT supplier_category, ROUND(AVG(on_time_pct),1) AS avg_on_time_pct, ROUND(AVG(avg_actual_lead_days - avg_quoted_lead_days),1) AS avg_gap_days,
       ROUND(AVG(on_time_pct) - (SELECT AVG(on_time_pct) FROM s),1) AS vs_overall_pts
FROM s GROUP BY supplier_category ORDER BY avg_on_time_pct;

-- BQ05 What share of maintenance cost and downtime comes from corrective work?
SELECT maintenance_type, COUNT(*) AS events, ROUND(100.0*SUM(total_cost)/SUM(SUM(total_cost)) OVER (),1) AS cost_share_pct,
       ROUND(100.0*SUM(downtime_hours)/SUM(SUM(downtime_hours)) OVER (),1) AS downtime_share_pct FROM fact_maintenance GROUP BY maintenance_type ORDER BY cost_share_pct DESC;

-- BQ06 Is unit cost per barrel improving year over year by field?
WITH y AS (SELECT field_id, EXTRACT(YEAR FROM month)::int AS year, SUM(opex_usd)/SUM(oil_sold_bbl) AS cost_per_bbl FROM v_field_financial_monthly GROUP BY 1,2)
SELECT field_id, year, ROUND(cost_per_bbl,2) AS cost_per_bbl, ROUND(cost_per_bbl - LAG(cost_per_bbl) OVER (PARTITION BY field_id ORDER BY year),2) AS yoy_change FROM y ORDER BY field_id, year;

-- BQ07 Which material categories combine high consumption value with long days of inventory?
WITH p AS (SELECT m.material_category, SUM(i.consumption*i.unit_cost) AS consumption_usd, AVG(i.closing_stock*i.unit_cost) AS avg_stock_usd_per_item
           FROM fact_inventory i JOIN dim_material m USING (material_id) GROUP BY m.material_category)
SELECT material_category, ROUND(consumption_usd) AS consumption_usd, ROUND(avg_stock_usd_per_item) AS avg_stock_usd_per_item FROM p ORDER BY consumption_usd DESC;

-- BQ08 HSE hot spots: field-months with the most incidents
SELECT field_id, month, incidents, lost_time_incidents FROM v_hse_monthly ORDER BY incidents DESC, lost_time_incidents DESC LIMIT 10;

-- BQ09 High-criticality equipment needing attention (score = criticality weight x downtime hours)
SELECT equipment_id, equipment_name, criticality, failures, ROUND(total_downtime_hours) AS downtime_h,
       ROUND(total_downtime_hours * CASE criticality WHEN 'High' THEN 3 WHEN 'Medium' THEN 2 ELSE 1 END) AS priority_score
FROM v_equipment_reliability ORDER BY priority_score DESC LIMIT 10;

-- BQ10 Wells whose rate fell most between the first and last 90 days AND had above-median downtime
WITH d AS (SELECT well_id, AVG(oil_production_bbl) FILTER (WHERE date < (SELECT MIN(date) FROM fact_production) + 90) AS early,
                          AVG(oil_production_bbl) FILTER (WHERE date > (SELECT MAX(date) FROM fact_production) - 90) AS late,
                          AVG(downtime_hours) AS avg_dt FROM fact_production GROUP BY well_id)
SELECT well_id, ROUND(early,1) AS early_rate, ROUND(late,1) AS late_rate, ROUND(100*(late/early-1),1) AS change_pct, ROUND(avg_dt,2) AS avg_downtime_h
FROM d WHERE early > 0 AND late IS NOT NULL AND avg_dt > (SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY avg_dt) FROM d) ORDER BY change_pct LIMIT 10;

-- BQ11 Field scorecard: normalised rank across loss %, cost per bbl and incident count (lower is better for each)
WITH a AS (SELECT field_id, 100.0*SUM(loss_bbl)/SUM(potential_bbl) AS loss_pct FROM v_field_monthly_production GROUP BY field_id),
b AS (SELECT field_id, SUM(opex_usd)/SUM(oil_sold_bbl) AS cost_bbl FROM v_field_financial_monthly GROUP BY field_id),
c AS (SELECT field_id, COUNT(*) AS incidents FROM fact_hse GROUP BY field_id)
SELECT a.field_id, ROUND(a.loss_pct,2) AS loss_pct, ROUND(b.cost_bbl,2) AS cost_per_bbl, c.incidents,
       RANK() OVER (ORDER BY a.loss_pct) + RANK() OVER (ORDER BY b.cost_bbl) + RANK() OVER (ORDER BY c.incidents) AS rank_sum
FROM a JOIN b USING (field_id) JOIN c USING (field_id) ORDER BY rank_sum;

-- BQ12 Executive monthly scorecard
WITH p AS (SELECT month, SUM(oil_bbl) AS oil_bbl, 100.0*SUM(loss_bbl)/SUM(potential_bbl) AS loss_pct FROM v_field_monthly_production GROUP BY month),
f AS (SELECT month, SUM(revenue_usd) AS revenue, SUM(opex_usd) AS opex FROM v_field_financial_monthly GROUP BY month),
h AS (SELECT month, SUM(incidents) AS incidents FROM v_hse_monthly GROUP BY month),
m AS (SELECT date_trunc('month', date)::date AS month, COUNT(*) FILTER (WHERE maintenance_type='Corrective') AS failures FROM fact_maintenance GROUP BY 1)
SELECT p.month, ROUND(p.oil_bbl) AS oil_bbl, ROUND(p.loss_pct,2) AS loss_pct, ROUND(f.revenue) AS revenue_usd, ROUND(f.opex) AS opex_usd, h.incidents, m.failures
FROM p JOIN f USING (month) LEFT JOIN h USING (month) LEFT JOIN m USING (month) ORDER BY p.month;
