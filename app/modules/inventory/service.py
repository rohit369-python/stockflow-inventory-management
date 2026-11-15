"""Transactional inventory commands; every quantity change writes an audit event."""
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.catalog.models import InventoryBalance, StockMovement, Product, Warehouse

def _scoped_entities(db, organization_id, warehouse_id, product_id):
    """Reject cross-tenant references before touching an inventory balance."""
    warehouse = db.scalar(select(Warehouse).where(Warehouse.id == warehouse_id,
        Warehouse.organization_id == organization_id, Warehouse.is_active.is_(True)))
    product = db.scalar(select(Product).where(Product.id == product_id,
        Product.organization_id == organization_id, Product.is_active.is_(True)))
    if not warehouse or not product: raise HTTPException(404, "Warehouse or product not found")

def adjust_stock(db: Session, *, organization_id, user_id, warehouse_id, product_id,
                 quantity, direction, reason, idempotency_key):
    """Apply a manual adjustment with idempotency and row-level locking on PostgreSQL."""
    existing = db.scalar(select(StockMovement).where(StockMovement.organization_id == organization_id,
        StockMovement.idempotency_key == idempotency_key))
    if existing: return existing
    _scoped_entities(db, organization_id, warehouse_id, product_id)
    stmt = select(InventoryBalance).where(InventoryBalance.organization_id == organization_id,
        InventoryBalance.warehouse_id == warehouse_id, InventoryBalance.product_id == product_id).with_for_update()
    balance = db.scalar(stmt)
    if balance is None:
        balance = InventoryBalance(organization_id=organization_id, warehouse_id=warehouse_id,
                                   product_id=product_id, on_hand=0, reserved=0)
        db.add(balance); db.flush()
    before = balance.on_hand
    delta = quantity if direction == "IN" else -quantity
    if balance.on_hand + delta < balance.reserved:
        raise HTTPException(409, "Adjustment would reduce stock below reserved quantity")
    balance.on_hand += delta
    movement = StockMovement(organization_id=organization_id, warehouse_id=warehouse_id,
        product_id=product_id, movement_type="ADJUSTMENT_IN" if delta > 0 else "ADJUSTMENT_OUT",
        quantity=quantity, before_on_hand=before, after_on_hand=balance.on_hand,
        reason=reason, idempotency_key=idempotency_key, created_by=user_id)
    db.add(movement); db.commit(); db.refresh(movement)
    return movement

def reserve_stock(db: Session, *, organization_id, user_id, warehouse_id, product_id, quantity, reference, idempotency_key):
    """Reserve available units without reducing physical on-hand stock."""
    existing = db.scalar(select(StockMovement).where(StockMovement.organization_id == organization_id,
        StockMovement.idempotency_key == idempotency_key))
    if existing: return existing
    _scoped_entities(db, organization_id, warehouse_id, product_id)
    balance = db.scalar(select(InventoryBalance).where(InventoryBalance.organization_id == organization_id,
        InventoryBalance.warehouse_id == warehouse_id, InventoryBalance.product_id == product_id).with_for_update())
    if not balance or balance.on_hand - balance.reserved < quantity:
        raise HTTPException(409, "Insufficient available stock")
    balance.reserved += quantity
    movement = StockMovement(organization_id=organization_id, warehouse_id=warehouse_id,
        product_id=product_id, movement_type="RESERVATION", quantity=quantity,
        before_on_hand=balance.on_hand, after_on_hand=balance.on_hand, reference=reference,
        idempotency_key=idempotency_key, created_by=user_id)
    db.add(movement); db.commit(); db.refresh(movement); return movement
