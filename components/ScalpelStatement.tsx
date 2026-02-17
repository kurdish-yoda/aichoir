
import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';

const ScalpelStatement: React.FC = () => {
  const shimmerRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const shimmer = shimmerRef.current;
    if (!shimmer) return;

    gsap.fromTo(shimmer,
      { backgroundPosition: '-200% 0' },
      {
        backgroundPosition: '200% 0',
        duration: 1.5,
        ease: 'power2.inOut',
        scrollTrigger: {
          trigger: shimmer,
          start: 'top 80%',
        }
      }
    );
  }, []);

  return (
    <section className="py-[100px] md:py-[180px] bg-[#0E1117] text-center overflow-hidden border-t border-[#E2DFD8]/10 md:border-t-0">
      <div className="container mx-auto px-6 max-w-[1100px]">
        <h2 className="font-['Syne'] font-bold text-[clamp(2rem,8vw,6rem)] text-[#E2DFD8] leading-tight mb-12">
          A <span 
            ref={shimmerRef} 
            className="relative inline-block px-2 text-[#E2DFD8] bg-clip-text"
            style={{
              backgroundImage: 'linear-gradient(110deg, transparent 40%, rgba(226,223,216,0.5) 50%, transparent 60%)',
              backgroundSize: '200% 100%',
              WebkitBackgroundClip: 'text',
            }}
          >scalpel,</span><br />
          not a sledgehammer.
        </h2>
        
        <p className="font-['Inter'] font-light text-[18px] text-[#7A7D85] max-w-[540px] mx-auto leading-[1.7]">
          We're not here to "AI-ify" your entire company. We find the three, four, maybe five precise changes that will genuinely transform how your team works.
        </p>
      </div>
    </section>
  );
};

export default ScalpelStatement;
