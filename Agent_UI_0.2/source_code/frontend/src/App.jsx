import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ ChatWindow";
import ChatInput from "./components/ ChatInput";

const newChat = () => ({
  id: Date.now(),
  title: "New Chat",
  messages: [
    { sender: "assistant", text: "Hello 👋 How can I help?" }
  ],
  files: []
});

export default function App() {
  const [chats, setChats] = useState([newChat()]);
  const [activeId, setActiveId] = useState(chats[0].id);

  const activeChat = chats.find(c => c.id === activeId);

  // ✅ MESSAGE ADD HANDLER
  const addMessage = (msg) => {
    setChats(prev =>
      prev.map(c =>
        c.id === activeId
          ? { ...c, messages: [...c.messages, msg] }
          : c
      )
    );
  };

  // ✅ FILE UPLOAD HANDLER (UI only)
  const addFiles = (files) => {
    setChats(prev =>
      prev.map(c =>
        c.id === activeId
          ? { ...c, files: [...c.files, ...files] }
          : c
      )
    );
  };

  return (
    <div className="flex h-screen">
      <Sidebar
        chats={chats}
        activeChatId={activeId}
        onNewChat={() => {
          const c = newChat();
          setChats([c, ...chats]);
          setActiveId(c.id);
        }}
        onSelectChat={setActiveId}
        onDeleteChat={(id) =>
          setChats(chats.filter(c => c.id !== id))
        }
      />

      <div className="flex-1 p-6">
        <ChatWindow messages={activeChat.messages} />

        {/* 🔥 IMPORTANT FIX */}
        <ChatInput
          onNewMessage={addMessage}
          onUpload={addFiles}
        />
      </div>
    </div>
  );
}
