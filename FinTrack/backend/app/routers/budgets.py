from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.database import get_db
from app.models.models import User, Budget, Transaction
from app.auth import get_current_user
from app.schemas.schemas import BudgetCreate, BudgetResponse

router = APIRouter()


def _enrich_budget(budget: Budget, db: Session, user_id: int) -> BudgetResponse:
    spent_rows = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.category == budget.category,
        Transaction.type == "expense",
    ).with_entities(Transaction.amount, Transaction.date).all()

    spent = sum(r[0] for r in spent_rows if r[1].month == budget.month and r[1].year == budget.year)
    percentage = round((spent / budget.limit_amount) * 100, 1) if budget.limit_amount > 0 else 0.0

    return BudgetResponse(
        id=budget.id,
        category=budget.category,
        limit_amount=budget.limit_amount,
        month=budget.month,
        year=budget.year,
        user_id=budget.user_id,
        spent=round(spent, 2),
        percentage=percentage,
        created_at=budget.created_at,
    )


@router.get("", response_model=list[BudgetResponse],
            summary="Ver presupuestos del mes",
            description="Lista presupuestos del mes actual con el gasto acumulado y porcentaje usado.")
def list_budgets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    now = datetime.utcnow()
    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.month == now.month,
        Budget.year == now.year,
    ).all()
    return [_enrich_budget(b, db, current_user.id) for b in budgets]


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED,
             summary="Crear presupuesto",
             description="Establece un límite mensual de gasto por categoría.")
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    budget = Budget(
        category=payload.category,
        limit_amount=payload.limit_amount,
        month=payload.month,
        year=payload.year,
        user_id=current_user.id,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return _enrich_budget(budget, db, current_user.id)
