
import React from 'react';

const TrustBar: React.FC = () => {
  const companies = ['Meridian Health', 'Apex Logistics', 'Folio Studio', 'Northway Partners', 'Redbrick Capital'];

  return (
    <div className="border-y border-[#E2DFD8]/06 py-10 bg-[#0E1117] relative z-10">
      <div className="container mx-auto px-6 max-w-[1100px] flex flex-col md:flex-row items-center gap-8 md:gap-12">
        <span className="font-['JetBrains_Mono'] text-[12px] uppercase tracking-[0.12em] text-[#4A4D55]">
          TRUSTED BY
        </span>
        
        <div className="flex flex-wrap justify-center md:justify-start gap-x-8 gap-y-4">
          {companies.map((company, i) => (
            <React.Fragment key={company}>
              <span className="font-['Inter'] text-[14px] text-[#4A4D55] whitespace-nowrap">
                {company}
              </span>
              {i < companies.length - 1 && (
                <span className="hidden md:inline text-[#4A4D55] opacity-30">·</span>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TrustBar;
