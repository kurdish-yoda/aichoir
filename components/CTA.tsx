
import React, { useState } from 'react';

const CTA: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ email: '', message: '' });
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('sending');
    try {
      const res = await fetch('https://formsubmit.co/ajax/contact@aichoir.xyz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          message: formData.message,
          _subject: 'New inquiry from aichoir.xyz',
        }),
      });
      if (res.ok) {
        setStatus('sent');
      } else {
        setStatus('error');
      }
    } catch {
      setStatus('error');
    }
  };

  return (
    <section id="contact" className="py-[140px] md:py-[180px] bg-[#0E1117] relative overflow-hidden">
      {/* Subtle Warm Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-[#D4C4B0] rounded-full blur-[140px] opacity-[0.05] pointer-events-none" />

      <div className="container mx-auto px-6 max-w-[1100px] relative z-10 text-center">
        <h2 className="font-['Syne'] font-bold text-[clamp(2rem,5vw,3.5rem)] text-[#E2DFD8] mb-8">
          Let's find your leverage points.
        </h2>

        <p className="font-['Inter'] font-light text-[18px] text-[#7A7D85] max-w-[480px] mx-auto mb-14 leading-[1.7]">
          Book a free 30-minute call. We'll talk about your workflow, your team, and whether AI actually makes sense for you. No pitch. No pressure.
        </p>

        <div className="flex flex-col items-center gap-6">
          <a
            href="https://calendly.com/ariyanwasi/30min"
            target="_blank"
            rel="noopener noreferrer"
            className="px-12 py-5 rounded-full border border-[#E2DFD8]/20 font-['Inter'] font-medium text-[17px] text-[#E2DFD8] hover:bg-[#E2DFD8]/05 hover:border-[#E2DFD8]/40 transition-all shadow-[0_0_40px_rgba(212,196,176,0.05)] interactive inline-block"
          >
            Book Your Free Call
          </a>

          {!showForm ? (
            <button
              onClick={() => setShowForm(true)}
              className="font-['Inter'] text-[13px] text-[#4A4D55] tracking-wide hover:text-[#7A7D85] transition-colors interactive"
            >
              or send us a message at <span className="text-[#7A7D85]">contact@aichoir.xyz</span>
            </button>
          ) : status !== 'sent' ? (
            <form onSubmit={handleSubmit} className="w-full max-w-[420px] mt-4 flex flex-col gap-4">
              <input
                type="email"
                required
                placeholder="Your email"
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                className="w-full px-5 py-3 rounded-lg border font-['Inter'] text-[14px] focus:outline-none transition-colors"
                style={{ backgroundColor: 'rgba(226,223,216,0.05)', borderColor: 'rgba(226,223,216,0.1)', color: '#E2DFD8' }}
              />
              <textarea
                required
                placeholder="Your message"
                rows={4}
                value={formData.message}
                onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
                className="w-full px-5 py-3 rounded-lg border font-['Inter'] text-[14px] focus:outline-none transition-colors resize-none"
                style={{ backgroundColor: 'rgba(226,223,216,0.05)', borderColor: 'rgba(226,223,216,0.1)', color: '#E2DFD8' }}
              />
              {status === 'error' && (
                <div className="font-['Inter'] text-[13px] text-red-400">
                  Something went wrong. Please try again.
                </div>
              )}
              <div className="flex gap-3 justify-center">
                <button
                  type="submit"
                  disabled={status === 'sending'}
                  className="px-8 py-3 rounded-full border border-[#E2DFD8]/20 font-['Inter'] font-medium text-[14px] text-[#E2DFD8] hover:bg-[#E2DFD8]/05 hover:border-[#E2DFD8]/40 transition-all interactive disabled:opacity-50"
                >
                  {status === 'sending' ? 'Sending...' : 'Send Message'}
                </button>
                <button
                  type="button"
                  onClick={() => { setShowForm(false); setFormData({ email: '', message: '' }); }}
                  className="px-6 py-3 font-['Inter'] text-[13px] text-[#4A4D55] hover:text-[#7A7D85] transition-colors interactive"
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="font-['Inter'] text-[14px] text-[#7A7D85] mt-4">
              Thanks! We'll get back to you soon.
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default CTA;
