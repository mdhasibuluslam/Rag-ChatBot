import React from "react";

const Sidebar = ({ chats, activeChatId, onNewChat, onSelectChat }) => {
  return (
    <div className="
      w-64 h-full p-3
      border-r border-cyan-500
      bg-black/80
      shadow-[0_0_20px_#22d3ee]
      flex flex-col
    ">
      <button
        onClick={onNewChat}
        className="
          mb-4 py-2 rounded-lg font-bold
          bg-gradient-to-r from-cyan-400 to-purple-600
          text-black
          shadow-[0_0_15px_#22d3ee]
          hover:scale-105 transition
        "
      >
        ➕ New Chat
      </button>

      <div className="flex-1 overflow-y-auto space-y-2">
        {chats.map(chat => (
          <div
            key={chat.id}
            onClick={() => onSelectChat(chat.id)}
            className={`
              cursor-pointer px-3 py-2 rounded-lg text-sm
              ${
                chat.id === activeChatId
                  ? "bg-cyan-500 text-black shadow-[0_0_10px_#22d3ee]"
                  : "bg-gray-800 text-gray-300 hover:bg-gray-700"
              }
            `}
          >
            💬 {chat.title}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
