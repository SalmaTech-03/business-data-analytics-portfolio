SET search_path TO og_oip;

CREATE OR REPLACE VIEW v_well_daily AS
SELECT p.date, p.well_id, w.well_name, w.field_id, f.field_name,
       p.operating_hours, p.downtime_hours, p.oil_production_bbl, p.gas_production_mcf, p.water_production_bbl,
       p.pressure_psi, p.temperature_c, p.water_cut_pct, p.potential_production_bbl,
       GREATEST(p.potential_production_bbl - p.oil_production_bbl, 0)                       AS production_loss_bbl,
       LEAST(p.potential_production_bbl * p.downtime_hours / 24.0,
             GREATEST(p.potential_production_bbl - p.oil_production_bbl, 0))               AS downtime_loss_bbl,
       (p.date - w.commission_date)                                                        AS well_age_days
FROM fact_production p
JOIN dim_well  w ON w.well_id  = p.well_id
JOIN dim_field f ON f.field_id = w.field_id;

CREATE OR REPLACE VIEW v_field_monthly_production AS
SELECT field_id, field_name, date_trunc('month', date)::date AS month,
       SUM(oil_production_bbl) AS oil_bbl, SUM(gas_production_mcf) AS gas_mcf, SUM(water_production_bbl) AS water_bbl,
       SUM(potential_production_bbl) AS potential_bbl, SUM(production_loss_bbl) AS loss_bbl,
       SUM(downtime_hours) AS downtime_hours
FROM v_well_daily GROUP BY field_id, field_name, date_trunc('month', date);

CREATE OR REPLACE VIEW v_equipment_reliability AS
WITH span AS (SELECT (MAX(date) - MIN(date) + 1) * 24.0 AS period_hours FROM dim_date),
m AS (
  SELECT equipment_id,
         COUNT(*) FILTER (WHERE maintenance_type = 'Corrective')                       AS failures,
         SUM(downtime_hours)                                                           AS total_downtime_hours,
         SUM(downtime_hours) FILTER (WHERE maintenance_type = 'Corrective')            AS corrective_downtime_hours,
         SUM(total_cost)                                                               AS maintenance_cost_usd
  FROM fact_maintenance GROUP BY equipment_id)
SELECT e.equipment_id, e.equipment_name, e.equipment_type, e.field_id, e.criticality,
       COALESCE(m.failures,0) AS failures, COALESCE(m.total_downtime_hours,0) AS total_downtime_hours,
       COALESCE(m.maintenance_cost_usd,0) AS maintenance_cost_usd,
       100.0 * (s.period_hours - COALESCE(m.total_downtime_hours,0)) / s.period_hours AS availability_pct,
       CASE WHEN COALESCE(m.failures,0) > 0 THEN (s.period_hours - m.total_downtime_hours) / m.failures END AS mtbf_hours,
       CASE WHEN COALESCE(m.failures,0) > 0 THEN m.corrective_downtime_hours / m.failures END AS mttr_hours
FROM dim_equipment e CROSS JOIN span s LEFT JOIN m ON m.equipment_id = e.equipment_id;

CREATE OR REPLACE VIEW v_field_financial_monthly AS
WITH s AS (SELECT field_id, date_trunc('month', date)::date AS month, SUM(oil_volume_bbl) AS oil_sold_bbl,
                  SUM(gas_volume_mcf) AS gas_sold_mcf, SUM(revenue_usd) AS revenue_usd FROM fact_sales GROUP BY 1,2),
c AS (SELECT field_id, date_trunc('month', date)::date AS month, SUM(cost_amount_usd) AS opex_usd FROM fact_operating_cost GROUP BY 1,2)
SELECT s.field_id, s.month, s.oil_sold_bbl, s.gas_sold_mcf, s.revenue_usd, c.opex_usd,
       s.revenue_usd - c.opex_usd AS operating_margin_usd, c.opex_usd / NULLIF(s.oil_sold_bbl,0) AS cost_per_bbl_oil_sold
FROM s JOIN c USING (field_id, month);

CREATE OR REPLACE VIEW v_inventory_position AS
SELECT i.material_id, m.material_name, m.material_category, i.warehouse_id, i.closing_stock, i.reorder_level,
       i.closing_stock * i.unit_cost AS stock_value_usd, (i.closing_stock <= i.reorder_level) AS at_or_below_reorder
FROM fact_inventory i JOIN dim_material m USING (material_id)
WHERE i.date = (SELECT MAX(date) FROM fact_inventory);

CREATE OR REPLACE VIEW v_supplier_performance AS
SELECT s.supplier_id, s.supplier_name, s.supplier_category, COUNT(*) AS pos_received,
       100.0 * AVG((po.received_date <= po.promised_date)::int)              AS on_time_pct,
       AVG(po.quoted_lead_time_days)                                          AS avg_quoted_lead_days,
       AVG(po.received_date - po.order_date)                                  AS avg_actual_lead_days
FROM fact_purchase_order po JOIN dim_supplier s USING (supplier_id)
WHERE po.received_date IS NOT NULL GROUP BY s.supplier_id, s.supplier_name, s.supplier_category;

CREATE OR REPLACE VIEW v_hse_monthly AS
SELECT field_id, date_trunc('month', date)::date AS month, COUNT(*) AS incidents, SUM(lost_time_flag) AS lost_time_incidents, SUM(days_lost) AS days_lost
FROM fact_hse GROUP BY field_id, date_trunc('month', date);
