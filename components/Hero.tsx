
import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';

const Hero: React.FC = () => {
  const sectionRef = useRef<HTMLElement>(null);
  const headlineRef = useRef<HTMLHeadingElement>(null);
  const subtitleRef = useRef<HTMLParagraphElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const scrollVelocity = useRef(0);
  const mousePos = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let w: number, h: number;
    const particleCount = 1200; // Significantly increased for more density
    const particles: Particle[] = [];

    const resize = () => {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    };

    class Particle {
      x: number; y: number; z: number;
      prevZ: number;
      size: number; opacity: number;
      color: string;

      constructor() {
        this.x = 0; this.y = 0; this.z = 0; this.prevZ = 0;
        this.size = 0; this.opacity = 0; this.color = '';
        this.reset(true);
      }

      reset(init = false) {
        // Wider spread for more perspective depth
        this.x = (Math.random() - 0.5) * 4500;
        this.y = (Math.random() - 0.5) * 4500;
        this.z = init ? Math.random() * 2000 : 2000;
        this.prevZ = this.z;
        this.size = 1.2 + Math.random() * 3.5; // Larger particles
        this.opacity = 0.2 + Math.random() * 0.7; // Brighter
        
        // Subtle color variance like the reference (mostly white, some faint warm/cool tones)
        const tones = ['#E2DFD8', '#E2DFD8', '#E2DFD8', '#F2EFE8', '#D8D5CC'];
        this.color = tones[Math.floor(Math.random() * tones.length)];
      }

      update(speed: number) {
        this.prevZ = this.z;
        // Base movement + aggressive multiplier for scroll velocity
        const moveAmount = 2.5 + (speed * 180);
        this.z -= moveAmount;
        
        if (this.z <= 1) {
          this.reset();
        }
      }

      draw() {
        if (!ctx) return;
        
        // Current projection
        const scale = 1200 / (1200 - (1200 - this.z));
        const px = (this.x + mousePos.current.x * 80) * scale + w / 2;
        const py = (this.y + mousePos.current.y * 80) * scale + h / 2;

        // Previous projection for motion blur streaks
        const prevScale = 1200 / (1200 - (1200 - this.prevZ));
        const ppx = (this.x + mousePos.current.x * 80) * prevScale + w / 2;
        const ppy = (this.y + mousePos.current.y * 80) * prevScale + h / 2;

        if (px > -100 && px < w + 100 && py > -100 && py < h + 100) {
          const alpha = this.opacity * (this.z / 2000);
          const s = this.size * scale;
          
          // Draw streak based on speed
          ctx.beginPath();
          ctx.strokeStyle = this.color;
          ctx.globalAlpha = alpha;
          ctx.lineWidth = s;
          ctx.lineCap = 'round';
          ctx.moveTo(px, py);
          ctx.lineTo(ppx, ppy);
          ctx.stroke();

          // Core point for more "sparkle"
          ctx.beginPath();
          ctx.fillStyle = this.color;
          ctx.globalAlpha = alpha * 0.8;
          ctx.arc(px, py, s / 1.5, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }

    const init = () => {
      resize();
      for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
      }
    };

    const render = () => {
      ctx.clearRect(0, 0, w, h);
      ctx.globalCompositeOperation = 'lighter'; // Makes overlapping particles glow
      particles.forEach(p => {
        p.update(scrollVelocity.current);
        p.draw();
      });
      animationFrameId = requestAnimationFrame(render);
    };

    const handleScroll = () => {
      const currentScroll = window.scrollY;
      // Faster response to scroll for a "punchier" feel
      const velocity = currentScroll / 4000;
      scrollVelocity.current = Math.min(velocity, 0.8);
    };

    const handleMouseMove = (e: MouseEvent) => {
      mousePos.current = {
        x: (e.clientX / window.innerWidth) - 0.5,
        y: (e.clientY / window.innerHeight) - 0.5
      };
    };

    init();
    render();
    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // Text Entrance Animations
  useEffect(() => {
    const lines = headlineRef.current?.querySelectorAll('.line-inner');
    if (!lines) return;

    const tl = gsap.timeline();

    tl.fromTo(lines, 
      { y: 120, opacity: 0, rotate: 2 },
      { y: 0, opacity: 1, rotate: 0, duration: 1.6, stagger: 0.15, ease: 'power4.out' }
    )
    .fromTo(subtitleRef.current,
      { y: 30, opacity: 0 },
      { y: 0, opacity: 1, duration: 1, ease: 'power2.out' },
      '-=1.0'
    )
    .fromTo(ctaRef.current,
      { y: 20, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.8, ease: 'power2.out' },
      '-=0.8'
    );
  }, []);

  return (
    <section ref={sectionRef} className="min-h-screen flex items-center pt-0 md:pt-24 pb-20 overflow-hidden relative bg-[#0E1117]">
      {/* Intense 3D Particle Canvas Background */}
      <canvas 
        ref={canvasRef} 
        className="absolute inset-0 w-full h-full pointer-events-none opacity-60 z-0"
      />
      
      {/* Vignette for more depth */}
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(circle_at_center,transparent_20%,rgba(14,17,23,0.4)_100%)] z-[1]" />

      <div className="container mx-auto px-6 max-w-[1100px] relative z-10">
        <div className="max-w-[850px]">
          <span className="font-['JetBrains_Mono'] text-[12px] uppercase tracking-[0.12em] text-[#4A4D55] mb-8 block">
            AI INTEGRATION AGENCY
          </span>
          
          <h1 ref={headlineRef} className="font-['Syne'] font-bold text-[clamp(2.8rem,7vw,6.4rem)] leading-[0.98] text-[#E2DFD8] mb-10 tracking-tighter">
            <div className="overflow-hidden mb-2">
              <span className="line-inner block">Your workflow,</span>
            </div>
            <div className="overflow-hidden">
              <span className="line-inner block">surgically optimized.</span>
            </div>
          </h1>
          
          <p ref={subtitleRef} className="font-['Inter'] font-light text-[18px] md:text-[22px] text-[#7A7D85] leading-[1.6] max-w-[620px] mb-12 opacity-0">
            We don't automate everything. We work alongside you to find exactly where AI removes the busywork — and where the human touch should stay.
          </p>
          
          <div ref={ctaRef} className="flex flex-col sm:flex-row items-center gap-6 sm:gap-10 opacity-0">
            <a href="#process" onClick={(e) => { e.preventDefault(); document.getElementById('process')?.scrollIntoView({ behavior: 'smooth' }); }} className="group relative px-10 py-4 rounded-full border border-[#E2DFD8]/20 font-['Inter'] font-medium text-[16px] text-[#E2DFD8] overflow-hidden transition-all interactive inline-block">
              <span className="relative z-10">See How We Work</span>
              <div className="absolute inset-0 bg-[#E2DFD8]/05 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
            </a>
            <a href="#contact" className="font-['Inter'] text-[14px] text-[#4A4D55] hover:text-[#E2DFD8] transition-colors flex items-center gap-2 interactive">
              or book a free call <span className="text-[18px]">→</span>
            </a>
          </div>
        </div>
      </div>
      
      <div className="absolute bottom-10 left-6 md:left-auto md:right-12 flex items-center gap-6 rotate-0 md:rotate-90 origin-left md:origin-right">
        <div className="font-['JetBrains_Mono'] text-[10px] tracking-[0.2em] text-[#4A4D55] uppercase whitespace-nowrap">
          Scroll to explore
        </div>
        <div className="w-12 h-[1px] bg-[#E2DFD8]/20"></div>
      </div>
    </section>
  );
};

export default Hero;
