interface Props {
  text: string;
  color: string;
}

export default function Badge({ text, color }: Props) {
  return (
    <span
      style={{
        backgroundColor: color,
        color: "white",
        fontSize: 12,
        padding: "4px 8px",
        borderRadius: 999,
        marginRight: 8,
        display: "inline-block",
      }}
    >
      {text}
    </span>
  );
}
