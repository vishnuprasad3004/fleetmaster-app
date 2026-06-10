# FleetMaster - Security & Compliance Architecture

## Security Overview

FleetMaster implements a comprehensive security framework covering authentication, authorization, data protection, and compliance with Indian regulations (DPDPA, IT Act 2000, GST).

## 1. Authentication & Authorization

### 1.1 JWT-Based Authentication

**Token Structure:**

```json
{
  "sub": "user_uuid",
  "email": "user@example.com",
  "fleet_ids": ["fleet_uuid_1", "fleet_uuid_2"],
  "role": "fleet_admin",
  "permissions": ["read:fleet", "write:vehicle", "read:tracking"],
  "exp": 1642262400,
  "iat": 1642258800,
  "iss": "fleetmaster",
  "jti": "token_id_for_blacklist"
}
```

**Token Lifecycle:**
- Access Token: 15 minutes expiry (short-lived for security)
- Refresh Token: 30 days expiry (stored securely in HttpOnly cookie)
- Token Blacklist: Maintained in Redis for logout

**Implementation:**

```python
# app/core/auth/jwt.py

from datetime import datetime, timedelta
import jwt
from app.config.settings import settings

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check if token is blacklisted
        jti = payload.get("jti")
        if await cache.get(f"blacklist:{jti}"):
            raise HTTPException(status_code=401, detail="Token has been revoked")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 1.2 Role-Based Access Control (RBAC)

**Role Hierarchy:**

```
SuperAdmin (System level)
    └─ FleetAdmin (Fleet level)
        ├─ Manager
        ├─ Driver
        └─ Viewer
```

**Permission Matrix:**

| Resource | SuperAdmin | FleetAdmin | Manager | Driver | Viewer |
|----------|-----------|-----------|---------|--------|--------|
| Fleet | CRUD | CRUD | R | - | R |
| Vehicle | CRUD | CRUD | RU | - | R |
| Driver | CRUD | CRUD | RU | R | R |
| Trip | CRUD | CRUD | CRUD | RU | R |
| Tracking | R | R | R | R | R |
| Maintenance | CRUD | CRUD | CRUD | R | R |
| Analytics | R | R | R | - | R |

**RBAC Implementation:**

```python
# app/core/auth/permissions.py

from enum import Enum
from typing import List

class Permission(str, Enum):
    CREATE_FLEET = "create:fleet"
    READ_FLEET = "read:fleet"
    UPDATE_FLEET = "update:fleet"
    DELETE_FLEET = "delete:fleet"
    
    CREATE_VEHICLE = "create:vehicle"
    READ_VEHICLE = "read:vehicle"
    UPDATE_VEHICLE = "update:vehicle"
    DELETE_VEHICLE = "delete:vehicle"
    # ... more permissions

class Role(str, Enum):
    SUPER_ADMIN = "super_admin"
    FLEET_ADMIN = "fleet_admin"
    MANAGER = "manager"
    DRIVER = "driver"
    VIEWER = "viewer"

ROLE_PERMISSIONS = {
    Role.SUPER_ADMIN: [Permission.*, "*"],  # All permissions
    Role.FLEET_ADMIN: [
        Permission.CREATE_FLEET, Permission.READ_FLEET, Permission.UPDATE_FLEET,
        Permission.CREATE_VEHICLE, Permission.READ_VEHICLE, Permission.UPDATE_VEHICLE,
        # ... more permissions
    ],
    Role.MANAGER: [
        Permission.READ_FLEET, Permission.READ_VEHICLE, Permission.UPDATE_VEHICLE,
        Permission.READ_DRIVER, Permission.UPDATE_DRIVER,
        # ... more permissions
    ],
    Role.DRIVER: [
        Permission.READ_VEHICLE, Permission.READ_TRIP, Permission.UPDATE_TRIP,
        # Limited permissions for drivers
    ],
    Role.VIEWER: [
        Permission.READ_FLEET, Permission.READ_VEHICLE, Permission.READ_TRACKING,
        # Read-only access
    ]
}

async def check_permission(current_user, required_permission: Permission):
    """Check if user has required permission"""
    user_permissions = ROLE_PERMISSIONS.get(current_user.role, [])
    
    if required_permission not in user_permissions and "*" not in user_permissions:
        raise PermissionDeniedException(f"Permission {required_permission} denied")
    
    return True
```

**Decorator-Based Permission Check:**

```python
# app/core/utils/decorators.py

from functools import wraps
from fastapi import Depends

def require_permission(permission: Permission):
    async def permission_checker(current_user = Depends(get_current_user)):
        await check_permission(current_user, permission)
        return current_user
    
    return permission_checker

