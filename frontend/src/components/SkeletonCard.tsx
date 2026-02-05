export default function SkeletonCard() {
  return (
    <div
      style={{
        background: "#ffffff",
        borderRadius: 12,
        padding: 16,
        marginBottom: 16,
        border: "1px solid #e5e7eb",
        animation: "pulse 1.5s infinite",
      }}
    >
      <div style={{ height: 20, width: "60%", background: "#e5e7eb", marginBottom: 8 }} />
      <div style={{ height: 14, width: "40%", background: "#e5e7eb", marginBottom: 12 }} />
      <div style={{ height: 10, width: "100%", background: "#e5e7eb" }} />
    </div>
  );
}
