import { useState, useEffect } from "react";
import { Hero2 } from "./index";
import { supabase } from "../../services/supabase";

import CitizenNotificationBell from "../../components/citizen/CitizenNotificationBell";

export default function Hero2Demo() {
  const [session, setSession] = useState<any>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  const roleType = session?.user?.user_metadata?.role_type;
  const isAuthority = roleType === 'authority';

  const customNavLinks = [
    { label: "Home", href: "/", active: true },
    { label: "Map", href: "/map" },
  ];

  if (isAuthority) {
    customNavLinks.push({ label: "Kanban", href: "/kanban", active: false } as any);
    customNavLinks.push({ 
      label: "Authority Dashboard", 
      href: "/authority",
      hasDropdown: true,
      dropdownItems: [
        { label: "Police Dashboard", href: "/authority?dept=police" },
        { label: "BMC Dashboard", href: "/authority?dept=bmc" }
      ]
    } as any);
  }
  
  const customSocialLinks = [
    { label: "Twitter", href: "#" },
    { label: "GitHub", href: "https://github.com/itssmansi/hackathon_project_grp3" },
  ];

  return (
    <div className="bg-background flex min-h-screen w-full flex-col justify-center">
      <Hero2
        brand={
          <div className="flex items-center gap-2">
            <svg className="w-7 h-7 text-unisafe-teal" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z" />
            </svg>
            <span className="text-xl font-bold tracking-tight text-unisafe-dark-midnight-blue">UniSafe</span>
          </div>
        }
        navLinks={customNavLinks}
        headline={
          <>
            Empower Communities,<br />
            Resolve <span className="italic font-medium font-serif text-unisafe-teal">Faster.</span>
          </>
        }
        description={"A unified civic operations platform bridging the gap between citizens and authorities for a safer, cleaner city."}
        primaryCtaLabel="Report an Issue"
        primaryCtaHref="/map"
        secondaryCtaLabel={isAuthority ? "View Kanban Board" : "Explore Map"}
        secondaryCtaHref={isAuthority ? "/kanban" : "/map"}
        socialLinks={customSocialLinks}
        headerActions={
          <div className="flex items-center gap-4">
            {session && <CitizenNotificationBell />}
            
            {session ? (
              <div className="flex items-center gap-3 border-l border-gray-300 pl-4">
                <span className="text-sm font-semibold text-unisafe-midnight-blue bg-unisafe-teal/10 px-3 py-1 rounded-full">
                  {roleType === 'authority' ? 'Authority' : 'Citizen'}
                </span>
                <button 
                  onClick={() => supabase.auth.signOut()} 
                  className="text-sm font-medium text-red-600 hover:text-red-700 transition-colors"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <>
                <div className="flex items-center gap-2 border-r border-gray-300 pr-4">
                  <span className="text-xs font-semibold uppercase tracking-wider text-unisafe-midnight-blue/50">Citizen</span>
                  <a href="/auth?role=citizen&mode=login" className="text-sm font-medium text-unisafe-midnight-blue hover:text-unisafe-teal transition-colors">
                    Login
                  </a>
                  <span className="text-unisafe-midnight-blue/30">/</span>
                  <a href="/auth?role=citizen&mode=register" className="text-sm font-medium text-unisafe-midnight-blue hover:text-unisafe-teal transition-colors">
                    Register
                  </a>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-unisafe-midnight-blue/50">Authority</span>
                  <a href="/auth?role=authority&mode=login" className="text-sm font-medium text-unisafe-midnight-blue hover:text-unisafe-teal transition-colors">
                    Login
                  </a>
                  <span className="text-unisafe-midnight-blue/30">/</span>
                  <a href="/auth?role=authority&mode=register" className="text-sm font-medium text-unisafe-midnight-blue hover:text-unisafe-teal transition-colors">
                    Register
                  </a>
                </div>
              </>
            )}
          </div>
        }
      />
    </div>
  );
}
