
import React, { useEffect, useState } from 'react';

const Navbar: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 80);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 left-0 w-full z-50 transition-all duration-500 h-[72px] flex items-center ${
      isScrolled ? 'bg-[#0E1117]/80 backdrop-blur-xl border-b border-[#E2DFD8]/05' : 'bg-transparent'
    }`}>
      <div className="container mx-auto px-6 max-w-[1100px] flex justify-between items-center">
        <div className="font-['Syne'] font-extrabold text-xl tracking-tight text-[#E2DFD8] interactive">
          AI CHOIR
        </div>
        
        <div className="hidden md:flex items-center gap-10">
          <div className="flex gap-8">
            {['Process', 'Results', 'About', 'Contact'].map((item) => (
              <a 
                key={item} 
                href={`#${item.toLowerCase()}`}
                className="font-['Inter'] text-[13px] text-[#7A7D85] hover:text-[#E2DFD8] transition-colors tracking-wide interactive"
              >
                {item}
              </a>
            ))}
          </div>
          
          <button className="px-6 py-2.5 rounded-full border border-[#E2DFD8]/15 font-['Inter'] font-medium text-[13px] text-[#E2DFD8] hover:bg-[#E2DFD8]/05 hover:border-[#E2DFD8]/30 transition-all interactive">
            Book a Call
          </button>
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
