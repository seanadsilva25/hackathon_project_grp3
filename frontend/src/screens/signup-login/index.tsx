import React, { useState } from "react";
import { motion, type Variants } from "motion/react";
import { supabase } from "../../services/supabase";

// Arrow Icon matching Hugeicons ArrowLeft01Icon
const ArrowLeft01Icon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg
    viewBox="0 0 24 24"
    width="1em"
    height="1em"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    <path d="M19 12H5M12 19l-7-7 7-7" />
  </svg>
);

const HugeiconsIcon = ({
  icon: Icon = ArrowLeft01Icon,
  className = "size-4",
}: {
  icon?: any;
  className?: string;
}) => {
  if (typeof Icon === "function") {
    const Component = Icon;
    return <Component className={className} />;
  }
  return <ArrowLeft01Icon className={className} />;
};

// Simple Google SVG Icon
const GoogleIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" width="1em" height="1em" {...props}>
    <path
      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      fill="#4285F4"
    />
    <path
      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.16v2.84C3.99 20.53 7.7 23 12 23z"
      fill="#34A853"
    />
    <path
      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.16C1.43 8.55 1 10.22 1 12s.43 3.45 1.16 4.93l3.68-2.84z"
      fill="#FBBC05"
    />
    <path
      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.16 7.07l3.68 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
      fill="#EA4335"
    />
  </svg>
);

