import { UserDocument } from './documentService';

export type ApplicationStatusType = 
  | 'Draft'
  | 'Documents Pending'
  | 'Ready for Submission'
  | 'Submitted'
  | 'Under Review'
  | 'Approved'
  | 'Rejected';

export interface ApplicationDraft {
  id: string;
  service_id: number;
  service_code: string;
  service_name: string;
  category: string;
  status: ApplicationStatusType;
  completion_percentage: number;
  current_step: number;
  answers: Record<string, any>;
  attached_documents: Record<string, number>; // doc_type -> user_doc_id
  last_saved_at: string;
}

export const applicationService = {
  getDrafts(): ApplicationDraft[] {
    const saved = localStorage.getItem('accessgov_application_drafts');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          // Remove the old fabricated demo record from previous builds.
          const cleaned = parsed.filter((d: ApplicationDraft) => d.id !== 'draft_scholarship_01');
          if (cleaned.length !== parsed.length) {
            localStorage.setItem('accessgov_application_drafts', JSON.stringify(cleaned));
          }
          return cleaned;
        }
      } catch {}
    }
    return [];
  },

  saveDraft(draft: Partial<ApplicationDraft> & { service_id: number; service_name: string }): ApplicationDraft {
    const drafts = this.getDrafts();
    const existingIndex = drafts.findIndex(d => d.service_id === draft.service_id && d.status === 'Draft');
    
    const updatedDraft: ApplicationDraft = {
      id: draft.id || `draft_${draft.service_id}_${Date.now()}`,
      service_id: draft.service_id,
      service_code: draft.service_code || 'GOV-SCH-01',
      service_name: draft.service_name,
      category: draft.category || 'General',
      status: draft.status || 'Draft',
      completion_percentage: draft.completion_percentage || 40,
      current_step: draft.current_step || 1,
      answers: draft.answers || {},
      attached_documents: draft.attached_documents || {},
      last_saved_at: new Date().toISOString()
    };

    if (existingIndex >= 0) {
      drafts[existingIndex] = updatedDraft;
    } else {
      drafts.unshift(updatedDraft);
    }

    localStorage.setItem('accessgov_application_drafts', JSON.stringify(drafts));
    return updatedDraft;
  },

  getDraftByServiceId(serviceId: number): ApplicationDraft | undefined {
    return this.getDrafts().find(d => d.service_id === serviceId);
  },

  // Auto-checks reusable vault documents against service required documents
  checkDocumentVaultMatch(requiredDocs: string[], vaultDocs: UserDocument[]) {
    return requiredDocs.map(reqDoc => {
      const match = vaultDocs.find(v => 
        v.document_type.toLowerCase() === reqDoc.toLowerCase() ||
        v.file_name.toLowerCase().includes(reqDoc.toLowerCase())
      );

      if (match) {
        const isExpiring = match.readiness_score < 70;
        return {
          required_doc: reqDoc,
          status: isExpiring ? ('warning' as const) : ('available' as const),
          document: match,
          message: isExpiring ? 'Document readiness score is low (review suggested).' : 'Available in My Documents.'
        };
      } else {
        return {
          required_doc: reqDoc,
          status: 'missing' as const,
          document: null,
          message: 'Not found in My Documents vault. Upload required.'
        };
      }
    });
  }
};
