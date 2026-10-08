import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

import { documentService } from '../../services/documentService';
import { OCRCard } from '../../components/common/OCRCard';

import {
  RefreshCw,
  Trash2,
  FileCheck,
  Loader2,
  Upload,
} from 'lucide-react';

interface UserDocument {
  id: number;
  filename?: string;
  original_filename?: string;
  document_type?: string;
  status?: string;
  readiness_score?: number;
  extracted_data?: Record<string, any>;
  analysis?: Record<string, any>;
  created_at?: string;
  [key: string]: any;
}

const DocumentUploadPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const requestedDocumentType = searchParams.get('type');

  const [documents, setDocuments] = useState<UserDocument[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [documentType, setDocumentType] = useState(
    requestedDocumentType || 'Aadhaar Card'
  );

  const [loading, setLoading] = useState(false);
  const [vaultLoading, setVaultLoading] = useState(true);
  const [selectedDocument, setSelectedDocument] =
    useState<UserDocument | null>(null);
  const [error, setError] = useState('');

  // Preselect the document type when arriving from
  // Service Details -> Upload Now.
  useEffect(() => {
    if (requestedDocumentType) {
      setDocumentType(requestedDocumentType);
    }
  }, [requestedDocumentType]);

  const loadVault = async () => {
    try {
      setVaultLoading(true);

      const result = await documentService.getUserDocuments();

      setDocuments(result || []);
    } catch (err: any) {
      console.error('Failed to load document vault:', err);

      setError(
        err?.response?.data?.detail ||
          'Unable to load your document vault.'
      );
    } finally {
      setVaultLoading(false);
    }
  };

  useEffect(() => {
    loadVault();
  }, []);

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0] || null;

    setSelectedFile(file);
    setSelectedDocument(null);
    setError('');
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a document first.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await documentService.uploadDocument(
        selectedFile,
        documentType,
        'en'
      );

      setSelectedDocument(result as UserDocument);

      await loadVault();

      setSelectedFile(null);

      const fileInput = document.getElementById(
        'document-file-input'
      ) as HTMLInputElement | null;

      if (fileInput) {
        fileInput.value = '';
      }
    } catch (err: any) {
      console.error('Document upload failed:', err);

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          'Document upload or OCR inspection failed.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      setError('');

      await documentService.deleteDocument(id);

      // Remove it immediately from the current UI.
      setDocuments((currentDocuments) =>
        currentDocuments.filter((doc) => doc.id !== id)
      );

      // If the deleted document was being inspected, clear it.
      if (selectedDocument?.id === id) {
        setSelectedDocument(null);
      }

      // Reload from the backend so the UI reflects the actual vault state.
      await loadVault();
    } catch (err: any) {
      console.error('Document deletion failed:', err);

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          'Unable to delete the document.'
      );
    }
  };

  const getDocumentName = (doc: UserDocument) =>
    doc.original_filename ||
    doc.filename ||
    `Document #${doc.id}`;

  return (
    <div className="max-w-5xl mx-auto space-y-8 font-sans">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-2xl font-extrabold text-slate-900">
          My Documents & Reusable Vault
        </h1>

        <p className="text-sm text-slate-500">
          Upload government documents for OCR inspection, readiness analysis,
          and reuse during service applications.
        </p>
      </div>

      {/* OCR Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-2xl p-5">
        <div className="flex items-start gap-3">
          <FileCheck className="w-5 h-5 text-blue-700 mt-0.5" />

          <div>
            <h2 className="font-bold text-blue-900">
              Automated OCR Inspection Notice
            </h2>

            <p className="text-xs text-blue-800 mt-1 leading-relaxed">
              AccessGov AI performs automated optical character recognition,
              document inspection, PII masking, and readability analysis.
              Official document verification is conducted by the relevant
              government authority upon submission.
            </p>
          </div>
        </div>
      </div>

      {/* Upload */}
      <section className="bg-white border border-slate-200 rounded-3xl shadow-sm p-6 space-y-5">
        <div>
          <h2 className="text-lg font-extrabold text-slate-900">
            Upload Document to Personal Vault
          </h2>

          <p className="text-xs text-slate-500 mt-1">
            Supported formats: PDF, PNG, JPG, JPEG
          </p>
        </div>

        {/* Document Type */}
        <div>
          <label
            htmlFor="document-type"
            className="block text-xs font-bold text-slate-700 mb-2"
          >
            Document Type
          </label>

          <select
            id="document-type"
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value)}
            className="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="Aadhaar Card">
              Aadhaar Card
            </option>

            <option value="Student ID or Bonafide Certificate">
              Student ID or Bonafide Certificate
            </option>

            <option value="Income Certificate">
              Income Certificate
            </option>

            <option value="Bank Account Details">
              Bank Account Details
            </option>

            <option value="Passport Photograph">
              Passport Photograph
            </option>

            <option value="Previous Marksheet">
              Previous Marksheet
            </option>

            <option value="Community / Caste Certificate">
              Community / Caste Certificate
            </option>

            <option value="Address Proof">
              Address Proof
            </option>

            <option value="Smart Ration Card / Family Card">
              Smart Ration Card / Family Card
            </option>

            <option value="Income Supporting Document">
              Income Supporting Document
            </option>

            <option value="Self-Declaration">
              Self-Declaration
            </option>

            <option value="Latest Salary Certificate">
              Latest Salary Certificate
            </option>

            <option value="PAN Card">
              PAN Card
            </option>

            <option value="Bank Passbook">
              Bank Passbook
            </option>

            <option value="Applicant Photo">
              Applicant Photo
            </option>

            <option value="Other Government Document">
              Other Government Document
            </option>
          </select>
        </div>

        {/* File */}
        <div>
          <label
            htmlFor="document-file-input"
            className="block text-xs font-bold text-slate-700 mb-2"
          >
            Select Document
          </label>

          <input
            id="document-file-input"
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={handleFileChange}
            className="block w-full text-sm text-slate-600
              file:mr-4 file:py-2.5 file:px-4
              file:rounded-xl file:border-0
              file:text-xs file:font-bold
              file:bg-slate-100 file:text-slate-700
              hover:file:bg-slate-200"
          />

          {selectedFile && (
            <p className="mt-2 text-xs text-slate-500">
              Selected:{' '}
              <span className="font-semibold">
                {selectedFile.name}
              </span>
            </p>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-xs font-medium">
            {error}
          </div>
        )}

        {/* Upload button */}
        <button
          type="button"
          onClick={handleUpload}
          disabled={!selectedFile || loading}
          className="w-full sm:w-auto px-5 py-3 rounded-xl bg-blue-700 text-white text-sm font-bold
            hover:bg-blue-800 transition
            disabled:opacity-50 disabled:cursor-not-allowed
            flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Inspecting Document...
            </>
          ) : (
            <>
              <Upload className="w-4 h-4" />
              Upload & Inspect Document
            </>
          )}
        </button>
      </section>

      {/* Newly uploaded result */}
      {selectedDocument && (
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-extrabold text-slate-900">
              Inspection Result
            </h2>

            <button
              type="button"
              onClick={() => setSelectedDocument(null)}
              className="px-3 py-2 bg-slate-100 text-slate-700 rounded-xl text-xs font-bold flex items-center gap-2"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Clear
            </button>
          </div>

          <OCRCard doc={selectedDocument as any} />
        </section>
      )}

      {/* Vault */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-extrabold text-slate-900">
              Reusable Personal Vault Repository
            </h2>

            <p className="text-xs text-slate-500 mt-1">
              Your previously uploaded documents.
            </p>
          </div>

          <button
            type="button"
            onClick={loadVault}
            disabled={vaultLoading}
            className="p-2 rounded-xl border border-slate-200 hover:bg-slate-50 disabled:opacity-50"
            title="Refresh vault"
          >
            <RefreshCw
              className={`w-4 h-4 ${
                vaultLoading ? 'animate-spin' : ''
              }`}
            />
          </button>
        </div>

        {vaultLoading ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center">
            <Loader2 className="w-6 h-6 animate-spin mx-auto text-blue-700" />

            <p className="text-xs text-slate-500 mt-3">
              Loading your document vault...
            </p>
          </div>
        ) : documents.length === 0 ? (
          <div className="bg-white border border-dashed border-slate-300 rounded-2xl p-10 text-center">
            <FileCheck className="w-8 h-8 mx-auto text-slate-300" />

            <p className="text-sm font-semibold text-slate-600 mt-3">
              No documents uploaded to your vault yet.
            </p>

            <p className="text-xs text-slate-400 mt-1">
              Upload a document above to begin.
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm"
              >
                <div className="flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <p className="font-bold text-sm text-slate-800 truncate">
                      {getDocumentName(doc)}
                    </p>

                    <p className="text-xs text-slate-500 mt-1">
                      {doc.document_type ||
                        'Government Document'}
                    </p>

                    {doc.created_at && (
                      <p className="text-[10px] text-slate-400 mt-1">
                        {new Date(
                          doc.created_at
                        ).toLocaleString()}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      type="button"
                      onClick={() =>
                        setSelectedDocument(doc)
                      }
                      className="px-3 py-2 rounded-xl bg-blue-50 text-blue-700 text-xs font-bold hover:bg-blue-100"
                    >
                      Inspect
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        handleDelete(doc.id)
                      }
                      className="p-2 rounded-xl bg-red-50 text-red-600 hover:bg-red-100"
                      title="Delete document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
};

export default DocumentUploadPage;