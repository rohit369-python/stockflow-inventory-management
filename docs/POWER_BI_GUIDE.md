# Power BI starter guide

Connect Power BI Desktop to PostgreSQL using a dedicated read-only role. Import `powerbi/sql/reporting_views.sql` after deploying it with a DBA-reviewed migration. Use `vw_inventory_position` for current stock and `vw_stock_movement_daily` for movement trends.

The included DAX file contains only measures supported by the implemented tables. Do not infer revenue, gross profit, supplier performance or overdue receivables until the corresponding complete facts, tax treatment and accounting rules exist. The future star schema should define one row per sales line, purchase line, movement event, payment event and daily inventory/product/warehouse snapshot. Avoid fact-to-fact joins.
