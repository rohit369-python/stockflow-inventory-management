"""Authentication dependencies used by protected API routes."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import jwt
from app.core.config import get_settings
from app.core.database import get_db
from app.modules.identity.models import User, Membership

bearer = HTTPBearer(auto_error=False)

def get_current_context(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    """Validate token and resolve membership from the database, not client headers."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = jwt.decode(credentials.credentials, get_settings().jwt_secret_key,
                             algorithms=[get_settings().jwt_algorithm])
        if payload.get("type") != "access":
            raise ValueError("Wrong token type")
        user = db.get(User, payload["sub"])
        membership = db.query(Membership).filter_by(user_id=payload["sub"],
            organization_id=payload["org"], is_active=True).first()
        if not user or not user.is_active or not membership:
            raise ValueError("Inactive account or membership")
        return {"user": user, "organization_id": membership.organization_id,
                "role": membership.role}
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from None

def require_roles(*roles: str):
    """Build a role guard; always enforce it on the server, independent of UI state."""
    def dependency(context=Depends(get_current_context)):
        if context["role"] not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return context
    return dependency
