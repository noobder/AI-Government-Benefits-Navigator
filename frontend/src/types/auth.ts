export interface Account {
  id: string;
  email: string;
  role: "user" | "admin";
  created_at: string;
  last_login_at: string | null;
}
