import { useState, useRef, useEffect } from "react";
import { sendChat } from "../api/chat";
import type { ChatResponse } from "../types/recommendation";

interface Props {
  onResults: (response: ChatResponse) => void;
  onLoading: (loading: boolean) => void;
}

const SUGGESTIONS = [
  "Free music events this weekend",
  "Tech meetups in Nairobi under KES 500",
  "Outdoor sports events near me",
  "Food festivals happening soon",
  "Comedy shows this month",
  "Business networking events",
];

export default function ChatBox({ onResults, onLoading }: Props) {
  const [message, setMessage] = useState("");
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [locating, setLocating] = useState(false);
  const [history, setHistory] = useState<{ role: "user" | "bot"; text: string }[]>([]);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const historyRef = useRef<HTMLDivElement>(null);

  // Auto-detect location silently on mount
  useEffect(() => {
    if (!navigator.geolocation) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setLocating(false);
      },
      () => setLocating(false),
      { timeout: 8000 }
    );
  }, []);

  // Scroll chat history to bottom
  useEffect(() => {
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [history]);

  async function handleSend(text?: string) {
    const query = (text ?? message).trim();
    if (!query) return;

    setMessage("");
    setError(null);
    setHistory((prev) => [...prev, { role: "user", text: query }]);
    onLoading(true);

    try {
      const response = await sendChat(
        query,
        userLocation?.lat ?? null,
        userLocation?.lng ?? null
      );

      if (response.needs_clarification && response.question) {
        setHistory((prev) => [...prev, { role: "bot", text: response.question! }]);
      } else {
        const count = response.results?.length ?? 0;
        const botMsg = count > 0
          ? `Found ${count} event${count !== 1 ? "s" : ""} matching your search.`
          : "No events found matching that. Try different keywords or broaden your search.";
        setHistory((prev) => [...prev, { role: "bot", text: botMsg }]);
        onResults(response);
      }
    } catch (err: any) {
      const msg = "Something went wrong. Please try again.";
      setError(msg);
      setHistory((prev) => [...prev, { role: "bot", text: msg }]);
    } finally {
      onLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chatbox-wrapper">
      {/* Location indicator */}
      <div className="chatbox-location">
        {locating ? (
          <span className="loc-detecting">⟳ Detecting location...</span>
        ) : userLocation ? (
          <span className="loc-found">📍 Location detected</span>
        ) : (
          <span className="loc-missing">📍 Location unavailable — results near Nairobi</span>
        )}
      </div>

      {/* Chat history */}
      {history.length > 0 && (
        <div className="chatbox-history" ref={historyRef}>
          {history.map((msg, i) => (
            <div key={i} className={`chat-bubble chat-bubble--${msg.role}`}>
              {msg.text}
            </div>
          ))}
        </div>
      )}

      {/* Suggestions */}
      {history.length === 0 && (
        <div className="chatbox-suggestions">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              className="suggestion-chip"
              onClick={() => handleSend(s)}
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="chatbox-input-row">
        <input
          ref={inputRef}
          className="chatbox-input"
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g. cheap music events near me this weekend..."
          autoComplete="off"
        />
        <button
          className="chatbox-send"
          onClick={() => handleSend()}
          disabled={!message.trim()}
        >
          ↑
        </button>
      </div>

      {error && <div className="chatbox-error">{error}</div>}
    </div>
  );
}
