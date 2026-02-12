import { useEffect, useState } from "react";
import { getSavedEvents, removeSaved } from "../api/saved";

export default function SavedPage() {
  const [savedIds, setSavedIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadSaved() {
    setLoading(true);
    try {
      const data = await getSavedEvents();
      setSavedIds(data);
    } catch {
      alert("Failed to load saved events");
    } finally {
      setLoading(false);
    }
  }

  async function handleRemove(id: string) {
    await removeSaved(id);
    setSavedIds((prev) => prev.filter((e) => e !== id));
  }

  useEffect(() => {
    loadSaved();
  }, []);

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Saved Events</h1>

      {loading && <p>Loading saved events...</p>}

      {!loading && savedIds.length === 0 && (
        <p>No saved events yet.</p>
      )}

      <ul>
        {savedIds.map((id) => (
          <li key={id} style={{ marginBottom: 10 }}>
            Event ID: {id}

            <button
              onClick={() => handleRemove(id)}
              style={{
                marginLeft: 10,
                background: "#ef4444",
                color: "white",
                border: "none",
                padding: "4px 8px",
                borderRadius: 4,
                cursor: "pointer",
              }}
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
