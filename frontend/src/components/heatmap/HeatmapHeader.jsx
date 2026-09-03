import React from 'react';
import { useUserRole } from '../../hooks/useUserRole';

export default function HeatmapHeader() {
  const { isAuthority } = useUserRole();

  return (
    <div className="w-full mb-6 sm:mb-8 font-sans">
      {/* 1. Sleek Dark Top Navigation Bar (#0B192C) */}
      <nav className="bg-[#0B192C] text-white px-6 h-16 rounded-2xl flex items-center justify-between shadow-sm mb-6 sm:mb-8">
        <div className="flex items-center gap-3">
          <span className="text-xs font-black uppercase tracking-widest text-white">
            UNISAFE PLATFORM
          </span>
          <span className="text-gray-600">•</span>
          <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#10B981]">
            <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
            Live Hotspots
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#10B981]"></span>
          <span className="text-xs font-medium text-gray-300">
            {isAuthority ? 'Authority Mode' : 'Citizen View (Read-Only)'}
          </span>
        </div>
      </nav>

      {/* 2. Un-carded Page Header (Pure Sans-Serif on #FBF9F5 cream background) */}
      <div className="px-1">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-[#0B192C] tracking-tight font-sans">
          Civic Risk Heatmap
        </h1>
        <p className="text-xs sm:text-sm text-[#64748B] font-medium mt-1.5">
          Monitor civic risk hotspots and identify areas requiring attention
        </p>
      </div>
    </div>
  );
}
