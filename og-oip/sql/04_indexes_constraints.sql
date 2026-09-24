SET search_path TO og_oip;
-- Primary keys / foreign keys are declared in 02 and 03. Extra indexes for analytical access paths:
CREATE INDEX idx_prod_date            ON fact_production (date);
CREATE INDEX idx_maint_equipment_date ON fact_maintenance (equipment_id, date);
CREATE INDEX idx_maint_type           ON fact_maintenance (maintenance_type);
CREATE INDEX idx_sensor_ts            ON fact_sensor (timestamp);
CREATE INDEX idx_sales_date           ON fact_sales (date);
CREATE INDEX idx_opcost_date_cat      ON fact_operating_cost (date, cost_category);
CREATE INDEX idx_inv_date             ON fact_inventory (date);
CREATE INDEX idx_inv_stockout         ON fact_inventory (stockout_flag) WHERE stockout_flag = 1;
CREATE INDEX idx_po_supplier          ON fact_purchase_order (supplier_id);
CREATE INDEX idx_hse_field_date       ON fact_hse (field_id, date);
CREATE INDEX idx_well_field           ON dim_well (field_id);
CREATE INDEX idx_equipment_field      ON dim_equipment (field_id);
ANALYZE;
