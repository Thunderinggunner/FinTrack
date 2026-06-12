import type {
  UserRegister, UserLogin, TokenResponse,
  AccountCreate, AccountUpdate, AccountResponse,
  TransactionCreate, TransactionUpdate, TransactionResponse,
  BudgetCreate, BudgetResponse,
  MonthlySummary, CategoryReport,
  NotificationResponse,
} from "../types/index.js";

const BASE_URL = "http://127.0.0.1:8000";

function getToken(): string | null {
  return localStorage.getItem("fintrack_token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  if (response.status === 204) return undefined as unknown as T;

  const data = await response.json();
  if (!response.ok) {
    const msg = Array.isArray(data.detail)
      ? data.detail.map((e: { msg: string }) => e.msg).join(", ")
      : (typeof data.detail === "string" ? data.detail : "Error desconocido");
    throw new Error(msg);
  }
  return data as T;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export async function register(payload: UserRegister): Promise<void> {
  await request<void>("/auth/register", { method: "POST", body: JSON.stringify(payload) });
}

export async function login(payload: UserLogin): Promise<TokenResponse> {
  return request<TokenResponse>("/auth/login", { method: "POST", body: JSON.stringify(payload) });
}

// ── Accounts ──────────────────────────────────────────────────────────────────

export async function getAccounts(): Promise<AccountResponse[]> {
  return request<AccountResponse[]>("/api/accounts");
}

export async function createAccount(payload: AccountCreate): Promise<AccountResponse> {
  return request<AccountResponse>("/api/accounts", { method: "POST", body: JSON.stringify(payload) });
}

export async function updateAccount(id: number, payload: AccountUpdate): Promise<AccountResponse> {
  return request<AccountResponse>(`/api/accounts/${id}`, { method: "PUT", body: JSON.stringify(payload) });
}

export async function deleteAccount(id: number): Promise<void> {
  return request<void>(`/api/accounts/${id}`, { method: "DELETE" });
}

// ── Transactions ──────────────────────────────────────────────────────────────

export interface TransactionFilters {
  account_id?: number;
  from_date?: string;
  to_date?: string;
  category?: string;
}

export async function getTransactions(filters: TransactionFilters = {}): Promise<TransactionResponse[]> {
  const params = new URLSearchParams();
  if (filters.account_id) params.set("account_id", String(filters.account_id));
  if (filters.from_date) params.set("from_date", filters.from_date);
  if (filters.to_date) params.set("to_date", filters.to_date);
  if (filters.category) params.set("category", filters.category);
  const qs = params.toString();
  return request<TransactionResponse[]>(`/api/transactions${qs ? "?" + qs : ""}`);
}

export async function createTransaction(payload: TransactionCreate): Promise<TransactionResponse> {
  return request<TransactionResponse>("/api/transactions", { method: "POST", body: JSON.stringify(payload) });
}

export async function updateTransaction(id: number, payload: TransactionUpdate): Promise<TransactionResponse> {
  return request<TransactionResponse>(`/api/transactions/${id}`, { method: "PUT", body: JSON.stringify(payload) });
}

export async function deleteTransaction(id: number): Promise<void> {
  return request<void>(`/api/transactions/${id}`, { method: "DELETE" });
}

// ── Budgets ───────────────────────────────────────────────────────────────────

export async function getBudgets(): Promise<BudgetResponse[]> {
  return request<BudgetResponse[]>("/api/budgets");
}

export async function createBudget(payload: BudgetCreate): Promise<BudgetResponse> {
  return request<BudgetResponse>("/api/budgets", { method: "POST", body: JSON.stringify(payload) });
}

// ── Reports ───────────────────────────────────────────────────────────────────

export async function getMonthlySummary(month?: number, year?: number): Promise<MonthlySummary> {
  const params = new URLSearchParams();
  if (month) params.set("month", String(month));
  if (year) params.set("year", String(year));
  const qs = params.toString();
  return request<MonthlySummary>(`/api/reports/summary${qs ? "?" + qs : ""}`);
}

export async function getByCategory(month?: number, year?: number): Promise<CategoryReport[]> {
  const params = new URLSearchParams();
  if (month) params.set("month", String(month));
  if (year) params.set("year", String(year));
  const qs = params.toString();
  return request<CategoryReport[]>(`/api/reports/by-category${qs ? "?" + qs : ""}`);
}

// ── Notifications ─────────────────────────────────────────────────────────────

export async function getNotifications(): Promise<NotificationResponse[]> {
  return request<NotificationResponse[]>("/api/notifications");
}

export async function markNotificationRead(id: number): Promise<NotificationResponse> {
  return request<NotificationResponse>(`/api/notifications/${id}/read`, { method: "PATCH" });
}
