interface Props {
  value: string;
  onChange: (value: any) => void;
}

export default function SortControl({ value, onChange }: Props) {
  return (
    <div style={{ margin: "16px 0", display: "flex", gap: "12px", flexWrap: "wrap", alignItems: "center" }}>
      <label style={{ fontWeight: 500, whiteSpace: "nowrap" }}>
        Sort by:
      </label>

      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{ padding: "6px 8px", minWidth: "150px" }}
      >
        <option value="best">Best Match</option>
        <option value="budget">Budget Fit</option>
        <option value="distance">Distance</option>
        <option value="crowd">Crowd Level</option>
        <option value="weather">Weather</option>
      </select>
    </div>
  );
}
