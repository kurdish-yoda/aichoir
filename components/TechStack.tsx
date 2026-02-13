
import React, { useLayoutEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

const TechStack: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      const layers = gsap.utils.toArray('.tech-layer');
      const totalLayers = layers.length;

      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: triggerRef.current,
          start: "top top",
          end: `+=${totalLayers * 100}%`,
          pin: true,
          scrub: 1.2,
          invalidateOnRefresh: true,
        }
      });

      layers.forEach((layer: any, i) => {
        if (i !== 0) {
          gsap.set(layer, { opacity: 0, scale: 0.2, filter: 'blur(10px)' });
        }

        tl.to(layer, {
          opacity: 1,
          scale: 1,
          filter: 'blur(0px)',
          duration: 1.5,
          ease: "power2.inOut"
        }, i === 0 ? 0 : ">-0.8");

        if (i < totalLayers - 1) {
          tl.to(layer, {
            opacity: 0,
            scale: 6,
            filter: 'blur(20px)',
            duration: 1.5,
            ease: "power2.in"
          }, ">0.5");
        }
      });
    }, triggerRef);

    return () => ctx.revert();
  }, []);

  const data = [
    {
      title: "Observational Audit",
      description: "We don't ask; we watch. Our proprietary auditing tool maps every click and context switch in your current workflow.",
      detail: "PATTERN RECOGNITION"
    },
    {
      title: "Semantic Analysis",
      description: "We leverage LLMs to understand the unstructured data flowing through your pipes, turning noise into actionable insights.",
      detail: "DATA REFINEMENT"
    },
    {
      title: "Surgical Automation",
      description: "Custom-tuned agents handle specific, high-leverage tasks while maintaining human oversight where it matters most.",
      detail: "PRECISION EXECUTION"
    },
    {
      title: "Feedback Loops",
      description: "The system learns from every human correction, continuously optimizing the model to match your specific business logic.",
      detail: "ADAPTIVE INTELLIGENCE"
    }
  ];

  return (
    <section ref={triggerRef} className="relative h-screen bg-[#0E1117] overflow-hidden">
      <div className="container mx-auto px-6 max-w-[1100px] h-full relative z-10 pointer-events-none">
        <div className="absolute top-24 left-6">
          <span className="font-['JetBrains_Mono'] text-[12px] uppercase tracking-[0.12em] text-[#4A4D55] mb-4 block">
            CORE ARCHITECTURE
          </span>
          <h2 className="font-['Syne'] font-bold text-[clamp(1.5rem,3vw,2.5rem)] text-[#E2DFD8]">
            Built for depth.
          </h2>
        </div>

        <div ref={containerRef} className="relative w-full h-full flex items-center justify-center">
          {data.map((item, i) => (
            <div 
              key={i} 
              className="tech-layer absolute w-full max-w-[700px] text-center px-6 will-change-transform"
            >
              <div className="mb-8 inline-block font-['JetBrains_Mono'] text-[11px] text-[#7A7D85] tracking-[0.4em] border-b border-[#E2DFD8]/10 pb-2 uppercase">
                {item.detail}
              </div>
              <h3 className="font-['Syne'] font-bold text-[clamp(2.5rem,5vw,5rem)] text-[#E2DFD8] leading-[1.1] mb-10 tracking-tight">
                {item.title}
              </h3>
              <p className="font-['Inter'] font-light text-[clamp(1rem,1.4vw,1.3rem)] text-[#7A7D85] leading-[1.8] max-w-[500px] mx-auto opacity-80">
                {item.description}
              </p>
            </div>
          ))}
        </div>
      </div>
      
      <div className="absolute bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-4 opacity-30">
        <div className="font-['JetBrains_Mono'] text-[10px] tracking-widest text-[#4A4D55]">DIVE</div>
        <div className="w-[1px] h-10 bg-gradient-to-b from-[#E2DFD8] to-transparent"></div>
      </div>
    </section>
  );
};

export default TechStack;
