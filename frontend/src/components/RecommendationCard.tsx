import ProgressBar from "./ProgressBar";
import { matchLabel } from "./utils/scoreLabels";
import type { Recommendation } from "../types/recommendation";
import Badge from "./badge";
import { budgetBadge,distanceBadge,crowdBadge,weatherBadge,} from "./utils/badges";


interface Props {
  recommendation: Recommendation;
}

export default function RecommendationCard({ recommendation }: Props) {
  const { event, relevance_score, score_breakdown } = recommendation;

  const match = matchLabel(relevance_score);

  return (
    <div
      style={{
        background: "#ffffff",
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
        border: "1px solid #e5e7eb",
      }}
    >
      <h3 style={{ marginBottom: 4, color: match.color }}>{event.name}</h3>
      <div style={{ fontSize: 14, color: "#6b7280", marginBottom: 12 }}>
        {event.date}
      </div>

      {/* PRIMARY SIGNAL */}
      <div style={{ marginBottom: 12 }}>
        <strong style={{ color: match.color }}>{match.label}</strong>
        <div style={{ marginTop: 6 }}>
          <ProgressBar value={relevance_score} color={match.color} />
        </div>
      </div>

      {/* SCORE BADGES */}
      <div style={{ marginTop: 12, display: "flex", flexWrap: "wrap" }}>
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

      {/* DETAILS */}
      <details>
        <summary style={{ cursor: "pointer", color: "#374151" }}>
          Why this was recommended
        </summary>

        <div style={{ marginTop: 12 }}>
          {Object.entries(score_breakdown).map(([key, detail]) => (
            <div key={key} style={{ marginBottom: 10, }}>
              <div style={{ fontSize: 13, marginBottom: 4, color: "#374151" }}>
                <strong>{key}</strong>
              </div>
              <ProgressBar value={detail.value} />
            </div>
          ))}
        </div>
      </details>
    </div>

    


  );
}
