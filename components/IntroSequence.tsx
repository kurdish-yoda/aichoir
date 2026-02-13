
import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';

const IntroSequence: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const tl = gsap.timeline();
    
    tl.to(textRef.current, {
      opacity: 1,
      duration: 0.8,
      ease: 'power2.out'
    })
    .to(textRef.current, {
      letterSpacing: '0.5em',
      duration: 1.2,
      ease: 'power1.inOut'
    }, '-=0.2')
    .to(containerRef.current, {
      opacity: 0,
      duration: 0.8,
      ease: 'power2.inOut',
      delay: 0.5
    });

    return () => {
      tl.kill();
    };
  }, []);

  return (
    <div 
      ref={containerRef}
      className="fixed inset-0 z-[100] flex items-center justify-center bg-[#0E1117]"
    >
      <div 
        ref={textRef}
        className="text-[#E2DFD8] font-['Syne'] font-extrabold text-4xl opacity-0 tracking-tight"
      >
        AI CHOIR
      </div>
    </div>
  );
};

export default IntroSequence;
