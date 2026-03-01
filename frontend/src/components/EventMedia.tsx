import { useEffect, useState } from "react";
import { uploadMedia, getEventMedia } from "../api/media";

interface Props {
  eventId: string;
}

export default function EventMedia({ eventId }: Props) {
  const [files, setFiles] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);

  async function loadMedia() {
    const data = await getEventMedia(eventId);
    setFiles(data);
  }

  useEffect(() => {
    loadMedia();
  }, [eventId]);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    if (!e.target.files?.length) return;

    setUploading(true);
    await uploadMedia(eventId, e.target.files[0]);
    setUploading(false);
    loadMedia();
  }

  return (
    <div style={{ marginTop: 10 }}>
      <strong>Live from event</strong>

      <div style={{ marginTop: 6 }}>
        <input type="file" onChange={handleUpload} />
        {uploading && <span> Uploading...</span>}
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 10, flexWrap: "wrap" }}>
        {files.map((m) => (
          <img
            key={m.id}
            src={`http://127.0.0.1:8000${m.file_url}`}
            style={{ width: 120, height: 90, objectFit: "cover", borderRadius: 6 }}
          />
        ))}
      </div>
    </div>
  );
}