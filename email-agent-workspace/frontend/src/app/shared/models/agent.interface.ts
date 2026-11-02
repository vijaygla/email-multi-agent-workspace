/**
 * TypeScript Data Contracts mirroring FastAPI Pydantic Models and MSSQL Schemas.
 */

export interface Email {
  id: number;
  thread_id?: string;
  subject: string;
  sender: string;
  recipient: string;
  body: string;
  received_at: string;
  status: 'unread' | 'processing' | 'processed' | 'clarification_needed' | 'failed';
  intent?: 'meeting' | 'task' | 'mixed_intent' | 'general_inquiry' | 'unknown';
  confidence?: number;
  is_read: boolean;
}

export interface EmailListResponse {
  total: number;
  emails: Email[];
}

export interface Task {
  id: number;
  email_id?: number;
  title: string;
  description?: string;
  owner: string;
  due_date?: string;
  urgency: 'low' | 'medium' | 'high' | 'urgent';
  status: 'pending' | 'in_progress' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface TaskListResponse {
  total: number;
  tasks: Task[];
}

export interface MeetingSlot {
  start_time: string;
  end_time: string;
  display?: string;
  title?: string;
  confidence?: number;
}

export interface MeetingProposal {
  id: number;
  email_id?: number;
  requested_dates?: string;
  participants?: string;
  proposed_slots_json: string;
  status: 'staged' | 'confirmed' | 'declined';
  stage: number; // 1 = Draft Review, 2 = Auto Coordinated
  created_at: string;
  // Parsed helper
  parsed_slots?: MeetingSlot[];
}

export interface MeetingProposalListResponse {
  total: number;
  proposals: MeetingProposal[];
}

export interface Draft {
  id: number;
  email_id?: number;
  recipient: string;
  subject: string;
  body: string;
  tone: 'professional' | 'friendly' | 'concise' | 'executive';
  status: 'staged' | 'approved' | 'sent';
  created_at: string;
  approved_at?: string;
  sent_at?: string;
}

export interface ClarificationRequest {
  id: number;
  email_id?: number;
  missing_fields: string;
  question: string;
  options_json: string;
  status: 'pending' | 'resolved';
  resolution?: string;
  created_at: string;
  // Parsed helper
  parsed_options?: string[];
}

export interface ProcessResponse {
  email_id: number;
  intent: string;
  confidence: number;
  status: string;
  meeting_proposal?: any;
  tasks?: any[];
  draft?: Draft;
  clarification?: {
    id: number;
    missing_fields: string;
    question: string;
    options: string[];
  };
  execution_time_ms: number;
}

export interface WebSocketEvent {
  event_type: 'connection_established' | 'agent_start' | 'agent_observe' | 'agent_think' | 'agent_act' | 'agent_finish' | 'autopilot_action' | 'email_ingested' | 'error' | string;
  email_id?: number;
  agent_name: string;
  step: string;
  details: {
    message?: string;
    intent?: string;
    confidence?: number;
    reasoning?: string;
    clarification?: any;
    draft_id?: number;
    status?: string;
    [key: string]: any;
  };
  timestamp: string;
}

export interface SystemStatus {
  status: string;
  app_name: string;
  version: string;
  database: {
    server: string;
    database: string;
    engine: string;
  };
  generative_engine: {
    endpoint: string;
    models: {
      router: string;
      extractor: string;
      reasoning: string;
      drafting: string;
      fallback: string;
    };
  };
  realtime_ws: string;
  autopilot?: AutopilotStatus;
}

export interface AutopilotStatus {
  is_running: boolean;
  polling_enabled: boolean;
  autonomy_level: string; // L0 | L1 | L2 | L3
  confidence_threshold: number;
  poll_interval_seconds: number;
  last_poll_time?: string;
  total_polls_count: number;
  total_emails_ingested: number;
  total_emails_processed: number;
}

export interface AutopilotConfigUpdate {
  autonomy_level?: string;
  background_polling_enabled?: boolean;
  confidence_threshold?: number;
  poll_interval_seconds?: number;
  task_deduplication_enabled?: boolean;
  critic_verification_enabled?: boolean;
}

