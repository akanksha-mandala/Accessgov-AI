import React from 'react';
import { useToast, ToastType } from '../../context/ToastContext';
import { CheckCircle2, AlertTriangle, Info, XCircle, X } from 'lucide-react';

const icons: Record<ToastType, React.ReactNode> = {
  success: <CheckCircle2 className="w-5 h-5 text-emerald-600" />,
  error: <XCircle className="w-5 h-5 text-red-600" />,
  warning: <AlertTriangle className="w-5 h-5 text-amber-600" />,
  info: <Info className="w-5 h-5 text-blue-600" />,
};

export const Toast: React.FC = () => {
  const { toasts, removeToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2 max-w-sm w-full">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className="bg-white border border-slate-200 rounded-lg shadow-lg p-3.5 flex items-start space-x-3 transition transform duration-200 ease-in-out"
        >
          <div className="shrink-0 mt-0.5">{icons[toast.type]}</div>
          <div className="flex-1 text-xs">
            <h4 className="font-semibold text-slate-800">{toast.title}</h4>
            {toast.message && <p className="text-slate-500 mt-0.5">{toast.message}</p>}
          </div>
          <button
            onClick={() => removeToast(toast.id)}
            className="text-slate-400 hover:text-slate-600 p-0.5 rounded"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
    </div>
  );
};

export default Toast;
