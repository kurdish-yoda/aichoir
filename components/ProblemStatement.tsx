
import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';

const ProblemStatement: React.FC = () => {
  const sectionRef = useRef<HTMLElement>(null);
  const textRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const words = textRef.current?.querySelectorAll('.word');
    if (!words) return;

    gsap.to(words, {
      color: '#E2DFD8',
      textShadow: '0 0 30px rgba(226, 223, 216, 0.15)',
      stagger: 0.02,
      scrollTrigger: {
        trigger: sectionRef.current,
        start: 'top 80%',
        end: 'center center',
        scrub: true,
      }
    });
  }, []);

  const mainText = "Most agencies want to automate everything they touch. More automations, bigger invoice. We think that's backwards. Some parts of your business need a human. Some don't. The hard part is knowing which is which.";
  const closingText = "That's what we do.";

  return (
    <section ref={sectionRef} id="about" className="py-[80px] md:py-[200px] bg-[#0E1117] border-t border-[#E2DFD8]/10 md:border-t-0">
      <div className="container mx-auto px-6 max-w-[1100px]">
        <div ref={textRef} className="max-w-[750px] mx-auto text-center font-['Syne'] font-normal text-[clamp(1.4rem,2.8vw,2.2rem)] leading-[1.4] text-[#4A4D55]">
          {mainText.split(' ').map((word, i) => (
            <span key={i} className="word inline-block mr-[0.3em] transition-colors duration-300">
              {word}
            </span>
          ))}
          <span className="block mt-8" />
          {closingText.split(' ').map((word, i) => (
            <span key={`closing-${i}`} className="word inline-block mr-[0.3em] transition-colors duration-300 font-semibold">
              {word}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ProblemStatement;
