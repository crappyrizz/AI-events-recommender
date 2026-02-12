import ProgressBar from "./ProgressBar";
import { matchLabel } from "./utils/scoreLabels";
import type { Recommendation } from "../types/recommendation";
import Badge from "./badge";
import {budgetBadge, distanceBadge, crowdBadge, weatherBadge,} from "./utils/badges";
import { useState } from "react";
import { sendInteraction } from "../api/interactions";
import { getSavedEvents, removeSaved} from "../api/saved";


interface Props {
  recommendation: Recommendation;
}

const USER_ID = 1;


function distanceLabel(distance: number) {
  if (distance == undefined) return "Distance unknown";
  if (distance <= 50) return `${distance} km away`;
  if (distance <= 200) return `${distance} km away (Regional)`;
  return `${distance} km away (Far)`;
}



export default function RecommendationCard({ recommendation }: Props) {
  const { event, relevance_score, score_breakdown } = recommendation;
  const [expanded, setExpanded] = useState(false);
  const match = matchLabel(relevance_score);
  const [saved, setSaved] = useState(false);


  // ✅ Handlers INSIDE component
  async function toggleSave() {
    if (saved) {
      await removeSaved(event.id);
      setSaved(false);
    } else {
      await getSavedEvents(event.id);
      setSaved(true);
    }
  }


  async function markInterested() {
    await sendInteraction(USER_ID, event.id, "INTERESTED");
  }

  async function markNotInterested() {
    await sendInteraction(USER_ID, event.id, "NOT_INTERESTED");
  }

  return (
    <article
      style={{
        background: "#ffffff",
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
        border: "1px solid #e5e7eb",
      }}
    >
      {/* HEADER */}
      <div>
        <h3 style={{ marginBottom: 4, color: "#111827" }}>
          {event.name}
        </h3>

        <button
          onClick={toggleSave}
          style={{
            marginTop: 8,
            background: "none",
            border: "none",
            cursor: "pointer",
            fontSize: 18,
          }}
        >
          {saved ? "❤️ Saved" : "🤍 Save"}
        </button>


        <div style={{ fontSize: 14, color: "#6b7280" }}>
          {event.date} • {event.genre}
        </div>

        <div style={{ fontSize: 13, color: "#6b7280", marginTop: 4 }}>
          📍 {distanceLabel(recommendation.distance_km ?? 0)} {/* Fallback to 0 if distance_km is undefined */}
        </div>

      </div>

      {/* MATCH */}
      <div style={{ marginTop: 12 }}>
        <strong style={{ color: match.color }}>
          {match.label}
        </strong>

        <div style={{ marginTop: 6 }}>
          <ProgressBar value={relevance_score} color={match.color} />
        </div>
      </div>

      {/* COMPACT BADGES */}
      {!expanded && (
        <div
          style={{
            marginTop: 12,
            display: "flex",
            flexWrap: "wrap",
            gap: 8,
          }}
        >
          {score_breakdown.budget && (() => {
            const b = budgetBadge(score_breakdown.budget.value);
            return <Badge text={`💵 Budget: ${b.label}`} color={b.color} />;
          })()}

          {score_breakdown.distance && (() => {
            const d = distanceBadge(score_breakdown.distance.value);
            return <Badge text={`📍 Distance: ${d.label}`} color={d.color} />;
          })()}

          {score_breakdown.crowd && (() => {
            const c = crowdBadge(score_breakdown.crowd.value);
            return <Badge text={`👥 Crowd: ${c.label}`} color={c.color} />;
          })()}

          {score_breakdown.weather && (() => {
            const w = weatherBadge(score_breakdown.weather.value);
            return <Badge text={`☀️ Weather: ${w.label}`} color={w.color} />;
          })()}
        </div>
      )}

      {/* INTERACTIONS */}
      <div style={{ marginTop: 12, display: "flex", gap: 10 }}>
        <button
          onClick={markInterested}
          style={{
            padding: "8px 14px",
            background: "#10b981",
            color: "white",
            borderRadius: 8,
            border: "none",
            cursor: "pointer",
          }}
        >
          👍 Interested
        </button>

        <button
          onClick={markNotInterested}
          style={{
            padding: "8px 14px",
            background: "#ef4444",
            color: "white",
            borderRadius: 8,
            border: "none",
            cursor: "pointer",
          }}
        >
          👎 Not Interested
        </button>
      </div>

      {/* TOGGLE */}
      <button
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
        style={{
          marginTop: 12,
          background: "none",
          border: "none",
          color: "#2563EB",
          cursor: "pointer",
          padding: 0,
          fontSize: 14,
        }}
      >
        {expanded ? "Hide details ▲" : "Show details ▼"}
      </button>

      {/* DETAILS */}
      {expanded && (
        <div
          style={{
            marginTop: 16,
            paddingTop: 16,
            borderTop: "1px solid #e5e7eb",
          }}
        >
          {Object.entries(score_breakdown).map(([key, detail]) => (
            <div key={key} style={{ marginBottom: 10 }}>
              <div style={{ fontSize: 13, marginBottom: 4, color: "#6b7280" }}>
                <strong>{key}</strong>
              </div>
              <ProgressBar value={detail.value} />
            </div>
          ))}
        </div>
      )}
    </article>
  );
}
