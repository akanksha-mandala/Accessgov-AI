import React from 'react';
import { MapPin, Users, CheckCircle2, ShieldAlert } from 'lucide-react';

export const DistrictInsightsPage: React.FC = () => {
  const districtData = [
    { district: 'Chennai', applications: 1420, readinessAvg: 94, topScheme: 'PMAY Housing' },
    { district: 'Coimbatore', applications: 980, readinessAvg: 91, topScheme: 'PM-Kisan' },
    { district: 'Madurai', applications: 760, readinessAvg: 88, topScheme: 'CM Health Insurance' },
    { district: 'Tiruchirappalli', applications: 620, readinessAvg: 92, topScheme: 'PMAY Housing' },
    { district: 'Salem', applications: 540, readinessAvg: 87, topScheme: 'PM-Kisan' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800">District Application Coverage & Telemetry</h1>
        <p className="text-xs text-slate-500">Geographic scheme uptake & average document readiness by district</p>
      </div>

      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-800 flex items-center">
          <MapPin className="w-4 h-4 mr-2 text-gov-blue" /> District Application Metrics Table
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase text-[10px]">
                <th className="p-3">District</th>
                <th className="p-3">Application Volume</th>
                <th className="p-3">Avg Readiness Score</th>
                <th className="p-3">Top Requested Scheme</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {districtData.map((row) => (
                <tr key={row.district} className="hover:bg-slate-50/50">
                  <td className="p-3 font-bold text-slate-800 flex items-center">
                    <MapPin className="w-3.5 h-3.5 mr-1.5 text-gov-gold" /> {row.district}
                  </td>
                  <td className="p-3 font-semibold text-slate-700">{row.applications.toLocaleString()}</td>
                  <td className="p-3 font-semibold text-emerald-600">{row.readinessAvg}%</td>
                  <td className="p-3 font-medium text-slate-600">{row.topScheme}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default DistrictInsightsPage;
