
import React, { useLayoutEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

const Process: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const mm = gsap.matchMedia();

    mm.add("(min-width: 768px)", () => {
      if (!containerRef.current || !triggerRef.current) return;

      const steps = containerRef.current.querySelectorAll('.process-step');
      const totalWidth = containerRef.current.scrollWidth;
      const windowWidth = window.innerWidth;
      
      const pin = gsap.to(containerRef.current, {
        x: () => -(totalWidth - windowWidth),
        ease: "none",
        scrollTrigger: {
          trigger: triggerRef.current,
          pin: true,
          scrub: 1,
          start: "top top",
          // The duration of the scroll is based on the width of the content
          end: () => `+=${totalWidth}`,
          invalidateOnRefresh: true,
        }
      });
      
      return () => pin.kill();
    });

    return () => mm.revert();
  }, []);

  const steps = [
    { number: '01', title: 'Listen', body: "We embed with your team. Not a questionnaire — actual observation. We map how work really flows, where time disappears, and what's already working well." },
    { number: '02', title: 'Diagnose', body: "Not everything needs automation. We pinpoint the specific processes eating your team's hours — and just as importantly, the ones that should stay human." },
    { number: '03', title: 'Build', body: "Surgical, targeted solutions for your exact workflow. Custom AI programs built around how your team actually operates — not a generic tool with your logo on it." },
    { number: '04', title: 'Maintain', body: "Your business evolves. Your systems should too. Continuous monitoring, updates, and optimization. We stay with you." },
  ];

  return (
    <section ref={triggerRef} className="bg-[#0E1117] min-h-screen">
      <div className="container mx-auto px-6 max-w-[1100px] pt-[100px] pb-20">
        <span className="font-['JetBrains_Mono'] text-[12px] uppercase tracking-[0.12em] text-[#4A4D55] mb-6 block">
          PROCESS
        </span>
        <h2 className="font-['Syne'] font-bold text-[clamp(2rem,4vw,3rem)] text-[#E2DFD8] mb-4">
          Precision over volume.
        </h2>
        <p className="font-['Inter'] font-light text-[18px] text-[#7A7D85]">
          A methodology designed for surgical integration.
        </p>
      </div>
      
      <div ref={containerRef} className="flex flex-col md:flex-row md:w-max h-auto md:h-[60vh]">
        {steps.map((step) => (
          <div 
            key={step.number} 
            className="process-step w-full md:w-[80vw] lg:w-[60vw] flex items-center px-6 md:px-[10vw] border-b md:border-b-0 md:border-r border-[#E2DFD8]/06 py-20 md:py-0"
          >
            <div className="relative">
              <span className="absolute -top-12 md:-top-20 left-0 font-['Syne'] font-extrabold text-[6rem] md:text-[8rem] text-[#4A4D55]/10 pointer-events-none">
                {step.number}
              </span>
              <div className="relative z-10">
                <h3 className="font-['Syne'] font-bold text-[1.8rem] text-[#E2DFD8] mb-6">
                  {step.title}
                </h3>
                <p className="font-['Inter'] font-light text-[17px] md:text-[19px] text-[#7A7D85] leading-[1.7] max-w-[450px]">
                  {step.body}
                </p>
              </div>
            </div>
          </div>
        ))}
        {/* End padding for desktop horizontal scroll */}
        <div className="hidden md:block w-[20vw]"></div>
      </div>
    </section>
  );
};

export default Process;
