import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AccessibilityProvider, useAccessibility } from './context/AccessibilityContext';
import { ConversationProvider } from './context/ConversationContext';
import { ToastProvider } from './context/ToastContext';

// Layout & Common Components
import Header from './components/common/Header';
import Sidebar from './components/common/Sidebar';
import Toast from './components/common/Toast';
import ChatDrawer from './components/assistant/ChatDrawer';
import FloatingAssistantButton from './components/assistant/FloatingAssistantButton';

// Auth Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// Citizen Pages
import CitizenDashboard from './pages/citizen/CitizenDashboard';
import ServiceCatalogPage from './pages/citizen/ServiceCatalogPage';
import ServiceDetailPage from './pages/citizen/ServiceDetailPage';
import MyApplicationsPage from './pages/citizen/MyApplicationsPage';
import DocumentUploadPage from './pages/citizen/DocumentUploadPage';
import ApplicationStatusPage from './pages/citizen/ApplicationStatusPage';
import HelpAccessibilityPage from './pages/citizen/HelpAccessibilityPage';
import EligibilityCheckerPage from './pages/citizen/EligibilityCheckerPage';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import ConversationAnalyticsPage from './pages/admin/ConversationAnalyticsPage';
import AccessibilityAnalyticsPage from './pages/admin/AccessibilityAnalyticsPage';
import DocumentAnalyticsPage from './pages/admin/DocumentAnalyticsPage';
import DistrictInsightsPage from './pages/admin/DistrictInsightsPage';

const ProtectedRoute: React.FC<{ children: React.ReactNode; allowedRole?: string }> = ({
  children,
  allowedRole,
}) => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRole && user?.role !== allowedRole) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isChatOpen, setIsChatOpen] = React.useState(false);
  const { voiceAccessEnabled, setVoiceAccessEnabled, announcement } = useAccessibility();

  // Voice Access Keyboard Shortcut (Alt+V)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && (e.key === 'v' || e.key === 'V')) {
        e.preventDefault();
        setVoiceAccessEnabled(!voiceAccessEnabled);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [voiceAccessEnabled, setVoiceAccessEnabled]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Screen Reader ARIA Live Region */}
      <div className="sr-only" aria-live="polite" aria-atomic="true">
        {announcement}
      </div>

      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main id="main-content" className="flex-1 p-4 sm:p-6 overflow-y-auto max-w-7xl mx-auto w-full">
          {children}
        </main>
      </div>
      <FloatingAssistantButton onClick={() => setIsChatOpen(true)} />
      <ChatDrawer isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
      <Toast />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <AccessibilityProvider>
        <ConversationProvider>
          <ToastProvider>
            <Router>
              <Routes>
                {/* Public Auth Routes */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* Citizen Integrated Journey Routes */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <AppLayout>
                        <CitizenDashboard />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/services"
                  element={
                    <ProtectedRoute>
                      <AppLayout>
                        <ServiceCatalogPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/services/:id"
                  element={
                    <ProtectedRoute>
                      <AppLayout>
                        <ServiceDetailPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/applications"
                  element={
                    <ProtectedRoute>
                      <AppLayout>
                        <MyApplicationsPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/documents"
                  element={
                    <ProtectedRoute>
                      <AppLayout>
                        <DocumentUploadPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/status"
                  element={
                    <ProtectedRoute>
                      <AppLayout>
                        <ApplicationStatusPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/help"
                  element={
                    <ProtectedRoute>
                      <AppLayout>
                        <HelpAccessibilityPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/eligibility"
                  element={
                    <ProtectedRoute>
                      <AppLayout>
                        <EligibilityCheckerPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />

                {/* Admin Protected Routes */}
                <Route
                  path="/admin"
                  element={
                    <ProtectedRoute allowedRole="admin">
                      <AppLayout>
                        <AdminDashboard />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/conversations"
                  element={
                    <ProtectedRoute allowedRole="admin">
                      <AppLayout>
                        <ConversationAnalyticsPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/accessibility"
                  element={
                    <ProtectedRoute allowedRole="admin">
                      <AppLayout>
                        <AccessibilityAnalyticsPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/documents"
                  element={
                    <ProtectedRoute allowedRole="admin">
                      <AppLayout>
                        <DocumentAnalyticsPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/districts"
                  element={
                    <ProtectedRoute allowedRole="admin">
                      <AppLayout>
                        <DistrictInsightsPage />
                      </AppLayout>
                    </ProtectedRoute>
                  }
                />

                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Router>
          </ToastProvider>
        </ConversationProvider>
      </AccessibilityProvider>
    </AuthProvider>
  );
};

export default App;
