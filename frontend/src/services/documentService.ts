import { apiClient } from './apiClient';

export interface UserDocument {
  id: number;
  document_type: string;
  file_name: string;
  file_path?: string;
  mime_type?: string;
  file_size_bytes?: number;
  ocr_status: string;
  readiness_score: number;
  readability_score: number;
  ocr_confidence: number;
  sharpness_score: number;
  quality_issues: string[];
  extracted_fields?: Record<string, string>;
  validation_errors?: string[];
  created_at: string;
}

export interface DocumentAnalytics {
  total_documents: number;
  successful_ocr: number;
  quality_issues: number;
  average_readiness: number;
  document_types: Array<{ type: string; count: number }>;
}

function mapAnalysisToDocument(data: any): UserDocument {
  return {
    id: Number(data.document_id),
    document_type: data.document_type || 'Unknown Document',
    file_name: data.file_name || 'Uploaded document',
    file_path: data.file_path,
    mime_type: data.mime_type,
    file_size_bytes: data.file_size_bytes,
    ocr_status: data.ocr_result?.status || 'unknown',
    readiness_score: Number(data.readiness_result?.readiness_score ?? 0),
    readability_score: Number(data.ocr_result?.readability_score ?? 0),
    ocr_confidence: Number(data.ocr_result?.confidence ?? 0) * 100,
    sharpness_score: Number(data.ocr_result?.sharpness_score ?? 0),
    quality_issues: data.ocr_result?.quality_issues || [],
    extracted_fields: data.extracted_fields || {},
    validation_errors: [
      ...(data.validation_result?.missing_fields || []),
      ...(data.validation_result?.warnings || []),
    ],
    created_at: data.created_at || new Date().toISOString(),
  };
}

export const documentService = {
  async uploadDocument(
    file: File,
    documentType: string,
    language = 'en'
  ): Promise<UserDocument> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    formData.append('language', language);

    const res = await apiClient.post('/documents/upload', formData, {
      timeout: 120000,
    });

    // Backend returns DocumentAnalysisResponse. Never fabricate a score when the request fails.
    return mapAnalysisToDocument(res.data);
  },

  async getUserDocuments(): Promise<UserDocument[]> {
    const res = await apiClient.get('/documents/me');

    console.log(
      'VAULT DOCUMENT #6:',
      JSON.stringify(res.data, null, 2)
    );

    return (res.data || []).map((d: any) => ({
      id: Number(d.id),
      document_type: d.document_type || 'Unknown Document',
      file_name: d.file_name,
      file_path: d.file_path,
      mime_type: d.mime_type,
      file_size_bytes: d.file_size_bytes,
      ocr_status: d.ocr_status || 'unknown',
      readiness_score: Number(d.readiness_score ?? 0),
      readability_score: Number(d.readability_score ?? 0),
      ocr_confidence: Number(d.ocr_confidence ?? 0),
      sharpness_score: Number(d.sharpness_score ?? 0),
      quality_issues: d.quality_issues || [],
      extracted_fields: d.extracted_fields || {},
      validation_errors: d.validation_errors || [],
      created_at: d.uploaded_at,
    }));
  },

  async analyzeDocument(documentId: number): Promise<UserDocument> {
    const res = await apiClient.post(`/documents/${documentId}/analyze`);
    return mapAnalysisToDocument(res.data);
  },

  async deleteDocument(documentId: number): Promise<void> {
    await apiClient.delete(`/documents/${documentId}`);
  },

  async getAdminAnalytics(): Promise<DocumentAnalytics> {
    const res = await apiClient.get('/documents/admin/analytics');
    return res.data;
  },
};