import React from 'react';
import { CheckCircle2, AlertTriangle, FileText, Lock } from 'lucide-react';
import { UserDocument } from '../../services/documentService';
import ReadinessGauge from './ReadinessGauge';

export const OCRCard: React.FC<{ doc: UserDocument }> = ({ doc }) => {
  const isQualityWarning = doc.readability_score < 75;
  const isReady = doc.readiness_score >= 80;

  return (
    <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">

      {/* Document Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-blue-50 text-gov-blue rounded-xl">
            <FileText className="w-6 h-6" />
          </div>

          <div>
            <h3 className="font-bold text-sm text-slate-800">
              {doc.document_type}
            </h3>

            <p className="text-[11px] text-slate-400 font-mono">
              {doc.file_name}
            </p>
          </div>
        </div>

        {/* REAL OCR READABILITY SCORE */}
        <ReadinessGauge
          score={doc.readability_score}
          size={50}
        />
      </div>

      {/* Real OCR Metrics */}
      <div className="space-y-2 pt-2 border-t border-slate-100">

        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-500 font-medium">
            OCR Readability
          </span>

          <span className="font-bold text-slate-800">
            {doc.readability_score.toFixed(0)}%
          </span>
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-500">
            OCR Confidence
          </span>

          <span className="font-semibold text-slate-700">
            {doc.ocr_confidence.toFixed(0)}%
          </span>
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-500">
            Image Sharpness
          </span>

          <span className="font-semibold text-slate-700">
            {doc.sharpness_score.toFixed(0)}%
          </span>
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-500">
            Application Readiness
          </span>

          <span className="font-semibold text-slate-700">
            {doc.readiness_score.toFixed(0)}%
          </span>
        </div>

      </div>

      {/* Inspection Status */}
      <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-100">

        <span className="text-slate-500 font-medium">
          Automated Inspection:
        </span>

        <span
          className={`flex items-center font-bold ${
            isQualityWarning
              ? 'text-amber-600'
              : isReady
              ? 'text-emerald-600'
              : 'text-amber-600'
          }`}
        >
          {isQualityWarning ? (
            <>
              <AlertTriangle className="w-3.5 h-3.5 mr-1" />
              Quality Warning
            </>
          ) : isReady ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
              Readable & Complete
            </>
          ) : (
            <>
              <AlertTriangle className="w-3.5 h-3.5 mr-1" />
              Readable but Incomplete
            </>
          )}
        </span>

      </div>

      {/* Actual Quality Issues */}
      {doc.quality_issues && doc.quality_issues.length > 0 && (
        <div className="bg-amber-50 p-3 rounded-lg border border-amber-200 text-amber-900 text-xs space-y-1">

          <p className="font-bold flex items-center">
            <AlertTriangle className="w-3.5 h-3.5 mr-1 text-amber-600" />
            Image Quality Issues
          </p>

          {doc.quality_issues.map((issue, index) => (
            <p
              key={index}
              className="text-[11px] text-amber-800"
            >
              • {issue}
            </p>
          ))}

        </div>
      )}

      {/* Extracted Fields */}
      {doc.extracted_fields &&
        Object.keys(doc.extracted_fields).length > 0 && (
          <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 space-y-1.5 text-xs">

            <div className="flex items-center text-slate-500 font-semibold text-[10px] uppercase tracking-wider mb-1">
              <Lock className="w-3 h-3 mr-1 text-slate-400" />
              Extracted Information (PII Masked)
            </div>

            {Object.entries(doc.extracted_fields).map(([key, val]) => (
              <div
                key={key}
                className="flex justify-between"
              >
                <span className="text-slate-500">
                  {key}:
                </span>

                <span className="font-mono text-slate-800 font-semibold">
                  {val}
                </span>
              </div>
            ))}

          </div>
        )}

    </div>
  );
};

export default OCRCard;

