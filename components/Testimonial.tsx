
import React from 'react';

const Testimonial: React.FC = () => {
  return (
    <section className="py-[80px] md:py-[200px] bg-[#0E1117] relative overflow-hidden border-t border-[#E2DFD8]/10 md:border-t-0">
      <div className="container mx-auto px-6 max-w-[750px] relative z-10 text-center">
        <blockquote className="mb-12">
          <p className="font-['Syne'] font-normal text-[clamp(1.2rem,2.2vw,1.7rem)] text-[#E2DFD8] leading-[1.5] italic mb-10">
            "They took the time to understand our consulting workflows before suggesting anything. The automations they built saved our team hours every week on reporting and client onboarding — without losing the personal touch our clients expect."
          </p>
          <cite className="not-italic">
            <div className="font-['Inter'] font-normal text-[15px] text-[#E2DFD8] mb-1">
              Silard Gal
            </div>
            <div className="font-['Inter'] font-light text-[13px] text-[#7A7D85] tracking-wide">
              Director — Embedded Consultants
            </div>
          </cite>
        </blockquote>
      </div>
    </section>
  );
};

export default Testimonial;
