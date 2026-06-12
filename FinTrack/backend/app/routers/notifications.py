from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.models import User, Notification
from app.auth import get_current_user
from app.schemas.schemas import NotificationResponse

router = APIRouter()


@router.get("", response_model=list[NotificationResponse],
            summary="Listar notificaciones",
            description="Retorna todas las notificaciones del usuario, ordenadas por fecha descendente.")
def list_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()


@router.patch("/{notification_id}/read", response_model=NotificationResponse,
              summary="Marcar como leída",
              description="Marca una notificación específica como leída.")
def mark_as_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificación no encontrada")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
