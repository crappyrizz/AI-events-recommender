interface Props {
  value: string;
  onChange: (value: any) => void;
}

export default function SortControl({ value, onChange }: Props) {
  return (
    <div style={{ margin: "16px 0" }}>
      <label style={{ marginRight: 8, fontWeight: 500 }}>
        Sort by:
      </label>

      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{ padding: 6 }}
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
