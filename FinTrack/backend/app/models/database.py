from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_triggers():
    """Crea los triggers SQLite después de que las tablas existen."""
    with engine.connect() as conn:
        # Trigger 1: Actualizar saldo al INSERTAR un movimiento
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS update_account_balance_insert
            AFTER INSERT ON transactions
            BEGIN
                UPDATE accounts
                SET balance = balance +
                    CASE WHEN NEW.type = 'income' THEN NEW.amount
                         ELSE -NEW.amount END
                WHERE id = NEW.account_id;
            END
        """))

        # Trigger 2: Revertir saldo al ELIMINAR un movimiento
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS update_account_balance_delete
            AFTER DELETE ON transactions
            BEGIN
                UPDATE accounts
                SET balance = balance +
                    CASE WHEN OLD.type = 'income' THEN -OLD.amount
                         ELSE OLD.amount END
                WHERE id = OLD.account_id;
            END
        """))

        # Trigger 3: Revertir saldo viejo y aplicar nuevo al ACTUALIZAR
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS update_account_balance_update
            AFTER UPDATE ON transactions
            BEGIN
                UPDATE accounts
                SET balance = balance +
                    CASE WHEN OLD.type = 'income' THEN -OLD.amount
                         ELSE OLD.amount END +
                    CASE WHEN NEW.type = 'income' THEN NEW.amount
                         ELSE -NEW.amount END
                WHERE id = NEW.account_id;
            END
        """))
        conn.commit()
