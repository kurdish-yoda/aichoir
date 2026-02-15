
import React, { useEffect, useRef, useState, useCallback } from 'react';
import gsap from 'gsap';

interface SearchParticle {
  x: number;
  y: number;
  targetX: number;
  targetY: number;
  idleX: number;
  idleY: number;
  angle: number;
  size: number;
  opacity: number;
  baseOpacity: number;
  color: string;
  active: boolean;
  noiseOffsetX: number;
  noiseOffsetY: number;
}

const PARTICLE_COUNT = 200;
const ACTIVE_COUNT = 50;
const CIRCLE_RADIUS = 80;
const PARTICLE_COLORS = ['#E2DFD8', '#F2EFE8', '#D8D5CC'];

const COUNTIES = [
  'Searching Miami-Dade County...',
  'Searching Broward County...',
  'Searching Palm Beach County...',
  'Searching New York County...',
  'Searching Kings County...',
  'Compiling results...',
];

function createParticles(w: number, h: number): SearchParticle[] {
  const particles: SearchParticle[] = [];
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    // Spread across the entire canvas, edge to edge
    const idleX = Math.random() * w;
    const idleY = Math.random() * h;
    particles.push({
      x: idleX,
      y: idleY,
      targetX: idleX,
      targetY: idleY,
      idleX,
      idleY,
      angle: (i / ACTIVE_COUNT) * Math.PI * 2,
      size: 1.5 + Math.random() * 2,
      opacity: 0.2 + Math.random() * 0.4,
      baseOpacity: 0.2 + Math.random() * 0.4,
      color: PARTICLE_COLORS[Math.floor(Math.random() * PARTICLE_COLORS.length)],
      active: i < ACTIVE_COUNT,
      noiseOffsetX: Math.random() * Math.PI * 2,
      noiseOffsetY: Math.random() * Math.PI * 2,
    });
  }
  return particles;
}

