import React, { useEffect, useRef } from "react";

const ChatWindow = ({ messages, typing }) => {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  return (
    <div className="h-[65vh] overflow-y-auto p-3 mb-2">
      {messages.map((msg, i) => (
        <div
          key={i}
          className={`my-2 flex ${
            msg.sender === "user" ? "justify-end" : "justify-start"
          } animate-[slideUp_0.3s_ease-out]`}
        >
          <div
            className={`px-4 py-2 rounded-xl max-w-[70%] text-sm
            ${
              msg.sender === "user"
                ? "bg-cyan-400 text-black shadow-[0_0_15px_#22d3ee]"
                : "bg-purple-600 text-white shadow-[0_0_15px_#a855f7]"
            }`}
          >
            {msg.text}
          </div>
        </div>
      ))}

      {typing && (
        <div className="text-purple-400 animate-pulse">
          AI is typing...
        </div>
      )}

      <div ref={endRef}></div>
    </div>
  );
};

export default ChatWindow;
