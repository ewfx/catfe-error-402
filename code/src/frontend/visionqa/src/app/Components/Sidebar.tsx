"use client";
import Link from "next/link";
import { useState } from "react";
import { FiMessageSquare, FiFileText, FiBarChart2 } from "react-icons/fi";
import {
  IoMdArrowDropleftCircle,
  IoMdArrowDroprightCircle,
} from "react-icons/io";

export default function Sidebar() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="flex">
      {/* Sidebar */}
      <div
        className={`h-screen p-6 text-white transition-all flex flex-col
        ${isSidebarOpen ? "w-72" : "w-20"} 
        bg-gradient-to-b from-[#1a172e] via-[#241b3b] to-[#18122b] border-r border-accentDarker`}
      >
        {/* Toggle Button */}
        <button
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="text-white text-3xl mb-6 hover:text-purple-400 transition-all self-end"
        >
          {isSidebarOpen ? (
            <IoMdArrowDropleftCircle />
          ) : (
            <IoMdArrowDroprightCircle />
          )}
        </button>

        {/* Sidebar Title */}
        {isSidebarOpen && (
          <h2 className="text-2xl font-bold text-textPrimary mb-6 font-playfair">
            Quick Access
          </h2>
        )}

        {/* Navigation Links */}
        <nav className="flex flex-col gap-6 text-lg text-textSecondary font-playfair">
          <Link
            href="/chat"
            className="flex items-center gap-3 hover:text-purple-400 transition-all"
          >
            <FiMessageSquare size={22} /> {isSidebarOpen && "Chat with AI"}
          </Link>
          <Link
            href="/summary"
            className="flex items-center gap-3 hover:text-purple-400 transition-all"
          >
            <FiFileText size={22} /> {isSidebarOpen && "Project Summary"}
          </Link>
          <Link
            href="/reports"
            className="flex items-center gap-3 hover:text-purple-400 transition-all"
          >
            <FiBarChart2 size={22} /> {isSidebarOpen && "BDD Reports"}
          </Link>
        </nav>
      </div>
    </div>
  );
}
