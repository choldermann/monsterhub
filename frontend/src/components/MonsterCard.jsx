import { useState } from "react";
import "./MonsterCard.css";

const STATE_LABELS = {
  running: "Läuft",
  stopped: "Gestoppt",
  partial: "Teilweise",
  not_installed: "Nicht installiert",
};

function StatusBadge({ state }) {
  return (
    <span className={`status-badge ${state}`}>
      <span className="status-dot" />
      {STATE_LABELS[state] ?? state}
    </span>
  );
}

function ContainerPills({ containers }) {
  if (!containers?.length) return null;
  return (
    <div className="containers">
      {containers.map((c) => (
        <span key={c.name} className="container-pill">
          <span className={`container-dot ${c.status}`} />
          {c.name.replace(/^(sm-|datenmonster-|rechnungsmonster-|pagemonster-)/, "")}
        </span>
      ))}
    </div>
  );
}

function LogModal({ monster, onClose }) {
  const [logs, setLogs] = useState(null);
  const [loading, setLoading] = useState(true);

  useState(() => {
    fetch(`/api/monsters/${monster.id}/logs`)
      .then((r) => r.json())
      .then((d) => {
        setLogs(d.logs);
        setLoading(false);
      })
      .catch(() => {
        setLogs("Fehler beim Laden der Logs.");
        setLoading(false);
      });
  }, [monster.id]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span className="modal-title">
            {monster.emoji} {monster.name} — Logs
          </span>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="modal-body">
          {loading ? (
            <div className="log-output">Lädt…</div>
          ) : (
            <pre className="log-output">{logs}</pre>
          )}
        </div>
      </div>
    </div>
  );
}

export default function MonsterCard({ monster, onAction }) {
  const [busy, setBusy] = useState(false);
  const [showLogs, setShowLogs] = useState(false);

  const state = monster.status?.state ?? "not_installed";
  const containers = monster.status?.containers ?? [];
  const isRunning = state === "running";
  const isNotInstalled = state === "not_installed";

  const act = async (action) => {
    setBusy(true);
    await onAction(monster.id, action);
    setTimeout(() => setBusy(false), 2000);
  };

  return (
    <>
      <div className="card" style={{ "--accent": monster.color }}>
        <div className="card-header">
          <div>
            <div className="card-title-row">
              <span className="card-emoji">{monster.emoji}</span>
              <div>
                <div className="card-name">{monster.name}</div>
                <div className="card-desc">{monster.description}</div>
              </div>
            </div>
          </div>
          <StatusBadge state={state} />
        </div>

        <ContainerPills containers={containers} />

        <div className="actions">
          {monster.url && isRunning && (
            <a
              className="btn btn-primary"
              href={monster.url}
              target="_blank"
              rel="noreferrer"
            >
              ↗ Öffnen
            </a>
          )}

          {!isNotInstalled && isRunning && (
            <button
              className="btn btn-ghost"
              onClick={() => act("restart")}
              disabled={busy}
            >
              ↺ Neustart
            </button>
          )}

          {!isNotInstalled && isRunning && (
            <button
              className="btn btn-danger"
              onClick={() => act("stop")}
              disabled={busy}
            >
              ⏹ Stoppen
            </button>
          )}

          {!isNotInstalled && !isRunning && state !== "not_installed" && (
            <button
              className="btn btn-success"
              onClick={() => act("start")}
              disabled={busy}
            >
              ▶ Starten
            </button>
          )}

          {!isNotInstalled && monster.primary_container && (
            <button
              className="btn btn-ghost"
              onClick={() => setShowLogs(true)}
            >
              ≡ Logs
            </button>
          )}

          {isNotInstalled && (
            <span
              className="btn btn-ghost"
              style={{ cursor: "default", opacity: 0.5 }}
            >
              Nicht installiert
            </span>
          )}
        </div>
      </div>

      {showLogs && (
        <LogModal monster={monster} onClose={() => setShowLogs(false)} />
      )}
    </>
  );
}