# Usage in endpoints
@router.post("/fleets")
async def create_fleet(
    fleet_data: FleetCreate,
    current_user = Depends(require_permission(Permission.CREATE_FLEET))
):
    # Only users with CREATE_FLEET permission can access
    ...
```

### 1.3 Multi-Factor Authentication (2FA)

**TOTP Implementation:**

```python
# app/services/auth/mfa_service.py

import pyotp
import qrcode
from io import BytesIO
import base64

class MFAService:
    @staticmethod
    def generate_secret() -> str:
        """Generate TOTP secret"""
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp(secret: str) -> pyotp.TOTP:
        """Get TOTP object"""
        return pyotp.TOTP(secret)
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        # Allow 30-second window tolerance
        return totp.verify(token, valid_window=1)
    
    @staticmethod
    def generate_qr_code(secret: str, email: str) -> str:
        """Generate QR code for TOTP setup"""
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=email, issuer_name="FleetMaster")
        
        qr = qrcode.QRCode()
        qr.add_data(uri)
        qr.make()
        
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        
        return base64.b64encode(buf.getvalue()).decode()
    
    @staticmethod
    def generate_backup_codes() -> List[str]:
        """Generate backup codes for account recovery"""
        import secrets
        codes = []
        for _ in range(10):
            code = secrets.token_hex(3).upper()  # 6-char hex code
            codes.append(f"{code[:3]}-{code[3:]}")
        return codes
```

## 2. Data Protection

### 2.1 Encryption at Rest

**Database Encryption:**

```python
# app/core/security/encryption.py

from cryptography.fernet import Fernet
from app.config.settings import settings

