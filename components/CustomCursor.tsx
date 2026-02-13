
import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';

const CustomCursor: React.FC = () => {
  const cursorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const cursor = cursorRef.current;
    if (!cursor) return;

    const onMouseMove = (e: MouseEvent) => {
      gsap.to(cursor, {
        x: e.clientX,
        y: e.clientY,
        duration: 0.15,
        ease: 'power2.out'
      });
    };

    const onMouseEnterLink = () => {
      gsap.to(cursor, {
        scale: 3,
        borderColor: '#B8B5AD',
        backgroundColor: 'rgba(226, 223, 216, 0.03)',
        duration: 0.3
      });
    };

    const onMouseLeaveLink = () => {
      gsap.to(cursor, {
        scale: 1,
        borderColor: '#7A7D85',
        backgroundColor: 'transparent',
        duration: 0.3
      });
    };

    window.addEventListener('mousemove', onMouseMove);

    const interactiveElements = document.querySelectorAll('a, button, .interactive');
    interactiveElements.forEach((el) => {
      el.addEventListener('mouseenter', onMouseEnterLink);
      el.addEventListener('mouseleave', onMouseLeaveLink);
    });

    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      interactiveElements.forEach((el) => {
        el.removeEventListener('mouseenter', onMouseEnterLink);
        el.removeEventListener('mouseleave', onMouseLeaveLink);
      });
    };
  }, []);

  return (
    <div 
      ref={cursorRef}
      className="fixed top-0 left-0 w-4 h-4 border border-[#7A7D85] rounded-full pointer-events-none z-[9999] hidden md:block -translate-x-1/2 -translate-y-1/2 will-change-transform"
    />
  );
};

export default CustomCursor;
