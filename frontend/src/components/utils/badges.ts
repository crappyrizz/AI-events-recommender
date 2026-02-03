export type Badge = {
  label: string;
  color: string;
};

export function budgetBadge(value: number): Badge {
  if (value >= 0.8) return { label: "Good fit", color: "#10B981" };
  if (value >= 0.5) return { label: "Fair", color: "#F59E0B" };
  return { label: "Over budget", color: "#EF4444" };
}

export function distanceBadge(value: number): Badge {
  if (value >= 0.7) return { label: "Close", color: "#10B981" };
  if (value >= 0.4) return { label: "Moderate", color: "#F59E0B" };
  return { label: "Far", color: "#EF4444" };
}

export function crowdBadge(value: number): Badge {
  if (value >= 0.7) return { label: "Low", color: "#10B981" };
  if (value >= 0.4) return { label: "Medium", color: "#F59E0B" };
  return { label: "High", color: "#EF4444" };
}

export function weatherBadge(value: number): Badge {
  if (value >= 0.7) return { label: "Good", color: "#10B981" };
  if (value >= 0.4) return { label: "Fair", color: "#F59E0B" };
  return { label: "Poor", color: "#9CA3AF" };
}
