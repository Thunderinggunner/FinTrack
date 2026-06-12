from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.database import get_db
from app.models.models import User, Transaction
from app.auth import get_current_user
from app.schemas.schemas import MonthlySummary, CategoryReport

router = APIRouter()


@router.get("/summary", response_model=MonthlySummary,
            summary="Resumen mensual",
            description="Retorna el total de ingresos, egresos y balance neto del mes.")
def monthly_summary(
    month: int = Query(default=None, ge=1, le=12),
    year: int = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    month = month or now.month
    year = year or now.year

    txs = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    filtered = [t for t in txs if t.date.month == month and t.date.year == year]

    total_income = round(sum(t.amount for t in filtered if t.type == "income"), 2)
    total_expense = round(sum(t.amount for t in filtered if t.type == "expense"), 2)

    return MonthlySummary(
        month=month, year=year,
        total_income=total_income,
        total_expense=total_expense,
        net_balance=round(total_income - total_expense, 2),
    )


@router.get("/by-category", response_model=list[CategoryReport],
            summary="Gastos por categoría",
            description="Retorna egresos agrupados por categoría con porcentaje del total.")
def by_category(
    month: int = Query(default=None, ge=1, le=12),
    year: int = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    month = month or now.month
    year = year or now.year

    expenses = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
    ).all()
    filtered = [t for t in expenses if t.date.month == month and t.date.year == year]
    total = sum(t.amount for t in filtered)

    by_cat: dict[str, list] = {}
    for t in filtered:
        by_cat.setdefault(t.category, []).append(t.amount)

    return [
        CategoryReport(
            category=cat,
            total=round(sum(amounts), 2),
            percentage=round((sum(amounts) / total) * 100, 1) if total > 0 else 0.0,
            transaction_count=len(amounts),
        )
        for cat, amounts in sorted(by_cat.items(), key=lambda x: -sum(x[1]))
    ]
