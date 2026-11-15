"""Identity use cases kept outside HTTP route handlers."""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.modules.identity.models import User, Organization, Membership
from app.core.security import hash_password, verify_password, create_access_token

def register(db: Session, payload):
    """Create the first tenant owner atomically with the tenant and membership."""
    email = payload.email.lower()
    if db.query(User).filter_by(email=email).first():
        raise HTTPException(409, "Email is already registered")
    organization = Organization(name=payload.organization_name)
    user = User(email=email, full_name=payload.full_name, password_hash=hash_password(payload.password))
    db.add_all([organization, user]); db.flush()
    db.add(Membership(user_id=user.id, organization_id=organization.id, role="organization_owner"))
    db.commit()
    return token_for(user, organization.id, "organization_owner")

def login(db: Session, email: str, password: str):
    """Authenticate user and select their first active membership for this demo."""
    user = db.query(User).filter_by(email=email.lower()).first()
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    membership = db.query(Membership).filter_by(user_id=user.id, is_active=True).first()
    if not membership: raise HTTPException(403, "No active organization membership")
    return token_for(user, membership.organization_id, membership.role)

def token_for(user, organization_id, role):
    return {"access_token": create_access_token(user.id, organization_id, role),
            "organization_id": organization_id, "role": role}
