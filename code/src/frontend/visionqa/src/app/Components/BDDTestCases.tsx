"use client";
import { motion } from "framer-motion";

export default function BDDTestCases() {
  return (
    <motion.div
      className="w-full bg-gray-800 p-5 rounded-lg shadow-lg"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-xl font-semibold text-yellow-400">
        BDD Test Cases 📝
      </h2>
      <ul className="list-disc list-inside text-gray-300 mt-3">
        <li>✅ Fraud Detection for High-Value Transactions</li>
        <li>✅ Fraud Score Calculation</li>
        <li>✅ Alert Generation Mechanism</li>
        <li>✅ User Behavior Analysis</li>
      </ul>
    </motion.div>
  );
}