const CourtSearchPage: React.FC = () => {
  const pageRef = useRef<HTMLElement>(null);
  const headerRef = useRef<HTMLDivElement>(null);
  const formRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const spinnerAnchorRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const buttonTextRef = useRef<HTMLSpanElement>(null);
  const statusRef = useRef<HTMLDivElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const particlesRef = useRef<SearchParticle[]>([]);
  const canvasSizeRef = useRef<{ w: number; h: number }>({ w: 0, h: 0 });
  const spinnerCenterRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const animFrameRef = useRef<number>(0);
  const rotationRef = useRef<number>(0);
  const modeRef = useRef<'idle' | 'loading' | 'done'>('idle');
  const timeRef = useRef<number>(0);

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [middleName, setMiddleName] = useState('');
  const [dob, setDob] = useState('');
  const [statusText, setStatusText] = useState('');
  const [searchComplete, setSearchComplete] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  // GSAP entrance animations
  useEffect(() => {
    if (headerRef.current) {
      gsap.fromTo(headerRef.current.children,
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, ease: 'power2.out', stagger: 0.08 }
      );
    }
    if (formRef.current) {
      gsap.fromTo(formRef.current,
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 1, ease: 'power2.out', delay: 0.3 }
      );
    }

    return () => {
      cancelAnimationFrame(animFrameRef.current);
    };
  }, []);

  // Single full-page canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    const page = pageRef.current;
    if (!canvas || !page) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      const w = page.offsetWidth;
      const h = page.offsetHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = w + 'px';
      canvas.style.height = h + 'px';
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const oldW = canvasSizeRef.current.w;
      canvasSizeRef.current = { w, h };

      if (particlesRef.current.length === 0 || oldW === 0) {
        particlesRef.current = createParticles(w, h);
      }

      // Update spinner center from anchor element
      updateSpinnerCenter();
    };

    const updateSpinnerCenter = () => {
      if (spinnerAnchorRef.current && pageRef.current) {
        const anchorRect = spinnerAnchorRef.current.getBoundingClientRect();
        const pageRect = pageRef.current.getBoundingClientRect();
        spinnerCenterRef.current = {
          x: anchorRect.left - pageRect.left + anchorRect.width / 2,
          y: anchorRect.top - pageRect.top + anchorRect.height / 2,
        };
      }
    };

    resize();
    window.addEventListener('resize', resize);
    window.addEventListener('scroll', updateSpinnerCenter);

    const animate = () => {
      const { w, h } = canvasSizeRef.current;
      ctx.clearRect(0, 0, w, h);
      ctx.globalCompositeOperation = 'lighter';
      timeRef.current += 0.01;
      const t = timeRef.current;
      const particles = particlesRef.current;
      const mode = modeRef.current;

      if (mode === 'loading') {
        rotationRef.current += 0.02;
      }

      const sc = spinnerCenterRef.current;

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        if (mode === 'idle') {
          p.targetX = p.idleX + Math.sin(t * 1.5 + p.noiseOffsetX) * 15;
          p.targetY = p.idleY + Math.cos(t * 1.2 + p.noiseOffsetY) * 15;
        } else if (mode === 'loading' && p.active) {
          const angle = p.angle + rotationRef.current;
          p.targetX = sc.x + Math.cos(angle) * CIRCLE_RADIUS;
          p.targetY = sc.y + Math.sin(angle) * CIRCLE_RADIUS;
        }

        // Faster lerp during loading so particles converge quicker
        const lerp = mode === 'loading' && p.active ? 0.06 : 0.08;
        p.x += (p.targetX - p.x) * lerp;
        p.y += (p.targetY - p.y) * lerp;

        if (p.opacity < 0.005) continue;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = p.opacity;
        ctx.fill();
      }

      ctx.globalAlpha = 1;
      animFrameRef.current = requestAnimationFrame(animate);
    };

    animFrameRef.current = requestAnimationFrame(animate);
    return () => {
      cancelAnimationFrame(animFrameRef.current);
      window.removeEventListener('resize', resize);
      window.removeEventListener('scroll', updateSpinnerCenter);
    };
  }, []);

  const handleSearch = useCallback(() => {
    if (!firstName.trim() || !lastName.trim() || isSearching) return;

    setIsSearching(true);
    setSearchComplete(false);
    modeRef.current = 'loading';
    const particles = particlesRef.current;

    const tl = gsap.timeline();

    // t=0.0s — button fades out
    tl.to(buttonRef.current, { opacity: 0, duration: 0.4, ease: 'power2.out' }, 0);

    // t=0.3s — inactive particles fade out while active ones travel to spinner
    tl.call(() => {
      for (let i = 0; i < particles.length; i++) {
        if (!particles[i].active) {
          gsap.to(particles[i], { opacity: 0, duration: 0.8 });
        }
      }
    }, [], 0.3);

    // t=1.2s — status text appears (gives particles time to arrive)
    tl.call(() => {
      setStatusText(COUNTIES[0]);
    }, [], 1.2);
    tl.fromTo(statusRef.current, { opacity: 0 }, { opacity: 1, duration: 0.4 }, 1.2);

    // County cycling every 1.2s
    for (let i = 1; i < COUNTIES.length; i++) {
      const countyIndex = i;
      tl.call(() => {
        setStatusText(COUNTIES[countyIndex]);
      }, [], 1.2 + i * 1.2);
    }

    // Particles scatter outward + fade, status fades
    const scatterTime = 1.2 + COUNTIES.length * 1.2;
    tl.call(() => {
      modeRef.current = 'done';
      const sc = spinnerCenterRef.current;
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        if (p.active) {
          const dirX = p.x - sc.x;
          const dirY = p.y - sc.y;
          const dist = Math.sqrt(dirX * dirX + dirY * dirY) || 1;
          gsap.to(p, {
            targetX: p.x + (dirX / dist) * 400,
            targetY: p.y + (dirY / dist) * 400,
            opacity: 0,
            duration: 0.8,
            ease: 'power2.in',
          });
        }
      }
    }, [], scatterTime);
    tl.to(statusRef.current, { opacity: 0, duration: 0.5 }, scatterTime);

    // Results area fades in
    tl.call(() => {
      setSearchComplete(true);
      setIsSearching(false);
    }, [], scatterTime + 0.8);
    tl.fromTo(resultsRef.current,
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out' },
      scatterTime + 0.8
    );
  }, [firstName, lastName, isSearching]);

  const handleReset = useCallback(() => {
    modeRef.current = 'idle';
    setSearchComplete(false);
    setIsSearching(false);
    setStatusText('');
    rotationRef.current = 0;

    const { w, h } = canvasSizeRef.current;
    particlesRef.current = createParticles(w, h);

    gsap.to(buttonRef.current, { opacity: 1, duration: 0.3 });
    if (resultsRef.current) {
      gsap.set(resultsRef.current, { opacity: 0 });
    }
  }, []);

  return (
    <main ref={pageRef} className="relative w-full overflow-x-hidden pt-[120px] pb-24 min-h-screen">
      {/* Single full-page canvas — covers everything, behind all content */}
      <canvas
        ref={canvasRef}
        className="absolute top-0 left-0 pointer-events-none"
        style={{ zIndex: 0 }}
      />

      {/* All page content above particles */}
      <div className="relative" style={{ zIndex: 1 }}>
        <div className="container mx-auto px-6 max-w-[1100px]">
          {/* Header */}
          <div ref={headerRef} className="text-center mb-16">
            <span className="font-['JetBrains_Mono'] text-[12px] uppercase tracking-[0.12em] text-[#4A4D55] block mb-4">
              Court Records Lookup
            </span>
            <h1 className="font-['Syne'] font-bold text-[#E2DFD8] text-4xl md:text-5xl mb-4">
              Civil Court Search
            </h1>
            <p className="font-['Inter'] font-light text-[#7A7D85] text-base md:text-lg max-w-[520px] mx-auto">
              Search across Florida and New York civil court records. Enter a name to begin.
            </p>
          </div>

          {/* Form card — visible card treatment so it doesn't blend */}
          <div ref={formRef} className="max-w-[640px] mx-auto mb-12">
            <div className="bg-[#141821]/60 border border-[#E2DFD8]/10 rounded-2xl p-8 backdrop-blur-sm">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
                <div>
                  <label className="font-['JetBrains_Mono'] text-[12px] uppercase tracking-[0.12em] text-[#7A7D85] block mb-2">
                    First Name *
                  </label>
                  <input
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    className="w-full bg-[#0E1117] border border-[#E2DFD8]/15 rounded-lg px-4 py-3 text-[#E2DFD8] font-['Inter'] text-sm focus:outline-none focus:border-[#E2DFD8]/40 transition-colors placeholder-[#4A4D55]"
                    placeholder="John"
                    disabled={isSearching}
                  />
                </div>
                <div>
                  <label className="font-['JetBrains_Mono'] text-[12px] uppercase tracking-[0.12em] text-[#7A7D85] block mb-2">
                    Last Name *
                  </label>
                  <input
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    className="w-full bg-[#0E1117] border border-[#E2DFD8]/15 rounded-lg px-4 py-3 text-[#E2DFD8] font-['Inter'] text-sm focus:outline-none focus:border-[#E2DFD8]/40 transition-colors placeholder-[#4A4D55]"
                    placeholder="Doe"
                    disabled={isSearching}
                  />
                </div>
                <div>
                  <label className="font-['JetBrains_Mono'] text-[12px] uppercase tracking-[0.12em] text-[#7A7D85] block mb-2">
                    Middle Name
                  </label>
                  <input
                    type="text"
                    value={middleName}
                    onChange={(e) => setMiddleName(e.target.value)}
                    className="w-full bg-[#0E1117] border border-[#E2DFD8]/15 rounded-lg px-4 py-3 text-[#E2DFD8] font-['Inter'] text-sm focus:outline-none focus:border-[#E2DFD8]/40 transition-colors placeholder-[#4A4D55]"
                    placeholder="Optional"
                    disabled={isSearching}
                  />
                </div>
                <div>
                  <label className="font-['JetBrains_Mono'] text-[12px] uppercase tracking-[0.12em] text-[#7A7D85] block mb-2">
                    Date of Birth
                  </label>
                  <input
                    type="text"
                    value={dob}
                    onChange={(e) => setDob(e.target.value)}
                    className="w-full bg-[#0E1117] border border-[#E2DFD8]/15 rounded-lg px-4 py-3 text-[#E2DFD8] font-['Inter'] text-sm focus:outline-none focus:border-[#E2DFD8]/40 transition-colors placeholder-[#4A4D55]"
                    placeholder="MM/DD/YYYY"
                    disabled={isSearching}
                  />
                </div>
              </div>

              {/* Search Button — prominent, stands out */}
              <div className="flex justify-center">
                <button
                  ref={buttonRef}
                  onClick={handleSearch}
                  disabled={!firstName.trim() || !lastName.trim() || isSearching}
                  className="px-14 py-4 rounded-full border border-[#E2DFD8]/30 bg-[#E2DFD8]/10 relative interactive disabled:opacity-40 disabled:cursor-not-allowed transition-all hover:bg-[#E2DFD8]/15 hover:border-[#E2DFD8]/50"
                >
                  <span
                    ref={buttonTextRef}
                    className="font-['JetBrains_Mono'] text-[13px] uppercase tracking-[0.15em] text-[#E2DFD8]"
                  >
                    Search Records
                  </span>
                </button>
              </div>
            </div>
          </div>

          {/* Spinner anchor — this invisible element marks where the spinner circle forms */}
          <div ref={spinnerAnchorRef} className="flex flex-col items-center mb-12" style={{ minHeight: 200 }}>
            {/* Status text below spinner */}
            <div className="mt-[180px]">
              <div ref={statusRef} className="opacity-0 h-6 text-center">
                <span className="font-['JetBrains_Mono'] text-[12px] tracking-[0.08em] text-[#7A7D85]">
                  {statusText}
                </span>
              </div>
            </div>
          </div>

          {/* Results Area */}
          <div ref={resultsRef} className="max-w-[640px] mx-auto opacity-0">
            {searchComplete && (
              <div className="bg-[#141821]/60 border border-[#E2DFD8]/10 rounded-2xl p-8 backdrop-blur-sm">
                <div className="text-center">
                  <span className="font-['JetBrains_Mono'] text-[12px] uppercase tracking-[0.12em] text-[#4A4D55] block mb-3">
                    Search Results
                  </span>
                  <p className="font-['Inter'] font-light text-[#7A7D85] text-sm mb-6">
                    No records found for {firstName} {lastName}.
                  </p>
                  <button
                    onClick={handleReset}
                    className="px-8 py-3 rounded-full border border-[#E2DFD8]/30 bg-[#E2DFD8]/10 font-['JetBrains_Mono'] text-[12px] uppercase tracking-[0.12em] text-[#E2DFD8] hover:bg-[#E2DFD8]/15 hover:border-[#E2DFD8]/50 transition-all interactive"
                  >
                    New Search
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
};

export default CourtSearchPage;
