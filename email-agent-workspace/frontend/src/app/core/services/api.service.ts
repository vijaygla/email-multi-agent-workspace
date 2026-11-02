import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Email,
  EmailListResponse,
  Task,
  TaskListResponse,
  MeetingProposal,
  MeetingProposalListResponse,
  Draft,
  ClarificationRequest,
  ProcessResponse,
  SystemStatus,
  AutopilotStatus,
  AutopilotConfigUpdate
} from '../../shared/models/agent.interface';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = 'http://127.0.0.1:8000';
  private readonly apiUrl = `${this.baseUrl}/api`;

  constructor(private http: HttpClient) {}

  // ---- System Status ----
  getSystemStatus(): Observable<SystemStatus> {
    return this.http.get<SystemStatus>(`${this.baseUrl}/`);
  }

  // ---- Emails ----
  getEmails(skip = 0, limit = 50, status?: string, intent?: string): Observable<EmailListResponse> {
    let params = new HttpParams()
      .set('skip', skip.toString())
      .set('limit', limit.toString());
    if (status) params = params.set('status', status);
    if (intent) params = params.set('intent', intent);

    return this.http.get<EmailListResponse>(`${this.apiUrl}/emails`, { params });
  }

  getEmail(emailId: number): Observable<Email> {
    return this.http.get<Email>(`${this.apiUrl}/emails/${emailId}`);
  }

  ingestEmail(payload: { subject: string; sender: string; recipient?: string; body: string; thread_id?: string }): Observable<Email> {
    return this.http.post<Email>(`${this.apiUrl}/emails`, {
      recipient: 'user@nexus.ai',
      ...payload
    });
  }

  markEmailAsRead(emailId: number): Observable<Email> {
    return this.http.patch<Email>(`${this.apiUrl}/emails/${emailId}/read`, {});
  }

  // ---- Multi-Agent Processing (Core Loop) ----
  processEmail(emailId: number, tone: string = 'professional'): Observable<ProcessResponse> {
    return this.http.post<ProcessResponse>(`${this.apiUrl}/process`, {
      email_id: emailId,
      tone
    });
  }

  // ---- Tasks (MSSQL Persistence) ----
  getTasks(status?: string, urgency?: string, emailId?: number): Observable<TaskListResponse> {
    let params = new HttpParams();
    if (status) params = params.set('status', status);
    if (urgency) params = params.set('urgency', urgency);
    if (emailId) params = params.set('email_id', emailId.toString());

    return this.http.get<TaskListResponse>(`${this.apiUrl}/tasks`, { params });
  }

  createTask(task: Partial<Task>): Observable<Task> {
    return this.http.post<Task>(`${this.apiUrl}/tasks`, task);
  }

  updateTask(taskId: number, updates: Partial<Task>): Observable<Task> {
    return this.http.put<Task>(`${this.apiUrl}/tasks/${taskId}`, updates);
  }

  deleteTask(taskId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/tasks/${taskId}`);
  }

  // ---- Calendar & Meetings ----
  getMeetings(status?: string, stage?: number): Observable<MeetingProposalListResponse> {
    let params = new HttpParams();
    if (status) params = params.set('status', status);
    if (stage !== undefined) params = params.set('stage', stage.toString());

    return this.http.get<MeetingProposalListResponse>(`${this.apiUrl}/scheduled-meetings`, { params });
  }

  confirmMeeting(proposalId: number): Observable<MeetingProposal> {
    return this.http.post<MeetingProposal>(`${this.apiUrl}/scheduled-meetings/${proposalId}/confirm`, {});
  }

  // ---- Drafts & Actions ----
  getDrafts(status?: string, emailId?: number): Observable<Draft[]> {
    let params = new HttpParams();
    if (status) params = params.set('status', status);
    if (emailId) params = params.set('email_id', emailId.toString());

    return this.http.get<Draft[]>(`${this.apiUrl}/drafts`, { params });
  }

  composeDraft(payload: { email_id?: number; recipient: string; subject: string; body: string; tone?: string }): Observable<Draft> {
    return this.http.post<Draft>(`${this.apiUrl}/compose`, payload);
  }

  approveDraft(draftId: number): Observable<Draft> {
    return this.http.post<Draft>(`${this.apiUrl}/drafts/${draftId}/approve`, {});
  }

  sendDraft(draftId: number): Observable<Draft> {
    return this.http.post<Draft>(`${this.apiUrl}/drafts/${draftId}/send`, {});
  }

  // ---- Clarifications (Supervisor Agent) ----
  getClarifications(status?: string, emailId?: number): Observable<ClarificationRequest[]> {
    let params = new HttpParams();
    if (status) params = params.set('status', status);
    if (emailId) params = params.set('email_id', emailId.toString());

    return this.http.get<ClarificationRequest[]>(`${this.apiUrl}/clarifications`, { params });
  }

  replyClarification(clarificationId: number, answer: string): Observable<ClarificationRequest> {
    return this.http.post<ClarificationRequest>(`${this.apiUrl}/clarifications/${clarificationId}/reply`, { answer });
  }

  // ---- Autopilot & Autonomous Engine ----
  getAutopilotStatus(): Observable<AutopilotStatus> {
    return this.http.get<AutopilotStatus>(`${this.apiUrl}/autopilot/status`);
  }

  configureAutopilot(config: AutopilotConfigUpdate): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/autopilot/configure`, config);
  }

  triggerPollNow(): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/autopilot/poll-now`, {});
  }

  startBackgroundWorker(): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/autopilot/worker/start`, {});
  }

  stopBackgroundWorker(): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/autopilot/worker/stop`, {});
  }
}
