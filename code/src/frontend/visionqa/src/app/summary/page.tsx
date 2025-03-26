"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import axios from "axios";
import ReactMarkdown from "react-markdown";

export default function SummaryPage() {
  const [data, setData] = useState(null); // Store summary data
  const [loading, setLoading] = useState(true); // Track loading state
  const [error, setError] = useState(null); // Track errors

  useEffect(() => {
    const fetchData = async () => {
      // Check if summary exists in localStorage
      const cachedSummary = localStorage.getItem("projectSummary");
      if (cachedSummary) {
        console.log("✅ Using cached summary from localStorage.");
        setData(JSON.parse(cachedSummary));
        setLoading(false);
        return;
      }

      console.log("🔄 Fetching summary from API...");
      try {
        const response = await axios.post("http://192.168.1.23:8080/chat", {
          message: `Generate a detailed project summary for my Fraud Detection API with the following structured format:\n\n\
          **Title:** Provide a concise, meaningful title.\n\n\
          **Project Summary:** Give a well-defined overview of the API, explaining its purpose, core functionality, and key features.\n\n\
          **Endpoints:** List the API endpoints in a structured format, including HTTP methods, paths, and their descriptions.\n\n\
          **Sample BDD Test Cases:** Provide at least three well-structured BDD test cases formatted with Given-When-Then statements.\n\n\
          **API Schema:** Define a clear JSON schema including attributes, types, and descriptions.\n\n\
          Ensure that the response is formatted in markdown with proper structuring. Do not include extra explanations outside the summary.`,
          thread_id: "",
        });

        console.log("API Response:", response.data);

        if (response.data && response.data.response) {
          const parsedData = parseResponse(response.data.response);
          setData(parsedData);
          localStorage.setItem("projectSummary", JSON.stringify(parsedData)); // Store in localStorage
        } else {
          setError("Invalid response format.");
        }
      } catch (err) {
        console.error("❌ Fetch Error:", err);
        setError("Failed to load summary.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const clearCache = () => {
    localStorage.removeItem("projectSummary");
    setData(null);
    setLoading(true);
    setError(null);
    window.location.reload();
  };

  return (
    <div className="relative w-full h-screen bg-gradient-to-b from-black via-[#0a021b] to-black flex items-center justify-center font-playfair">
      {/* 🏠 NAVIGATION */}
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
        {/* 🔄 Update Context Button */}

        <Link href="/onboarding">
          <button className="font-playfair ml-16 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-3 rounded-full text-lg font-semibold shadow-lg hover:scale-105 transition-all">
            Get Started
          </button>
        </Link>
      </nav>

      <SummaryDisplay data={data} loading={loading} error={error} />
    </div>
  );
}

// Function to parse the API response into structured sections
const parseResponse = (responseText) => {
  const sections = {};
  const lines = responseText.split("\n");
  let currentSection = "";
  let currentContent = [];

  lines.forEach((line) => {
    if (line.startsWith("**")) {
      // Save the previous section's content
      if (currentSection) {
        sections[currentSection] = currentContent.join("\n").trim();
      }

      // Extract section title and remove bold markdown syntax (**Title**)
      currentSection = line.replace(/\*\*/g, "").trim();
      currentContent = [];
    } else if (currentSection) {
      currentContent.push(line);
    }
  });

  // Save the last section
  if (currentSection) {
    sections[currentSection] = currentContent.join("\n").trim();
  }

  return sections;
};

const SummaryDisplay = ({ data, loading, error }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const updateContext = async () => {
    try {
      setIsSubmitting(true);
      setErrorMessage("");

      // Get URLs from local storage
      const storedLinks = localStorage.getItem("projectLinks");
      const urls = storedLinks ? JSON.parse(storedLinks) : [];

      if (urls.length === 0) {
        setErrorMessage("⚠️ No project links found in local storage.");
        return;
      }

      console.log("📡 Sending embedding request with URLs:", urls);

      const embeddingResponse = await fetch(
        "http://192.168.1.23:8080/post_embeddings",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ urls }),
        }
      );

      if (!embeddingResponse.ok) {
        throw new Error("Failed to process embeddings");
      }

      console.log("✅ Embedding updated successfully!");
      fetchData(); // Refresh summary data after updating embeddings
    } catch (error) {
      setErrorMessage("🚨 Please try again. Some issue in our server.");
    } finally {
      setIsSubmitting(false);
    }
  };
  return (
    <motion.div
      className="bg-[#1e1b2e] p-8 rounded-lg shadow-xl w-[900px] min-h-[600px] flex flex-col justify-between items-center overflow-hidden relative z-20"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex flex-col w-full h-[450px] overflow-y-auto px-4 py-6 space-y-4 scrollbar-thin scrollbar-thumb-transparent scrollbar-track-transparent">
        <button
          onClick={updateContext}
          disabled={isSubmitting}
          className={`bg-green-500 text-white px-2 py-1 rounded-full text-lg font-semibold shadow-lg ${
            isSubmitting
              ? "opacity-50 cursor-not-allowed"
              : "hover:scale-105 transition-all"
          }`}
        >
          {isSubmitting ? "Updating..." : "Update Context"}
        </button>
        {loading ? (
          <div className="flex justify-center items-center h-full">
            <p className="text-white text-xl font-semibold italic opacity-30">
              Processing the data you shared...
            </p>
          </div>
        ) : error ? (
          <div className="flex justify-center items-center h-full">
            <p className="text-red-500 text-xl font-semibold italic opacity-80">
              {error}
            </p>
          </div>
        ) : (
          <div className="text-white text-lg space-y-6">
            {Object.keys(data).map((key, index) => (
              <div key={index}>
                <h2 className="text-2xl font-bold text-purple-400">{key}</h2>
                <pre className="bg-gray-900 text-white p-3 mt-3 rounded-md text-sm overflow-x-auto">
                  <code className="font-mono ">
                    <ReactMarkdown>{data[key]}</ReactMarkdown>
                  </code>
                </pre>
              </div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
};
