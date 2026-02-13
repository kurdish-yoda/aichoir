
import React, { useEffect, useLayoutEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from '@studio-freight/lenis';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import TrustBar from './components/TrustBar';
import ProblemStatement from './components/ProblemStatement';
import Features from './components/Features';
import Process from './components/Process';
import TechStack from './components/TechStack';
import ScalpelStatement from './components/ScalpelStatement';
import Stats from './components/Stats';
import Testimonial from './components/Testimonial';
import CTA from './components/CTA';
import Footer from './components/Footer';
import CustomCursor from './components/CustomCursor';
import NoiseOverlay from './components/NoiseOverlay';
import BackgroundOrbs from './components/BackgroundOrbs';
import IntroSequence from './components/IntroSequence';

gsap.registerPlugin(ScrollTrigger);

const App: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const lenisRef = useRef<Lenis | null>(null);

  useLayoutEffect(() => {
    // Initialize Lenis with high-performance settings
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 2,
      infinite: false,
    });

    lenisRef.current = lenis;

    // Connect GSAP ScrollTrigger to Lenis
    lenis.on('scroll', ScrollTrigger.update);

    // Standard high-performance RAF loop
    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
    };
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2200);
    return () => clearTimeout(timer);
  }, []);

  // Sync scroll height and triggers after layout changes
  useEffect(() => {
    if (!isLoading) {
      const timer = setTimeout(() => {
        ScrollTrigger.refresh();
        if (lenisRef.current) {
          lenisRef.current.resize();
        }
        window.scrollTo(0, 0);
      }, 150);
      return () => clearTimeout(timer);
    }
  }, [isLoading]);

  return (
    <div className={`relative bg-[#0E1117] ${isLoading ? 'h-screen overflow-hidden' : 'min-h-screen'}`}>
      {isLoading && <IntroSequence />}
      
      <div 
        className={`relative z-10 transition-opacity duration-1000 ${
          isLoading ? 'opacity-0' : 'opacity-100'
        }`}
      >
        <CustomCursor />
        <NoiseOverlay />
        <BackgroundOrbs />
        
        <Navbar />
        
        <main className="relative w-full overflow-x-hidden">
          <Hero />
          <TrustBar />
          <ProblemStatement />
          <Features />
          <Process />
          <TechStack />
          <ScalpelStatement />
          <Stats />
          <Testimonial />
          <CTA />
        </main>
        
        <Footer />
      </div>
    </div>
  );
};

export default App;
