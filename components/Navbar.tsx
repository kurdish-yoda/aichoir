
import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import gsap from 'gsap';

const Navbar: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const mobileMenuRef = useRef<HTMLDivElement>(null);
  const line1Ref = useRef<HTMLDivElement>(null);
  const line2Ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 80);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    if (isMobileOpen) {
      document.body.style.overflow = 'hidden';
      gsap.to(mobileMenuRef.current, { opacity: 1, duration: 0.3, ease: 'power2.out' });
      gsap.to(mobileMenuRef.current?.querySelectorAll('.mobile-link') || [], {
        y: 0, opacity: 1, stagger: 0.08, duration: 0.5, ease: 'power2.out', delay: 0.1
      });
      gsap.to(line1Ref.current, { rotate: 45, y: 3, width: 24, duration: 0.3 });
      gsap.to(line2Ref.current, { rotate: -45, y: -3, width: 24, duration: 0.3 });
    } else {
      document.body.style.overflow = '';
      gsap.to(mobileMenuRef.current, { opacity: 0, duration: 0.2, ease: 'power2.in' });
      gsap.to(line1Ref.current, { rotate: 0, y: 0, width: 24, duration: 0.3 });
      gsap.to(line2Ref.current, { rotate: 0, y: 0, width: 16, duration: 0.3 });
    }
  }, [isMobileOpen]);

  // Close menu on route change
  useEffect(() => {
    setIsMobileOpen(false);
  }, [location.pathname]);

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    setIsMobileOpen(false);
    if (location.pathname === '/') {
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth' });
      }
    } else {
      navigate(`/#${id}`);
    }
  };

  const isCourtSearch = location.pathname === '/court-search';

  return (
    <nav className={`fixed top-0 left-0 w-full transition-all duration-500 h-[72px] flex items-center ${
      isMobileOpen ? 'z-[60] bg-transparent' : isScrolled ? 'z-50 bg-[#0E1117]/80 backdrop-blur-xl border-b border-[#E2DFD8]/05' : 'z-50 bg-transparent'
    }`}>
      <div className="container mx-auto px-6 max-w-[1100px] flex justify-between items-center">
        <Link to="/" className="font-['Syne'] font-extrabold text-xl tracking-tight text-[#E2DFD8] interactive relative z-[60]">
          AI CHOIR
        </Link>

        <div className="hidden md:flex items-center gap-10">
          <div className="flex gap-8">
            <Link
              to="/court-search"
              className={`font-['Inter'] text-[13px] transition-colors tracking-wide interactive ${
                isCourtSearch ? 'text-[#E2DFD8]' : 'text-[#7A7D85] hover:text-[#E2DFD8]'
              }`}
            >
              Court Search
            </Link>
          </div>

          <a
            href="#contact"
            onClick={(e) => handleNavClick(e, 'contact')}
            className="px-6 py-2.5 rounded-full border border-[#E2DFD8]/15 font-['Inter'] font-medium text-[13px] text-[#E2DFD8] hover:bg-[#E2DFD8]/05 hover:border-[#E2DFD8]/30 transition-all interactive"
          >
            Book a Call
          </a>
        </div>

        {/* Mobile Menu Toggle */}
        <button
          className="md:hidden flex flex-col gap-1.5 interactive relative z-[60]"
          onClick={() => setIsMobileOpen(!isMobileOpen)}
          aria-label="Toggle menu"
        >
          <div ref={line1Ref} className="w-6 h-[1px] bg-[#E2DFD8] origin-center"></div>
          <div ref={line2Ref} className="w-4 h-[1px] bg-[#E2DFD8] ml-auto origin-center"></div>
        </button>
      </div>

      {/* Mobile Menu Overlay — portaled to body to escape backdrop-blur containing block */}
      {createPortal(
        <div
          ref={mobileMenuRef}
          className={`fixed inset-0 z-[55] bg-[#0E1117] flex flex-col items-center justify-center gap-10 opacity-0 md:hidden ${
            isMobileOpen ? 'pointer-events-auto' : 'pointer-events-none'
          }`}
        >
          {/* Close button */}
          <button
            onClick={() => setIsMobileOpen(false)}
            className="absolute top-6 right-6 w-10 h-10 flex items-center justify-center"
            aria-label="Close menu"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="#E2DFD8" strokeWidth="1.5" strokeLinecap="round">
              <line x1="4" y1="4" x2="16" y2="16" />
              <line x1="16" y1="4" x2="4" y2="16" />
            </svg>
          </button>

          <Link
            to="/court-search"
            className="mobile-link font-['Inter'] font-medium text-[15px] text-[#E2DFD8] opacity-0 translate-y-4 px-8 py-3 rounded-full border border-[#E2DFD8]/15"
            onClick={() => setIsMobileOpen(false)}
          >
            Court Search
          </Link>
          <a
            href="#contact"
            onClick={(e) => handleNavClick(e, 'contact')}
            className="mobile-link font-['Inter'] font-medium text-[15px] text-[#E2DFD8] opacity-0 translate-y-4 px-8 py-3 rounded-full border border-[#E2DFD8]/15"
          >
            Book a Call
          </a>
        </div>,
        document.body
      )}
    </nav>
  );
};

export default Navbar;
