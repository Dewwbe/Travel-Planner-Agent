"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { ArrowRight, Sparkles } from "lucide-react";
import { api } from "@/lib/api";

export default function AuthForm({ mode }: { mode: "login" | "register" }) {
  const router = useRouter(); const [error,setError]=useState(""); const [loading,setLoading]=useState(false);
  async function submit(e:FormEvent<HTMLFormElement>) { e.preventDefault(); setError(""); setLoading(true); const data=Object.fromEntries(new FormData(e.currentTarget)); try { const result=await api<{access_token:string}>(`/auth/${mode}`,{method:"POST",body:JSON.stringify(data)}); localStorage.setItem("token",result.access_token); router.push("/dashboard"); } catch(err){setError(err instanceof Error?err.message:"Unable to continue");} finally{setLoading(false);} }
  const register=mode==="register";
  return <main className="authPage"><div className="authCard"><Link href="/" className="brand"><Sparkles size={21}/> TripPilot <span>AI</span></Link><h1>{register?"Create your account":"Welcome back"}</h1><p>{register?"Your next journey begins here.":"Continue planning your next adventure."}</p><form onSubmit={submit}>{register&&<label>Name<input name="name" placeholder="Alex Morgan" minLength={2} required/></label>}<label>Email<input name="email" type="email" placeholder="alex@example.com" required/></label><label>Password<input name="password" type="password" placeholder="At least 8 characters" minLength={8} required/></label>{error&&<div className="error">{error}</div>}<button className="primary" disabled={loading}>{loading?"Please wait...":register?"Create account":"Sign in"}<ArrowRight size={17}/></button></form><div className="authSwitch">{register?"Already have an account? ":"New to TripPilot? "}<Link href={register?"/login":"/register"}>{register?"Sign in":"Create an account"}</Link></div></div></main>;
}

