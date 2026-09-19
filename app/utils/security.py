from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.utils.configs import project_settings as settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash mật khẩu kết hợp SHA-256 + Bcrypt"""
    sha256_password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(sha256_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu"""
    if not hashed_password:
        return False
    sha256_password = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(sha256_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo Access Token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def generate_refresh_token() -> str:
    """Sinh random string an toàn làm Refresh Token"""
    return secrets.token_urlsafe(64)

def hash_token(token: str) -> str:
    """Băm token để lưu an toàn vào cơ sở dữ liệu"""
    return hashlib.sha256(token.encode()).hexdigest()

def get_refresh_token_expiry() -> datetime:
    """Tính ngày hết hạn của refresh token"""
    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

def decode_token(token: str) -> Optional[dict]:
    """Giải mã Token"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None

