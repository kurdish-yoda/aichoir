
import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-[#0E1117] border-t border-[#E2DFD8]/06 py-8 md:py-10">
      <div className="container mx-auto px-6 max-w-[1100px]">
        <div className="flex items-center justify-between">
          <div className="font-['Syne'] font-extrabold text-[14px] text-[#7A7D85] tracking-tight">
            AI CHOIR
          </div>
          <div className="font-['JetBrains_Mono'] text-[11px] text-[#4A4D55] uppercase tracking-[0.12em]">
            © 2026 AI CHOIR
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
