
import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Hero from '../components/Hero';
import TrustBar from '../components/TrustBar';
import ProblemStatement from '../components/ProblemStatement';
import Features from '../components/Features';
import Process from '../components/Process';
import TechStack from '../components/TechStack';
import ScalpelStatement from '../components/ScalpelStatement';
import Stats from '../components/Stats';
import Testimonial from '../components/Testimonial';
import CTA from '../components/CTA';

const LandingPage: React.FC = () => {
  const location = useLocation();

  useEffect(() => {
    if (location.hash) {
      const id = location.hash.replace('#', '');
      const timer = setTimeout(() => {
        const el = document.getElementById(id);
        if (el) {
          el.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [location.hash]);

  return (
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
  );
};

export default LandingPage;
