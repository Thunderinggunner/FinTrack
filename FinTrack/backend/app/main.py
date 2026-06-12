from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.database import Base, engine, create_triggers
from app.routers import accounts, transactions, budgets, reports, notifications, auth

Base.metadata.create_all(bind=engine)
create_triggers()

app = FastAPI(
    title="FinTrack API",
    description="Sistema Integral de Gestión Financiera — ThunderingGunners",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["Cuentas"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Movimientos"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["Presupuestos"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reportes"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notificaciones"])


@app.get("/", tags=["Root"])
def root():
    return {"message": "FinTrack API — ThunderingGunners", "docs": "/docs"}
