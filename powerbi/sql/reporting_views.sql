-- Tenant-aware starting point for read-only BI connections.
-- Grant the Power BI database role SELECT only on approved reporting views.
CREATE OR REPLACE VIEW vw_inventory_position AS
SELECT b.organization_id, b.warehouse_id, b.product_id,
       b.on_hand, b.reserved, (b.on_hand - b.reserved) AS available
FROM inventory_balances AS b;

CREATE OR REPLACE VIEW vw_stock_movement_daily AS
SELECT organization_id, CAST(created_at AS DATE) AS movement_date,
       movement_type, product_id, warehouse_id, SUM(quantity) AS units
FROM stock_movements
GROUP BY organization_id, CAST(created_at AS DATE), movement_type, product_id, warehouse_id;
