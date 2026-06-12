# 💰 FinTrack — Sistema Integral de Gestión Financiera

**Materia:** Programación III  
**TP:** Trabajo Práctico IV  
**Grupo:** `ThunderingGunners`  
**Integrantes:** `Salomon Jose Riveras` · `Nieva Mauricio`

---

## 📋 Descripción del Proyecto

Sistema web para la gestión de ingresos y egresos personales. Permite controlar múltiples cuentas (Efectivo, Banco, Mercado Pago), categorizar gastos, establecer presupuestos mensuales y visualizar reportes del estado financiero en tiempo real.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.10+ con FastAPI |
| Frontend | HTML + CSS + TypeScript (sin frameworks) |
| Base de datos | SQLite + SQLAlchemy |
| Autenticación | JWT (JSON Web Tokens) |
| Control de versiones | Git + GitHub |

---

## 📂 Estructura del Proyecto

```
ThunderingGunners/
├── backend/
│   ├── app/
│   │   ├── routers/              ← Endpoints HTTP (solo manejo de request/response)
│   │   │   ├── auth.py
│   │   │   ├── accounts.py
│   │   │   ├── transactions.py
│   │   │   ├── budgets.py
│   │   │   ├── reports.py
│   │   │   └── notifications.py
│   │   ├── services/             ← Lógica de negocio (cálculos, validaciones, alertas)
│   │   │   ├── account_service.py
│   │   │   └── transaction_service.py
│   │   ├── models/               ← Modelos SQLAlchemy (ORM) + triggers SQLite
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── schemas/              ← Schemas Pydantic (validación de datos)
│   │   │   └── schemas.py
│   │   ├── auth.py               ← JWT + bcrypt
│   │   ├── config.py             ← Variables de entorno
│   │   └── main.py               ← Punto de entrada FastAPI
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── types/index.ts        ← Interfaces TypeScript (sin any)
│   │   ├── services/api.ts       ← Llamadas a la API tipadas
│   │   └── services/validation.ts← Validación dual frontend
│   ├── index.html                ← SPA completa
│   └── tsconfig.json
├── .gitignore
└── README.md
```

---

## ⚙️ Instalación y Configuración

### Requisitos previos
- Python 3.10 o superior
- Node.js (para TypeScript)
- Git

### Backend

```bash
cd backend

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

copy .env.example .env       # Windows
# cp .env.example .env       # Mac/Linux
# Editá el .env con tus valores

uvicorn app.main:app --reload
```

Servidor disponible en `http://localhost:8000`  
Swagger en `http://localhost:8000/docs`

### Frontend

Abrí `frontend/index.html` con **Live Server** en VS Code, o:

```bash
cd frontend
python -m http.server 5500
# Abrí http://localhost:5500
```

---

## 🔑 Variables de Entorno

