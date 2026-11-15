"""Catalog, partner, warehouse and order records."""
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Numeric, Integer, Text, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

def uid(): return str(uuid4())
def now_utc(): return datetime.now(timezone.utc)

class Product(Base):
    """Sellable/purchasable SKU. Historical documents keep price snapshots."""
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("organization_id", "sku", name="uq_product_org_sku"),
                      CheckConstraint("purchase_price >= 0 AND selling_price >= 0", name="ck_product_prices"))
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    sku: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(14,2), default=Decimal("0"))
    selling_price: Mapped[Decimal] = mapped_column(Numeric(14,2), default=Decimal("0"))
    reorder_level: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

class Supplier(Base):
    """Supplier directory entry owned by one organization."""
    __tablename__ = "suppliers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    gstin: Mapped[str | None] = mapped_column(String(15))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Customer(Base):
    """Customer directory entry owned by one organization."""
    __tablename__ = "customers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    gstin: Mapped[str | None] = mapped_column(String(15))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Warehouse(Base):
    """Physical inventory location."""
    __tablename__ = "warehouses"
    __table_args__ = (UniqueConstraint("organization_id", "code", name="uq_warehouse_org_code"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class InventoryBalance(Base):
    """Current stock projection; ledger entries remain the audit source."""
    __tablename__ = "inventory_balances"
    __table_args__ = (UniqueConstraint("organization_id", "warehouse_id", "product_id", name="uq_balance_scope"),
                      CheckConstraint("on_hand >= 0 AND reserved >= 0 AND reserved <= on_hand", name="ck_balance_nonnegative"))
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"))
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    on_hand: Mapped[int] = mapped_column(Integer, default=0)
    reserved: Mapped[int] = mapped_column(Integer, default=0)
    @property
    def available(self) -> int: return self.on_hand - self.reserved

class StockMovement(Base):
    """Append-only stock event with before/after quantities and an idempotency key."""
    __tablename__ = "stock_movements"
    __table_args__ = (UniqueConstraint("organization_id", "idempotency_key", name="uq_movement_idempotency"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"))
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    movement_type: Mapped[str] = mapped_column(String(40))
    quantity: Mapped[int] = mapped_column(Integer)
    before_on_hand: Mapped[int] = mapped_column(Integer)
    after_on_hand: Mapped[int] = mapped_column(Integer)
    reference: Mapped[str | None] = mapped_column(String(100))
    reason: Mapped[str | None] = mapped_column(Text)
    idempotency_key: Mapped[str] = mapped_column(String(100))
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

class PurchaseOrder(Base):
    """Purchase order header; inventory changes only on goods receipt."""
    __tablename__ = "purchase_orders"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"))
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"))
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    total: Mapped[Decimal] = mapped_column(Numeric(14,2), default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

class PurchaseOrderItem(Base):
    """Purchase line with immutable agreed unit price."""
    __tablename__ = "purchase_order_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    purchase_order_id: Mapped[str] = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    received_quantity: Mapped[int] = mapped_column(Integer, default=0)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14,2))

class SalesOrder(Base):
    """Sales order header with a simple reservation lifecycle."""
    __tablename__ = "sales_orders"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"))
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    total: Mapped[Decimal] = mapped_column(Numeric(14,2), default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)

class SalesOrderItem(Base):
    """Sales line with unit-price snapshot."""
    __tablename__ = "sales_order_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    sales_order_id: Mapped[str] = mapped_column(ForeignKey("sales_orders.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14,2))

class Invoice(Base):
    """Invoice record; this portfolio build does not claim statutory GST compliance."""
    __tablename__ = "invoices"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    sales_order_id: Mapped[str] = mapped_column(ForeignKey("sales_orders.id"), unique=True)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True)
    total: Mapped[Decimal] = mapped_column(Numeric(14,2))
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(14,2), default=Decimal("0"))
    status: Mapped[str] = mapped_column(String(20), default="UNPAID")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
