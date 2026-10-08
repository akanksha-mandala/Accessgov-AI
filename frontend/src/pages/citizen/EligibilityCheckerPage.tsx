import React, { useState } from 'react';
import {
  servicesService,
  EligibilityResult,
  ALL_CURATED_SERVICES,
} from '../../services/servicesService';
import { useAccessibility } from '../../context/AccessibilityContext';
import {
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  ArrowLeft,
} from 'lucide-react';
import ReadinessGauge from '../../components/common/ReadinessGauge';

export const EligibilityCheckerPage: React.FC = () => {
  const { speakAnnouncement } = useAccessibility();

  const [step, setStep] = useState<number>(1);

  /*
   * IMPORTANT:
   * ALL_CURATED_SERVICES uses frontend/demo IDs such as 101.
   * The backend database uses:
   *   1 = Scholarship
   *   2 = Income Certificate
   *
   * We therefore resolve the real backend ID before calling
   * the eligibility API.
   */
  const [selectedServiceId, setSelectedServiceId] =
    useState<number>(101);

  // Step 2 & 3 Profile Form States
  const [annualIncome, setAnnualIncome] =
    useState<string>('220000');

  const [academicMarks, setAcademicMarks] =
    useState<string>('75');

  const [socialCategory, setSocialCategory] =
    useState<string>('OBC');

  const [state, setState] =
    useState<string>('Tamil Nadu');

  const [hasLand, setHasLand] =
    useState<boolean>(false);

  const [result, setResult] =
    useState<EligibilityResult | null>(null);

  const [loading, setLoading] =
    useState<boolean>(false);

  const selectedService =
    ALL_CURATED_SERVICES.find(
      (s) => s.id === selectedServiceId
    ) || ALL_CURATED_SERVICES[0];

  /*
   * Resolve frontend curated service IDs to actual backend
   * database service IDs.
   *
   * Current backend services:
   *   ID 1 = SCHOLARSHIP
   *   ID 2 = INCOME_CERTIFICATE
   */
  const getBackendServiceId = (): number => {
    if (selectedService.service_code === 'SCHOLARSHIP') {
      return 1;
    }

    if (
      selectedService.service_code === 'INCOME_CERTIFICATE'
    ) {
      return 2;
    }

    // For any future service where frontend and backend IDs
    // already match, preserve the selected ID.
    return selectedServiceId;
  };

  const isScholarship =
    selectedService.service_code === 'SCHOLARSHIP';

  const handleEvaluate = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    setLoading(true);

    speakAnnouncement(
      'Evaluating eligibility rules for ' +
        selectedService.name
    );

    try {
      const backendServiceId =
        getBackendServiceId();

      console.log(
        '[AccessGov Eligibility] Frontend Service ID:',
        selectedServiceId
      );

      console.log(
        '[AccessGov Eligibility] Backend Service ID:',
        backendServiceId
      );

      console.log(
        '[AccessGov Eligibility] Service Code:',
        selectedService.service_code
      );

      const res =
        await servicesService.checkEligibility(
          backendServiceId,
          {
            income: parseInt(annualIncome, 10),
            marks: isScholarship
              ? parseInt(academicMarks, 10)
              : undefined,
            category: socialCategory,
            state,
            has_land: hasLand,
            is_student: isScholarship,
            occupation: isScholarship
              ? 'Student'
              : undefined,
          }
        );

      console.log(
        '[AccessGov Eligibility] Evaluation Result:',
        res
      );

      setResult(res);
      setStep(5);

      /*
       * Use the backend eligibility status instead of only
       * is_eligible.
       *
       * This prevents:
       *   Partially Eligible → QUALIFIED FOR SCHEME
       *
       * Only a definitive "Eligible" result gets the
       * qualified banner.
       */
      const isFullyEligible =
        res.eligibility_status === 'Eligible';

      if (isFullyEligible) {
        speakAnnouncement(
          `Eligibility evaluation complete. You are qualified for ${selectedService.name}. Eligibility score: ${res.score} percent.`
        );
      } else if (
        res.eligibility_status === 'Partially Eligible'
      ) {
        speakAnnouncement(
          `Eligibility evaluation complete. Your profile is partially eligible for ${selectedService.name}. Please review the discrepancies and required documents.`
        );
      } else {
        speakAnnouncement(
          `Eligibility evaluation complete. You are not eligible for ${selectedService.name} based on the evaluated mandatory conditions.`
        );
      }
    } catch (error) {
      console.error(
        '[AccessGov Eligibility] Evaluation failed:',
        error
      );
    } finally {
      setLoading(false);
    }
  };

  /*
   * Result state helpers
   */
  const isFullyEligible =
    result?.eligibility_status === 'Eligible';

  const isPartiallyEligible =
    result?.eligibility_status ===
    'Partially Eligible';

  const isNotEligible =
    result?.eligibility_status === 'Not Eligible';

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-xl font-bold text-slate-800">
          AI Guided Eligibility Evaluation Engine
        </h1>

        <p className="text-xs text-slate-500">
          Step-by-step rule evaluation for tuition fee
          waivers, scholarships & certificates
        </p>
      </div>

      {/* 5-Step Progress Indicator Bar */}
      <nav
        aria-label="Eligibility Step Progress"
        className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between text-xs"
      >
        {[
          { num: 1, name: 'Select Scheme' },
          { num: 2, name: 'Basic Details' },
          { num: 3, name: 'Income & Criteria' },
          { num: 4, name: 'Review' },
          { num: 5, name: 'Results' },
        ].map((s) => (
          <div
            key={s.num}
            className="flex items-center space-x-1.5"
          >
            <div
              className={`w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs ${
                step === s.num
                  ? 'bg-gov-blue text-white ring-2 ring-gov-gold'
                  : step > s.num
                  ? 'bg-emerald-600 text-white'
                  : 'bg-slate-100 text-slate-400'
              }`}
            >
              {step > s.num ? '✓' : s.num}
            </div>

            <span
              className={`hidden sm:inline font-semibold ${
                step === s.num
                  ? 'text-gov-blue font-bold'
                  : 'text-slate-500'
              }`}
            >
              {s.name}
            </span>
          </div>
        ))}
      </nav>

      {/* Step Content Card */}
      <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">

        {/* ===================================================== */}
        {/* STEP 1 */}
        {/* ===================================================== */}

        {step === 1 && (
          <div className="space-y-6">
            <div className="border-b border-slate-100 pb-3">
              <h3 className="font-bold text-base text-slate-800">
                Step 1: Select Government Scheme
              </h3>

              <p className="text-xs text-slate-500">
                Choose a scheme to check rules and required
                documents.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {ALL_CURATED_SERVICES.map((svc) => (
                <div
                  key={svc.id}
                  onClick={() =>
                    setSelectedServiceId(svc.id)
                  }
                  className={`p-5 rounded-xl border-2 cursor-pointer transition flex flex-col justify-between ${
                    selectedServiceId === svc.id
                      ? 'border-gov-blue bg-blue-50/50 shadow'
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] bg-gov-blue text-white font-bold px-2 py-0.5 rounded">
                        {svc.category}
                      </span>

                      {svc.is_flagship && (
                        <span className="text-[10px] bg-gov-gold text-slate-900 font-bold px-2 py-0.5 rounded">
                          FLAGSHIP DEMO
                        </span>
                      )}
                    </div>

                    <h4 className="font-bold text-sm text-slate-800">
                      {svc.name}
                    </h4>

                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                      {svc.description}
                    </p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-200 flex items-center justify-between text-xs">
                    <span className="text-slate-400 font-mono">
                      {svc.service_code}
                    </span>

                    <span
                      className={`font-bold ${
                        selectedServiceId === svc.id
                          ? 'text-gov-blue'
                          : 'text-slate-400'
                      }`}
                    >
                      {selectedServiceId === svc.id
                        ? 'Selected ✓'
                        : 'Select'}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-4 border-t border-slate-100">
              <button
                onClick={() => {
                  setStep(2);
                  speakAnnouncement(
                    'Step 2: Basic Details.'
                  );
                }}
                className="px-6 py-2.5 bg-gov-blue hover:bg-blue-900 text-white font-bold text-xs rounded-lg shadow transition flex items-center"
              >
                Next: Basic Details
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </button>
            </div>
          </div>
        )}

        {/* ===================================================== */}
        {/* STEP 2 */}
        {/* ===================================================== */}

        {step === 2 && (
          <div className="space-y-6">
            <div className="border-b border-slate-100 pb-3">
              <h3 className="font-bold text-base text-slate-800">
                Step 2: Applicant Profile Details
              </h3>

              <p className="text-xs text-slate-500">
                Provide basic demographic details for{' '}
                {selectedService.name}.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  State of Permanent Residence
                </label>

                <input
                  type="text"
                  value={state}
                  onChange={(e) =>
                    setState(e.target.value)
                  }
                  className="w-full text-xs border border-slate-300 rounded-md px-3 py-2.5 focus:outline-none focus:border-gov-blue"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Social Reservation Category
                </label>

                <select
                  value={socialCategory}
                  onChange={(e) =>
                    setSocialCategory(e.target.value)
                  }
                  className="w-full text-xs border border-slate-300 rounded-md px-3 py-2.5 focus:outline-none focus:border-gov-blue"
                >
                  <option value="OBC">
                    OBC / BC / MBC
                  </option>

                  <option value="SC">
                    SC (Scheduled Caste)
                  </option>

                  <option value="ST">
                    ST (Scheduled Tribe)
                  </option>

                  <option value="General">
                    General / EWS
                  </option>
                </select>
              </div>
            </div>

            <div className="flex justify-between pt-4 border-t border-slate-100">
              <button
                onClick={() => setStep(1)}
                className="px-4 py-2 bg-slate-100 text-slate-700 font-bold text-xs rounded-lg hover:bg-slate-200 transition flex items-center"
              >
                <ArrowLeft className="w-4 h-4 mr-1.5" />
                Back
              </button>

              <button
                onClick={() => {
                  setStep(3);
                  speakAnnouncement(
                    'Step 3: Income and Academic Criteria.'
                  );
                }}
                className="px-6 py-2.5 bg-gov-blue hover:bg-blue-900 text-white font-bold text-xs rounded-lg shadow transition flex items-center"
              >
                Next: Criteria
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </button>
            </div>
          </div>
        )}

        {/* ===================================================== */}
        {/* STEP 3 */}
        {/* ===================================================== */}

        {step === 3 && (
          <div className="space-y-6">
            <div className="border-b border-slate-100 pb-3">
              <h3 className="font-bold text-base text-slate-800">
                Step 3: Income & Criteria Information
              </h3>

              <p className="text-xs text-slate-500">
                Provide financial and profile information
                for deterministic rule matching.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Annual Household / Family Income (INR)
                </label>

                <input
                  type="number"
                  value={annualIncome}
                  onChange={(e) =>
                    setAnnualIncome(e.target.value)
                  }
                  className="w-full text-xs border border-slate-300 rounded-md px-3 py-2.5 focus:outline-none focus:border-gov-blue"
                />

                {isScholarship ? (
                  <p className="text-[11px] text-slate-400 mt-1">
                    Scholarship income ceiling:
                    Rs 2,50,000 per year.
                  </p>
                ) : (
                  <p className="text-[11px] text-slate-400 mt-1">
                    Income Certificate service has no
                    income ceiling. The declared income is
                    recorded for certification.
                  </p>
                )}
              </div>

              {isScholarship && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Academic Percentage (%)
                  </label>

                  <input
                    type="number"
                    value={academicMarks}
                    onChange={(e) =>
                      setAcademicMarks(e.target.value)
                    }
                    className="w-full text-xs border border-slate-300 rounded-md px-3 py-2.5 focus:outline-none focus:border-gov-blue"
                  />

                  <p className="text-[11px] text-slate-400 mt-1">
                    Academic percentage is recorded for
                    scholarship profile/selection context.
                    It is not treated as a universal
                    mandatory cutoff in this scheme profile.
                  </p>
                </div>
              )}

              <div className="flex items-center space-x-2 pt-2">
                <input
                  type="checkbox"
                  id="land_check"
                  checked={hasLand}
                  onChange={(e) =>
                    setHasLand(e.target.checked)
                  }
                  className="rounded text-gov-blue"
                />

                <label
                  htmlFor="land_check"
                  className="text-xs text-slate-700 font-medium"
                >
                  Family owns agricultural landholding
                </label>
              </div>
            </div>

            <div className="flex justify-between pt-4 border-t border-slate-100">
              <button
                onClick={() => setStep(2)}
                className="px-4 py-2 bg-slate-100 text-slate-700 font-bold text-xs rounded-lg hover:bg-slate-200 transition flex items-center"
              >
                <ArrowLeft className="w-4 h-4 mr-1.5" />
                Back
              </button>

              <button
                onClick={() => {
                  setStep(4);
                  speakAnnouncement(
                    'Step 4: Review Application before evaluation.'
                  );
                }}
                className="px-6 py-2.5 bg-gov-blue hover:bg-blue-900 text-white font-bold text-xs rounded-lg shadow transition flex items-center"
              >
                Next: Review
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </button>
            </div>
          </div>
        )}

        {/* ===================================================== */}
        {/* STEP 4 */}
        {/* ===================================================== */}

        {step === 4 && (
          <div className="space-y-6">
            <div className="border-b border-slate-100 pb-3">
              <h3 className="font-bold text-base text-slate-800">
                Step 4: Review Submitted Inputs
              </h3>

              <p className="text-xs text-slate-500">
                Confirm parameters before executing the
                deterministic evaluation engine.
              </p>
            </div>

            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2 text-xs">
              <p>
                <strong className="text-slate-900">
                  Target Scheme:
                </strong>{' '}
                {selectedService.name}
              </p>

              <p>
                <strong className="text-slate-900">
                  Service Code:
                </strong>{' '}
                {selectedService.service_code}
              </p>

              <p>
                <strong className="text-slate-900">
                  Backend Service ID:
                </strong>{' '}
                {getBackendServiceId()}
              </p>

              <p>
                <strong className="text-slate-900">
                  State Jurisdiction:
                </strong>{' '}
                {state}
              </p>

              <p>
                <strong className="text-slate-900">
                  Category:
                </strong>{' '}
                {socialCategory}
              </p>

              <p>
                <strong className="text-slate-900">
                  Declared Family Income:
                </strong>{' '}
                Rs{' '}
                {parseInt(
                  annualIncome || '0',
                  10
                ).toLocaleString()}
              </p>

              {isScholarship && (
                <p>
                  <strong className="text-slate-900">
                    Academic Score:
                  </strong>{' '}
                  {academicMarks}%
                </p>
              )}
            </div>

            <div className="flex justify-between pt-4 border-t border-slate-100">
              <button
                onClick={() => setStep(3)}
                className="px-4 py-2 bg-slate-100 text-slate-700 font-bold text-xs rounded-lg hover:bg-slate-200 transition flex items-center"
              >
                <ArrowLeft className="w-4 h-4 mr-1.5" />
                Back
              </button>

              <button
                onClick={handleEvaluate}
                disabled={loading}
                className="px-6 py-2.5 bg-gov-gold hover:bg-amber-600 text-slate-900 font-extrabold text-xs rounded-lg shadow transition flex items-center disabled:opacity-60"
              >
                <Sparkles className="w-4 h-4 mr-1.5" />

                {loading
                  ? 'Evaluating Rules...'
                  : 'Run Eligibility Rule Engine'}
              </button>
            </div>
          </div>
        )}

        {/* ===================================================== */}
        {/* STEP 5 */}
        {/* ===================================================== */}

        {step === 5 && result && (
          <div className="space-y-6">
            <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base text-slate-800">
                  Step 5: Official Eligibility Evaluation Result
                </h3>

                <p className="text-xs text-slate-500">
                  {result.service_name}
                </p>
              </div>

              <button
                onClick={() => {
                  setResult(null);
                  setStep(1);
                }}
                className="text-xs text-gov-blue font-bold hover:underline"
              >
                Evaluate Another Scheme
              </button>
            </div>

            {/* ================================================= */}
            {/* RESULT HEADER */}
            {/* ================================================= */}

            <div
              className={`p-6 rounded-xl border-2 flex items-center justify-between ${
                isFullyEligible
                  ? 'bg-emerald-50/50 border-emerald-500 text-emerald-900'
                  : isPartiallyEligible
                  ? 'bg-amber-50 border-amber-400 text-amber-900'
                  : 'bg-red-50/50 border-red-400 text-red-900'
              }`}
            >
              <div className="space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                  Evaluation Outcome
                </span>

                <h3 className="text-xl font-extrabold">
                  {isFullyEligible
                    ? 'QUALIFIED FOR SCHEME'
                    : isPartiallyEligible
                    ? 'PARTIALLY ELIGIBLE'
                    : 'NOT ELIGIBLE'}
                </h3>

                <p className="text-xs text-slate-600">
                  {isFullyEligible
                    ? 'Your profile satisfies the evaluated mandatory eligibility conditions.'
                    : isPartiallyEligible
                    ? 'Your profile satisfies the evaluated eligibility conditions, but additional information or required documents are still needed.'
                    : 'Your profile does not satisfy one or more mandatory eligibility conditions.'}
                </p>

                <p className="text-[11px] font-bold text-slate-500 mt-2">
                  Status:{' '}
                  {result.eligibility_status}
                </p>
              </div>

              <ReadinessGauge
                score={result.score}
                size={65}
              />
            </div>

            {/* ================================================= */}
            {/* MATCHED + DISCREPANCIES */}
            {/* ================================================= */}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

              {/* Matched Criteria */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2">
                <h4 className="text-xs font-bold text-slate-800 flex items-center">
                  <CheckCircle2 className="w-4 h-4 mr-1.5 text-emerald-600" />
                  Matched Criteria:
                </h4>

                {(result.matched_criteria ?? []).length > 0 ? (
                  <ul className="space-y-1 text-xs text-slate-700">
                    {(result.matched_criteria ?? []).map(
                      (criterion, index) => (
                        <li
                          key={index}
                          className="flex items-start"
                        >
                          <span className="text-emerald-600 mr-1.5">
                            ✓
                          </span>

                          {criterion}
                        </li>
                      )
                    )}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-400">
                    No mandatory criteria were matched.
                  </p>
                )}
              </div>

              {/* Discrepancies */}
              {(result.missing_criteria ?? []).length >
                0 && (
                <div
                  className={`p-4 rounded-xl border space-y-2 ${
                    isNotEligible
                      ? 'bg-red-50 border-red-200'
                      : 'bg-amber-50 border-amber-200'
                  }`}
                >
                  <h4
                    className={`text-xs font-bold flex items-center ${
                      isNotEligible
                        ? 'text-red-900'
                        : 'text-amber-900'
                    }`}
                  >
                    <AlertTriangle className="w-4 h-4 mr-1.5" />

                    {isNotEligible
                      ? 'Eligibility Discrepancies:'
                      : 'Discrepancies:'}
                  </h4>

                  <ul
                    className={`space-y-1 text-xs ${
                      isNotEligible
                        ? 'text-red-800'
                        : 'text-amber-800'
                    }`}
                  >
                    {(result.missing_criteria ?? []).map(
                      (criterion, index) => (
                        <li
                          key={index}
                          className="flex items-start"
                        >
                          <span
                            className={`mr-1.5 ${
                              isNotEligible
                                ? 'text-red-600'
                                : 'text-amber-600'
                            }`}
                          >
                            •
                          </span>

                          {criterion}
                        </li>
                      )
                    )}
                  </ul>
                </div>
              )}
            </div>

            {/* ================================================= */}
            {/* RECOMMENDED NEXT ACTIONS */}
            {/* ================================================= */}

            <div className="bg-blue-50 p-5 rounded-xl border border-blue-200 space-y-3">
              <h4 className="text-xs font-bold text-gov-blue flex items-center">
                <ShieldCheck className="w-4 h-4 mr-1.5 text-gov-gold" />
                Recommended Next Steps
              </h4>

              {(result.recommendations ?? []).length >
              0 ? (
                <ul className="space-y-1.5 text-xs text-slate-700">
                  {(result.recommendations ?? []).map(
                    (recommendation, index) => (
                      <li
                        key={index}
                        className="flex items-start"
                      >
                        <span className="text-gov-blue font-bold mr-2">
                          {index + 1}.
                        </span>

                        {recommendation}
                      </li>
                    )
                  )}
                </ul>
              ) : (
                <p className="text-xs text-slate-500">
                  No additional actions were returned by
                  the eligibility engine.
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EligibilityCheckerPage;