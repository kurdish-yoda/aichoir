
import React, { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from '@studio-freight/lenis';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import CustomCursor from './components/CustomCursor';
import NoiseOverlay from './components/NoiseOverlay';
import BackgroundOrbs from './components/BackgroundOrbs';
import IntroSequence from './components/IntroSequence';
import LandingPage from './pages/LandingPage';
import CourtSearchPage from './pages/CourtSearchPage';

gsap.registerPlugin(ScrollTrigger);

const AppContent: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const lenisRef = useRef<Lenis | null>(null);
  const location = useLocation();

  useLayoutEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 2,
      infinite: false,
    });

    lenisRef.current = lenis;
    lenis.on('scroll', ScrollTrigger.update);

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
    };
  }, [location.pathname]);

  // Kill all ScrollTriggers on route change
  useEffect(() => {
    return () => {
      ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
    };
  }, [location.pathname]);

  // Scroll to top on route change (except hash navigation)
  useEffect(() => {
    if (!location.hash) {
      window.scrollTo(0, 0);
    }
  }, [location.pathname]);

  useEffect(() => {
    if (location.pathname === '/') {
      const timer = setTimeout(() => {
        setIsLoading(false);
      }, 2200);
      return () => clearTimeout(timer);
    } else {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isLoading) {
      const timer = setTimeout(() => {
        ScrollTrigger.refresh();
        if (lenisRef.current) {
          lenisRef.current.resize();
        }
      }, 150);
      return () => clearTimeout(timer);
    }
  }, [isLoading, location.pathname]);

  const showIntro = isLoading && location.pathname === '/';

  return (
    <div className={`relative bg-[#0E1117] ${showIntro ? 'h-screen overflow-hidden' : 'min-h-screen'}`}>
      {showIntro && <IntroSequence />}

      <div
        className={`relative z-10 transition-opacity duration-1000 ${
          showIntro ? 'opacity-0' : 'opacity-100'
        }`}
      >
        <CustomCursor />
        <NoiseOverlay />
        <BackgroundOrbs />

        <Navbar />

        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/court-search" element={<CourtSearchPage />} />
        </Routes>

        <Footer />
      </div>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
};

export default App;