```env
DATABASE_URL=sqlite:///./fintrack.db
JWT_SECRET=tu_clave_secreta_aqui
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> ⚠️ El archivo `.env` nunca debe subirse a GitHub. Ya está en el `.gitignore`.

---

## 🗺️ Endpoints de la API

Todos los endpoints (salvo `/auth/*`) requieren JWT en el header:
```
Authorization: Bearer <token>
```

### Autenticación
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `POST` | `/auth/register` | No | Registrar nuevo usuario |
| `POST` | `/auth/login` | No | Login — devuelve JWT |

### Cuentas
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `GET` | `/api/accounts` | JWT | Listar cuentas |
| `POST` | `/api/accounts` | JWT | Crear cuenta |
| `PUT` | `/api/accounts/{id}` | JWT | Editar cuenta |
| `DELETE` | `/api/accounts/{id}` | JWT | Eliminar cuenta |

### Movimientos
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `GET` | `/api/transactions` | JWT | Listar con filtros |
| `POST` | `/api/transactions` | JWT | Registrar movimiento |
| `PUT` | `/api/transactions/{id}` | JWT | Editar movimiento |
| `DELETE` | `/api/transactions/{id}` | JWT | Eliminar movimiento |

### Presupuestos
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `GET` | `/api/budgets` | JWT | Ver presupuestos del mes |
| `POST` | `/api/budgets` | JWT | Crear presupuesto |

### Reportes
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `GET` | `/api/reports/summary` | JWT | Resumen mensual |
| `GET` | `/api/reports/by-category` | JWT | Gastos por categoría |

### Notificaciones
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `GET` | `/api/notifications` | JWT | Listar notificaciones |
| `PATCH` | `/api/notifications/{id}/read` | JWT | Marcar como leída |

---

## 🗄️ Triggers SQLite

Se implementaron **3 triggers** para mantener el saldo de cada cuenta actualizado automáticamente:

```sql
-- Trigger 1: Al insertar un movimiento
CREATE TRIGGER update_account_balance_insert
AFTER INSERT ON transactions
BEGIN
    UPDATE accounts
    SET balance = balance +
        CASE WHEN NEW.type = 'income' THEN NEW.amount
             ELSE -NEW.amount END
    WHERE id = NEW.account_id;
END;

-- Trigger 2: Al eliminar un movimiento (revierte el saldo)
CREATE TRIGGER update_account_balance_delete
AFTER DELETE ON transactions
BEGIN
    UPDATE accounts
    SET balance = balance +
        CASE WHEN OLD.type = 'income' THEN -OLD.amount
             ELSE OLD.amount END
    WHERE id = OLD.account_id;
END;

-- Trigger 3: Al actualizar un movimiento (revierte el viejo, aplica el nuevo)
CREATE TRIGGER update_account_balance_update
AFTER UPDATE ON transactions
BEGIN
    UPDATE accounts
    SET balance = balance +
        CASE WHEN OLD.type = 'income' THEN -OLD.amount ELSE OLD.amount END +
        CASE WHEN NEW.type = 'income' THEN NEW.amount ELSE -NEW.amount END
    WHERE id = NEW.account_id;
END;
```

---

## ✅ Funcionalidades Implementadas

- [x] **Auth:** Registro y login con JWT. Contraseñas hasheadas con bcrypt.
- [x] **Cuentas:** CRUD completo. Saldo actualizado automáticamente por triggers.
- [x] **Movimientos:** Alta, baja y modificación con validaciones (sin montos negativos ni fechas futuras).
- [x] **Presupuestos:** Límite mensual por categoría con alertas al 80% y 100%.
- [x] **Dashboard:** Gráfico de torta de distribución de gastos. Resumen mensual.
- [x] **Reportes:** Ingresos/egresos del mes y gastos agrupados por categoría.
- [x] **Notificaciones:** Alertas persistentes al superar presupuestos. Marcado como leído.
- [x] **Triggers SQLite:** INSERT, UPDATE y DELETE mantienen el saldo consistente.
- [x] **Swagger:** Todos los endpoints documentados en `/docs`.
- [x] **Validación dual:** Frontend (JS) + Backend (Pydantic).
- [x] **TypeScript sin `any`:** Todos los tipos declarados explícitamente.

---

## 🏗️ Decisiones de Arquitectura

**Separación en capas:**
- **Routers:** Solo reciben el request y devuelven la response. Sin lógica de negocio.
- **Services:** Toda la lógica vive acá: cálculo de saldos, validaciones, alertas de presupuesto.
- **Models / Schemas:** ORM (SQLAlchemy) y validación de inputs (Pydantic).

**Contratos de datos:** Cada interface TypeScript del frontend corresponde exactamente a un schema Pydantic del backend.

**Validación dual:** Los datos se validan primero en el frontend (UX) y luego en el backend con Pydantic (seguridad).

---

## 📊 Rúbrica

| Criterio | Puntaje |
|---|---|
| Funcionalidad MVP (5 módulos) | 30 pts |
| Arquitectura en capas | 15 pts |
| TypeScript sin `any` | 10 pts |
| Trigger SQLite implementado | 10 pts |
| Seguridad (.env / JWT / bcrypt) | 10 pts |
| Swagger documentado | 10 pts |
| Flujo GitHub (+10 commits/integrante + PR) | 10 pts |
| Validación dual | 5 pts |
| **Total** | **100 pts** |
