import React, { useEffect, useState } from 'react';
import { applicationService, ApplicationDraft } from '../../services/applicationService';
import { servicesService } from '../../services/servicesService';
import {
  AlertTriangle,
  Clock,
  FileText,
} from 'lucide-react';

interface ApplicationProgress {
  readyCount: number;
  requiredCount: number;
  percentage: number;
}

export const ApplicationStatusPage: React.FC = () => {
  const [drafts, setDrafts] = useState<ApplicationDraft[]>([]);
  const [progress, setProgress] = useState<
    Record<string, ApplicationProgress>
  >({});

  useEffect(() => {
    const loadStatus = async () => {
      const savedDrafts = applicationService.getDrafts();

      setDrafts(savedDrafts);

      if (savedDrafts.length === 0) {
        return;
      }

      const progressMap: Record<string, ApplicationProgress> = {};

      for (const app of savedDrafts) {
        try {
          const service = await servicesService.getServiceById(
            app.service_id
          );

          const requiredCount =
            service.required_documents?.length || 0;

          /*
           * Application completion is currently document-preparation
           * progress. The saved application percentage is therefore
           * used to determine how many required documents are ready.
           *
           * Example:
           * 40% of 5 required documents = 2 ready.
           */
          const readyCount =
            requiredCount > 0
              ? Math.round(
                  (app.completion_percentage / 100) *
                    requiredCount
                )
              : 0;

          progressMap[app.id] = {
            readyCount,
            requiredCount,
            percentage: app.completion_percentage || 0,
          };
        } catch (error) {
          console.error(
            `Failed to load service information for ${app.service_name}:`,
            error
          );

          progressMap[app.id] = {
            readyCount: 0,
            requiredCount: 0,
            percentage: app.completion_percentage || 0,
          };
        }
      }

      setProgress(progressMap);
    };

    loadStatus();
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-800">
          Application Tracking & Status
        </h1>

        <p className="text-xs text-slate-500">
          Track your saved application preparation progress and
          document readiness
        </p>
      </div>

      {/* Prototype Status Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl text-amber-900 text-xs flex items-start space-x-3">
        <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />

        <div>
          <h4 className="font-bold">
            Prototype Status Information
          </h4>

          <p className="text-amber-800 mt-0.5">
            AccessGov AI provides application preparation,
            document-readiness scoring, and guidance. Official
            government verification, submission, and certificate
            issuance are handled through the relevant government
            authorities and portals.
          </p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
        <h3 className="font-bold text-sm text-slate-800">
          Tracked Applications
        </h3>

        {drafts.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-400">
            <FileText className="w-10 h-10 mx-auto mb-3 text-slate-300" />

            No application records tracked yet. Start a service
            application to view status updates.
          </div>
        ) : (
          <div className="space-y-4">
            {drafts.map((app) => {
              const calculated = progress[app.id];

              const readyCount =
                calculated?.readyCount ?? 0;

              const requiredCount =
                calculated?.requiredCount ?? 0;

              const percentage =
                calculated?.percentage ??
                app.completion_percentage ??
                0;

              return (
                <div
                  key={app.id}
                  className="p-4 rounded-lg border border-slate-200 bg-slate-50/50 space-y-4"
                >
                  {/* Header */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-3">
                    <div>
                      <span className="text-[10px] bg-blue-100 text-gov-blue font-bold px-2 py-0.5 rounded">
                        {app.service_code}
                      </span>

                      <h4 className="font-bold text-sm text-slate-800 mt-1">
                        {app.service_name}
                      </h4>
                    </div>

                    <span className="text-xs font-bold px-3 py-1 rounded bg-amber-100 text-amber-900 border border-amber-300">
                      Status: {app.status}
                    </span>
                  </div>

                  {/* Progress */}
                  <div>
                    <div className="flex items-center justify-between text-xs mb-2">
                      <span className="text-slate-500 font-medium">
                        Application Progress
                      </span>

                      <span className="font-bold text-gov-blue">
                        {percentage}% Prepared
                      </span>
                    </div>

                    <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-gov-blue h-2 rounded-full transition-all duration-500"
                        style={{
                          width: `${percentage}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Details */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-slate-600">
                    <div>
                      <span className="text-slate-400 block text-[10px] font-bold uppercase">
                        Completion
                      </span>

                      <span className="font-bold text-slate-800">
                        {percentage}% Prepared
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-400 block text-[10px] font-bold uppercase">
                        Documents Ready
                      </span>

                      <span className="font-bold text-emerald-600">
                        {readyCount} of {requiredCount} Ready
                      </span>
                    </div>

                    <div>
                      <span className="text-slate-400 block text-[10px] font-bold uppercase">
                        Last Activity
                      </span>

                      <span className="font-medium text-slate-700 flex items-center">
                        <Clock className="w-3.5 h-3.5 mr-1 text-slate-400" />

                        {new Date(
                          app.last_saved_at
                        ).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {/* Preparation status */}
                  <div className="pt-2">
                    <div className="text-[11px] text-slate-500">
                      Documents shown here represent{' '}
                      <span className="font-semibold">
                        AccessGov AI vault readiness
                      </span>
                      . They are not government-verified documents.
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default ApplicationStatusPage;