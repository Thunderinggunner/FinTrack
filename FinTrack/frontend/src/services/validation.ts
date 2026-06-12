// ── Validación dual — Capa frontend ──────────────────────────────────────────
// Los mismos campos se revalidan en el backend con Pydantic (Capa 2).

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export function validateRegister(email: string, username: string, password: string): ValidationResult {
  const errors: string[] = [];
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) errors.push("Email inválido");
  if (!username || username.trim().length < 2) errors.push("Nombre: mínimo 2 caracteres");
  if (!password || password.length < 6) errors.push("Contraseña: mínimo 6 caracteres");
  return { valid: errors.length === 0, errors };
}

export function validateTransaction(amount: string, category: string, date: string, accountId: string): ValidationResult {
  const errors: string[] = [];
  const parsedAmount = parseFloat(amount);
  if (isNaN(parsedAmount) || parsedAmount <= 0) errors.push("El monto debe ser mayor a 0");
  if (!category || category.trim().length === 0) errors.push("La categoría es obligatoria");
  if (!date) errors.push("La fecha es obligatoria");
  else if (new Date(date) > new Date()) errors.push("No se permiten fechas futuras");
  if (!accountId) errors.push("Debe seleccionar una cuenta");
  return { valid: errors.length === 0, errors };
}

export function validateAccount(name: string): ValidationResult {
  const errors: string[] = [];
  if (!name || name.trim().length === 0) errors.push("El nombre de la cuenta es obligatorio");
  if (name.length > 100) errors.push("El nombre no puede superar 100 caracteres");
  return { valid: errors.length === 0, errors };
}

export function validateBudget(category: string, limit: string): ValidationResult {
  const errors: string[] = [];
  if (!category || category.trim().length === 0) errors.push("La categoría es obligatoria");
  const parsedLimit = parseFloat(limit);
  if (isNaN(parsedLimit) || parsedLimit <= 0) errors.push("El límite debe ser mayor a 0");
  return { valid: errors.length === 0, errors };
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("es-AR", {
    style: "currency", currency: "ARS", maximumFractionDigits: 2,
  }).format(amount);
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("es-AR", {
    day: "2-digit", month: "2-digit", year: "numeric",
  });
}
