
import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const Navbar: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 80);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
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
    <nav className={`fixed top-0 left-0 w-full z-50 transition-all duration-500 h-[72px] flex items-center ${
      isScrolled ? 'bg-[#0E1117]/80 backdrop-blur-xl border-b border-[#E2DFD8]/05' : 'bg-transparent'
    }`}>
      <div className="container mx-auto px-6 max-w-[1100px] flex justify-between items-center">
        <Link to="/" className="font-['Syne'] font-extrabold text-xl tracking-tight text-[#E2DFD8] interactive">
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

        {/* Mobile Menu Icon Placeholder */}
        <div className="md:hidden flex flex-col gap-1.5 interactive">
          <div className="w-6 h-[1px] bg-[#E2DFD8]"></div>
          <div className="w-4 h-[1px] bg-[#E2DFD8] ml-auto"></div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
