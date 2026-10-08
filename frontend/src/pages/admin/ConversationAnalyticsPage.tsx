import React, { useEffect, useState } from 'react';
import { analyticsService, ConversationAnalytics } from '../../services/analyticsService';
import { MessageSquare, Clock, AlertTriangle, Layers } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#1e3a8a', '#d97706', '#059669', '#dc2626'];

export const ConversationAnalyticsPage: React.FC = () => {
  const [data, setData] = useState<ConversationAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsService.getConversationAnalytics().then((res) => {
      setData(res);
      setLoading(false);
    });
  }, []);

  if (loading || !data) {
    return <div className="p-8 text-center text-xs text-slate-400">Loading conversation analytics...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Conversation Intelligence Analytics</h1>
        <p className="text-xs text-slate-500">AI agent response latency, language usage & intent routing metrics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-500 font-medium">Conversations Today</p>
          <h3 className="text-2xl font-bold text-slate-800 mt-1">{data.conversations_today}</h3>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-500 font-medium">Active Sessions Today</p>
          <h3 className="text-2xl font-bold text-slate-800 mt-1">{data.active_sessions_today}</h3>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-500 font-medium">Avg Response Latency</p>
          <h3 className="text-2xl font-bold text-slate-800 mt-1">{data.avg_latency_ms} ms</h3>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-500 font-medium">Fallback Response Count</p>
          <h3 className="text-2xl font-bold text-slate-800 mt-1">{data.fallback_count}</h3>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-800">Language Usage Distribution</h3>
          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.language_distribution}
                  dataKey="count"
                  nameKey="language"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {data.language_distribution.map((_, i) => (
                    <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-sm text-slate-800">Intent Routing Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.intent_distribution}>
                <XAxis dataKey="intent" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#d97706" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationAnalyticsPage;
