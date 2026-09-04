import { Hero2 } from "./index";

export default function Hero2Demo() {
  const customNavLinks = [
    { label: "Home", href: "/", active: true },
    { label: "Kanban", href: "/kanban" },
    { label: "Map", href: "/map" },
    { 
      label: "Authority Dashboard", 
      href: "/authority",
      hasDropdown: true,
      dropdownItems: [
        { label: "Police Dashboard", href: "/authority?dept=police" },
        { label: "BMC Dashboard", href: "/authority?dept=bmc" }
      ]
    },
  ];
  
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
        secondaryCtaLabel="View Kanban Board"
        secondaryCtaHref="/kanban"
        socialLinks={customSocialLinks}
        headerActions={
          <div className="flex items-center gap-4">
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
          </div>
        }
      />
    </div>
  );
}
