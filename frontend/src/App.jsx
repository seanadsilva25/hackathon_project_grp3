import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import Heatmap from "./pages/Heatmap";

function Home() {
  const [backendStatus, setBackendStatus] = useState("Checking...");

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/health")
      .then((response) => response.json())
      .then((data) => {
        setBackendStatus(data.message);
      })
      .catch(() => {
        setBackendStatus("Backend connection failed");
      });
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F7F8F4] p-4">
      <div className="text-center p-8 bg-white rounded-2xl border border-gray-200 shadow-xs max-w-md w-full">
        <h1 className="text-3xl font-bold text-[#152937]">
          UniSafe Platform
        </h1>

        <p className="mt-3 text-sm text-gray-600 font-medium">
          Backend Status: <span className="text-[#10B981] font-bold">{backendStatus}</span>
        </p>

        <div className="mt-6 pt-6 border-t border-gray-100">
          <Link
            to="/heatmap"
            className="inline-block px-5 py-2.5 bg-[#1E3A5F] text-white font-semibold text-sm rounded-xl hover:bg-[#152937] transition shadow-xs"
          >
            Open Civic Risk Heatmap →
          </Link>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/heatmap" element={<Heatmap />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;