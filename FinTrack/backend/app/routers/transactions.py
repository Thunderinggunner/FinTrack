from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.models.database import get_db
from app.models.models import User
from app.auth import get_current_user
from app.schemas.schemas import TransactionCreate, TransactionUpdate, TransactionResponse
from app.services import transaction_service

router = APIRouter()


@router.get("", response_model=list[TransactionResponse],
            summary="Listar movimientos",
            description="Retorna movimientos del usuario. Soporta filtros por cuenta, fecha y categoría.")
def list_transactions(
    account_id: Optional[int] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return transaction_service.get_transactions(db, current_user.id, account_id, from_date, to_date, category)


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED,
             summary="Registrar movimiento",
             description="Registra un ingreso o egreso. El trigger SQLite actualiza el saldo automáticamente.")
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return transaction_service.create_transaction(db, current_user.id, payload)


@router.put("/{transaction_id}", response_model=TransactionResponse,
            summary="Editar movimiento",
            description="Actualiza un movimiento. El trigger revierte el saldo anterior y aplica el nuevo.")
def update_transaction(transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return transaction_service.update_transaction(db, transaction_id, current_user.id, payload)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar movimiento",
               description="Elimina un movimiento. El trigger revierte el saldo automáticamente.")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    transaction_service.delete_transaction(db, transaction_id, current_user.id)
