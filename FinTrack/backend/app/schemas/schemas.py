from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Accounts ──────────────────────────────────────────────────────────────────

class AccountCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    initial_balance: float = Field(default=0.0, ge=0)

    @field_validator("initial_balance")
    @classmethod
    def round_balance(cls, v: float) -> float:
        return round(v, 2)


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class AccountResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    balance: float
    user_id: int
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Transactions ──────────────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    date: datetime
    account_id: int

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: float) -> float:
        return round(v, 2)

    @field_validator("date")
    @classmethod
    def no_future_dates(cls, v: datetime) -> datetime:
        if v > datetime.now(timezone.utc):
            raise ValueError("La fecha no puede ser futura")
        return v


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    date: Optional[datetime] = None

    @field_validator("amount")
    @classmethod
    def round_amount(cls, v: Optional[float]) -> Optional[float]:
        return round(v, 2) if v is not None else None

    @field_validator("date")
    @classmethod
    def no_future_dates(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v > datetime.now(timezone.utc):
            raise ValueError("La fecha no puede ser futura")
        return v


class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: TransactionType
    category: str
    description: Optional[str]
    date: datetime
    account_id: int
    user_id: int
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Budgets ───────────────────────────────────────────────────────────────────

class BudgetCreate(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    limit_amount: float = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020)

    @field_validator("limit_amount")
    @classmethod
    def round_limit(cls, v: float) -> float:
        return round(v, 2)


class BudgetResponse(BaseModel):
    id: int
    category: str
    limit_amount: float
    month: int
    year: int
    user_id: int
    spent: float = 0.0
    percentage: float = 0.0
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Reports ───────────────────────────────────────────────────────────────────

class MonthlySummary(BaseModel):
    month: int
    year: int
    total_income: float
    total_expense: float
    net_balance: float


class CategoryReport(BaseModel):
    category: str
    total: float
    percentage: float
    transaction_count: int


# ── Notifications ─────────────────────────────────────────────────────────────

class NotificationResponse(BaseModel):
    id: int
    message: str
    is_read: bool
    user_id: int
    created_at: datetime
    model_config = {"from_attributes": True}
