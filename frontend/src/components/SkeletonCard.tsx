export default function SkeletonCard() {
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
      {/* Title */}
      <div className="skeleton skeleton-title" />

      {/* Subtitle */}
      <div className="skeleton skeleton-subtitle" />

      {/* Match bar */}
      <div className="skeleton skeleton-bar" />

      {/* Badges */}
      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <div className="skeleton skeleton-badge" />
        <div className="skeleton skeleton-badge" />
        <div className="skeleton skeleton-badge" />
      </div>
    </div>
  );
}
