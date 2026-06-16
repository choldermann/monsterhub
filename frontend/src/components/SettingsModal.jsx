import { useState, useEffect } from "react";
import "./SettingsModal.css";

export default function SettingsModal({ monsters, onClose, onSaved }) {
  const [settings, setSettings] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch("/api/settings")
      .then((r) => r.json())
      .then(setSettings)
      .catch(() => setSettings({ monstersuite_url: "https://monstersuite.de", license_keys: {} }));
  }, []);

  const setUrl = (val) =>
    setSettings((s) => ({ ...s, monstersuite_url: val }));

  const setKey = (monsterId, val) =>
    setSettings((s) => ({
      ...s,
      license_keys: { ...s.license_keys, [monsterId]: val },
    }));

  const save = async () => {
    setSaving(true);
    try {
      await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });
      onSaved();
      onClose();
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  };

  const configurableMonsters = monsters.filter((m) => m.status?.state !== "not_installed");

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <span className="settings-title">Einstellungen</span>
          <button className="settings-close" onClick={onClose}>×</button>
        </div>

        {!settings ? (
          <div style={{ padding: "32px", color: "#555", textAlign: "center" }}>Lädt…</div>
        ) : (
          <>
            <div className="settings-body">
              <div>
                <div className="settings-section-title">MonsterSuite</div>
                <div className="settings-field">
                  <label className="settings-label">Server-URL</label>
                  <input
                    className="settings-input"
                    type="url"
                    value={settings.monstersuite_url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://monstersuite.de"
                  />
                </div>
              </div>

              {configurableMonsters.length > 0 && (
                <div>
                  <div className="settings-section-title">Lizenzschlüssel</div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                    {configurableMonsters.map((m) => (
                      <div key={m.id} className="settings-field">
                        <label className="settings-label">
                          <span>{m.emoji}</span>
                          {m.name}
                        </label>
                        <input
                          className="settings-input"
                          type="text"
                          value={settings.license_keys?.[m.id] ?? ""}
                          onChange={(e) => setKey(m.id, e.target.value)}
                          placeholder="Lizenzschlüssel eingeben…"
                          spellCheck={false}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="settings-footer">
              <button className="settings-close" style={{ fontSize: "13px", color: "#666", padding: "8px 14px" }} onClick={onClose}>
                Abbrechen
              </button>
              <button className="btn-save" onClick={save} disabled={saving}>
                {saving ? "Speichert…" : "Speichern"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
