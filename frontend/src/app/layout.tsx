import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "TripPilot AI", description: "Plan smarter journeys with an agentic travel assistant" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}

