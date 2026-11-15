"""Pydantic contracts for catalog and warehouse resources."""
from decimal import Decimal
from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=180)
    description: str | None = None
    purchase_price: Decimal = Field(default=Decimal("0"), ge=0)
    selling_price: Decimal = Field(default=Decimal("0"), ge=0)
    reorder_level: int = Field(default=0, ge=0)

class PartnerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    email: str | None = None
    gstin: str | None = Field(default=None, max_length=15)

class WarehouseCreate(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=160)
    address: str | None = None

class StockAdjustment(BaseModel):
    warehouse_id: str
    product_id: str
    quantity: int = Field(gt=0)
    direction: str = Field(pattern="^(IN|OUT)$")
    reason: str = Field(min_length=5, max_length=500)
    idempotency_key: str = Field(min_length=8, max_length=100)
