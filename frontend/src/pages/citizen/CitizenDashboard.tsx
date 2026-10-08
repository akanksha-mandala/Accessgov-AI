import React, { useEffect, useState } from 'react';
import { servicesService, GovernmentService, FLAGSHIP_SERVICES } from '../../services/servicesService';
import { useAccessibility } from '../../context/AccessibilityContext';
import { useI18n } from '../../hooks/useI18n';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search,
  CheckCircle2,
  FileCheck,
  MessageSquare,
  ShieldCheck,
  ArrowRight,
  Volume2,
  Globe,
  Eye,
  ZoomIn,
  Sparkles,
  BookOpen,
  FileText
} from 'lucide-react';

export const CitizenDashboard: React.FC = () => {
  const [flagships, setFlagships] = useState<GovernmentService[]>(FLAGSHIP_SERVICES);
  const { setVoiceAccessEnabled, readPageContentAloud } = useAccessibility();
  const { t } = useI18n();
  const navigate = useNavigate();

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Hero Banner */}
      <section aria-label="Welcome Banner" className="bg-gradient-to-r from-gov-blue via-blue-900 to-gov-blue-dark text-white p-8 rounded-2xl shadow-lg border-l-8 border-gov-gold relative overflow-hidden">
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center space-x-2 bg-gov-gold/20 text-gov-gold px-3 py-1 rounded-full text-xs font-bold border border-gov-gold/40">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Accessible Public Welfare & Intelligence Platform</span>
          </div>
          
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight leading-tight">
            {t('heroTitle')}
          </h1>
          
          <p className="text-sm sm:text-base text-slate-200 leading-relaxed font-normal">
            {t('heroSub')}
          </p>

          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              to="/services"
              className="px-5 py-2.5 bg-gov-gold hover:bg-amber-600 text-slate-900 text-xs font-bold rounded-lg shadow-md transition flex items-center"
            >
              <Search className="w-4 h-4 mr-2" /> Find a Service
            </Link>
            <Link
              to="/eligibility"
              className="px-5 py-2.5 bg-white/10 hover:bg-white/20 text-white border border-white/30 text-xs font-bold rounded-lg shadow transition flex items-center"
            >
              <CheckCircle2 className="w-4 h-4 mr-2 text-gov-gold" /> Check Eligibility
            </Link>
          </div>
        </div>
      </section>

      {/* 4 Primary Action Cards Grid */}
      <section aria-label="Primary Actions" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          onClick={() => navigate('/services')}
          className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer flex flex-col justify-between group"
        >
          <div>
            <div className="w-12 h-12 bg-blue-50 text-gov-blue rounded-xl flex items-center justify-center mb-4 group-hover:bg-gov-blue group-hover:text-white transition">
              <Search className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-slate-800">{t('findService')}</h3>
            <p className="text-xs text-slate-500 mt-1">Explore scholarship, income certificate, healthcare and welfare schemes.</p>
          </div>
          <span className="text-xs text-gov-blue font-bold mt-4 flex items-center">
            Browse Schemes <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </span>
        </div>

        <div
          onClick={() => navigate('/eligibility')}
          className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer flex flex-col justify-between group"
        >
          <div>
            <div className="w-12 h-12 bg-amber-50 text-gov-gold rounded-xl flex items-center justify-center mb-4 group-hover:bg-gov-gold group-hover:text-slate-900 transition">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-slate-800">{t('checkEligibility')}</h3>
            <p className="text-xs text-slate-500 mt-1">Step-by-step rule evaluation for tuition fee waivers and certificates.</p>
          </div>
          <span className="text-xs text-gov-gold font-bold mt-4 flex items-center">
            Evaluate Criteria <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </span>
        </div>

        <div
          onClick={() => navigate('/documents')}
          className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer flex flex-col justify-between group"
        >
          <div>
            <div className="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center mb-4 group-hover:bg-emerald-600 group-hover:text-white transition">
              <FileCheck className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-slate-800">{t('uploadDocuments')}</h3>
            <p className="text-xs text-slate-500 mt-1">OCR scanning, PII masking, and application readiness score (0-100%).</p>
          </div>
          <span className="text-xs text-emerald-600 font-bold mt-4 flex items-center">
            Document Vault <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </span>
        </div>

        <div
          onClick={() => setVoiceAccessEnabled(true)}
          className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition cursor-pointer flex flex-col justify-between group"
        >
          <div>
            <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center mb-4 group-hover:bg-purple-600 group-hover:text-white transition">
              <Volume2 className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-base text-slate-800">{t('askAssistant')}</h3>
            <p className="text-xs text-slate-500 mt-1">Hands-free voice assistant for blind and low-vision citizens.</p>
          </div>
          <span className="text-xs text-purple-600 font-bold mt-4 flex items-center">
            Start Voice Access <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </span>
        </div>
      </section>

      {/* Flagship Demonstration Services */}
      <section aria-label="Flagship Demonstration Schemes" className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div>
            <span className="text-[10px] bg-gov-gold/20 text-slate-900 font-bold px-2.5 py-0.5 rounded border border-gov-gold/30 uppercase">
              Primary Flagship Journeys
            </span>
            <h2 className="text-lg font-bold text-slate-800 mt-1 flex items-center">
              <ShieldCheck className="w-5 h-5 mr-2 text-gov-gold" /> Featured Demonstration Schemes
            </h2>
          </div>
          <Link to="/services" className="text-xs text-gov-blue font-bold hover:underline">
            View All 8+ Schemes →
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Flagship 1: Scholarship Assistance */}
          <div className="bg-slate-50 p-6 rounded-xl border-2 border-gov-blue/20 flex flex-col justify-between hover:border-gov-blue transition shadow-sm">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs bg-gov-blue text-white font-bold px-3 py-1 rounded-full">
                  Education & Welfare
                </span>
                <span className="text-xs text-slate-400 font-mono font-semibold">{FLAGSHIP_SERVICES[0].service_code}</span>
              </div>

              <h3 className="text-lg font-bold text-slate-800 flex items-center">
                <BookOpen className="w-5 h-5 mr-2 text-gov-blue shrink-0" />
                {FLAGSHIP_SERVICES[0].name}
              </h3>

              <p className="text-xs text-slate-600 leading-relaxed">
                {FLAGSHIP_SERVICES[0].description}
              </p>

              <div className="bg-white p-3 rounded-lg border border-slate-200 text-xs space-y-1 text-slate-700">
                <p><strong className="text-slate-900">Key Benefit:</strong> {FLAGSHIP_SERVICES[0].benefits}</p>
                <p><strong className="text-slate-900">Required Documents:</strong> Income Cert, Caste Cert, Aadhaar Card, Marksheet.</p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-200 flex items-center justify-between">
              <Link
                to="/services/101"
                className="text-xs bg-gov-blue hover:bg-blue-900 text-white font-bold px-4 py-2 rounded-lg transition"
              >
                View Scholarship Flow
              </Link>
              <Link
                to="/eligibility"
                className="text-xs text-gov-gold font-bold hover:underline"
              >
                Check Scholarship Eligibility →
              </Link>
            </div>
          </div>

          {/* Flagship 2: Income Certificate */}
          <div className="bg-slate-50 p-6 rounded-xl border-2 border-gov-gold/30 flex flex-col justify-between hover:border-gov-gold transition shadow-sm">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs bg-gov-gold text-slate-900 font-bold px-3 py-1 rounded-full">
                  Revenue Certificate
                </span>
                <span className="text-xs text-slate-400 font-mono font-semibold">{FLAGSHIP_SERVICES[1].service_code}</span>
              </div>

              <h3 className="text-lg font-bold text-slate-800 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-gov-gold shrink-0" />
                {FLAGSHIP_SERVICES[1].name}
              </h3>

              <p className="text-xs text-slate-600 leading-relaxed">
                {FLAGSHIP_SERVICES[1].description}
              </p>

              <div className="bg-white p-3 rounded-lg border border-slate-200 text-xs space-y-1 text-slate-700">
                <p><strong className="text-slate-900">Prerequisite For:</strong> 40+ government welfare schemes and tuition fee waivers.</p>
                <p><strong className="text-slate-900">Required Documents:</strong> Aadhaar Card, Ration Card, Salary Slip / Self-Declaration.</p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-200 flex items-center justify-between">
              <Link
                to="/services/102"
                className="text-xs bg-slate-900 hover:bg-black text-white font-bold px-4 py-2 rounded-lg transition"
              >
                View Income Cert Flow
              </Link>
              <Link
                to="/documents"
                className="text-xs text-gov-blue font-bold hover:underline"
              >
                Upload Documents for OCR →
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* How AccessGov AI Helps Workflow */}
      <section aria-label="How AccessGov AI Helps" className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
        <h2 className="text-lg font-bold text-slate-800 text-center">How AccessGov AI Helps You</h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-50 p-5 rounded-xl border border-slate-200 text-center space-y-2">
            <div className="w-10 h-10 bg-gov-blue text-white font-extrabold rounded-full flex items-center justify-center mx-auto text-sm shadow">
              1
            </div>
            <h4 className="font-bold text-sm text-slate-800">1. Discover</h4>
            <p className="text-xs text-slate-500">Search 8+ verified central and state welfare schemes in simple terms.</p>
          </div>

          <div className="bg-slate-50 p-5 rounded-xl border border-slate-200 text-center space-y-2">
            <div className="w-10 h-10 bg-gov-gold text-slate-900 font-extrabold rounded-full flex items-center justify-center mx-auto text-sm shadow">
              2
            </div>
            <h4 className="font-bold text-sm text-slate-800">2. Understand Eligibility</h4>
            <p className="text-xs text-slate-500">Run deterministic rule evaluation for income and reservation criteria.</p>
          </div>

          <div className="bg-slate-50 p-5 rounded-xl border border-slate-200 text-center space-y-2">
            <div className="w-10 h-10 bg-emerald-600 text-white font-extrabold rounded-full flex items-center justify-center mx-auto text-sm shadow">
              3
            </div>
            <h4 className="font-bold text-sm text-slate-800">3. Check Documents</h4>
            <p className="text-xs text-slate-500">OCR scans papers, masks sensitive PII, and outputs 0-100% readiness scores.</p>
          </div>

          <div className="bg-slate-50 p-5 rounded-xl border border-slate-200 text-center space-y-2">
            <div className="w-10 h-10 bg-purple-600 text-white font-extrabold rounded-full flex items-center justify-center mx-auto text-sm shadow">
              4
            </div>
            <h4 className="font-bold text-sm text-slate-800">4. Accessible Guidance</h4>
            <p className="text-xs text-slate-500">Blind users navigate the whole portal hands-free via spoken voice commands.</p>
          </div>
        </div>
      </section>

      {/* Designed for Everyone Accessibility Features Grid */}
      <section aria-label="Accessibility Capabilities" className="bg-slate-900 text-white p-6 sm:p-8 rounded-2xl shadow-lg border-2 border-gov-gold space-y-6">
        <div className="text-center max-w-xl mx-auto space-y-2">
          <h2 className="text-xl font-bold text-gov-gold flex items-center justify-center">
            <Eye className="w-5 h-5 mr-2" /> Designed for Everyone — WCAG 2.1 AA Compliant
          </h2>
          <p className="text-xs text-slate-300">
            Empowering blind, low-vision, and non-literate citizens with complete voice and accessibility controls.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
          <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 space-y-1">
            <div className="flex items-center text-gov-gold font-bold">
              <Volume2 className="w-4 h-4 mr-2" /> Hands-Free Voice Access
            </div>
            <p className="text-slate-300">Say "Find Scholarship" or "Read Page" to navigate without looking at the screen.</p>
          </div>

          <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 space-y-1">
            <div className="flex items-center text-gov-gold font-bold">
              <Globe className="w-4 h-4 mr-2" /> 5 Indian Languages
            </div>
            <p className="text-slate-300">Full voice and text assistant in English, Tamil, Telugu, Hindi, and Kannada.</p>
          </div>

          <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 space-y-1">
            <div className="flex items-center text-gov-gold font-bold">
              <Eye className="w-4 h-4 mr-2" /> High Contrast Mode
            </div>
            <p className="text-slate-300">Yellow-on-black high contrast mode for low-vision citizens.</p>
          </div>

          <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 space-y-1">
            <div className="flex items-center text-gov-gold font-bold">
              <ZoomIn className="w-4 h-4 mr-2" /> Dynamic Text Scaling
            </div>
            <p className="text-slate-300">Font size scaling from 85% to 145% across all portal elements.</p>
          </div>

          <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 space-y-1">
            <div className="flex items-center text-gov-gold font-bold">
              <CheckCircle2 className="w-4 h-4 mr-2" /> Screen Reader ARIA Live
            </div>
            <p className="text-slate-300">Semantic HTML and ARIA live regions for NVDA, JAWS, and VoiceOver.</p>
          </div>

          <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 space-y-1">
            <div className="flex items-center text-gov-gold font-bold">
              <ShieldCheck className="w-4 h-4 mr-2" /> Keyboard Shortcuts
            </div>
            <p className="text-slate-300">Full keyboard navigation using Tab, Enter, and Alt+V for Voice Access.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default CitizenDashboard;
