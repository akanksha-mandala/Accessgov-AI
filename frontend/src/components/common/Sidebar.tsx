import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useI18n } from '../../hooks/useI18n';
import {
  LayoutDashboard,
  Search,
  FileText,
  Clock,
  HelpCircle,
  BarChart3,
  MessageSquare,
  Eye,
  MapPin,
  ShieldAlert,
  Briefcase
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { user } = useAuth();
  const { t } = useI18n();
  const isAdmin = user?.role === 'admin' || user?.role === 'official';

  const citizenNav = [
    { name: t('home'), path: '/', icon: LayoutDashboard },
    { name: t('services'), path: '/services', icon: Search },
    { name: t('myApplications'), path: '/applications', icon: Briefcase },
    { name: t('myDocuments'), path: '/documents', icon: FileText },
    { name: t('applicationStatus'), path: '/status', icon: Clock },
    { name: t('helpAccessibility'), path: '/help', icon: HelpCircle },
  ];

  const adminNav = [
    { name: 'Admin Dashboard', path: '/admin', icon: BarChart3 },
    { name: 'Conversations', path: '/admin/conversations', icon: MessageSquare },
    { name: 'Accessibility', path: '/admin/accessibility', icon: Eye },
    { name: 'Documents', path: '/admin/documents', icon: FileText },
    { name: 'District Insights', path: '/admin/districts', icon: MapPin },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] p-4 flex flex-col justify-between shadow-sm shrink-0">
      <div className="space-y-6">
        <div>
          <p className="px-3 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
            Citizen Journey
          </p>
          <nav className="space-y-1">
            {citizenNav.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-3 py-2.5 text-xs font-semibold rounded-lg transition ${
                    isActive
                      ? 'bg-gov-blue text-white shadow font-bold'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`
                }
              >
                <item.icon className="w-4 h-4 mr-3 shrink-0" />
                {item.name}
              </NavLink>
            ))}
          </nav>
        </div>

        {isAdmin && (
          <div>
            <p className="px-3 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
              <span>Admin Telemetry</span>
              <ShieldAlert className="w-3.5 h-3.5 text-gov-gold" />
            </p>
            <nav className="space-y-1">
              {adminNav.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center px-3 py-2.5 text-xs font-semibold rounded-lg transition ${
                      isActive
                        ? 'bg-amber-500 text-slate-900 font-bold shadow'
                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                    }`
                  }
                >
                  <item.icon className="w-4 h-4 mr-3 shrink-0" />
                  {item.name}
                </NavLink>
              ))}
            </nav>
          </div>
        )}
      </div>

      <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-500 space-y-1">
        <p className="font-bold text-slate-700">Toll-Free Helpline</p>
        <p className="text-gov-blue font-bold">1800-111-2026</p>
      </div>
    </aside>
  );
};

export default Sidebar;
