import { useEffect, useState } from "react";
import { getSavedEvents, unsaveEvent } from "../api/saved";
import { useSaved } from "../context/SavedContext";
// import { useUser } from "../context/UserContext";




interface SavedEvent {
  id: number;
  event_id: string;
  event_name: string;
  event_date: string;
  event_genre: string;
}

export default function SavedPage() {
  const [events, setEvents] = useState<SavedEvent[]>([]);
  const [loading, setLoading] = useState(true);
  

  // Only what we need from context
  const { refreshSaved } = useSaved();

  // Load saved events
  async function loadSaved() {
    setLoading(true);
    try {
      const data = await getSavedEvents();
      setEvents(data);
    } catch (error) {
      console.error("Failed to load saved events", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSaved();
  }, []);

  // Remove event
  async function handleRemove(eventId: string) {
    try {
    
        await unsaveEvent(eventId);

      // Refresh this page
      setEvents((prev) =>
        prev.filter((e) => e.event_id !== eventId)
      );

      // Sync Home / Recommendation cards
      await refreshSaved();
    } catch (error) {
      console.error("Failed to remove event", error);
    }
  }

  if (loading) {
    return <div style={{ padding: 20 }}>Loading saved events...</div>;
  }

  if (events.length === 0) {
    return (
      <div style={{ padding: 20 }}>
        <h2>No saved events yet</h2>
        <p>Save events from the Home page to see them here.</p>
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: 800, margin: "0 auto" }}>
      <h2>Saved Events</h2>

      {events.map((event) => (
        <div
          key={event.event_id}
          style={{
            border: "1px solid #e5e7eb",
            borderRadius: 10,
            padding: 16,
            marginTop: 12,
            background: "#fff",
          }}
        >
          <h3 style={{ margin: 0 }}>{event.event_name}</h3>
          <div style={{ color: "#6b7280", fontSize: 14 }}>
            {event.event_date} • {event.event_genre}
          </div>

          <button
            onClick={() => handleRemove(event.event_id)}
            style={{
              marginTop: 10,
              padding: "6px 12px",
              background: "#ef4444",
              color: "white",
              border: "none",
              borderRadius: 6,
              cursor: "pointer",
            }}
          >
            Remove
          </button>
        </div>
      ))}
    </div>
  );
}