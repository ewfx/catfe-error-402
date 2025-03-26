"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  FaRobot,
  FaChartBar,
  FaCloudUploadAlt,
  FaBug,
  FaCodeBranch,
  FaDocker,
} from "react-icons/fa";

export default function about() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-[#0a021b] to-black text-white font-playfair">
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

      {/* Hero Section */}
      <motion.div
        className="flex flex-col items-center justify-center text-center py-32"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        <h1 className="text-5xl font-extrabold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          About VisionQA
        </h1>
        <p className="text-gray-300 text-lg mt-4 w-3/5">
          VisionQA is an AI-powered Context-aware testing system that automates
          API testing, integrates with Confluence, Jira, and GitHub, and ensures
          seamless software quality.
        </p>
      </motion.div>

      {/* Features Section */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10 px-16 py-12"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1.2 }}
      >
        {/* Feature Cards */}
        {features.map((feature, index) => (
          <motion.div
            key={index}
            className="bg-[#1e1b2e] p-6 rounded-2xl shadow-lg border border-gray-700 hover:scale-105 transition-all cursor-pointer h-56 flex flex-col justify-between"
            whileHover={{ scale: 1.05 }}
          >
            <feature.icon className="text-4xl text-purple-400 mb-4" />
            <h3 className="text-xl font-semibold">{feature.title}</h3>
            <p className="text-gray-400 mt-2">{feature.description}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* Team Section */}
      <div className="text-center py-24">
        <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          Meet Our Team
        </h2>
        <p className="text-gray-300 mt-4">The minds behind VisionQA 🚀</p>

        <div className="flex flex-wrap justify-center gap-12 mt-12">
          {team.map((member, index) => (
            <motion.div
              key={index}
              className="bg-[#2c2940] p-6 rounded-lg shadow-md text-center border border-gray-700 w-72"
              whileHover={{ scale: 1.05 }}
            >
              <img
                src={member.image}
                alt={member.name}
                className="w-24 h-24 bg-purple-500 rounded-full mx-auto mb-4"
              />

              <h3 className="text-lg font-semibold">{member.name}</h3>
              <p className="text-gray-400 text-sm">{member.role}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center py-8 text-gray-500 text-sm">
        &copy; {new Date().getFullYear()} VisionQA. All rights reserved.
      </footer>
    </div>
  );
}

/* Feature Data */
const features = [
  {
    title: "AI-Powered Testing",
    description:
      "Uses Llama 3.1 with Groq Cloud for smart, context-aware testing.",
    icon: FaRobot,
  },
  {
    title: "Automated API Testing",
    description:
      "Fetches API schema, validates endpoints, and executes BDD tests.",
    icon: FaBug,
  },
  {
    title: "Seamless Integrations",
    description:
      "Connects with Jira, GitHub, and Confluence for better project tracking.",
    icon: FaChartBar,
  },
  {
    title: "Cloud Storage",
    description:
      "Securely stores project-related files and metadata in AWS S3.",
    icon: FaCloudUploadAlt,
  },
  {
    title: "LangChain & LangGraph",
    description:
      "Enhancing AI workflows with dynamic execution graphs and modular components.",
    icon: FaCodeBranch,
  },
  {
    title: "Dockerized Deployment",
    description:
      "Fully containerized environment for seamless CI/CD and test execution.",
    icon: FaDocker,
  },
];

/* Team Data */
const team = [
  {
    name: "Pratham Bist",
    role: "Frontend Designer & AI Engineer",
    image: "/assets/pratham.jpg",
  },
  {
    name: "Atishay Patni",
    role: "Backend Developer & AI Engineer",
    image: "/assets/atishay.jpg",
  },
  {
    name: "Pranav Sharma",
    role: "Backend Designer & AI Engineer",
    image: "/assets/pranav.jpg",
  },
];
