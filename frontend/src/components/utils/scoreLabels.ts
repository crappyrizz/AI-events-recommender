export function matchLabel(score: number) {
  if (score >= 0.9) return { label: "EXCELLENT", color: "#10B981" };
  if (score >= 0.7) return { label: "GOOD", color: "#3B82F6" };
  if (score >= 0.5) return { label: "FAIR", color: "#F59E0B" };
  return { label: "CONSIDER", color: "#9CA3AF" };
}
