import React from 'react';

export const ReadinessGauge: React.FC<{ score: number; size?: number }> = ({ score, size = 60 }) => {
  const strokeWidth = 6;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const getColor = (val: number) => {
    if (val >= 80) return '#059669'; // Emerald
    if (val >= 50) return '#d97706'; // Gold/Amber
    return '#dc2626'; // Red
  };

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#e2e8f0"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        {/* Readiness progress ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={getColor(score)}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-500 ease-out"
        />
      </svg>
      <span className="absolute text-xs font-bold text-slate-700">
        {score}%
      </span>
    </div>
  );
};

export default ReadinessGauge;
