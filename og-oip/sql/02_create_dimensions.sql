SET search_path TO og_oip;

CREATE TABLE dim_date (
    date_key     INTEGER PRIMARY KEY,
    date         DATE NOT NULL UNIQUE,
    year         SMALLINT NOT NULL,
    quarter      SMALLINT NOT NULL,
    month        SMALLINT NOT NULL,
    month_name   VARCHAR(12) NOT NULL,
    week         SMALLINT NOT NULL,
    day          SMALLINT NOT NULL,
    day_of_week  SMALLINT NOT NULL,
    is_weekend   BOOLEAN NOT NULL
);

CREATE TABLE dim_field (
    field_id         VARCHAR(12) PRIMARY KEY,
    field_name       VARCHAR(60) NOT NULL,
    region           VARCHAR(40),
    basin            VARCHAR(40),
    field_type       VARCHAR(12) CHECK (field_type IN ('Onshore','Offshore')),
    operator         VARCHAR(60),
    commission_date  DATE,
    status           VARCHAR(20)
);

CREATE TABLE dim_supplier (
    supplier_id        VARCHAR(12) PRIMARY KEY,
    supplier_name      VARCHAR(80) NOT NULL,
    supplier_category  VARCHAR(40),
    region             VARCHAR(40),
    lead_time_days     INTEGER CHECK (lead_time_days > 0),
    supplier_rating    NUMERIC(2,1) CHECK (supplier_rating BETWEEN 1 AND 5)
);

CREATE TABLE dim_warehouse (
    warehouse_id    VARCHAR(12) PRIMARY KEY,
    warehouse_name  VARCHAR(60) NOT NULL,
    field_id        VARCHAR(12) NOT NULL REFERENCES dim_field(field_id)
);

CREATE TABLE dim_equipment (
    equipment_id       VARCHAR(12) PRIMARY KEY,
    equipment_name     VARCHAR(60) NOT NULL,
    equipment_type     VARCHAR(30) NOT NULL,
    field_id           VARCHAR(12) NOT NULL REFERENCES dim_field(field_id),
    manufacturer       VARCHAR(60),
    installation_date  DATE,
    criticality        VARCHAR(10) CHECK (criticality IN ('Low','Medium','High')),
    status             VARCHAR(20)
);

CREATE TABLE dim_well (
    well_id               VARCHAR(12) PRIMARY KEY,
    well_name             VARCHAR(30) NOT NULL,
    field_id              VARCHAR(12) NOT NULL REFERENCES dim_field(field_id),
    well_type             VARCHAR(20),
    reservoir             VARCHAR(30),
    depth_m               INTEGER,
    latitude              NUMERIC(8,4),   -- synthetic local grid coordinate, NOT a geographic position
    longitude             NUMERIC(8,4),   -- synthetic local grid coordinate, NOT a geographic position
    commission_date       DATE,
    status                VARCHAR(20),
    primary_equipment_id  VARCHAR(12) REFERENCES dim_equipment(equipment_id)
);

CREATE TABLE dim_material (
    material_id          VARCHAR(12) PRIMARY KEY,
    material_name        VARCHAR(60) NOT NULL,
    material_category    VARCHAR(30) NOT NULL,
    unit                 VARCHAR(8),
    unit_cost            NUMERIC(12,2) CHECK (unit_cost > 0),
    reorder_level        INTEGER,
    lead_time_days       INTEGER,
    primary_supplier_id  VARCHAR(12) REFERENCES dim_supplier(supplier_id)
);

-- Which wells are affected when an equipment item is down (impact_factor = share of well downtime attributed)
CREATE TABLE bridge_equipment_well (
    equipment_id   VARCHAR(12) NOT NULL REFERENCES dim_equipment(equipment_id),
    well_id        VARCHAR(12) NOT NULL REFERENCES dim_well(well_id),
    impact_factor  NUMERIC(4,2) NOT NULL CHECK (impact_factor > 0 AND impact_factor <= 1),
    PRIMARY KEY (equipment_id, well_id)
);
