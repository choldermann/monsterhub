import { useState, useEffect, useCallback } from "react";
import MonsterCard from "./components/MonsterCard";

const REFRESH_INTERVAL = 10000;

export default function App() {
  const [monsters, setMonsters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((msg) => {
    const id = Date.now();
    setToasts((t) => [...t, { id, msg }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 3500);
  }, []);

  const fetchMonsters = useCallback(async () => {
    try {
      const res = await fetch("/api/monsters");
      const data = await res.json();
      setMonsters(data);
    } catch {
      // silent on refresh failures
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMonsters();
    const interval = setInterval(fetchMonsters, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchMonsters]);

  const handleAction = async (monsterId, action) => {
    const labels = {
      start: "wird gestartet",
      stop: "wird gestoppt",
      restart: "wird neugestartet",
    };
    addToast(`Monster ${labels[action] ?? action}…`);
    try {
      await fetch(`/api/monsters/${monsterId}/${action}`, { method: "POST" });
      setTimeout(fetchMonsters, 1500);
    } catch {
      addToast("Fehler beim Ausführen der Aktion.");
    }
  };

  const runningCount = monsters.filter(
    (m) => m.status?.state === "running"
  ).length;

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <span className="header-logo">🧩</span>
          <div>
            <div className="header-title">Monster Hub</div>
            <div className="header-subtitle">Lokale Verwaltungszentrale</div>
          </div>
        </div>
        {!loading && (
          <div className="header-badge">
            <span>{runningCount}</span> von {monsters.length} aktiv
          </div>
        )}
      </header>

      {loading ? (
        <div className="loading">Verbinde mit Docker…</div>
      ) : (
        <div className="grid">
          {monsters.map((m) => (
            <MonsterCard key={m.id} monster={m} onAction={handleAction} />
          ))}
        </div>
      )}

      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className="toast">
            {t.msg}
          </div>
        ))}
      </div>
    </div>
  );
}
