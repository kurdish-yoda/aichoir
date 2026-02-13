
import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';

const BackgroundOrbs: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const orbs = containerRef.current?.children;
    if (!orbs) return;

    Array.from(orbs).forEach((orb, i) => {
      gsap.to(orb, {
        x: '+=100',
        y: '+=80',
        duration: 20 + i * 5,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut'
      });
    });
  }, []);

  return (
    <div ref={containerRef} className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      <div 
        className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full blur-[120px] opacity-[0.08]"
        style={{ background: '#C4B8CB' }}
      />
      <div 
        className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] rounded-full blur-[120px] opacity-[0.1]"
        style={{ background: '#D4C4B0' }}
      />
      <div 
        className="absolute top-[30%] right-[10%] w-[400px] h-[400px] rounded-full blur-[120px] opacity-[0.06]"
        style={{ background: '#B0C4C4' }}
      />
    </div>
  );
};

export default BackgroundOrbs;