export default function Auth9() {
  const location = window.location;
  const urlParams = new URLSearchParams(location.search);
  const initialRole = urlParams.get("role") as "citizen" | "authority" | null;

  const [step, setStep] = useState(initialRole ? 2 : 1);
  const [role, setRole] = useState<"citizen" | "authority" | null>(initialRole);
  
  // Authority details
  const [department, setDepartment] = useState("");
  const [jurisdiction, setJurisdiction] = useState("");
  const [authorityRole, setAuthorityRole] = useState("");

  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 15 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 24,
      },
    },
  };

  const handleGoogleLogin = async () => {
    // Save pending role data to localStorage before redirect
    localStorage.setItem("pending_auth_role", role || "citizen");
    if (role === "authority") {
      localStorage.setItem("pending_auth_details", JSON.stringify({
        department,
        jurisdiction,
        authorityRole
      }));
    }

    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: window.location.origin + "/status"
      }
    });

    if (error) {
      console.error("Error logging in:", error.message);
      alert("Failed to initiate Google login");
    }
  };

  return (
    <div className="flex min-h-screen w-full flex-col bg-white font-sans text-neutral-950 antialiased selection:bg-blue-500/30 selection:text-neutral-900 lg:flex-row">
      {/* Left Image Panel */}
      <div className="relative flex w-full flex-col justify-between overflow-hidden p-8 md:p-12 lg:w-1/2 min-h-[420px] lg:min-h-screen shrink-0">
        <img
          src="https://assets.watermelon.sh/auth-9.avif"
          alt="Abstract blue background"
          className="absolute inset-0 h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-black/40 pointer-events-none" />

        <div className="relative z-10 flex items-center justify-between">
          <span className="text-xl lg:text-2xl font-bold tracking-tight text-white drop-shadow-sm">
            Hackathon
          </span>

          <a
            href="/"
            className="flex items-center gap-2 text-xs md:text-sm font-medium text-white/95 transition-all hover:text-white bg-white/15 hover:bg-white/25 backdrop-blur-md px-4 py-2 rounded-full border border-white/20 shadow-sm"
          >
            <HugeiconsIcon icon={ArrowLeft01Icon} className="size-4" />
            Back to Home
          </a>
        </div>

        <div className="relative z-10 mt-12 lg:mt-0 pb-4">
          <h1 className="mb-4 max-w-xl text-3xl font-semibold leading-[1.15] tracking-tight text-white sm:text-4xl lg:text-5xl drop-shadow-md">
            Join the <br /> Civic Platform
          </h1>
          <p className="max-w-md text-sm md:text-base leading-relaxed text-white/90 drop-shadow-sm">
            Report issues, track resolutions, and collaborate with authorities for a better community.
          </p>
        </div>
      </div>

      {/* Right Form Panel */}
      <div className="flex w-full flex-1 flex-col items-center justify-center p-6 sm:p-12 lg:p-16 lg:w-1/2 min-h-screen">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="w-full max-w-md md:max-w-lg xl:max-w-xl my-auto"
        >
          {step === 1 && (
            <>
              <motion.div variants={itemVariants} className="mb-6">
                <h2 className="mb-2 text-3xl md:text-4xl font-semibold tracking-tight text-neutral-900">
                  Welcome
                </h2>
                <p className="text-sm md:text-base text-neutral-500">
                  Select your role to continue
                </p>
              </motion.div>
              
              <motion.div variants={itemVariants} className="flex flex-col gap-4">
                <button
                  onClick={() => { setRole("citizen"); setStep(2); }}
                  className="flex w-full flex-col items-start gap-2 rounded-xl border border-neutral-200 bg-white p-6 text-left transition-all hover:border-blue-500 hover:bg-blue-50 hover:shadow-md cursor-pointer"
                >
                  <h3 className="text-lg font-semibold text-neutral-900">I am a Citizen</h3>
                  <p className="text-sm text-neutral-500">Report issues and track their resolution status in your area.</p>
                </button>
                
                <button
                  onClick={() => { setRole("authority"); setStep(2); }}
                  className="flex w-full flex-col items-start gap-2 rounded-xl border border-neutral-200 bg-white p-6 text-left transition-all hover:border-emerald-500 hover:bg-emerald-50 hover:shadow-md cursor-pointer"
                >
                  <h3 className="text-lg font-semibold text-neutral-900">I am an Authority</h3>
                  <p className="text-sm text-neutral-500">Manage, verify, and resolve issues reported by citizens.</p>
                </button>
              </motion.div>
            </>
          )}

          {step === 2 && (
            <>
              <motion.div variants={itemVariants} className="mb-6 flex items-center gap-3">
                <button 
                  onClick={() => setStep(1)}
                  className="p-2 rounded-full hover:bg-neutral-100 transition-colors cursor-pointer"
                >
                  <HugeiconsIcon icon={ArrowLeft01Icon} className="size-5 text-neutral-600" />
                </button>
                <div>
                  <h2 className="text-2xl font-semibold tracking-tight text-neutral-900">
                    {role === "authority" ? "Authority Setup" : "Citizen Sign In"}
                  </h2>
                </div>
              </motion.div>

              {role === "authority" && (
                <motion.div variants={itemVariants} className="mb-6 flex flex-col gap-4">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-medium text-neutral-900">Department</label>
                    <select 
                      value={department}
                      onChange={(e) => setDepartment(e.target.value)}
                      className="w-full rounded-xl border border-neutral-200 bg-white px-4 py-3 text-sm text-neutral-900 focus:border-blue-600 focus:outline-none focus:ring-4 focus:ring-blue-600/10 transition-all cursor-pointer"
                    >
                      <option value="">Select Department</option>
                      <option value="Sanitation">Sanitation</option>
                      <option value="Traffic">Traffic Police</option>
                      <option value="Infrastructure">Infrastructure & Roads</option>
                      <option value="Water">Water & Sewage</option>
                    </select>
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-medium text-neutral-900">Jurisdiction</label>
                    <select 
                      value={jurisdiction}
                      onChange={(e) => setJurisdiction(e.target.value)}
                      className="w-full rounded-xl border border-neutral-200 bg-white px-4 py-3 text-sm text-neutral-900 focus:border-blue-600 focus:outline-none focus:ring-4 focus:ring-blue-600/10 transition-all cursor-pointer"
                    >
                      <option value="">Select Jurisdiction Zone</option>
                      <option value="North Zone">North Zone</option>
                      <option value="South Zone">South Zone</option>
                      <option value="East Zone">East Zone</option>
                      <option value="West Zone">West Zone</option>
                      <option value="Central Zone">Central Zone</option>
                    </select>
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <label className="text-sm font-medium text-neutral-900">Role / Title</label>
                    <select 
                      value={authorityRole}
                      onChange={(e) => setAuthorityRole(e.target.value)}
                      className="w-full rounded-xl border border-neutral-200 bg-white px-4 py-3 text-sm text-neutral-900 focus:border-blue-600 focus:outline-none focus:ring-4 focus:ring-blue-600/10 transition-all cursor-pointer"
                    >
                      <option value="">Select Role</option>
                      <option value="Inspector">Inspector</option>
                      <option value="Manager">Manager</option>
                      <option value="Field Officer">Field Officer</option>
                      <option value="Dispatcher">Dispatcher</option>
                    </select>
                  </div>
                </motion.div>
              )}

              <motion.div variants={itemVariants} className="mt-4">
                <button
                  type="button"
                  onClick={handleGoogleLogin}
                  disabled={role === "authority" && (!department || !jurisdiction || !authorityRole)}
                  className="flex w-full items-center justify-center gap-3 rounded-xl border border-neutral-200 bg-white py-3.5 px-4 text-sm font-medium text-neutral-700 transition-all hover:bg-neutral-50 hover:border-neutral-300 active:bg-neutral-100 shadow-xs disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                >
                  <GoogleIcon className="text-xl" />
                  Continue with Google
                </button>
                {role === "authority" && (!department || !jurisdiction || !authorityRole) && (
                  <p className="text-xs text-center text-rose-500 mt-2">Please fill all fields to continue</p>
                )}
              </motion.div>
            </>
          )}

        </motion.div>
      </div>
    </div>
  );
}
