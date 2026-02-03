interface Props {
  value: number; // 0..1
  color?: string;
}

export default function ProgressBar({ value, color = "#3B82F6" }: Props) {
  const width = Math.max(0, Math.min(1, value)) * 100;

  return (
    <div
      style={{
        background: "#e5e7eb",
        borderRadius: 6,
        height: 8,
        width: "100%",
      }}
    >
      <div
        style={{
          width: `${width}%`,
          background: color,
          height: "100%",
          borderRadius: 6,
          transition: "width 0.3s ease",
        }}
      />
    </div>
  );
}
