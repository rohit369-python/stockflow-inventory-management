"""Versioned API composition root."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_context, require_roles
from app.modules.identity.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.modules.identity.service import register, login
from app.modules.identity.models import Organization
from app.modules.catalog.models import Product, Supplier, Customer, Warehouse, InventoryBalance, StockMovement
from app.modules.catalog.schemas import ProductCreate, PartnerCreate, WarehouseCreate, StockAdjustment
from app.modules.inventory.service import adjust_stock

router = APIRouter()

@router.post("/auth/register", response_model=TokenResponse, status_code=201)
def register_tenant(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Register a tenant and its initial organization owner."""
    return register(db, payload)

@router.post("/auth/login", response_model=TokenResponse)
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    """Exchange credentials for an access token."""
    return login(db, payload.email, payload.password)

@router.get("/auth/me")
def me(context=Depends(get_current_context)):
    """Return identity and tenant claims from the verified database membership."""
    user = context["user"]
    return {"id": user.id, "email": user.email, "full_name": user.full_name,
            "organization_id": context["organization_id"], "role": context["role"]}

@router.post("/products", status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), context=Depends(require_roles("organization_owner", "organization_admin", "inventory_manager"))):
    """Create a tenant-scoped SKU; database constraint prevents duplicate tenant SKUs."""
    product = Product(organization_id=context["organization_id"], **payload.model_dump())
    db.add(product)
    try: db.commit()
    except Exception:
        db.rollback(); raise HTTPException(409, "SKU already exists or product violates a constraint") from None
    db.refresh(product); return product_out(product)

def product_out(p):
    return {"id": p.id, "sku": p.sku, "name": p.name, "purchase_price": str(p.purchase_price),
            "selling_price": str(p.selling_price), "reorder_level": p.reorder_level, "is_active": p.is_active}

@router.get("/products")
def list_products(db: Session = Depends(get_db), context=Depends(get_current_context), limit: int = 50, offset: int = 0):
    """List products within the authenticated tenant only."""
    rows = db.scalars(select(Product).where(Product.organization_id == context["organization_id"]).order_by(Product.name).limit(min(limit, 200)).offset(offset)).all()
    return [product_out(p) for p in rows]

@router.post("/suppliers", status_code=201)
def create_supplier(payload: PartnerCreate, db: Session = Depends(get_db), context=Depends(get_current_context)):
    row = Supplier(organization_id=context["organization_id"], **payload.model_dump()); db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "name": row.name, "email": row.email, "gstin": row.gstin}

@router.post("/customers", status_code=201)
def create_customer(payload: PartnerCreate, db: Session = Depends(get_db), context=Depends(get_current_context)):
    row = Customer(organization_id=context["organization_id"], **payload.model_dump()); db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "name": row.name, "email": row.email, "gstin": row.gstin}

@router.post("/warehouses", status_code=201)
def create_warehouse(payload: WarehouseCreate, db: Session = Depends(get_db), context=Depends(get_current_context)):
    row = Warehouse(organization_id=context["organization_id"], **payload.model_dump()); db.add(row)
    try: db.commit()
    except Exception: db.rollback(); raise HTTPException(409, "Warehouse code already exists") from None
    db.refresh(row); return {"id": row.id, "code": row.code, "name": row.name, "address": row.address}

@router.post("/inventory/adjustments", status_code=201)
def stock_adjustment(payload: StockAdjustment, db: Session = Depends(get_db), context=Depends(require_roles("organization_owner", "organization_admin", "inventory_manager", "warehouse_manager"))):
    """Adjust stock through the centralized ledger-aware inventory service."""
    movement = adjust_stock(db, organization_id=context["organization_id"], user_id=context["user"].id,
        warehouse_id=payload.warehouse_id, product_id=payload.product_id, quantity=payload.quantity,
        direction=payload.direction, reason=payload.reason, idempotency_key=payload.idempotency_key)
    return movement_out(movement)

def movement_out(m):
    return {"id": m.id, "movement_type": m.movement_type, "quantity": m.quantity,
            "before_on_hand": m.before_on_hand, "after_on_hand": m.after_on_hand,
            "reference": m.reference, "idempotency_key": m.idempotency_key}

@router.get("/inventory/balances")
def inventory_balances(db: Session = Depends(get_db), context=Depends(get_current_context)):
    """Return stock projections scoped to the caller's organization."""
    rows = db.scalars(select(InventoryBalance).where(InventoryBalance.organization_id == context["organization_id"])).all()
    return [{"warehouse_id": x.warehouse_id, "product_id": x.product_id, "on_hand": x.on_hand,
             "reserved": x.reserved, "available": x.available} for x in rows]

@router.get("/inventory/movements")
def inventory_movements(db: Session = Depends(get_db), context=Depends(get_current_context), limit: int = 100):
    """Read the append-only stock event history for the active tenant."""
    rows = db.scalars(select(StockMovement).where(StockMovement.organization_id == context["organization_id"]).order_by(StockMovement.created_at.desc()).limit(min(limit, 500))).all()
    return [movement_out(x) for x in rows]
