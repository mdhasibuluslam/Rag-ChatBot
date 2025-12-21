import React, { useState } from "react";
import FileUpload from "./FileUpload";

const ChatInput = ({ onNewMessage, onUpload }) => {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!text.trim()) return;

    // 🧠 user message
    onNewMessage({ sender: "user", text });

    setLoading(true);
    setText("");

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: text })
      });

      if (!res.ok) {
        const errText = await res.text();
        console.error("/chat error", res.status, errText);
        onNewMessage({ sender: "assistant", text: `Error: ${res.status} ${errText}` });
        setLoading(false);
        return;
      }

      let data = null;
      try {
        data = await res.json();
      } catch (e) {
        console.error("Failed to parse /chat JSON", e);
      }

      const answer = data && data.answer ? data.answer : "(No answer returned)";
      onNewMessage({ sender: "assistant", text: answer });

    } catch (e) {
      console.error("Fetch /chat failed", e);
      onNewMessage({ sender: "assistant", text: `Request failed: ${e.message}` });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-3 space-y-2">

      {/* ✅ FIXED: onUpload passed */}
      <FileUpload onUploadComplete={() => {
        onNewMessage({
          sender: "assistant",
          text: "📄 File uploaded & indexed successfully."
        });
      }} />

      <div className="flex gap-2">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Ask something..."
          className="flex-1 px-4 py-2 rounded-lg bg-slate-800 outline-none"
          onKeyDown={(e) => e.key === "Enter" && submit()}
        />

        <button
          onClick={submit}
          className="px-4 rounded-lg bg-slate-700 hover:bg-slate-600"
          disabled={loading}
        >
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
    </div>
  );
};

export default ChatInput;
