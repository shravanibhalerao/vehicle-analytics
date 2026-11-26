import { useEffect, useState } from "react";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip,
  CartesianGrid, ResponsiveContainer, Cell,
} from "recharts";
import VideoPlayer from "./VideoPlayer";
import "./App.css";

// ---------- Settings ----------
const API = "http://localhost:8000/api";
const STREAM_URL = "http://localhost:8888/traffic/index.m3u8";
const REFRESH_MS = 5000;
// ------------------------------

const COLOR_FILL = {
  black: "#3a3a3a", white: "#f0f0f0", silver: "#c0c0c0", grey: "#808080",
  red: "#e53935", blue: "#1e88e5", other: "#9c27b0",
};
const TYPE_FILL = "#4fc3f7";

// Accepts {car: 10} or [{type: "car", count: 10}] style data
function toPairs(data) {
  if (Array.isArray(data)) {
    return data.map((d) => ({
      name: String(d.type ?? d.vehicle_type ?? d.color ?? d.name ?? Object.values(d)[0]),
      value: Number(d.count ?? d.total ?? Object.values(d)[1] ?? 0),
    }));
  }
  if (data && typeof data === "object") {
    return Object.entries(data).map(([name, value]) => ({ name, value: Number(value) }));
  }
  return [];
}

function toTotal(data) {
  if (typeof data === "number") return data;
  return Number(data?.total ?? data?.count ?? Object.values(data ?? {})[0] ?? 0);
}

function formatTime(value, withDate = false) {
  const d = new Date(value);
  if (isNaN(d)) return String(value ?? "");
  return withDate
    ? d.toLocaleString([], { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", second: "2-digit" })
    : d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

async function get(path) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

export default function App() {
  const [total, setTotal] = useState(0);
  const [types, setTypes] = useState([]);
  const [colors, setColors] = useState([]);
  const [events, setEvents] = useState([]);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");
  const [updated, setUpdated] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const [t, ty, co, ev, hi] = await Promise.all([
          get("/total"),
          get("/stats/types"),
          get("/stats/colors"),
          get("/events/recent"),
          get("/analytics/history?hours=24"),
        ]);
        setTotal(toTotal(t));
        setTypes(toPairs(ty));
        setColors(toPairs(co));
        setEvents(Array.isArray(ev) ? ev : ev?.events ?? []);
        setHistory((Array.isArray(hi) ? hi : []).map((h) => ({
          hour: formatTime(h.hour), count: Number(h.count),
        })));
        setError("");
        setUpdated(new Date());
      } catch (e) {
        setError(`Backend se data nahi aaya (${e.message}). Kya uvicorn chal raha hai?`);
      }
    }
    load();
    const id = setInterval(load, REFRESH_MS);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>Vehicle Analytics Dashboard</h1>
        {updated && <span className="updated">Last update: {updated.toLocaleTimeString()}</span>}
      </header>

      {error && <div className="error">{error}</div>}

      <section className="stats">
        <div className="stat main">
          <div className="label">Total vehicles</div>
          <div className="value">{total}</div>
        </div>
        {types.map((t) => (
          <div className="stat" key={t.name}>
            <div className="label">{t.name}</div>
            <div className="value">{t.value}</div>
          </div>
        ))}
      </section>

      <section className="grid">
        <div className="card">
          <h2>Live stream</h2>
          <VideoPlayer src={STREAM_URL} />
        </div>

        <div className="card">
          <h2>Vehicles per hour (last 24h)</h2>
          {history.length === 0 ? <p className="empty">Abhi data nahi hai</p> : (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={history}>
                <CartesianGrid stroke="#2a323d" />
                <XAxis dataKey="hour" stroke="#8a96a3" />
                <YAxis allowDecimals={false} stroke="#8a96a3" />
                <Tooltip contentStyle={{ background: "#1a2029", border: "none" }} />
                <Line type="monotone" dataKey="count" stroke="#4fc3f7" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card">
          <h2>By vehicle type</h2>
          {types.length === 0 ? <p className="empty">Abhi data nahi hai</p> : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={types}>
                <CartesianGrid stroke="#2a323d" />
                <XAxis dataKey="name" stroke="#8a96a3" />
                <YAxis allowDecimals={false} stroke="#8a96a3" />
                <Tooltip contentStyle={{ background: "#1a2029", border: "none" }} />
                <Bar dataKey="value" fill={TYPE_FILL} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card">
          <h2>By colour</h2>
          {colors.length === 0 ? <p className="empty">Abhi data nahi hai</p> : (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={colors}>
                <CartesianGrid stroke="#2a323d" />
                <XAxis dataKey="name" stroke="#8a96a3" />
                <YAxis allowDecimals={false} stroke="#8a96a3" />
                <Tooltip contentStyle={{ background: "#1a2029", border: "none" }} />
                <Bar dataKey="value">
                  {colors.map((c) => (
                    <Cell key={c.name} fill={COLOR_FILL[c.name] ?? "#9c27b0"} stroke="#555" />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card wide">
          <h2>Recent events</h2>
          {events.length === 0 ? <p className="empty">Abhi koi event nahi</p> : (
            <table>
              <thead>
                <tr><th>Time</th><th>Type</th><th>Colour</th><th>Direction</th></tr>
              </thead>
              <tbody>
                {events.slice(0, 15).map((e, i) => (
                  <tr key={e.id ?? i}>
                    <td>{formatTime(e.timestamp ?? e.time ?? e.created_at, true)}</td>
                    <td>{e.vehicle_type ?? e.type}</td>
                    <td>{e.vehicle_color ?? e.color}</td>
                    <td>{e.direction}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  );
}