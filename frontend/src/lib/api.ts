const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const response = await fetch(`${API_URL}${path}`, { ...options, headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers } });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Something went wrong");
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export type User = { id:number; name:string; email:string; created_at:string };
export type Trip = { id:number; destination:string; start_date:string; end_date:string; budget:number; currency:string; status:string; request_text?:string; created_at:string };

