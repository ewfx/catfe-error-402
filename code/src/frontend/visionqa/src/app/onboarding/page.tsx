"use client";
import { motion } from "framer-motion";
import { useState } from "react";
import Link from "next/link";
import Typewriter from "typewriter-effect";
import Lottie from "lottie-react";
import successAnimation from "@/app/public/assets/success.json";

export default function Onboarding() {
  const [step, setStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [submitted, setSubmitted] = useState(false); // Track if the form is submitted
  const [formData, setFormData] = useState({
    projectName: "",
    projectLinks: [],
    description: "",
    files: [] as File[],
  });
  const [url, setUrl] = useState("");

  const questions = [
    { text: "Hey there! What's your project called?", field: "projectName" },
    {
      text: "Cool! Share any relevant links (Jira, GitHub, etc.)",
      field: "projectLinks",
    },
    {
      text: "Nice! Upload any images or documents if needed.",
      field: "files",
      type: "file",
    },
    {
      text: "Almost done! Briefly describe your project.",
      field: "description",
    },
  ];

  const handleAddUrl = () => {
    if (url.trim() && !formData.projectLinks.includes(url.trim())) {
      const updatedLinks = [...formData.projectLinks, url.trim()];

      setFormData((prev) => ({
        ...prev,
        projectLinks: updatedLinks,
      }));

      localStorage.setItem("projectLinks", JSON.stringify(updatedLinks));
      setUrl("");
    }
  };

  const handleRemoveUrl = (index: number) => {
    const updatedLinks = formData.projectLinks.filter((_, i) => i !== index);

    setFormData((prev) => ({
      ...prev,
      projectLinks: updatedLinks,
    }));

    localStorage.setItem("projectLinks", JSON.stringify(updatedLinks));
  };
  const isStepValid = () => {
    const field = questions[step].field;
    return field === "files"
      ? formData.files.length > 0
      : Boolean(formData[field]);
  };

  const handleNextStep = () => {
    if (isStepValid() && step < questions.length - 1) setStep(step + 1);
  };

  const handleChange = (e: any) => {
    const { name, value, files } = e.target;
    if (name === "files") {
      setFormData((prev) => ({ ...prev, files: Array.from(files) }));
    } else {
      setFormData((prev) => {
        const updatedForm = { ...prev, [name]: value };

        // Save projectName in localStorage
        if (name === "projectName") {
          localStorage.setItem("projectName", value);
        }

        return updatedForm;
      });
    }
  };

  const handleSubmit = async () => {
    localStorage.setItem("update", url);
    if (!formData.projectName || !formData.description) {
      alert("Please fill in all fields!");
      return;
    }
    setIsSubmitting(true);
    setErrorMessage("");

    const data = new FormData();
    data.append("projectName", formData.projectName);
    data.append("description", formData.description);
    formData.files.forEach((file) => data.append("file", file));

    // Ensure projectLinks is an array before appending
    if (Array.isArray(formData.projectLinks)) {
      formData.projectLinks.forEach((link) =>
        data.append("projectLinks", link)
      );
    }

    try {
      // Step 1: Upload Project Data to S3
      const response = await fetch("http://192.168.1.5:8001/upload/", {
        method: "POST",
        body: data,
      });

      if (!response.ok)
        throw new Error(`HTTP error! Status: ${response.status}`);

      await response.json();
      setSubmitted(true);

      // Step 2: Call /post_embeddings with projectLinks
      if (
        Array.isArray(formData.projectLinks) &&
        formData.projectLinks.length > 0
      ) {
        const embeddingResponse = await fetch(
          "http://192.168.1.23:8080/post_embeddings",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ urls: formData.projectLinks }),
          }
        );

        if (!embeddingResponse.ok) {
          throw new Error("Failed to process embeddings");
        }
      }
    } catch (error) {
      setErrorMessage("🚨 Please try again. Some issue in our server.");
    } finally {
      setIsSubmitting(false);
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
      {/* Onboarding Box */}
      <motion.div
        className="bg-[#1e1b2e] p-12 rounded-lg shadow-xl w-[600px] min-h-[400px] text-center flex flex-col justify-center items-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {!submitted ? (
          <>
            <h2 className="text-white text-3xl font-bold mb-6">
              🚀 AI Chat Onboarding
            </h2>
            <p className="text-gray-300 text-lg font-medium mb-6 h-10 flex items-center justify-center">
              <Typewriter
                options={{
                  strings: questions[step].text,
                  autoStart: true,
                  delay: 40,
                }}
              />
            </p>
            {step === 1 ? (
              <>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="w-full p-3 rounded bg-[#2c2940] text-white border"
                  placeholder="Enter a URL..."
                />
                <button
                  onClick={handleAddUrl}
                  className="mt-4 bg-purple-500 text-white px-4 py-2 rounded"
                >
                  Add URL
                </button>
                {formData.projectLinks && formData.projectLinks.length > 0 && (
                  <pre className="mt-4 w-full overflow-x-auto bg-[#2c2940] p-2 rounded text-white">
                    {formData.projectLinks &&
                      formData.projectLinks.map((link, index) => (
                        <div
                          key={index}
                          className="flex justify-between items-center"
                        >
                          <code>{link}</code>
                          <button
                            onClick={() => handleRemoveUrl(index)}
                            className="text-red-500"
                          >
                            ❌
                          </button>
                        </div>
                      ))}
                  </pre>
                )}
              </>
            ) : (
              <input
                type={questions[step].type === "file" ? "file" : "text"}
                name={questions[step].field}
                onChange={handleChange}
                className="w-full p-3 rounded bg-[#2c2940] text-white border"
                placeholder="Type your answer..."
              />
            )}
            <button
              onClick={
                step < questions.length - 1 ? handleNextStep : handleSubmit
              }
              disabled={!isStepValid()}
              className="mt-5 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-7 py-2 rounded-lg"
            >
              {step < questions.length - 1 ? "Next" : "Submit"}
            </button>
          </>
        ) : (
          <>
            <Lottie
              animationData={successAnimation}
              style={{ width: 200, height: 200 }}
            />
            <p className="text-white text-lg mt-4">🎉 Project onboarded!</p>
          </>
        )}
      </motion.div>
    </div>
  );
}
