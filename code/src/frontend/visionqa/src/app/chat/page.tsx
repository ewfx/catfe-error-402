"use client";
import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { FiSend } from "react-icons/fi";

export default function ChatWithAI() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<{ user: string; ai: string }[]>(
    () => {
      // Get stored chat history from localStorage (if exists)
      const storedMessages = localStorage.getItem("chat_history");
      return storedMessages ? JSON.parse(storedMessages) : []; // Parse or return empty array
    }
  );

  const [loading, setLoading] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const storedMessages = localStorage.getItem("chat_history");
    if (storedMessages) {
      setMessages(JSON.parse(storedMessages));
    }
  }, []);

  useEffect(() => {
    chatContainerRef.current?.scrollTo(
      0,
      chatContainerRef.current.scrollHeight
    );

    // 🔹 Store messages in localStorage whenever they change
    localStorage.setItem("chat_history", JSON.stringify(messages));
  }, [messages]);

  const handleSendMessage = async () => {
    if (!message.trim()) return;
    setLoading(true);

    const storedThreadId = localStorage.getItem("thread_id_chat");

    // Store user message immediately in chat
    setMessages((prev) => [...prev, { user: message, ai: "..." }]);
    setMessage("");

    try {
      const response = await fetch("http://192.168.1.23:8080/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message,
          thread_id: storedThreadId || undefined,
        }),
      });

      // ✅ FIX: Parse the response correctly
      const data = await response.json(); // <-- This is missing in your code

      const aiResponse = (() => {
        try {
          const parsedResponse = data.response; // Ensure it's properly parsed
          return parsedResponse || "No response received";
        } catch (error) {
          console.error("Error parsing AI response:", error);
          return "Error parsing response.";
        }
      })();

      const threadId = data?.thread_id;

      if (threadId && !storedThreadId) {
        localStorage.setItem("thread_id_chat", threadId);
      }

      setMessages((prev) =>
        prev.map((msg, index) =>
          index === prev.length - 1 ? { ...msg, ai: aiResponse } : msg
        )
      );
    } catch (error) {
      console.error("Error fetching AI response:", error);
      setMessages((prev) =>
        prev.map((msg, index) =>
          index === prev.length - 1
            ? { ...msg, ai: "Error retrieving response. Try again." }
            : msg
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const formatResponse = (text: string) => {
    return text.split("\n").map((line, index) => (
      <p
        key={index}
        dangerouslySetInnerHTML={{
          __html: line.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"),
        }}
      />
    ));
  };

  // Handle enter key press
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault(); // Prevent new line in input field
      handleSendMessage();
    }
  };

  return (
    <div className="relative w-full h-screen bg-gradient-to-b from-black via-[#0a021b] to-black flex items-center justify-center font-playfair">
      {/* Navbar */}
      <nav className="absolute top-0 w-full flex justify-center items-center px-16 py-5 bg-[#100d23] bg-opacity-40 backdrop-blur-lg shadow-lg">
        <motion.h1
          className="text-white text-3xl font-extrabold tracking-wide font-[Inter] bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mr-20 font-playfair"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1 }}
        >
          <Link href="/">VisionQA 🚀</Link>
        </motion.h1>

        <div className="ml-30 flex gap-12 text-white font-semibold text-lg font-playfair">
          <Link
            href="/features"
            className="text-xl hover:text-purple-400 transition-all"
          >
            Features
          </Link>
          <Link
            href="/pricing"
            className="text-xl hover:text-purple-400 transition-all"
          >
            Pricing
          </Link>
          <Link
            href="/about"
            className="text-xl hover:text-purple-400 transition-all"
          >
            About
          </Link>
        </div>

        <Link href="/onboarding">
          <button className="font-playfair ml-16 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-3 rounded-full text-lg font-semibold shadow-lg hover:scale-105 transition-all">
            Get Started
          </button>
        </Link>
      </nav>

      {/* Chat Window */}
      <motion.div
        className="bg-[#1e1b2e] p-10 rounded-lg shadow-xl w-[900px] min-h-[600px] flex flex-col justify-between items-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div
          ref={chatContainerRef}
          className="flex flex-col w-full h-[450px] overflow-y-auto px-4 py-6 space-y-4 scrollbar-thin scrollbar-thumb-transparent scrollbar-track-transparent"
        >
          {messages.length === 0 ? (
            <div className="flex justify-center items-center h-full">
              <p className="text-white text-xl font-semibold italic opacity-30">
                Start the conversation with AI! Ask Project Related Questions!
              </p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className="flex flex-col space-y-2">
                <div className="flex flex-row-reverse space-x-2 space-x-reverse">
                  <p className="text-white p-3 bg-purple-500 rounded-lg text-m">
                    {msg.user}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <p className="text-white p-3 bg-gray-700 rounded-lg text-m">
                    {loading && index === messages.length - 1 ? (
                      <div className="text-white italic flex items-center gap-1">
                        Generating Response
                        <motion.span
                          className="dot"
                          animate={{ opacity: [0, 1, 0] }}
                          transition={{ repeat: Infinity, duration: 1 }}
                        >
                          .
                        </motion.span>
                        <motion.span
                          className="dot"
                          animate={{ opacity: [0, 1, 0] }}
                          transition={{
                            repeat: Infinity,
                            duration: 1,
                            delay: 0.2,
                          }}
                        >
                          .
                        </motion.span>
                        <motion.span
                          className="dot"
                          animate={{ opacity: [0, 1, 0] }}
                          transition={{
                            repeat: Infinity,
                            duration: 1,
                            delay: 0.4,
                          }}
                        >
                          .
                        </motion.span>
                      </div>
                    ) : (
                      <p className="text-white p-3 bg-gray-700 rounded-lg text-m">
                        {formatResponse(msg.ai)}
                      </p>
                    )}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="flex items-center justify-between w-full mt-4">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
            placeholder="Type your message here..."
            className="w-full p-3 rounded bg-[#2c2940] text-white border border-gray-500"
          />
          <button
            onClick={handleSendMessage}
            className="ml-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-3 rounded-lg hover:scale-105 transition-all"
            disabled={loading}
          >
            <FiSend size={20} />
          </button>
        </div>
      </motion.div>
    </div>
  );
}
