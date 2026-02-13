
import React from 'react';

const CTA: React.FC = () => {
  return (
    <section id="contact" className="py-[140px] md:py-[180px] bg-[#0E1117] relative overflow-hidden">
      {/* Subtle Warm Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#D4C4B0] rounded-full blur-[140px] opacity-[0.05] pointer-events-none" />
      
      <div className="container mx-auto px-6 max-w-[1100px] relative z-10 text-center">
        <h2 className="font-['Syne'] font-bold text-[clamp(2rem,5vw,3.5rem)] text-[#E2DFD8] mb-8">
          Let's find your leverage points.
        </h2>
        
        <p className="font-['Inter'] font-light text-[18px] text-[#7A7D85] max-w-[480px] mx-auto mb-14 leading-[1.7]">
          Book a free 30-minute call. We'll talk about your workflow, your team, and whether AI actually makes sense for you. No pitch. No pressure.
        </p>
        
        <div className="flex flex-col items-center gap-6">
          <button className="px-12 py-5 rounded-full border border-[#E2DFD8]/20 font-['Inter'] font-medium text-[17px] text-[#E2DFD8] hover:bg-[#E2DFD8]/05 hover:border-[#E2DFD8]/40 transition-all shadow-[0_0_40px_rgba(212,196,176,0.05)] interactive">
            Book Your Free Call
          </button>
          <div className="font-['Inter'] text-[13px] text-[#4A4D55] tracking-wide">
            or reach us at <span className="text-[#7A7D85] hover:text-[#E2DFD8] cursor-pointer transition-colors">hello@aichoir.com</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTA;
