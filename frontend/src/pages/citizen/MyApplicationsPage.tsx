import React, { useState, useEffect } from 'react';
import { applicationService, ApplicationDraft } from '../../services/applicationService';
import { Link, useNavigate } from 'react-router-dom';
import { FileText, Clock, ArrowRight, Play, CheckCircle2, ShieldCheck } from 'lucide-react';

export const MyApplicationsPage: React.FC = () => {
  const [drafts, setDrafts] = useState<ApplicationDraft[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    setDrafts(applicationService.getDrafts());
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-800">My Saved Applications & Drafts</h1>
          <p className="text-xs text-slate-500">Continue saved application progress where you left off</p>
        </div>

        <Link
          to="/services"
          className="px-4 py-2 bg-gov-blue hover:bg-blue-900 text-white font-bold text-xs rounded-lg shadow transition"
        >
          + Start New Service Application
        </Link>
      </div>

      {drafts.length === 0 ? (
        <div className="bg-white p-8 rounded-xl border border-slate-200 text-center space-y-3">
          <FileText className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="font-bold text-sm text-slate-700">No Application Drafts Found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            When you explore government services and start eligibility checks, your progress will be automatically saved here.
          </p>
          <Link
            to="/services"
            className="inline-block px-4 py-2 bg-gov-gold text-slate-900 font-bold text-xs rounded-lg hover:bg-amber-600 transition"
          >
            Explore Services
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {drafts.map((draft) => (
            <div
              key={draft.id}
              className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="space-y-2 flex-1">
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] bg-blue-100 text-gov-blue font-bold px-2 py-0.5 rounded">
                    {draft.category}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono font-semibold">{draft.service_code}</span>
                  <span className="text-[10px] bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded">
                    Status: {draft.status}
                  </span>
                </div>

                <h3 className="font-bold text-base text-slate-800">{draft.service_name}</h3>

                {/* Completion Progress Bar */}
                <div className="max-w-md space-y-1">
                  <div className="flex items-center justify-between text-xs text-slate-600 font-medium">
                    <span>Application Progress</span>
                    <span>{draft.completion_percentage}% Completed</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-gov-blue h-2 rounded-full transition-all duration-500"
                      style={{ width: `${draft.completion_percentage}%` }}
                    />
                  </div>
                </div>

                <div className="flex items-center text-[11px] text-slate-400 space-x-4 pt-1">
                  <span className="flex items-center">
                    <Clock className="w-3.5 h-3.5 mr-1 text-slate-400" /> Last Saved: {new Date(draft.last_saved_at).toLocaleDateString()} {new Date(draft.last_saved_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                  <span>Step {draft.current_step} of 5</span>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row items-center gap-2">
                <Link
                  to={`/services/${draft.service_id}`}
                  className="w-full sm:w-auto px-5 py-2.5 bg-gov-blue hover:bg-blue-900 text-white font-bold text-xs rounded-lg shadow transition flex items-center justify-center"
                >
                  <Play className="w-3.5 h-3.5 mr-1.5 fill-current" /> Continue Application
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyApplicationsPage;
