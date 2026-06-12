// ── Auth ──────────────────────────────────────────────────────────────────────

export interface UserRegister {
  email: string;
  username: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserResponse {
  id: number;
  email: string;
  username: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

// ── Accounts ──────────────────────────────────────────────────────────────────

export interface AccountCreate {
  name: string;
  description?: string;
  initial_balance?: number;
}

export interface AccountUpdate {
  name?: string;
  description?: string;
}

export interface AccountResponse {
  id: number;
  name: string;
  description?: string;
  balance: number;
  user_id: number;
  created_at: string;
}

// ── Transactions ──────────────────────────────────────────────────────────────

export type TransactionType = "income" | "expense";

export interface TransactionCreate {
  amount: number;
  type: TransactionType;
  category: string;
  description?: string;
  date: string;
  account_id: number;
}

export interface TransactionUpdate {
  amount?: number;
  type?: TransactionType;
  category?: string;
  description?: string;
  date?: string;
}

export interface TransactionResponse {
  id: number;
  amount: number;
  type: TransactionType;
  category: string;
  description?: string;
  date: string;
  account_id: number;
  user_id: number;
  created_at: string;
}

// ── Budgets ───────────────────────────────────────────────────────────────────

export interface BudgetCreate {
  category: string;
  limit_amount: number;
  month: number;
  year: number;
}

export interface BudgetResponse {
  id: number;
  category: string;
  limit_amount: number;
  month: number;
  year: number;
  user_id: number;
  spent: number;
  percentage: number;
  created_at: string;
}

// ── Reports ───────────────────────────────────────────────────────────────────

export interface MonthlySummary {
  month: number;
  year: number;
  total_income: number;
  total_expense: number;
  net_balance: number;
}

export interface CategoryReport {
  category: string;
  total: number;
  percentage: number;
  transaction_count: number;
}

// ── Notifications ─────────────────────────────────────────────────────────────

export interface NotificationResponse {
  id: number;
  message: string;
  is_read: boolean;
  user_id: number;
  created_at: string;
}

// ── API Error ─────────────────────────────────────────────────────────────────

export interface ApiError {
  detail: string | { msg: string; type: string }[];
}
