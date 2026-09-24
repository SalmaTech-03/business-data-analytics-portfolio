SET search_path TO og_oip;

CREATE TABLE fact_production (
    date                      DATE NOT NULL,
    well_id                   VARCHAR(12) NOT NULL REFERENCES dim_well(well_id),
    operating_hours           NUMERIC(5,2) CHECK (operating_hours BETWEEN 0 AND 24),
    downtime_hours            NUMERIC(5,2) CHECK (downtime_hours BETWEEN 0 AND 24),
    oil_production_bbl        NUMERIC(12,1) CHECK (oil_production_bbl >= 0),
    gas_production_mcf        NUMERIC(12,1) CHECK (gas_production_mcf >= 0),
    water_production_bbl      NUMERIC(12,1) CHECK (water_production_bbl >= 0),
    pressure_psi              NUMERIC(8,1),
    temperature_c             NUMERIC(6,1),
    water_cut_pct             NUMERIC(5,2) CHECK (water_cut_pct BETWEEN 0 AND 100),
    potential_production_bbl  NUMERIC(12,1) CHECK (potential_production_bbl >= 0),   -- SIMULATED potential (see methodology)
    dq_flag                   VARCHAR(200),
    PRIMARY KEY (well_id, date)
);

CREATE TABLE fact_sensor (
    timestamp               TIMESTAMP NOT NULL,
    equipment_id            VARCHAR(12) NOT NULL REFERENCES dim_equipment(equipment_id),
    temperature_c           NUMERIC(7,2),
    pressure_psi            NUMERIC(8,1),
    vibration_mm_s          NUMERIC(8,3),
    flow_rate               NUMERIC(10,2),
    energy_consumption_kwh  NUMERIC(10,1),
    operating_hours         NUMERIC(5,2),
    dq_flag                 VARCHAR(300),
    PRIMARY KEY (equipment_id, timestamp)
);

CREATE TABLE fact_maintenance (
    maintenance_id     VARCHAR(16) PRIMARY KEY,
    equipment_id       VARCHAR(12) NOT NULL REFERENCES dim_equipment(equipment_id),
    date               DATE NOT NULL,
    maintenance_type   VARCHAR(12) NOT NULL CHECK (maintenance_type IN ('Corrective','Preventive','Inspection')),
    failure_type       VARCHAR(40),
    downtime_hours     NUMERIC(7,2) CHECK (downtime_hours >= 0),
    labor_cost         NUMERIC(12,2) CHECK (labor_cost >= 0),
    material_cost      NUMERIC(12,2) CHECK (material_cost >= 0),
    contractor_cost    NUMERIC(12,2) CHECK (contractor_cost >= 0),
    total_cost         NUMERIC(12,2) CHECK (total_cost >= 0),
    priority           VARCHAR(10),
    work_order_status  VARCHAR(20)
);

CREATE TABLE fact_maintenance_material (
    maintenance_id  VARCHAR(16) NOT NULL REFERENCES fact_maintenance(maintenance_id),
    material_id     VARCHAR(12) NOT NULL REFERENCES dim_material(material_id),
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    warehouse_id    VARCHAR(12) NOT NULL REFERENCES dim_warehouse(warehouse_id),
    PRIMARY KEY (maintenance_id, material_id)
);

CREATE TABLE fact_sales (
    date            DATE NOT NULL,
    field_id        VARCHAR(12) NOT NULL REFERENCES dim_field(field_id),
    oil_volume_bbl  NUMERIC(14,1),
    gas_volume_mcf  NUMERIC(14,1),
    oil_price_usd   NUMERIC(8,2),
    gas_price_usd   NUMERIC(8,3),
    revenue_usd     NUMERIC(16,2),
    PRIMARY KEY (field_id, date)
);

CREATE TABLE fact_operating_cost (
    date             DATE NOT NULL,
    field_id         VARCHAR(12) NOT NULL REFERENCES dim_field(field_id),
    cost_category    VARCHAR(20) NOT NULL CHECK (cost_category IN ('Production','Energy','Labor','Maintenance','Transportation','Utilities','Other')),
    cost_amount_usd  NUMERIC(14,2) CHECK (cost_amount_usd >= 0),
    PRIMARY KEY (field_id, date, cost_category)
);

CREATE TABLE fact_inventory (
    date           DATE NOT NULL,
    material_id    VARCHAR(12) NOT NULL REFERENCES dim_material(material_id),
    supplier_id    VARCHAR(12) NOT NULL REFERENCES dim_supplier(supplier_id),
    warehouse_id   VARCHAR(12) NOT NULL REFERENCES dim_warehouse(warehouse_id),
    opening_stock  NUMERIC(12,1) CHECK (opening_stock >= 0),
    receipts       NUMERIC(12,1) CHECK (receipts >= 0),
    consumption    NUMERIC(12,1) CHECK (consumption >= 0),
    closing_stock  NUMERIC(12,1) CHECK (closing_stock >= 0),
    reorder_level  NUMERIC(10,1),
    unit_cost      NUMERIC(12,2),
    stockout_flag  SMALLINT CHECK (stockout_flag IN (0,1)),
    PRIMARY KEY (material_id, warehouse_id, date)
);

CREATE TABLE fact_purchase_order (
    po_id                  VARCHAR(12) PRIMARY KEY,
    order_date             DATE NOT NULL,
    material_id            VARCHAR(12) NOT NULL REFERENCES dim_material(material_id),
    supplier_id            VARCHAR(12) NOT NULL REFERENCES dim_supplier(supplier_id),
    warehouse_id           VARCHAR(12) NOT NULL REFERENCES dim_warehouse(warehouse_id),
    quantity               INTEGER NOT NULL,
    quoted_lead_time_days  INTEGER,
    promised_date          DATE,
    received_date          DATE,          -- NULL for open orders
    unit_cost              NUMERIC(12,2),
    status                 VARCHAR(10) CHECK (status IN ('Open','Received'))
);

CREATE TABLE fact_hse (
    incident_id    VARCHAR(12) PRIMARY KEY,
    date           DATE NOT NULL,
    field_id       VARCHAR(12) NOT NULL REFERENCES dim_field(field_id),
    incident_type  VARCHAR(30),
    severity       VARCHAR(10) CHECK (severity IN ('Low','Medium','High','Critical')),
    lost_time_flag SMALLINT CHECK (lost_time_flag IN (0,1)),
    days_lost      INTEGER CHECK (days_lost >= 0),
    root_cause     VARCHAR(40),
    department     VARCHAR(30)
);
