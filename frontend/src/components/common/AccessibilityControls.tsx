import React from 'react';
import { useAccessibility } from '../../context/AccessibilityContext';
import { ZoomIn, ZoomOut, Eye, Volume2, RotateCcw } from 'lucide-react';

export const AccessibilityControls: React.FC = () => {
  const {
    fontScale,
    setFontScale,
    highContrast,
    setHighContrast,
    screenReaderEnabled,
    setScreenReaderEnabled,
    resetAccessibility
  } = useAccessibility();

  return (
    <div className="flex items-center space-x-1 bg-blue-900/60 p-1 rounded-md text-white text-xs">
      {/* Font Zoom Controls */}
      <button
        onClick={() => setFontScale(Math.max(85, fontScale - 10))}
        title="Decrease Font Size"
        className="p-1.5 hover:bg-blue-800 rounded text-slate-200 hover:text-white"
      >
        <ZoomOut className="w-3.5 h-3.5" />
      </button>
      <span className="px-1 text-[11px] font-mono">{fontScale}%</span>
      <button
        onClick={() => setFontScale(Math.min(145, fontScale + 10))}
        title="Increase Font Size"
        className="p-1.5 hover:bg-blue-800 rounded text-slate-200 hover:text-white"
      >
        <ZoomIn className="w-3.5 h-3.5" />
      </button>

      {/* High Contrast Toggle */}
      <button
        onClick={() => setHighContrast(!highContrast)}
        title="Toggle High Contrast Mode"
        className={`p-1.5 rounded transition ${
          highContrast ? 'bg-gov-gold text-slate-900 font-bold' : 'hover:bg-blue-800 text-slate-200'
        }`}
      >
        <Eye className="w-3.5 h-3.5" />
      </button>

      {/* Screen Reader Toggle */}
      <button
        onClick={() => setScreenReaderEnabled(!screenReaderEnabled)}
        title="Toggle Screen Reader Mode"
        className={`p-1.5 rounded transition ${
          screenReaderEnabled ? 'bg-emerald-500 text-white font-bold' : 'hover:bg-blue-800 text-slate-200'
        }`}
      >
        <Volume2 className="w-3.5 h-3.5" />
      </button>

      {/* Reset */}
      <button
        onClick={resetAccessibility}
        title="Reset Accessibility Settings"
        className="p-1.5 hover:bg-blue-800 rounded text-slate-200 hover:text-white"
      >
        <RotateCcw className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};

export default AccessibilityControls;
