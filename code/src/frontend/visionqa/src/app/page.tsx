import Navbar from "@/app/components/Navbar";
import Sidebar from "@/app/components/Sidebar";
import Footer from "@/app/components/Footer";
import LandingPage from "@/app/components/LandingPage";
import Head from "next/head";

export default function Home() {
  return (
    <div className="flex-1">
      <LandingPage />
    </div>
  );
}
