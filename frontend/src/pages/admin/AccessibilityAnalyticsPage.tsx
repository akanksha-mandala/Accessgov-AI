import React, { useEffect, useState } from 'react';
import { analyticsService, AccessibilityAnalytics } from '../../services/analyticsService';
import { Eye, Volume2, ZoomIn, ShieldCheck } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const AccessibilityAnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AccessibilityAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsService.getAccessibilityAnalytics().then((res) => {
      setData(res);
      setLoading(false);
    });
  }, []);

  if (loading || !data) {
    return <div className="p-8 text-center text-xs text-slate-400">Loading accessibility telemetry analytics...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Accessibility Telemetry Intelligence</h1>
        <p className="text-xs text-slate-500">WCAG 2.1 AA telemetry trends, font scale adjustments & screen reader usage</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-blue-50 text-gov-blue rounded-lg">
            <Eye className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Total Telemetry Events</p>
            <h3 className="text-2xl font-bold text-slate-800">{data.total_telemetry_events}</h3>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg">
            <Volume2 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Screen Reader Sessions</p>
            <h3 className="text-2xl font-bold text-slate-800">{data.screen_reader_users}</h3>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="p-3 bg-amber-50 text-gov-gold rounded-lg">
            <ZoomIn className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-slate-500 font-medium">High Contrast Toggles</p>
            <h3 className="text-2xl font-bold text-slate-800">
              {data.contrast_mode_distribution.find((m) => m.mode === 'high-contrast')?.count || 0}
            </h3>
          </div>
        </div>
      </div>

      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-800">Font Scale Preference Distribution</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.font_scale_distribution}>
              <XAxis dataKey="scale" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#1e3a8a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default AccessibilityAnalyticsPage;
