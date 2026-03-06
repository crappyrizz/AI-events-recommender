import { useState } from "react";
import { matchLabel } from "./utils/scoreLabels";
import type { Recommendation } from "../types/recommendation";
import Badge from "./badge";
import { budgetBadge, distanceBadge, crowdBadge, weatherBadge } from "./utils/badges";
import { sendInteraction } from "../api/interactions";
import { saveEvent } from "../api/saved";
import { useSaved } from "../context/SavedContext";
import EventMedia from "./EventMedia";

interface Props {
  recommendation: Recommendation;
}

function distanceLabel(distance: number) {
  if (distance == undefined) return "";
  if (distance <= 50) return `${distance} km away`;
  if (distance <= 200) return `${distance} km away · Regional`;
  return `${distance} km away · Far`;
}

const GENRE_EMOJI: Record<string, string> = {
  Music: "🎵", Tech: "💻", Food: "🍽", Sports: "⚽",
  Travel: "✈️", Business: "💼", Arts: "🎨", Nightlife: "🌙",
  Education: "📚", Wellness: "🧘", Culture: "🌍",
};

function matchTier(score: number): "excellent" | "good" | "fair" | "low" {
  if (score >= 0.85) return "excellent";
  if (score >= 0.65) return "good";
  if (score >= 0.45) return "fair";
  return "low";
}

export default function RecommendationCard({ recommendation }: Props) {
  const { event, relevance_score, score_breakdown } = recommendation;
  const [expanded, setExpanded] = useState(false);
  const match = matchLabel(relevance_score);
  const tier = matchTier(relevance_score);
  const { savedIds, refreshSaved } = useSaved();
  const [saving, setSaving] = useState(false);
  const saved = savedIds.includes(event.id);
  const emoji = GENRE_EMOJI[event.genre ?? ""] ?? "🎭";

  async function toggleSave() {
    if (saving || saved) return;
    setSaving(true);
    try {
      await saveEvent(event.id);
      await refreshSaved();
    } catch (err) {
      console.error("Save failed:", err);
    } finally {
      setSaving(false);
    }
  }

  async function markInterested() {
    try { await sendInteraction(event.id, "INTERESTED"); } catch {}
  }

  async function markNotInterested() {
    try { await sendInteraction(event.id, "NOT_INTERESTED"); } catch {}
  }

  return (
    <article className="rec-card" data-match={tier}>
      {/* POSTER */}
      {event.media?.poster_url ? (
        <img src={event.media.poster_url} alt={event.name} className="rec-card-poster" />
      ) : (
        <div className="rec-card-poster-placeholder">{emoji}</div>
      )}

      <div className="rec-card-body">
        {/* NAME + VERIFIED */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
          <h3 className="rec-card-name">{event.name}</h3>
          {event.is_verified && <span className="verified-badge">✓ Verified</span>}
        </div>

        {/* META */}
        <div className="rec-card-meta">
          <span>{event.date} · {event.genre ?? "Uncategorised"}</span>
          {event.location?.venue_name && (
            <span>📍 {event.location.venue_name}{event.location.city ? `, ${event.location.city}` : ""}</span>
          )}
          {recommendation.distance_km != null && (
            <span>🗺 {distanceLabel(recommendation.distance_km)}</span>
          )}
        </div>

        {/* PRICE */}
        <div className="rec-card-price">
          {event.ticketing?.is_free ? "🎟 Free entry" : `🎟 ${event.ticketing?.currency ?? "KES"} ${event.ticketing?.price ?? 0}`}
        </div>

        {/* MATCH SCORE */}
        <div className="rec-card-match">
          <span className="rec-card-match-label" style={{ color: match.color }}>{match.label}</span>
          <div style={{ flex: 1, background: "#e8e2d9", borderRadius: 6, height: 6 }}>
            <div style={{
              width: `${Math.min(relevance_score, 1) * 100}%`,
              background: match.color,
              height: "100%",
              borderRadius: 6,
              transition: "width 0.3s ease",
            }} />
          </div>
        </div>

        {/* BADGES */}
        {!expanded && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {score_breakdown.budget && (() => { const b = budgetBadge(score_breakdown.budget.value); return <Badge text={`💵 ${b.label}`} color={b.color} />; })()}
            {score_breakdown.distance && (() => { const d = distanceBadge(score_breakdown.distance.value); return <Badge text={`📍 ${d.label}`} color={d.color} />; })()}
            {score_breakdown.crowd && (() => { const c = crowdBadge(score_breakdown.crowd.value); return <Badge text={`👥 ${c.label}`} color={c.color} />; })()}
            {score_breakdown.weather && (() => { const w = weatherBadge(score_breakdown.weather.value); return <Badge text={`☀️ ${w.label}`} color={w.color} />; })()}
          </div>
        )}

        {/* ACTIONS */}
        <div className="rec-card-actions">
          <button className={`btn-save ${saved ? "btn-save--saved" : "btn-save--unsaved"}`} onClick={toggleSave} disabled={saving}>
            {saving ? "..." : saved ? "✓ Saved" : "Save"}
          </button>
          <button className="btn-interested" onClick={markInterested}>👍</button>
          <button className="btn-not-interested" onClick={markNotInterested}>👎</button>
          {event.ticketing?.ticket_url && (
            <a href={event.ticketing.ticket_url} target="_blank" rel="noopener noreferrer" className="btn-ticket">
              Get Tickets →
            </a>
          )}
        </div>

        {/* TOGGLE */}
        <button className="btn-toggle-details" onClick={() => setExpanded(v => !v)}>
          {expanded ? "Hide details ▲" : "Show details ▼"}
        </button>

        {/* EXPANDED */}
        {expanded && (
          <div className="rec-card-details">
            {Object.entries(score_breakdown).map(([key, detail]) => (
              <div key={key}>
                <div style={{ fontSize: "0.75rem", color: "#4A5568", marginBottom: 3 }}>
                  <strong>{key}</strong> — {detail.description}
                </div>
                <div className="progress-bar-track">
                  <div className="progress-bar-fill" style={{ width: `${Math.min(detail.value, 1) * 100}%`, background: "#C1440E" }} />
                </div>
              </div>
            ))}
            <EventMedia eventId={event.id} />
          </div>
        )}
      </div>
    </article>
  );
}
