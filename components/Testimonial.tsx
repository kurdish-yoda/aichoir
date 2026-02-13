
import React from 'react';

const Testimonial: React.FC = () => {
  return (
    <section className="py-[140px] md:py-[200px] bg-[#0E1117] relative overflow-hidden">
      {/* Background Decorative Quote Mark */}
      <div className="absolute top-[20%] left-1/2 -translate-x-1/2 font-['Syne'] font-extrabold text-[15rem] md:text-[25rem] text-[#4A4D55]/05 pointer-events-none select-none">
        &ldquo;
      </div>
      
      <div className="container mx-auto px-6 max-w-[750px] relative z-10 text-center">
        <blockquote className="mb-12">
          <p className="font-['Syne'] font-normal text-[clamp(1.2rem,2.2vw,1.7rem)] text-[#E2DFD8] leading-[1.5] italic mb-10">
            "They didn't try to change everything. They watched how we actually work, found the three things costing us the most time, and fixed them. We handle 40% more volume now — and the team leaves on time."
          </p>
          <cite className="not-italic">
            <div className="font-['Inter'] font-normal text-[15px] text-[#E2DFD8] mb-1">
              Sarah Chen
            </div>
            <div className="font-['Inter'] font-light text-[13px] text-[#7A7D85] tracking-wide">
              Operations Director — Meridian Health
            </div>
          </cite>
        </blockquote>
      </div>
    </section>
  );
};

export default Testimonial;
