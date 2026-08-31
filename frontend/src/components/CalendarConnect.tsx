"use client";
import { useEffect, useState } from "react";
import { CalendarCheck, LoaderCircle } from "lucide-react";
import { api } from "@/lib/api";

export default function CalendarConnect(){
  const [connected,setConnected]=useState(false); const [loading,setLoading]=useState(true); const [error,setError]=useState("");
  useEffect(()=>{api<{connected:boolean}>("/calendar/status").then(x=>setConnected(x.connected)).catch(e=>setError(e.message)).finally(()=>setLoading(false));},[]);
  async function connect(){setLoading(true);setError("");try{const result=await api<{authorization_url:string}>("/calendar/oauth/start");window.location.href=result.authorization_url;}catch(e){setError(e instanceof Error?e.message:"Could not connect calendar");setLoading(false);}}
  return <div className="calendarConnect"><button className={connected?"secondary":"primary"} onClick={connect} disabled={loading||connected}>{loading?<LoaderCircle size={16}/>:<CalendarCheck size={16}/>} {connected?"Calendar connected":"Connect Calendar"}</button>{error&&<small>{error}</small>}</div>;
}