class EncryptionService:
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY)
    
    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt sensitive field"""
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt_field(self, ciphertext: str) -> str:
        """Decrypt sensitive field"""
        return self.cipher.decrypt(ciphertext.encode()).decode()

# Encrypted fields in database
class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(UUID, primary_key=True)
    aadhaar_number_encrypted = Column(String, nullable=True)  # Encrypted
    pan_number_encrypted = Column(String, nullable=True)      # Encrypted
    license_number = Column(String, nullable=False)
    
    @property
    def aadhaar_number(self) -> str:
        if self.aadhaar_number_encrypted:
            return encryption_service.decrypt_field(self.aadhaar_number_encrypted)
        return None
    
    @aadhaar_number.setter
    def aadhaar_number(self, value: str):
        if value:
            self.aadhaar_number_encrypted = encryption_service.encrypt_field(value)
```

### 2.2 Encryption in Transit

**TLS/SSL Configuration:**

```nginx
# nginx.conf for reverse proxy

server {
    listen 443 ssl http2;
    server_name api.fleetmaster.com;
    
    # SSL/TLS Certificates
    ssl_certificate /etc/ssl/certs/fleetmaster.crt;
    ssl_certificate_key /etc/ssl/private/fleetmaster.key;
    
    # TLS Version (only 1.2 and 1.3)
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Strong Cipher Suites
    ssl_ciphers HIGH:!aNULL:!MD5:!3DES:!DES:!RC4:!IDEA:!SEED:!aDSS:!SRP:!PSK;
    ssl_prefer_server_ciphers on;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Security Headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2.3 Password Security

**Password Hashing:**

```python
# app/core/security/password.py

from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Computational cost factor
)

def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

# Password validation rules
PASSWORD_REQUIREMENTS = {
    "min_length": 8,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_numbers": True,
    "require_special": True
}

def validate_password(password: str) -> bool:
    import re
    
    if len(password) < PASSWORD_REQUIREMENTS["min_length"]:
        return False
    if PASSWORD_REQUIREMENTS["require_uppercase"] and not re.search(r'[A-Z]', password):
        return False
    if PASSWORD_REQUIREMENTS["require_lowercase"] and not re.search(r'[a-z]', password):
        return False
    if PASSWORD_REQUIREMENTS["require_numbers"] and not re.search(r'\d', password):
        return False
    if PASSWORD_REQUIREMENTS["require_special"] and not re.search(r'[!@#$%^&*]', password):
        return False
    
    return True
```

## 3. API Security

### 3.1 Rate Limiting

```python
# app/core/middleware/rate_limit.py

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Different rate limits for different endpoints
RATE_LIMITS = {
    "auth_login": "10/minute",
    "auth_register": "5/minute",
    "api_general": "1000/minute",
    "export": "100/day"
}

# Usage
@router.post("/auth/login")
@limiter.limit(RATE_LIMITS["auth_login"])
async def login(request: Request, credentials: LoginRequest):
    ...
```

### 3.2 Input Validation

```python
# app/api/v1/schemas/vehicle/request.py

from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class VehicleCreate(BaseModel):
    registration_number: str = Field(
        ...,
        min_length=1,
        max_length=20,
        pattern=r"^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$"  # Indian reg format
    )
    make: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900, le=2100)
    vin: Optional[str] = Field(None, min_length=17, max_length=17)
    
    @validator('year')
    def validate_year(cls, v):
        from datetime import datetime
        current_year = datetime.now().year
        if v > current_year + 1:
            raise ValueError('Year cannot be in future')
        return v
    
    @validator('registration_number')
    def validate_registration(cls, v):
        # Additional validation logic
        if not re.match(r"^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$", v):
            raise ValueError('Invalid registration number format')
        return v.upper()
    
    class Config:
        schema_extra = {
            "example": {
                "registration_number": "DL01AB1234",
                "make": "Toyota",
                "model": "Innova",
                "year": 2022
            }
        }
```

### 3.3 SQL Injection Prevention

```python
# Using SQLAlchemy ORM (safe)
user = db.query(User).filter(User.email == user_email).first()

# Never use string concatenation
# NEVER DO THIS:
# query = f"SELECT * FROM users WHERE email = '{user_email}'"

# Using parameterized queries with raw SQL if needed:
from sqlalchemy import text
user = db.execute(
    text("SELECT * FROM users WHERE email = :email"),
    {"email": user_email}
).first()
```

## 4. Compliance

### 4.1 DPDPA Compliance (Digital Personal Data Protection Act, 2023)

**Key Requirements:**

1. **User Consent Management**
   ```python
   class UserConsent(Base):
       __tablename__ = "user_consents"
       
       id = Column(UUID, primary_key=True)
       user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
       consent_type = Column(String)  # marketing, analytics, etc
       granted = Column(Boolean, default=False)
       granted_at = Column(DateTime, nullable=True)
       revoked_at = Column(DateTime, nullable=True)
   ```

2. **Data Rights**
   ```python
   # Right to Access
   @router.get("/users/{user_id}/data")
   async def export_user_data(user_id: str):
       """DPDPA Right to Access - Export user data"""
       user_data = await collect_user_data(user_id)
       return generate_data_export(user_data)
   
   # Right to Erasure (Right to be Forgotten)
   @router.delete("/users/{user_id}")
   async def delete_user_data(user_id: str):
       """DPDPA Right to Erasure"""
       await anonymize_user_data(user_id)
       user = await get_user(user_id)
       user.deleted_at = datetime.utcnow()
       db.commit()
   ```

3. **Breach Notification**
   ```python
   class DataBreach(Base):
       __tablename__ = "data_breaches"
       
       id = Column(UUID, primary_key=True)
       detected_at = Column(DateTime, default=datetime.utcnow)
       nature_of_breach = Column(String)
       personal_data_affected = Column(String)
       likely_consequences = Column(Text)
       notified_at = Column(DateTime, nullable=True)
       notification_method = Column(String)  # email, sms, etc
   ```

### 4.2 IT Act 2000 Compliance

**Key Requirements:**

1. **Digital Signature Support**
   ```python
   from cryptography.hazmat.primitives import hashes
   from cryptography.hazmat.primitives.asymmetric import rsa, padding
   
   def sign_document(document_data: bytes, private_key) -> bytes:
       """Create digital signature for document"""
       signature = private_key.sign(
           document_data,
           padding.PSS(
               mgf=padding.MGF1(hashes.SHA256()),
               salt_length=padding.PSS.MAX_LENGTH
           ),
           hashes.SHA256()
       )
       return signature
   ```

2. **Audit Trail Logging**
   ```python
   class AuditLog(Base):
       __tablename__ = "audit_logs"
       
       id = Column(UUID, primary_key=True)
       user_id = Column(UUID, ForeignKey("users.id"), nullable=True)
       action = Column(String, nullable=False)  # create, update, delete, etc
       resource_type = Column(String, nullable=False)  # vehicle, driver, etc
       resource_id = Column(UUID, nullable=False)
       old_values = Column(JSON, nullable=True)
       new_values = Column(JSON, nullable=True)
       ip_address = Column(String, nullable=False)
       user_agent = Column(String, nullable=True)
       timestamp = Column(DateTime, default=datetime.utcnow)
       
       # Index for efficient querying
       __table_args__ = (
           Index('idx_audit_timestamp', 'timestamp', 'user_id'),
       )
   ```

3. **Record Retention Policy**
   ```python
   # Audit logs: Keep for 7 years
   # User data: Keep for contract period + 1 year
   # Transaction logs: Keep for 5 years
   
   async def archive_old_data():
       """Archive data older than retention period"""
       seven_years_ago = datetime.utcnow() - timedelta(days=365*7)
       old_logs = db.query(AuditLog).filter(
           AuditLog.timestamp < seven_years_ago
       ).all()
       
       # Archive to cold storage (S3 Glacier)
       for log_batch in batch(old_logs, 1000):
           await archive_to_s3(log_batch)
           db.delete(log_batch)
   ```

### 4.3 GST Compliance

**GST Invoice Generation:**

```python
# app/services/billing/gst_service.py

class GSTService:
    GST_RATE = 0.18  # 18% GST (or applicable rate)
    IGST_RATE = 0.18  # Interstate GST
    
    def calculate_gst(self, amount: Decimal) -> Decimal:
        """Calculate GST amount"""
        return amount * Decimal(str(self.GST_RATE))
    
    def generate_invoice(self, order_data: dict) -> Invoice:
        """Generate GST-compliant invoice"""
        subtotal = order_data['amount']
        gst_amount = self.calculate_gst(subtotal)
        total = subtotal + gst_amount
        
        invoice = Invoice(
            invoice_number=self.generate_invoice_number(),
            invoice_date=datetime.utcnow(),
            seller_gstin="GSTIN_NUMBER",
            buyer_gstin=order_data.get('buyer_gstin'),
            subtotal=subtotal,
            gst_amount=gst_amount,
            total=total,
            line_items=order_data['items']
        )
        
        return invoice
    
    def generate_invoice_number(self) -> str:
        """Generate unique GST invoice number"""
        from datetime import datetime
        year = datetime.now().year
        month = datetime.now().month
        sequence = self.get_next_sequence(year, month)
        return f"INV-{year}-{month:02d}-{sequence:06d}"
```

## 5. Security Testing

### 5.1 Security Testing Checklist

```yaml
Authentication:
  - [ ] Password reset token expiry
  - [ ] JWT token expiry
  - [ ] Concurrent session limits
  - [ ] Failed login attempt lockout

Authorization:
  - [ ] Role-based access control
  - [ ] Cross-tenant data isolation
  - [ ] Privilege escalation prevention

Data Protection:
  - [ ] Data encryption at rest
  - [ ] Data encryption in transit
  - [ ] Secure password hashing
  - [ ] Sensitive data masking in logs

API Security:
  - [ ] SQL injection prevention
  - [ ] XSS prevention
  - [ ] CSRF protection
  - [ ] Rate limiting
  - [ ] Input validation

Compliance:
  - [ ] DPDPA user rights
  - [ ] Data retention policies
  - [ ] Audit trail accuracy
  - [ ] Breach notification process
```

### 5.2 Penetration Testing

```bash
# Regular security assessments
- Quarterly automated vulnerability scans (OWASP ZAP)
- Annual third-party penetration testing
- Code review focused on security
- Dependency vulnerability scanning (snyk, dependabot)
```

## 6. Security Operations

### 6.1 Incident Response Plan

```python
class IncidentResponse:
    SEVERITY_LEVELS = {
        "CRITICAL": "P0",  # Immediate action required
        "HIGH": "P1",      # Within 1 hour
        "MEDIUM": "P2",    # Within 4 hours
        "LOW": "P3"        # Within 24 hours
    }
    
    async def handle_security_incident(incident: SecurityIncident):
        """Handle security incidents"""
        # 1. Detect and Alert
        await send_security_alert(incident)
        
        # 2. Contain
        if incident.severity == "CRITICAL":
            await isolate_affected_systems()
        
        # 3. Investigate
        await collect_forensics(incident)
        
        # 4. Eradicate
        await remove_threat(incident)
        
        # 5. Recover
        await restore_services()
        
        # 6. Post-mortem
        await conduct_postmortem(incident)
```

### 6.2 Security Monitoring

```python
# Monitor for suspicious activities
SECURITY_MONITORS = [
    "Multiple failed login attempts",
    "Unusual data access patterns",
    "Large data exports",
    "API rate limit violations",
    "Unauthorized API calls",
    "Database query anomalies"
]

# Alert configuration
alert_config = {
    "failed_logins_threshold": 5,
    "failed_logins_window": "10 minutes",
    "export_size_threshold": "100 MB",
    "unusual_data_access": ">2 std dev from baseline"
}
```

## 7. Compliance Checklist

### Pre-Launch Checklist

- [ ] Encryption enabled for all sensitive data
- [ ] Rate limiting implemented
- [ ] Audit logging comprehensive
- [ ] DPDPA consent mechanism implemented
- [ ] Data retention policies enforced
- [ ] Secure password requirements
- [ ] 2FA optional/enforced for admins
- [ ] CORS properly configured
- [ ] Security headers added
- [ ] API authentication required
- [ ] Role-based access control
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Dependencies scanned for vulnerabilities
- [ ] Penetration testing completed
- [ ] Incident response plan documented
- [ ] Security training completed
- [ ] Privacy policy updated
- [ ] Terms of service legal review

---

This comprehensive security framework ensures FleetMaster protects user data and maintains compliance with Indian regulations while maintaining platform security and integrity.
