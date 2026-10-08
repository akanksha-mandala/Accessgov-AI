import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useAccessibility, SUPPORTED_LANGUAGES, LanguageCode } from '../../context/AccessibilityContext';
import { AccessibilityControls } from './AccessibilityControls';
import { useI18n } from '../../hooks/useI18n';
import { VoiceAccessBar } from './VoiceAccessBar';
import { LogOut, User as UserIcon, Shield, Search, CheckCircle2, FileText, MessageSquare, LayoutDashboard, Globe } from 'lucide-react';

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const { t } = useI18n();
  const { selectedLanguage, setSelectedLanguage } = useAccessibility();
  const navigate = useNavigate();

  const citizenNav = [
    { name: t('home'), path: '/', icon: LayoutDashboard },
    { name: t('services'), path: '/services', icon: Search },
    { name: t('checkEligibility'), path: '/eligibility', icon: CheckCircle2 },
    { name: t('documents'), path: '/documents', icon: FileText },
  ];

  const adminNav = [
    { name: 'Admin Dashboard', path: '/admin' },
    { name: 'Analytics', path: '/admin/conversations' },
    { name: 'Accessibility', path: '/admin/accessibility' },
    { name: 'Documents', path: '/admin/documents' },
    { name: 'District Insights', path: '/admin/districts' },
  ];

  return (
    <header className="bg-gov-blue text-white shadow-md border-b-4 border-gov-gold">
      {/* Top Accessible Voice Access Toolbar */}
      <VoiceAccessBar />

      {/* Main Header Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-4">
        {/* Emblem & Branding Title */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => navigate('/')}>
          <div className="w-10 h-10 bg-gov-gold text-gov-blue font-bold rounded-full flex items-center justify-center text-xl shadow">
            🏛️
          </div>
          <div>
            <h1 className="text-base sm:text-lg font-bold tracking-wide flex items-center">
              AccessGov AI <span className="ml-2 text-[10px] bg-gov-gold text-slate-900 font-semibold px-2 py-0.5 rounded">PUBLIC SERVICE</span>
            </h1>
            <p className="text-xs text-slate-200">Accessible Public Service Intelligence Platform</p>
          </div>
        </div>

        {/* Multilingual Selector & Accessibility Toolbar */}
        <div className="flex items-center space-x-3">
          {/* Language Selector */}
          <div className="flex items-center space-x-1.5 bg-blue-900/80 px-2 py-1 rounded border border-blue-700 text-xs">
            <Globe className="w-3.5 h-3.5 text-gov-gold" />
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value as LanguageCode)}
              aria-label="Select preferred language"
              className="bg-transparent text-white text-xs font-semibold focus:outline-none cursor-pointer"
            >
              {SUPPORTED_LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code} className="bg-slate-900 text-white">
                  {lang.nativeLabel} ({lang.label})
                </option>
              ))}
            </select>
          </div>

          <AccessibilityControls />

          {/* User Profile */}
          {user && (
            <div className="flex items-center space-x-2 border-l border-blue-700 pl-3">
              <div className="flex items-center space-x-1.5">
                <div className="p-1 bg-blue-800 rounded-full text-slate-200">
                  <UserIcon className="w-3.5 h-3.5" />
                </div>
                <div className="hidden md:block text-left text-xs">
                  <p className="font-semibold leading-tight">{user.full_name}</p>
                  <p className="text-[9px] text-gov-gold uppercase tracking-wider font-bold">{user.role}</p>
                </div>
              </div>
              <button
                onClick={logout}
                title="Sign Out"
                aria-label="Sign out of AccessGov AI account"
                className="p-1.5 text-slate-200 hover:text-white hover:bg-blue-800 rounded transition"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Horizontal Main Navigation Bar */}
      <nav aria-label="Main Navigation" className="bg-blue-950 px-4 sm:px-6 lg:px-8 border-t border-blue-900/50">
        <div className="max-w-7xl mx-auto flex items-center justify-between overflow-x-auto text-xs font-semibold">
          <div className="flex items-center space-x-1 sm:space-x-2 py-2">
            {citizenNav.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `px-3 py-1.5 rounded-md transition flex items-center space-x-1.5 ${
                    isActive
                      ? 'bg-gov-gold text-slate-900 font-bold shadow'
                      : 'text-slate-200 hover:bg-blue-900 hover:text-white'
                  }`
                }
              >
                <item.icon className="w-3.5 h-3.5" />
                <span>{item.name}</span>
              </NavLink>
            ))}

            {user?.role === 'admin' && (
              <div className="flex items-center space-x-1 border-l border-blue-800 pl-2 ml-2">
                {adminNav.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `px-2.5 py-1.5 rounded-md transition text-[11px] ${
                        isActive
                          ? 'bg-amber-500 text-slate-900 font-bold'
                          : 'text-slate-300 hover:bg-blue-900 hover:text-white'
                      }`
                    }
                  >
                    {item.name}
                  </NavLink>
                ))}
              </div>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;
