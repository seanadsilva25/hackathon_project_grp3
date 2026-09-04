import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import { supabase } from "./services/supabase";

import Auth9Demo from "./screens/signup-login/demo";
import Hero2Demo from "./screens/home/demo";
import KanbanBoard from "./screens/kanban-board/KanbanBoard";
import InteractiveMap from "./screens/interactive-map/InteractiveMap";
import ResolutionVerification from "./screens/verification/ResolutionVerification";
import VerificationHub from "./screens/verification/VerificationHub";

function Home({ user }) {
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

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-gradient-to-b from-slate-50 to-slate-100/60 font-sans">
      <div className="max-w-md w-full bg-white p-8 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 text-center">
        
        {/* User Status Bar */}
        {user && (
          <div className="mb-6 p-3 bg-blue-50 rounded-xl border border-blue-100 flex items-center justify-between">
            <div className="text-left">
              <p className="text-xs text-blue-500 font-semibold uppercase tracking-wider">Logged In As</p>
              <p className="text-sm font-bold text-blue-900">{user.user_metadata?.role_type || 'User'}</p>
            </div>
            <button onClick={handleLogout} className="text-xs bg-white text-slate-600 px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm hover:bg-slate-50">
              Sign Out
            </button>
          </div>
        )}

        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-xs font-semibold text-blue-600 mb-4">
          <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
          Group 3 Workspace
        </div>

        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          Hackathon Project
        </h1>

        <p className="mt-2 text-sm text-slate-500 flex items-center justify-center gap-2">
          <span>Backend Status:</span>
          <span className={`font-semibold px-2.5 py-0.5 rounded-full text-xs ${backendStatus === "Checking..." ? "bg-amber-50 text-amber-600" : backendStatus.includes("failed") ? "bg-rose-50 text-rose-600" : "bg-emerald-50 text-emerald-600"}`}>
            {backendStatus}
          </span>
        </p>

        <div className="mt-8 pt-6 border-t border-slate-100 flex flex-col gap-3">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400 text-left">Screens & Demos</p>

          <Link
            to="/auth"
            className="group flex items-center justify-between p-3.5 rounded-2xl border border-slate-200/80 bg-white hover:border-blue-300 hover:shadow-md hover:shadow-blue-500/5 transition-all text-left"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold text-lg shadow-sm">
                W
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">Watermelon Auth</h3>
                <p className="text-xs text-slate-500">Sign Up / Login Screen (Auth9)</p>
              </div>
            </div>
            <span className="text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all text-sm font-bold">→</span>
          </Link>

          <Link
            to="/kanban"
            className="group flex items-center justify-between p-3.5 rounded-2xl border border-slate-200/80 bg-white hover:border-slate-400 hover:shadow-md hover:shadow-slate-900/5 transition-all text-left"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-slate-900 text-white flex items-center justify-center font-bold text-sm shadow-sm">
                📋
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-900 group-hover:text-slate-700 transition-colors">Kanban Board</h3>
                <p className="text-xs text-slate-500">Drag & Drop project board</p>
              </div>
            </div>
            <span className="text-slate-400 group-hover:text-slate-900 group-hover:translate-x-0.5 transition-all text-sm font-bold">→</span>
          </Link>

          <Link
            to="/map"
            className="group flex items-center justify-between p-3.5 rounded-2xl border border-slate-200/80 bg-white hover:border-emerald-400 hover:shadow-md hover:shadow-emerald-500/5 transition-all text-left"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-sm shadow-sm">
                🗺️
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-900 group-hover:text-emerald-600 transition-colors">Interactive Map</h3>
                <p className="text-xs text-slate-500">Leaflet issue reporting map</p>
              </div>
            </div>
            <span className="text-slate-400 group-hover:text-emerald-600 group-hover:translate-x-0.5 transition-all text-sm font-bold">→</span>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAndApplyPendingRole = async (currentSession) => {
    if (!currentSession?.user) return;

    const pendingRole = localStorage.getItem('pending_auth_role');
    
    // Only update if there's pending metadata to apply
    if (pendingRole) {
      const updates = {
        role_type: pendingRole
      };

      if (pendingRole === 'authority') {
        updates.department = localStorage.getItem('pending_auth_dept');
        updates.jurisdiction = localStorage.getItem('pending_auth_jurisdiction');
        updates.job_role = localStorage.getItem('pending_auth_job');
      }

      console.log("Applying pending auth data to user metadata:", updates);
      
      const { error } = await supabase.auth.updateUser({
        data: updates
      });

      if (!error) {
        // Clean up local storage once successfully applied
        localStorage.removeItem('pending_auth_role');
        localStorage.removeItem('pending_auth_dept');
        localStorage.removeItem('pending_auth_jurisdiction');
        localStorage.removeItem('pending_auth_job');
        console.log("Successfully applied metadata!");
      } else {
        console.error("Failed to update user metadata:", error);
      }
    }
  };

  useEffect(() => {
    // 1. Check active session on load
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      checkAndApplyPendingRole(session);
      setLoading(false);
    });

    // 2. Listen to login/logout events
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      checkAndApplyPendingRole(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-500 font-sans">Loading App...</div>;
  }

  // Define a simple ProtectedRoute component
  const ProtectedRoute = ({ children }) => {
    if (!session) {
      return <Navigate to="/auth" replace />;
    }
    return children;
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Hero2Demo />} />
        <Route path="/status" element={<Home user={session?.user} />} />
        <Route path="/home" element={<Hero2Demo />} />
        
        {/* Auth Routes */}
        <Route path="/auth" element={session ? <Navigate to="/status" replace /> : <Auth9Demo />} />
        <Route path="/login" element={session ? <Navigate to="/status" replace /> : <Auth9Demo />} />
        <Route path="/signup" element={session ? <Navigate to="/status" replace /> : <Auth9Demo />} />
        
        {/* Protected Routes (You can wrap these when ready, keeping them unprotected for easy testing during hackathon unless you want them protected now) */}
        <Route path="/kanban" element={<KanbanBoard />} />
        <Route path="/map" element={<InteractiveMap />} />
        <Route path="/verify" element={<VerificationHub />} />
        <Route path="/verify/:id" element={<ResolutionVerification />} />
      </Routes>
    </BrowserRouter>
  );
}