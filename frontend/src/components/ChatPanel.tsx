"use client";

import { FormEvent, useState } from "react";
import {
  Bot,
  Building2,
  CalendarDays,
  LoaderCircle,
  Send,
  Sparkles,
} from "lucide-react";

import {
  api,
  HotelOffer,
  PlanResponse,
} from "@/lib/api";

type Message = {
  role: "assistant" | "user";
  content: string;
};

type ChatPanelProps = {
  onTripPlanned?: () => void;
};

export default function ChatPanel({
  onTripPlanned,
}: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Where would you like to go? Include dates, budget, travelers, and preferences.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PlanResponse | null>(null);
  const [hotels, setHotels] = useState<HotelOffer[]>([]);
  const [error, setError] = useState("");

  async function send(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const prompt = input.trim();

    if (!prompt || loading) {
      return;
    }

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: prompt,
      },
    ]);

    setInput("");
    setLoading(true);
    setError("");
    setResult(null);
    setHotels([]);

    try {
      const planned = await api<PlanResponse>("/agent/plan", {
        method: "POST",
        body: JSON.stringify({ prompt }),
      });

      setResult(planned);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: planned.plan.summary,
        },
      ]);

      onTripPlanned?.();

      try {
        const hotelResponse = await api<{
          hotels: HotelOffer[];
        }>("/hotels/search", {
          method: "POST",
          body: JSON.stringify({
            city_code: planned.plan.city_code,
            check_in: planned.plan.start_date,
            check_out: planned.plan.end_date,
            adults: planned.plan.travelers,
            max_price: planned.plan.max_hotel_total_price,
            currency: planned.plan.currency,
            rating: planned.plan.hotel_rating,
            limit: 5,
          }),
        });

        setHotels(hotelResponse.hotels);
      } catch (hotelError) {
        const message =
          hotelError instanceof Error
            ? hotelError.message
            : "Hotel search unavailable";

        setError(`Plan created. Hotel search: ${message}`);
      }
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to create plan"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel chatPanel">
      <div className="panelTitle">
        <span className="iconBox">
          <Bot size={18} />
        </span>

        <div>
          <h2>Plan with TripPilot</h2>
          <p>AI planner + live Hotel MCP search</p>
        </div>
      </div>

      <div className="messages">
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={`message ${message.role}`}
          >
            {message.content}
          </div>
        ))}

        {loading && (
          <div className="agentLoading">
            <LoaderCircle size={17} />
            Planning and checking hotels...
          </div>
        )}

        {error && <div className="error">{error}</div>}

        {result && (
          <div className="planResult">
            <div className="resultHeading">
              <Sparkles size={17} />
              <b>{result.plan.destination}</b>

              <span>
                {result.plan.currency}{" "}
                {Number(result.plan.total_budget).toLocaleString()}
              </span>
            </div>

            <div className="planMeta">
              <span>
                <CalendarDays size={14} />
                {result.plan.start_date} — {result.plan.end_date}
              </span>

              <span>{result.plan.days.length} planned days</span>
            </div>

            <div className="dayChips">
              {result.plan.days.map((day) => (
                <span key={day.day}>
                  Day {day.day}: {day.theme}
                </span>
              ))}
            </div>

            {hotels.length > 0 && (
              <div className="hotelResults">
                <h3>
                  <Building2 size={16} />
                  Live hotel offers
                </h3>

                {hotels.map((hotel) => (
                  <article key={hotel.hotel_id}>
                    <div>
                      <b>{hotel.name}</b>

                      <small>
                        {hotel.rating
                          ? `${hotel.rating}-star · `
                          : ""}

                        {hotel.room_description || "Available room"}
                      </small>
                    </div>

                    <strong>
                      {hotel.currency}{" "}
                      {Number(hotel.price_total).toLocaleString()}
                    </strong>
                  </article>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      <form className="chatInput" onSubmit={send}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Plan 4 days in Bangkok under $800..."
        />

        <button
          type="submit"
          aria-label="Send"
          disabled={loading}
        >
          <Send size={17} />
        </button>
      </form>
    </section>
  );
}