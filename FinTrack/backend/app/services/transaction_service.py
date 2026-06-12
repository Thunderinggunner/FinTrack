from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional
from app.models.models import Account, Transaction, Budget, Notification
from app.schemas.schemas import TransactionCreate, TransactionUpdate


def get_transactions(
    db: Session, user_id: int,
    account_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    category: Optional[str] = None,
) -> list[Transaction]:
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if from_date:
        query = query.filter(Transaction.date >= from_date)
    if to_date:
        query = query.filter(Transaction.date <= to_date)
    if category:
        query = query.filter(Transaction.category == category)
    return query.order_by(Transaction.date.desc()).all()


def create_transaction(db: Session, user_id: int, payload: TransactionCreate) -> Transaction:
    account = db.query(Account).filter(Account.id == payload.account_id, Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta no encontrada")

    transaction = Transaction(
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        description=payload.description,
        date=payload.date,
        account_id=payload.account_id,
        user_id=user_id,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    if payload.type == "expense":
        _check_budget_alerts(db, user_id, payload.category, payload.date)

    return transaction


def update_transaction(db: Session, transaction_id: int, user_id: int, payload: TransactionUpdate) -> Transaction:
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id, Transaction.user_id == user_id
    ).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")

    if payload.amount is not None:
        transaction.amount = payload.amount
    if payload.type is not None:
        transaction.type = payload.type
    if payload.category is not None:
        transaction.category = payload.category
    if payload.description is not None:
        transaction.description = payload.description
    if payload.date is not None:
        transaction.date = payload.date

    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, transaction_id: int, user_id: int) -> None:
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id, Transaction.user_id == user_id
    ).first()
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")
    db.delete(transaction)
    db.commit()


def _check_budget_alerts(db: Session, user_id: int, category: str, date: datetime) -> None:
    budget = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.category == category,
        Budget.month == date.month,
        Budget.year == date.year,
    ).first()
    if not budget:
        return

    spent_rows = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.category == category,
        Transaction.type == "expense",
    ).with_entities(Transaction.amount).all()

    total_spent = sum(r[0] for r in spent_rows)
    percentage = (total_spent / budget.limit_amount) * 100

    message = None
    if percentage >= 100:
        message = f"⚠️ Superaste el 100% del presupuesto de '{category}' (${total_spent:.2f} / ${budget.limit_amount:.2f})"
    elif percentage >= 80:
        message = f"🔔 Usaste el {percentage:.0f}% del presupuesto de '{category}' (${total_spent:.2f} / ${budget.limit_amount:.2f})"

    if message:
        db.add(Notification(message=message, user_id=user_id))
        db.commit()
