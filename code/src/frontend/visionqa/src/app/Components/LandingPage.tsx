"use client";
import Link from "next/link";
import { motion } from "framer-motion";

export default function LandingPage() {
  return (
    <div className="relative w-full h-screen bg-gradient-to-b from-black via-[#0a021b] to-black flex items-center justify-center font-[Poppins]">
      <nav className="absolute top-0 w-full flex justify-center items-center px-16 py-5 bg-[#100d23] bg-opacity-40 backdrop-blur-lg shadow-lg">
        {/* Logo */}
        <motion.h1
          className="text-white text-3xl font-extrabold tracking-wide font-[Inter] bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mr-20  font-playfair"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1 }}
        >
          VisionQA 🚀
        </motion.h1>

        {/* Navigation Links */}
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

        {/* Get Started Button */}
        <Link href="/onboarding">
          <button className="font-playfair ml-16 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-3 rounded-full text-lg font-semibold shadow-lg hover:scale-105 transition-all">
            Get Started
          </button>
        </Link>
      </nav>

      {/* Hero Section */}
      <div className="flex flex-col items-center text-center px-6">
        <motion.h1
          className="text-white text-5xl font-bold mb-4 font-playfair"
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          AI-Powered Test Case Generation
        </motion.h1>
        <motion.p
          className="mt-4 text-gray-300 text-lg max-w-2xl font-playfair text-justify"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          Automate BDD test case generation using AI. We intelligently extract
          project context from Confluence, Jira, and API documentation, process
          it into structured data, and store it in a high-performance vector
          database. Using LangChain and LLMs, our system dynamically generates
          comprehensive, behavior-driven test cases tailored to your
          application. This ensures higher test coverage, reduced manual effort,
          and improved software quality
        </motion.p>

        <Link href="/onboarding">
          <button className="font-playfair mt-8 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-3 rounded-full text-lg font-semibold shadow-lg hover:scale-105 transition-all">
            Get Started
          </button>
        </Link>
      </div>
    </div>
  );
}
