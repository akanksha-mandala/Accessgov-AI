import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { User, Mail, Lock, UserPlus, CheckCircle, AlertCircle } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError(''); setSuccess(false);
    try {
      await register(name, email, password, 'citizen');
      setSuccess(true);
      setTimeout(() => navigate('/'), 700);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || 'Account creation failed. Please try again.');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <div className="bg-white max-w-md w-full rounded-xl shadow-xl border border-slate-200 overflow-hidden">
        <div className="bg-gov-blue p-6 text-white text-center border-b-4 border-gov-gold">
          <h2 className="text-xl font-bold">Create AccessGov AI Account</h2>
          <p className="text-xs text-slate-200 mt-1">Access public services and AI eligibility checker</p>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div><label className="block text-xs font-semibold text-slate-700 mb-1">Full Name</label><div className="relative"><User className="w-4 h-4 text-slate-400 absolute left-3 top-3"/><input type="text" required value={name} onChange={e=>setName(e.target.value)} className="w-full text-xs border border-slate-300 rounded-md pl-9 pr-3 py-2.5"/></div></div>
          <div><label className="block text-xs font-semibold text-slate-700 mb-1">Email Address</label><div className="relative"><Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3"/><input type="email" required value={email} onChange={e=>setEmail(e.target.value)} className="w-full text-xs border border-slate-300 rounded-md pl-9 pr-3 py-2.5"/></div></div>
          <div><label className="block text-xs font-semibold text-slate-700 mb-1">Password</label><div className="relative"><Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3"/><input type="password" minLength={8} required value={password} onChange={e=>setPassword(e.target.value)} className="w-full text-xs border border-slate-300 rounded-md pl-9 pr-3 py-2.5"/></div></div>
          <div className="bg-slate-50 border border-slate-200 rounded-md p-3 text-[11px] text-slate-600"><b>Account type:</b> Citizen. Government Official/Admin accounts are managed separately and cannot be self-created from this public registration form.</div>
          {error && <div className="bg-red-50 border border-red-200 text-red-800 p-3 rounded text-xs flex gap-2"><AlertCircle className="w-4 h-4 shrink-0"/>{error}</div>}
          {success && <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-3 rounded text-xs flex gap-2"><CheckCircle className="w-4 h-4 shrink-0"/>Account created successfully. You are now signed in.</div>}
          <button type="submit" disabled={loading || success} className="w-full bg-gov-blue text-white font-semibold py-2.5 rounded-md text-xs flex items-center justify-center"><UserPlus className="w-4 h-4 mr-2 text-gov-gold"/>{loading?'Creating Account...':'Create Account'}</button>
          <div className="text-center pt-2 text-xs text-slate-500">Already have an account? <Link to="/login" className="text-gov-blue font-semibold hover:underline">Sign In</Link></div>
        </form>
      </div>
    </div>
  );
};
export default RegisterPage;
