import { apiClient } from './apiClient';

export interface OverviewAnalytics {
  total_citizens: number;
  new_citizens_today: number;
  total_documents: number;
  avg_readiness_score: number;
  ocr_success_rate: number;
  total_conversations: number;
}

export interface ConversationAnalytics {
  total_conversations: number;
  conversations_today: number;
  active_sessions_today: number;
  avg_latency_ms: number;
  avg_confidence: number;
  fallback_count: number;
  language_distribution: Array<{ language: string; count: number }>;
  hourly_activity: Array<{ hour: string; count: number }>;
  intent_distribution: Array<{ intent: string; count: number }>;
}

export interface AccessibilityAnalytics {
  total_telemetry_events: number;
  font_scale_distribution: Array<{ scale: string; count: number }>;
  contrast_mode_distribution: Array<{ mode: string; count: number }>;
  screen_reader_users: number;
}

export const analyticsService = {
  async getOverviewAnalytics(): Promise<OverviewAnalytics> {
    try {
      const res = await apiClient.get('/analytics/overview');
      if (res.data) return res.data;
    } catch {}

    // Database fallback (Zero / Actual DB state)
    return {
      total_citizens: 0,
      new_citizens_today: 0,
      total_documents: 0,
      avg_readiness_score: 0.0,
      ocr_success_rate: 0.0,
      total_conversations: 0
    };
  },

  async getConversationAnalytics(): Promise<ConversationAnalytics> {
    try {
      const res = await apiClient.get('/analytics/conversations');
      if (res.data) return res.data;
    } catch {}

    return {
      total_conversations: 0,
      conversations_today: 0,
      active_sessions_today: 0,
      avg_latency_ms: 0,
      avg_confidence: 0.0,
      fallback_count: 0,
      language_distribution: [],
      hourly_activity: [],
      intent_distribution: []
    };
  },

  async getAccessibilityAnalytics(): Promise<AccessibilityAnalytics> {
    try {
      const res = await apiClient.get('/analytics/accessibility');
      if (res.data) return res.data;
    } catch {}

    return {
      total_telemetry_events: 0,
      font_scale_distribution: [],
      contrast_mode_distribution: [],
      screen_reader_users: 0
    };
  }
};
