"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, CalendarCheck, MapPin, Sparkles } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  useEffect(() => { if (localStorage.getItem("token")) router.replace("/dashboard"); else setReady(true); }, [router]);
  if (!ready) return null;
  return <main className="landing">
    <nav className="nav"><div className="brand"><Sparkles size={21}/> TripPilot <span>AI</span></div><button className="textButton" onClick={() => router.push("/login")}>Sign in</button></nav>
    <section className="hero">
      <div className="eyebrow">Your intelligent travel copilot</div>
      <h1>Go somewhere<br/><em>unforgettable.</em></h1>
      <p>Describe your dream trip. TripPilot turns it into an organized plan, ready for live hotels and calendar coordination.</p>
      <button className="primary large" onClick={() => router.push("/register")}>Start planning <ArrowRight size={18}/></button>
      <div className="featureRow"><span><MapPin size={17}/> Personalized trips</span><span><CalendarCheck size={17}/> Calendar-ready</span><span><Sparkles size={17}/> AI planning</span></div>
    </section>
    <div className="orb one"/><div className="orb two"/>
  </main>;
}

