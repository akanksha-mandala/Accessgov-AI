import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  Upload,
  Save,
  FileText,
} from 'lucide-react';

import {
  servicesService,
  GovernmentService,
} from '../../services/servicesService';

import {
  applicationService,
  ApplicationDraft,
} from '../../services/applicationService';

import {
  documentService,
  UserDocument,
} from '../../services/documentService';

interface DocumentMatch {
  required_doc: string;
  status: 'available' | 'warning' | 'missing';
  document: UserDocument | null;
  message: string;
}

export const ServiceDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [service, setService] = useState<GovernmentService | null>(null);
  const [vaultDocs, setVaultDocs] = useState<UserDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [docMatches, setDocMatches] = useState<DocumentMatch[]>([]);
  const [existingDraft, setExistingDraft] =
    useState<ApplicationDraft | undefined>(undefined);

  useEffect(() => {
    const loadService = async () => {
      try {
        setLoading(true);

        const serviceId = Number(id);

        const [serviceData, documents] = await Promise.all([
          servicesService.getServiceById(serviceId),
          documentService.getUserDocuments(),
        ]);

        setService(serviceData);
        setVaultDocs(documents);

        const matches =
          applicationService.checkDocumentVaultMatch(
            serviceData.required_documents || [],
            documents
          );

        setDocMatches(matches);

        const draft =
          applicationService.getDraftByServiceId(serviceId);

        setExistingDraft(draft);
      } catch (error) {
        console.error(
          'Failed to load service details:',
          error
        );
      } finally {
        setLoading(false);
      }
    };

    loadService();
  }, [id]);

  /*
   * A document is considered ready for application preparation
   * when it exists in the user's vault.
   *
   * "warning" means the document exists but its readiness
   * score is low and should be reviewed.
   *
   * It is still counted as vault-ready because the document
   * is available for reuse.
   */
  const readyDocumentCount = docMatches.filter(
    (item) =>
      item.status === 'available' ||
      item.status === 'warning'
  ).length;

  const requiredDocumentCount =
    service?.required_documents?.length || 0;

  const calculatedCompletionPercentage =
    requiredDocumentCount > 0
      ? Math.round(
          (readyDocumentCount / requiredDocumentCount) * 100
        )
      : 0;

  /*
   * Keep the saved draft percentage synchronized with the
   * actual vault-ready document count.
   */
  useEffect(() => {
    if (!service || !existingDraft) {
      return;
    }

    if (
      existingDraft.status === 'Draft' &&
      existingDraft.completion_percentage !==
        calculatedCompletionPercentage
    ) {
      const updatedDraft = applicationService.saveDraft({
        ...existingDraft,
        completion_percentage:
          calculatedCompletionPercentage,
      });

      setExistingDraft(updatedDraft);
    }
  }, [
    service,
    existingDraft,
    calculatedCompletionPercentage,
  ]);

  const handleStartApplication = () => {
    if (!service) {
      return;
    }

    const draft = applicationService.saveDraft({
      id: existingDraft?.id,
      service_id: service.id,
      service_code: service.service_code,
      service_name: service.name,
      category: service.category,
      status: 'Draft',
      completion_percentage:
        calculatedCompletionPercentage,
      current_step: existingDraft?.current_step || 1,
      answers: existingDraft?.answers || {},
      attached_documents:
        existingDraft?.attached_documents || {},
    });

    setExistingDraft(draft);

    navigate('/eligibility');
  };

  const handleUploadDocument = (
    documentType: string
  ) => {
    const encodedType =
      encodeURIComponent(documentType);

    navigate(
      `/documents/upload?documentType=${encodedType}`
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-sm text-slate-500">
          Loading service details...
        </div>
      </div>
    );
  }

  if (!service) {
    return (
      <div className="space-y-4">
        <button
          onClick={() => navigate('/services')}
          className="flex items-center text-sm text-gov-blue font-semibold"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Services
        </button>

        <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
          <h2 className="font-bold text-slate-800">
            Service Not Found
          </h2>

          <p className="text-sm text-slate-500 mt-2">
            The requested government service could not be
            loaded.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">

      {/* Back */}
      <button
        onClick={() => navigate('/services')}
        className="flex items-center text-xs font-semibold text-slate-600 hover:text-gov-blue"
      >
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Services
      </button>

      {/* Service Header */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-6">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">

            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-[10px] bg-blue-100 text-gov-blue font-bold px-2 py-0.5 rounded">
                  {service.category}
                </span>

                <span className="text-[10px] text-slate-400 font-mono font-semibold">
                  {service.service_code}
                </span>
              </div>

              <h1 className="text-xl font-bold text-slate-800">
                {service.name}
              </h1>

              <p className="text-xs text-slate-500 mt-1">
                {service.department}
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-2">

              <button
                onClick={handleStartApplication}
                className="px-4 py-2 bg-gov-blue hover:bg-blue-900 text-white font-bold text-xs rounded-lg shadow transition flex items-center justify-center"
              >
                <Save className="w-3.5 h-3.5 mr-1.5" />
                Save Service
              </button>

              <button
                onClick={handleStartApplication}
                className="px-4 py-2 bg-gov-gold hover:bg-amber-600 text-slate-900 font-bold text-xs rounded-lg shadow transition flex items-center justify-center"
              >
                Start Application & Check Eligibility
              </button>

            </div>
          </div>
        </div>
      </div>

      {/* Service Description */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="text-sm font-bold text-slate-800 mb-2">
          Service Description
        </h2>

        <p className="text-xs text-slate-600 leading-6">
          {service.description}
        </p>
      </div>

      {/* Required Documents */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-5">

          <div>
            <h2 className="text-sm font-bold text-slate-800">
              Required Documents & Vault Reusability Check
            </h2>

            <p className="text-[11px] text-slate-500 mt-1">
              Documents already available in your personal
              vault can be reused for application preparation.
            </p>
          </div>

          <div className="text-xs font-bold text-gov-blue">
            {readyDocumentCount} of {requiredDocumentCount} ready
          </div>

        </div>

        <div className="space-y-3">

          {docMatches.map((item) => (
            <div
              key={item.required_doc}
              className="border border-slate-200 rounded-lg p-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">

                <div className="flex items-start gap-3">

                  <div className="mt-0.5">

                    {item.status === 'available' && (
                      <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                    )}

                    {item.status === 'warning' && (
                      <AlertTriangle className="w-5 h-5 text-amber-600" />
                    )}

                    {item.status === 'missing' && (
                      <FileText className="w-5 h-5 text-slate-400" />
                    )}

                  </div>

                  <div>
                    <h3 className="text-xs font-bold text-slate-800">
                      {item.required_doc}
                    </h3>

                    <p className="text-[11px] text-slate-500 mt-1">
                      {item.message}
                    </p>
                  </div>

                </div>

                <div>

                  {item.status === 'available' && (
                    <span className="inline-flex items-center text-[10px] bg-emerald-100 text-emerald-700 font-bold px-2.5 py-1 rounded">
                      Vault Ready ✓
                    </span>
                  )}

                  {item.status === 'warning' && (
                    <span className="inline-flex items-center text-[10px] bg-amber-100 text-amber-800 font-bold px-2.5 py-1 rounded">
                      Vault Ready ✓
                    </span>
                  )}

                  {item.status === 'missing' && (
                    <button
                      onClick={() =>
                        handleUploadDocument(
                          item.required_doc
                        )
                      }
                      className="inline-flex items-center text-[10px] bg-gov-blue hover:bg-blue-900 text-white font-bold px-2.5 py-1 rounded transition"
                    >
                      <Upload className="w-3 h-3 mr-1" />
                      Upload Now
                    </button>
                  )}

                </div>

              </div>
            </div>
          ))}

        </div>

        {/* Application Progress */}
        <div className="mt-6 pt-5 border-t border-slate-200">

          <div className="flex items-center justify-between text-xs text-slate-600 font-medium mb-2">

            <span>
              {readyDocumentCount} of {requiredDocumentCount} required documents ready
            </span>

            <span className="font-bold text-gov-blue">
              {calculatedCompletionPercentage}% prepared
            </span>

          </div>

          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">

            <div
              className="bg-gov-blue h-2 rounded-full transition-all duration-500"
              style={{
                width: `${calculatedCompletionPercentage}%`,
              }}
            />

          </div>

        </div>

      </div>

      {/* Important Information */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-5">

        <h2 className="text-sm font-bold text-slate-800 mb-3">
          Important Information & Terms
        </h2>

        <ul className="space-y-2 text-xs text-slate-600">

          <li>
            • Applicant must possess valid native resident
            status in Tamil Nadu.
          </li>

          <li>
            • Documents uploaded are inspected for OCR
            readability and PII masking.
          </li>

          <li>
            • Application progress is saved in My Applications.
          </li>

        </ul>

      </div>

      {/* Official Government Source */}
      <div className="text-xs">

        <a
          href="https://tnesevai.tn.gov.in/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-gov-blue font-semibold hover:underline"
        >
          Official Government Source: TNeGA e-Sevai Portal
        </a>

      </div>

    </div>
  );
};

export default ServiceDetailPage;