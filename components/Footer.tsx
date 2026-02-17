
import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-[#0E1117] border-t border-[#E2DFD8]/06 pt-10 md:pt-20 pb-8 md:pb-12">
      <div className="container mx-auto px-6 max-w-[1100px]">
        {/* Mobile: single row, logo left / copyright right */}
        <div className="flex md:hidden items-center justify-between">
          <div className="font-['Syne'] font-extrabold text-[14px] text-[#7A7D85] tracking-tight">
            AI CHOIR
          </div>
          <div className="font-['JetBrains_Mono'] text-[11px] text-[#4A4D55] uppercase tracking-[0.12em]">
            © 2026
          </div>
        </div>

        {/* Desktop: original stacked layout */}
        <div className="hidden md:block">
          <div className="mb-20">
            <div className="font-['Syne'] font-extrabold text-[14px] text-[#7A7D85] tracking-tight">
              AI CHOIR
            </div>
          </div>
          <div className="text-center">
            <div className="font-['JetBrains_Mono'] text-[11px] text-[#4A4D55] uppercase tracking-[0.12em] mb-4">
              © 2026 AI CHOIR
            </div>
            <div className="w-full h-[1px] bg-[#E2DFD8]/06"></div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
