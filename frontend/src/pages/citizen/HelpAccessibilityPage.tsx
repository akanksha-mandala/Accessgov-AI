import React from 'react';
import { useAccessibility, SUPPORTED_LANGUAGES, LanguageCode } from '../../context/AccessibilityContext';
import { Volume2, Eye, Globe, ZoomIn, HelpCircle, ShieldCheck, PhoneCall } from 'lucide-react';

export const HelpAccessibilityPage: React.FC = () => {
  const {
    fontScale,
    setFontScale,
    highContrast,
    setHighContrast,
    screenReaderEnabled,
    setScreenReaderEnabled,
    voiceAccessEnabled,
    setVoiceAccessEnabled,
    speakResponsesAloud,
    setSpeakResponsesAloud,
    selectedLanguage,
    setSelectedLanguage,
    resetAccessibility
  } = useAccessibility();

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Help & Accessibility Center</h1>
        <p className="text-xs text-slate-500">WCAG 2.1 AA accessibility controls, voice access commands, and public service helpline</p>
      </div>

      {/* Accessibility Control Panel */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
        <h3 className="font-bold text-sm text-slate-800 border-b border-slate-100 pb-3 flex items-center">
          <Eye className="w-4 h-4 mr-2 text-gov-blue" /> Personal Accessibility Preferences
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-xs">
          {/* Font Scaling */}
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
            <h4 className="font-bold text-slate-800 flex items-center">
              <ZoomIn className="w-4 h-4 mr-1.5 text-gov-blue" /> Text Size Scaling
            </h4>
            <p className="text-slate-500 text-[11px]">Adjust display font scaling across all portal elements.</p>
            <div className="flex items-center space-x-2">
              {[85, 100, 115, 130, 145].map((scale) => (
                <button
                  key={scale}
                  onClick={() => setFontScale(scale)}
                  className={`px-3 py-1.5 rounded font-bold transition ${
                    fontScale === scale
                      ? 'bg-gov-blue text-white shadow'
                      : 'bg-white border border-slate-300 text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  {scale}%
                </button>
              ))}
            </div>
          </div>

          {/* Language Selection */}
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
            <h4 className="font-bold text-slate-800 flex items-center">
              <Globe className="w-4 h-4 mr-1.5 text-gov-gold" /> System Language
            </h4>
            <p className="text-slate-500 text-[11px]">Select preferred language for text, AI assistant, and speech output.</p>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value as LanguageCode)}
              className="w-full bg-white text-slate-800 font-bold border border-slate-300 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-gov-blue"
            >
              {SUPPORTED_LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.nativeLabel} ({lang.label})
                </option>
              ))}
            </select>
          </div>

          {/* Voice Access Toggle */}
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
            <h4 className="font-bold text-slate-800 flex items-center">
              <Volume2 className="w-4 h-4 mr-1.5 text-purple-600" /> Voice Access Mode (Hands-Free)
            </h4>
            <p className="text-slate-500 text-[11px]">Enables continuous speech command recognition for blind citizens.</p>
            <button
              onClick={() => setVoiceAccessEnabled(!voiceAccessEnabled)}
              className={`px-4 py-2 rounded-lg font-bold transition shadow ${
                voiceAccessEnabled
                  ? 'bg-red-600 text-white'
                  : 'bg-gov-blue text-white hover:bg-blue-900'
              }`}
            >
              {voiceAccessEnabled ? 'Voice Access Active (Click to Turn Off)' : 'Activate Voice Access (Alt+V)'}
            </button>
          </div>

          {/* High Contrast & Speech Options */}
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
            <h4 className="font-bold text-slate-800 flex items-center">
              <ShieldCheck className="w-4 h-4 mr-1.5 text-emerald-600" /> Contrast & Speech Feedback
            </h4>
            <div className="space-y-2">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={highContrast}
                  onChange={(e) => setHighContrast(e.target.checked)}
                  className="rounded text-gov-blue"
                />
                <span className="font-semibold text-slate-700">Yellow-on-Black High Contrast Mode</span>
              </label>

              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={speakResponsesAloud}
                  onChange={(e) => setSpeakResponsesAloud(e.target.checked)}
                  className="rounded text-gov-blue"
                />
                <span className="font-semibold text-slate-700">Automatically Speak Assistant Responses</span>
              </label>
            </div>
          </div>
        </div>

        <div className="pt-2 text-right">
          <button
            onClick={resetAccessibility}
            className="text-xs text-slate-500 underline hover:text-slate-800 font-semibold"
          >
            Reset All Accessibility Settings to Default
          </button>
        </div>
      </div>

      {/* Official Support & Help Helpline */}
      <div className="bg-blue-900 text-white p-6 rounded-2xl shadow-md flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <PhoneCall className="w-5 h-5 text-gov-gold" />
            <h3 className="font-bold text-base">Toll-Free Public Helpline Assistance</h3>
          </div>
          <p className="text-xs text-slate-200">
            Need help navigating government schemes or submitting official forms? Call 24/7 toll-free support.
          </p>
        </div>
        <div className="text-right">
          <span className="text-lg font-bold text-gov-gold">1800-111-2026</span>
          <p className="text-[10px] text-slate-300 uppercase tracking-wider">Toll-Free All India</p>
        </div>
      </div>
    </div>
  );
};

export default HelpAccessibilityPage;
