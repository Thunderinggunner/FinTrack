from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import Account, Transaction
from app.schemas.schemas import AccountCreate, AccountUpdate


def get_all_accounts(db: Session, user_id: int) -> list[Account]:
    return db.query(Account).filter(Account.user_id == user_id).all()


def create_account(db: Session, user_id: int, payload: AccountCreate) -> Account:
    account = Account(
        name=payload.name,
        description=payload.description,
        balance=payload.initial_balance,
        user_id=user_id,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def update_account(db: Session, account_id: int, user_id: int, payload: AccountUpdate) -> Account:
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta no encontrada")
    if payload.name is not None:
        account.name = payload.name
    if payload.description is not None:
        account.description = payload.description
    db.commit()
    db.refresh(account)
    return account


def delete_account(db: Session, account_id: int, user_id: int) -> None:
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cuenta no encontrada")
    has_transactions = db.query(Transaction).filter(Transaction.account_id == account_id).first()
    if has_transactions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar una cuenta con movimientos registrados",
        )
    db.delete(account)
    db.commit()
