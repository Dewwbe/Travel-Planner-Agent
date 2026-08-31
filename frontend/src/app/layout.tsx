import type { Metadata } from "next";
import "./globals.css";
import "./agent.css";
import "./stages45.css";

export const metadata: Metadata = { title: "TripPilot AI", description: "Plan smarter journeys with an agentic travel assistant" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
