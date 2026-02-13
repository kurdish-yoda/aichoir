
import React, { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';

const StatItem = ({ number, label, suffix = "" }: { number: number, label: string, suffix?: string }) => {
  const [displayValue, setDisplayValue] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (number === 0) {
      setDisplayValue(0);
      return;
    }

    const obj = { value: 0 };
    gsap.to(obj, {
      value: number,
      duration: 2,
      ease: 'power2.out',
      scrollTrigger: {
        trigger: containerRef.current,
        start: 'top 90%',
      },
      onUpdate: () => setDisplayValue(Math.floor(obj.value))
    });
  }, [number]);

  return (
    <div ref={containerRef} className="flex flex-col items-center py-12 md:py-20 border-b md:border-b-0 md:border-r last:border-0 border-[#E2DFD8]/06">
      <div className="font-['Syne'] font-bold text-[clamp(3rem,6vw,4.5rem)] text-[#E2DFD8] mb-2">
        {displayValue}{suffix}
      </div>
      <div className="font-['JetBrains_Mono'] text-[11px] uppercase tracking-[0.12em] text-[#4A4D55] text-center max-w-[200px]">
        {label}
      </div>
    </div>
  );
};

const Stats: React.FC = () => {
  return (
    <section className="bg-[#141821]">
      <div className="container mx-auto max-w-[1100px] px-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4">
          <StatItem number={40} suffix="%" label="REDUCTION IN MANUAL TASKS" />
          <StatItem number={3} suffix="×" label="FASTER PROCESS TURNAROUND" />
          <StatItem number={100} suffix="%" label="CLIENTS ON ONGOING SUPPORT" />
          <StatItem number={0} label="UNNECESSARY AUTOMATIONS SHIPPED" />
        </div>
      </div>
    </section>
  );
};

export default Stats;
