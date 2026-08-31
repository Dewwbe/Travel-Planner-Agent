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
export type Activity = { time:string; title:string; description:string; estimated_cost:number };
export type DayPlan = { day:number; date:string; theme:string; activities:Activity[] };
export type TripPlan = { destination:string; city_code:string; start_date:string; end_date:string; travelers:number; currency:string; total_budget:number; max_hotel_total_price:number; hotel_rating?:number; summary:string; days:DayPlan[]; assumptions:string[] };
export type PlanResponse = { trip_id:number; status:"planned"; plan:TripPlan };
export type HotelOffer = { hotel_id:string; name:string; rating?:number; city_code:string; room_description?:string; price_total:number; currency:string; check_in:string; check_out:string };
export type ReviewResult = { valid:boolean; budget_valid:boolean; calendar_conflict:boolean; hotel_results:number; issues:string[] };
export type AgentRunResponse = { thread_id:string; trip_id:number; plan:TripPlan; hotels:HotelOffer[]; calendar:Record<string,unknown>; review:ReviewResult; pending_action_id:string|null; requires_approval:boolean };
export type ActionResponse = { action_id:string; status:"approved"|"rejected"; result?:{html_link?:string;event_id?:string} };
