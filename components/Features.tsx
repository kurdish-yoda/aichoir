
import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';

const FeatureCard = ({ icon, title, body, index }: { icon: React.ReactNode, title: string, body: string, index: number }) => {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    gsap.fromTo(cardRef.current,
      { y: 40, opacity: 0 },
      { 
        y: 0, 
        opacity: 1, 
        duration: 1.2, 
        ease: 'power2.out',
        scrollTrigger: {
          trigger: cardRef.current,
          start: 'top 90%',
        },
        delay: index * 0.15
      }
    );
  }, [index]);

  return (
    <div 
      ref={cardRef}
      className="bg-[#1E2433] border border-[#E2DFD8]/06 rounded-[12px] p-10 md:p-12 transition-all duration-500 hover:bg-[#1A1F2B] hover:border-[#E2DFD8]/10 hover:shadow-[0_0_40px_rgba(196,184,203,0.08)] interactive"
    >
      <div className="w-12 h-12 mb-10 text-[#7A7D85]">
        {icon}
      </div>
      <h3 className="font-['Syne'] font-bold text-[1.4rem] text-[#E2DFD8] mb-6">
        {title}
      </h3>
      <p className="font-['Inter'] font-light text-[16px] text-[#7A7D85] leading-[1.7]">
        {body}
      </p>
    </div>
  );
};

const Features: React.FC = () => {
  return (
    <section className="py-[80px] md:py-[140px] bg-[#0E1117] border-t border-[#E2DFD8]/10 md:border-t-0">
      <div className="container mx-auto px-6 max-w-[1100px]">
        <div className="mb-20">
          <span className="font-['JetBrains_Mono'] text-[12px] uppercase tracking-[0.12em] text-[#4A4D55] mb-6 block">
            THE OUTCOME
          </span>
          <h2 className="font-['Syne'] font-bold text-[clamp(2rem,4vw,3rem)] text-[#E2DFD8] mb-8">
            Less busywork. More revenue.
          </h2>
          <p className="font-['Inter'] font-light text-[18px] text-[#7A7D85] max-w-[500px]">
            Real improvements your team can feel on day one.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard 
            index={0}
            icon={<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M3 17L9 11L13 15L21 7M21 7V12M21 7H16" strokeLinecap="round" strokeLinejoin="round"/></svg>}
            title="Revenue that grows"
            body="Our optimizations don't just save time. They unlock capacity your team didn't know it had. Clients see measurable revenue increases in the first quarter."
          />
          <FeatureCard 
            index={1}
            icon={<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z"/><path d="M12 14C8.13401 14 5 17.134 5 21H19C19 17.134 15.866 14 12 14Z"/><path d="M18 10L21 13L18 16" strokeLinecap="round" strokeLinejoin="round"/></svg>}
            title="People who stay"
            body="Nobody signed up for data entry and copy-pasting. We remove the repetitive work so your team can do what they were actually hired to do."
          />
          <FeatureCard 
            index={2}
            icon={<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M4 4V9H4.58152M19.9381 11C19.446 7.05361 16.0796 4 12 4C9.27304 4 6.8647 5.3852 5.40543 7.5M20 20V15H19.4185M4.06189 13C4.55399 16.9464 7.92038 20 12 20C14.727 20 17.1353 18.6148 18.5946 16.5" strokeLinecap="round" strokeLinejoin="round"/></svg>}
            title="Systems that last"
            body="We don't build it and leave. Ongoing maintenance and monitoring means your optimizations evolve as your business does."
          />
        </div>
      </div>
    </section>
  );
};

export default Features;
