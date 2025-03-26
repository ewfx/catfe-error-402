"use client";
import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";

export default function Reports() {
  const [apiDetails, setApiDetails] = useState(null);
  const [bddTests, setBddTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingBDD, setLoadingBDD] = useState(false);
  const [error, setError] = useState(null);
  const [errorBDD, setErrorBDD] = useState(null);
  const [loadingRunTests, setLoadingRunTests] = useState(false);
  const [savedApiDetails, setSavedApiDetails] = useState(null);
  const [sendingBDD, setSendingBDD] = useState(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const [url, setUrl] = useState(null);

  useEffect(() => {
    const storedApiDetails = localStorage.getItem("apiDetails");
    if (storedApiDetails) {
      setApiDetails(JSON.parse(storedApiDetails));
      setLoading(false);
      return;
    }
    const fetchApiDetails = async () => {
      try {
        const response = await fetch("http://192.168.1.17:5000/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message:
              "Extract the base URL and all API endpoints for the 'Fraud Detection API'. Return it in this format: base_url: {base_url}, endpoints: {endpoint1, endpoint2, ...}",
            thread_id: "",
          }),
        });

        const data = await response.json();

        if (data?.response) {
          localStorage.setItem("fullResponse", data.response); // Store full response string
          const parsedData = parseContent(data.response);
          localStorage.setItem("apiDetails", JSON.stringify(parsedData)); // Store parsed JSON
          setApiDetails(parsedData);
        } else {
          throw new Error("Invalid response format");
        }
      } catch (err) {
        setError("Failed to fetch API details.");
      }
      setLoading(false);
    };
    const parseContent = (str) => {
      const baseUrlMatch = str.match(/base_url:\s*(https?:\/\/[^\s]+)/i);
      const base_url = baseUrlMatch ? baseUrlMatch[1] : "";

      const endpointMatches = [...str.matchAll(/\d+\.\s*(\w+)\s+([^\s]+)/g)];
      const endpoints = endpointMatches.map((match) => ({
        method: match[1],
        path: match[2],
      }));

      return { base_url, endpoints };
    };

    fetchApiDetails();
  }, []);

  const handleInputChange = (field, value) => {
    setApiDetails((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const saveApiDetails = () => {
    if (apiDetails) {
      localStorage.setItem("apiDetails", JSON.stringify(apiDetails));
      setSavedApiDetails(apiDetails);
    }
  };

  const handleEndpointChange = (method, value) => {
    setApiDetails((prev) => ({
      ...prev,
      endpoints: {
        ...prev.endpoints,
        [method]: value,
      },
    }));
  };
  const generateBDDTests = async () => {
    setLoadingBDD(true);
    setErrorBDD(null);

    try {
      const apiDetails = JSON.parse(localStorage.getItem("apiDetails"));

      if (!apiDetails || !apiDetails.base_url || !apiDetails.endpoints) {
        throw new Error("API details not found in localStorage.");
      }

      const base_url = apiDetails.base_url.replace(/\/$/, ""); // Remove trailing slash if any
      const endpoints = apiDetails.endpoints.map(
        (endpoint) => `${endpoint.method} ${endpoint.path}`
      );

      const requestBody = {
        endpoints,
        base_url,
        application_name: "Fraud Detection",
      };

      const response = await fetch("http://192.168.1.23:8080/generate_bdd", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) throw new Error("Failed to generate BDD tests.");

      const data = await response.json();
      setBddTests(data.response || []);
    } catch (err) {
      setErrorBDD(err.message);
    } finally {
      setLoadingBDD(false);
    }
  };

  // Function to extract individual test scenarios from Gherkin text
  // const extractTestCases = (gherkinText) => {
  //   const scenarios = gherkinText.split("\nScenario:").slice(1); // Split on 'Scenario:'
  //   return scenarios.map((scenario) => ({
  //     name: "Scenario: " + scenario.split("\n")[0].trim(),
  //     description: scenario.trim(),
  //   }));
  // };

  useEffect(() => {
    if (url) {
      console.log("URL Updated:", url);
      localStorage.setItem("bddTests", bddTests);
    }
  }, [url, bddTests]);

  const runBDDTests = async () => {
    setLoadingRunTests(true);
    setErrorBDD(null);

    try {
      // Retrieve API details from localStorage
      const apiDetails = JSON.parse(localStorage.getItem("apiDetails"));

      if (!apiDetails || !apiDetails.base_url || !apiDetails.endpoints) {
        throw new Error("API details not found in localStorage.");
      }

      // Extract base_url and endpoints from localStorage
      const base_url = apiDetails.base_url.replace(/\/$/, ""); // Remove trailing slash if any
      const endpoints = apiDetails.endpoints.map(
        (endpoint) => `${endpoint.method} ${endpoint.path}`
      );

      if (!bddTests || bddTests.length === 0) {
        throw new Error("No BDD tests available to run.");
      }
      let projectSummary = JSON.parse(localStorage.getItem("projectSummary"));
      console.log(projectSummary);

      let apiSchemaString = projectSummary["API Schema:"];
      const jsonMatch = apiSchemaString.match(/\{[\s\S]*\}/);
      const jsonString = jsonMatch ? jsonMatch[0] : null;

      const requestBody = {
        endpoints,
        base_url,
        application_name: "Fraud Detection",
        bdd_list: bddTests,
        api_schema: jsonString,
      };

      const response = await fetch(
        "http://192.168.1.23:8080/generate_reports",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        }
      );

      const data = await response.json();
      if (!response.ok) throw new Error("Failed to run BDD tests.");

      setUrl(data);
      console.log(url);
    } catch (err) {
      setErrorBDD(err.message);
    } finally {
      setLoadingRunTests(false);
    }
  };

  return (
    <div className="relative w-full h-screen bg-gradient-to-b from-black via-[#0a021b] to-black flex flex-col items-center font-playfair">
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

      <div className="flex w-full h-full p-10 gap-12 mt-24">
        {/* Left Side - API Details */}
        <div className="w-1/3 bg-[#1e1b2e] p-8 rounded-lg shadow-xl">
          <h2 className="text-white text-2xl font-bold mb-4 font-playfair">
            API Details
          </h2>
          {loading ? (
            <div className="text-white italic flex items-center gap-1">
              Loading API details
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
                transition={{ repeat: Infinity, duration: 1, delay: 0.2 }}
              >
                .
              </motion.span>
              <motion.span
                className="dot"
                animate={{ opacity: [0, 1, 0] }}
                transition={{ repeat: Infinity, duration: 1, delay: 0.4 }}
              >
                .
              </motion.span>
            </div>
          ) : error ? (
            <p className="text-red-500">{error}</p>
          ) : (
            <div className="space-y-4">
              <div className="text-white">
                <p className="font-bold">Base URL:</p>
                <input
                  className="mt-2 bg-[#2c2940] text-white p-3 rounded w-full"
                  value={apiDetails?.base_url || "Not available"}
                  onChange={(e) =>
                    handleInputChange("base_url", e.target.value)
                  }
                />
              </div>
              {apiDetails?.endpoints &&
                apiDetails.endpoints.map((endpoint, index) => (
                  <div key={index} className="text-white">
                    <p className="font-bold">{endpoint.method}:</p>
                    <input
                      className="mt-2 bg-[#2c2940] text-white p-3 rounded w-full"
                      value={endpoint.path}
                      onChange={(e) =>
                        handleEndpointChange(index, e.target.value)
                      }
                    />
                  </div>
                ))}
              <p className="!mt-6 text-gray-300 mt-4">
                Please edit your API details and click on <b>Save</b> before
                proceeding to generate BDD.
              </p>
              <button
                onClick={saveApiDetails}
                className="!mt-5 bg-green-500 text-white px-6 py-2 rounded-lg hover:scale-105 transition-all"
              >
                Save Details
              </button>
            </div>
          )}
        </div>

        {/* BDD Reports */}

        {/* BDD Reports */}
        <div className="w-2/3 bg-[#1e1b2e] p-8 rounded-lg shadow-xl">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-white text-2xl font-bold">BDD Reports</h2>
            <button
              onClick={generateBDDTests}
              className={`bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-3 rounded-lg hover:scale-105 transition-all ${
                loadingBDD ? "opacity-50 cursor-not-allowed" : ""
              }`}
              disabled={loadingBDD}
            >
              {loadingBDD ? "Generating..." : "Generate BDD"}
            </button>
          </div>

          {loadingBDD && (
            <p className="text-white italic">Generating BDD reports...</p>
          )}
          {errorBDD && <p className="text-red-500">{errorBDD}</p>}

          {bddTests.length > 0 && (
            <>
              <h3 className="text-white text-xl font-bold mb-2">
                Generated BDD Tests:
              </h3>

              <div className="max-h-[500px] overflow-y-auto space-y-3 pr-2">
                {bddTests.map((test, index) => (
                  <div
                    key={index}
                    className="bg-[#2c2940] p-4 rounded-lg shadow-md"
                  >
                    <div className="p-1 rounded-lg text-white text-sm overflow-x-auto whitespace-pre-wrap">
                      <pre>{test}</pre>
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={runBDDTests}
                className="mt-6 bg-blue-500 text-white px-3 py-3 rounded-lg hover:scale-105 transition-all"
                disabled={loadingRunTests}
              >
                {loadingRunTests ? (
                  <span className="flex items-center space-x-2">
                    <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></span>
                    <span>Running...</span>
                  </span>
                ) : (
                  "Run BDD Tests"
                )}
              </button>

              {url && (
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block mt-4 text-center bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition"
                >
                  View Reports
                </a>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
