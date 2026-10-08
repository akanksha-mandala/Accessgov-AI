import React, { useCallback, useEffect, useState } from 'react';
import {
  documentService,
  DocumentAnalytics,
} from '../../services/documentService';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export const DocumentAnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<DocumentAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAnalytics = useCallback(async () => {
    try {
      const data = await documentService.getAdminAnalytics();
      setAnalytics(data);
      setError(null);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          'Unable to load document analytics.'
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAnalytics();

    // Keep admin analytics synchronized with PostgreSQL.
    const interval = window.setInterval(loadAnalytics, 10000);

    return () => {
      window.clearInterval(interval);
    };
  }, [loadAnalytics]);

  if (loading) {
    return (
      <div className="p-8 text-center text-xs text-slate-400">
        Loading document telemetry...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <p className="text-xs text-red-600">{error}</p>

        <button
          type="button"
          onClick={loadAnalytics}
          className="mt-3 px-4 py-2 rounded-lg bg-slate-800 text-white text-xs font-semibold hover:bg-slate-700"
        >
          Retry
        </button>
      </div>
    );
  }

  const data: DocumentAnalytics = analytics || {
    total_documents: 0,
    successful_ocr: 0,
    quality_issues: 0,
    average_readiness: 0,
    document_types: [],
  };

  const verifiedRate =
    data.total_documents > 0
      ? Math.round(
          (data.successful_ocr / data.total_documents) * 100
        )
      : 0;

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold text-slate-800">
            Document Analytics & Readability Telemetry
          </h1>

          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            LIVE
          </span>
        </div>

        <p className="text-xs text-slate-500 mt-1">
          Anonymous aggregate document metrics synchronized with
          PostgreSQL
        </p>
      </div>

      {/* Privacy notice */}
      <div className="bg-blue-50 border border-blue-200 p-3 rounded-xl text-xs text-blue-900">
        <strong>Privacy Notice:</strong> only aggregate document
        metrics are shown. Citizen identities, Aadhaar numbers and
        uploaded files are never exposed to administrators.
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Metric
          label="Total Documents Uploaded"
          value={data.total_documents}
          sub={
            data.total_documents
              ? 'Live PostgreSQL records'
              : 'No documents uploaded yet'
          }
        />

        <Metric
          label="Verified Documents"
          value={data.successful_ocr}
          sub={
            data.total_documents
              ? `${verifiedRate}% verified`
              : '0% verified'
          }
        />

        <Metric
          label="Quality Issues / Rejected"
          value={data.quality_issues}
          sub={
            data.quality_issues
              ? 'Review/re-upload suggested'
              : 'None rejected'
          }
        />

        <Metric
          label="Readiness Score"
          value={`${data.average_readiness}%`}
          sub={
            data.average_readiness > 0
              ? 'Stored readiness metric'
              : 'OCR readiness not persisted yet'
          }
        />
      </div>

      {/* Document type breakdown */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-sm text-slate-800">
              Uploaded Document Type Breakdown
            </h3>

            <p className="text-[10px] text-slate-400 mt-1">
              Counts are calculated directly from uploaded_documents
            </p>
          </div>

          <span className="text-[10px] text-slate-400">
            Auto-refresh: 10s
          </span>
        </div>

        {data.document_types.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-400">
            No document analytics available yet.
          </div>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.document_types}>
                <XAxis
                  dataKey="type"
                  tick={{ fontSize: 10 }}
                  interval={0}
                />

                <YAxis
                  allowDecimals={false}
                  tick={{ fontSize: 10 }}
                />

                <Tooltip />

                <Bar
                  dataKey="count"
                  name="Documents"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

const Metric: React.FC<{
  label: string;
  value: React.ReactNode;
  sub: string;
}> = ({ label, value, sub }) => (
  <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
    <p className="text-xs text-slate-500 font-semibold">
      {label}
    </p>

    <h3 className="text-2xl font-bold text-slate-800 mt-1">
      {value}
    </h3>

    <p className="text-[10px] text-slate-400 font-semibold mt-1">
      {sub}
    </p>
  </div>
);

export default DocumentAnalyticsPage;
