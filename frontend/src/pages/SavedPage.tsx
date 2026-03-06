import { useEffect, useState } from "react";
import { getSavedEvents, unsaveEvent } from "../api/saved";
import { useSaved } from "../context/SavedContext";
import { API_BASE_URL, authHeaders } from "../api/config";

interface SavedEventRecord {
  id: number;
  event_id: string;
  saved_at?: string;
}

interface EventDetail {
  id: string;
  name: string;
  date?: string;
  genre?: string;
  location?: { venue_name?: string; city?: string; };
  ticketing?: { price: number; is_free: boolean; currency: string; ticket_url?: string; };
  media?: { poster_url?: string; };
}

const GENRE_EMOJI: Record<string, string> = {
  Music: "🎵", Tech: "💻", Food: "🍽", Sports: "⚽",
  Travel: "✈️", Business: "💼", Arts: "🎨", Nightlife: "🌙",
  Education: "📚", Wellness: "🧘", Culture: "🌍",
};

export default function SavedPage() {
  const [savedRecords, setSavedRecords] = useState<SavedEventRecord[]>([]);
  const [eventDetails, setEventDetails] = useState<Record<string, EventDetail>>({});
  const [loading, setLoading] = useState(true);
  const { refreshSaved } = useSaved();

  async function loadSaved() {
    setLoading(true);
    try {
      const data = await getSavedEvents();
      setSavedRecords(data);
    } catch (err) {
      console.error("Failed to load saved events", err);
    } finally {
      setLoading(false);
    }
  }

  async function loadEventDetails(records: SavedEventRecord[]) {
    const details: Record<string, EventDetail> = {};
    await Promise.all(
      records.map(async (record) => {
        try {
          const resp = await fetch(`${API_BASE_URL}/events/${record.event_id}`, {
            headers: authHeaders(),
          });
          if (resp.ok) details[record.event_id] = await resp.json();
        } catch {}
      })
    );
    setEventDetails(details);
  }

  useEffect(() => { loadSaved(); }, []);
  useEffect(() => { if (savedRecords.length > 0) loadEventDetails(savedRecords); }, [savedRecords]);

  async function handleRemove(eventId: string) {
    try {
      await unsaveEvent(eventId);
      setSavedRecords((prev) => prev.filter((e) => e.event_id !== eventId));
      await refreshSaved();
    } catch (err) {
      console.error("Failed to remove event", err);
    }
  }

  if (loading) {
    return (
      <div className="saved-page">
        <h2>Saved Events</h2>
        <p style={{ color: "#4A5568" }}>Loading...</p>
      </div>
    );
  }

  if (savedRecords.length === 0) {
    return (
      <div className="saved-page">
        <h2>Saved Events</h2>
        <div className="empty-state-content" style={{ marginTop: "2rem" }}>
          <div className="empty-state-icon">🎭</div>
          <h3>Nothing saved yet</h3>
          <p className="empty-state-description">
            Save events from the Discover page to find them here later.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="saved-page">
      <h2>Saved Events ({savedRecords.length})</h2>

      {savedRecords.map((record) => {
        const detail = eventDetails[record.event_id];
        const emoji = GENRE_EMOJI[detail?.genre ?? ""] ?? "🎭";

        return (
          <div key={record.event_id} className="saved-card">
            {detail?.media?.poster_url ? (
              <img src={detail.media.poster_url} alt={detail.name} className="saved-card-poster" />
            ) : (
              <div style={{
                height: 80,
                background: "linear-gradient(135deg, #0F1923 0%, #1e3a4a 100%)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "1.8rem",
              }}>
                {emoji}
              </div>
            )}

            <div className="saved-card-body">
              <div className="saved-card-name">
                {detail?.name ?? `Event ${record.event_id.slice(0, 8)}...`}
              </div>

              <div className="saved-card-meta">
                {detail?.date ?? "Date unknown"}
                {detail?.genre ? ` · ${detail.genre}` : ""}
                {detail?.location?.venue_name ? ` · ${detail.location.venue_name}` : ""}
                {detail?.location?.city ? `, ${detail.location.city}` : ""}
              </div>

              {detail?.ticketing && (
                <div style={{ fontSize: "0.82rem", fontWeight: 600, color: "#C1440E", marginBottom: 8 }}>
                  {detail.ticketing.is_free ? "🎟 Free" : `🎟 ${detail.ticketing.currency} ${detail.ticketing.price}`}
                </div>
              )}

              <div style={{ display: "flex", gap: 8 }}>
                {detail?.ticketing?.ticket_url && (
                  <a href={detail.ticketing.ticket_url} target="_blank" rel="noopener noreferrer" className="btn-ticket">
                    Get Tickets →
                  </a>
                )}
                <button className="btn-remove" onClick={() => handleRemove(record.event_id)}>
                  Remove
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
