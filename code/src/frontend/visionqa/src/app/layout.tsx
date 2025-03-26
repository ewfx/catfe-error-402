import Sidebar from "@/app/components/Sidebar";
import Footer from "@/app/components/Footer";
import { Metadata } from "next";
import Navbar from "@/app/components/Navbar";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: "VisionQA",
  description:
    "Welcome to VisionQA – Empowering Your Application with AI-Driven BDD Test Case Generation.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-white min-h-screen flex flex-col">
        {/* Page Content: Sidebar + Main Content */}
        <div className="flex flex-1 h-screen">
          {/* Sidebar - Stays on the left */}
          <Sidebar />

          {/* Main Content (Takes Remaining Space) */}
          <main className="flex-1 overflow-auto">{children}</main>
        </div>

        {/* Footer at the bottom */}
        <Footer />
      </body>
    </html>
  );
}
