from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.models import User
from app.auth import get_current_user
from app.schemas.schemas import AccountCreate, AccountUpdate, AccountResponse
from app.services import account_service

router = APIRouter()


@router.get("", response_model=list[AccountResponse],
            summary="Listar cuentas",
            description="Retorna todas las cuentas del usuario autenticado con sus saldos actuales.")
def list_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return account_service.get_all_accounts(db, current_user.id)


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED,
             summary="Crear cuenta",
             description="Crea una nueva cuenta. El saldo inicial es 0 por defecto.")
def create_account(payload: AccountCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return account_service.create_account(db, current_user.id, payload)


@router.put("/{account_id}", response_model=AccountResponse,
            summary="Editar cuenta",
            description="Actualiza el nombre o descripción de una cuenta existente.")
def update_account(account_id: int, payload: AccountUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return account_service.update_account(db, account_id, current_user.id, payload)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar cuenta",
               description="Elimina una cuenta. Solo si no tiene movimientos asociados.")
def delete_account(account_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    account_service.delete_account(db, account_id, current_user.id)
