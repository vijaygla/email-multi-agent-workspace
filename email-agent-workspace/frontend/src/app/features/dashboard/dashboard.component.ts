import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';

import { ApiService } from '../../core/services/api.service';
import { WebSocketService } from '../../core/services/websocket.service';
import { ToastService } from '../../shared/components/toast/toast.service';
import {
  Email,
  Task,
  MeetingProposal,
  Draft,
  ClarificationRequest,
  WebSocketEvent,
  SystemStatus,
  AutopilotStatus
} from '../../shared/models/agent.interface';

import { SidebarComponent } from '../sidebar/sidebar.component';
import { EmailListComponent } from '../email-list/email-list.component';
import { AiAnalysisComponent } from '../ai-analysis/ai-analysis.component';
import { TaskBoardComponent } from '../task-board/task-board.component';
import { MeetingsComponent } from '../meetings/meetings.component';
import { TelemetryComponent } from '../telemetry/telemetry.component';
import { ComposeModalComponent } from '../compose-modal/compose-modal.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    SidebarComponent,
    EmailListComponent,
    AiAnalysisComponent,
    TaskBoardComponent,
    MeetingsComponent,
    TelemetryComponent,
    ComposeModalComponent
  ],
  template: `
    <div class="dashboard-root">
      <!-- Panel 1: Sidebar -->
      <app-sidebar
        [activeTab]="activeTab"
        [unreadCount]="unreadCount"
        [tasksCount]="pendingTasksCount"
        [meetingsCount]="stagedMeetingsCount"
        [clarificationsCount]="pendingClarificationsCount"
        [isWsConnected]="isWsConnected"
        [isCollapsed]="isSidebarCollapsed"
        [autopilotStatus]="autopilotStatus"
        (tabChange)="activeTab = $event"
        (toggleCollapse)="isSidebarCollapsed = $event"
        (openCompose)="showComposeModal = true"
        (changeAutonomyLevel)="onChangeAutonomyLevel($event)"
        (triggerPollNow)="onTriggerPollNow()"
      ></app-sidebar>

      <!-- Main Workspace Panel Based on Active Tab -->
      <ng-container [ngSwitch]="activeTab">
        <!-- Default: Inbox 3-Column Experience -->
        <div *ngSwitchCase="'inbox'" class="inbox-panels">
          <!-- Panel 2: Email Deck -->
          <app-email-list
            [emails]="emails"
            [selectedEmail]="selectedEmail"
            (emailSelect)="onSelectEmail($event)"
            (refresh)="onManualSync()"
          ></app-email-list>

          <!-- Panel 3: AI Intelligence Hub -->
          <app-ai-analysis
            [email]="selectedEmail"
            [isProcessing]="isProcessing"
            [currentStepIndex]="currentStepIndex"
            [meetingProposal]="activeMeetingProposal"
            [tasks]="activeTasks"
            [draft]="activeDraft"
            [clarification]="activeClarification"
            [recentEvents]="recentEvents"
            (runPipeline)="onRunPipeline($event)"
            (confirmMeeting)="onConfirmMeeting($event)"
            (taskStatusToggle)="onToggleTaskStatus($event)"
            (approveDraft)="onApproveDraft($event)"
            (sendDraft)="onSendDraft($event)"
            (submitClarificationReply)="onSubmitClarificationReply($event)"
          ></app-ai-analysis>
        </div>

        <!-- Tab 2: Full Task Board (MSSQL) -->
        <app-task-board
          *ngSwitchCase="'tasks'"
          [tasks]="tasks"
          (taskUpdate)="onUpdateTask($event.id, $event.updates)"
          (taskCreate)="onCreateTask($event)"
          (deleteTask)="onDeleteTask($event)"
        ></app-task-board>

        <!-- Tab 3: Calendar Proposals (Outlook) -->
        <app-meetings
          *ngSwitchCase="'meetings'"
          [proposals]="meetings"
          (confirmMeeting)="onConfirmMeeting($event)"
        ></app-meetings>

        <!-- Tab 4: Clarifications -->
        <div *ngSwitchCase="'clarifications'" class="clarifications-view">
          <div class="header">
            <h2>Pending Clarification Requests (Case 5)</h2>
            <p class="subtitle">Requests paused by the Supervisor Agent awaiting clarification.</p>
          </div>

          <div *ngIf="clarifications.length === 0" class="empty-state glass-panel">
            <p>All email requests are clear! No pending clarifications.</p>
          </div>

          <div class="clarifications-grid">
            <div *ngFor="let c of clarifications" class="clarification-card glass-panel" [class.resolved]="c.status === 'resolved'">
              <div class="card-top">
                <span class="badge badge-clarification">Request #{{ c.id }}</span>
                <span class="status-tag">{{ c.status | uppercase }}</span>
              </div>
              <p class="question">{{ c.question }}</p>
              
              <div class="options-container" *ngIf="c.status === 'pending'">
                <div class="opt-label">Quick select:</div>
                <div class="opts-list">
                  <button *ngFor="let opt of c.parsed_options" class="btn btn-secondary" (click)="onSubmitClarificationReply({ id: c.id, answer: opt })">
                    {{ opt }}
                  </button>
                </div>
              </div>

              <div *ngIf="c.status === 'resolved'" class="resolution-box">
                <strong>Resolution provided:</strong> {{ c.resolution }}
              </div>
            </div>
          </div>
        </div>

        <!-- Tab 5: Live Telemetry & Spans -->
        <app-telemetry
          *ngSwitchCase="'telemetry'"
          [events]="eventsLog"
          [systemStatus]="systemStatus"
        ></app-telemetry>
      </ng-container>

      <!-- Ingest / Compose Modal -->
      <app-compose-modal
        *ngIf="showComposeModal"
        (close)="showComposeModal = false"
        (ingest)="onIngestEmail($event)"
      ></app-compose-modal>
    </div>
  `,
  styles: [`
    .dashboard-root {
      display: flex;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      background: var(--bg-primary);
    }
    .inbox-panels {
      display: flex;
      flex: 1;
      min-width: 0;
      height: 100vh;
      overflow: hidden;
    }
    .clarifications-view {
      flex: 1;
      height: 100vh;
      overflow-y: auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .header h2 {
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--text-primary);
    }
    .subtitle {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-top: 4px;
    }
    .empty-state {
      padding: 40px;
      text-align: center;
      color: var(--text-muted);
    }
    .clarifications-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
      gap: 16px;
    }
    .clarification-card {
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      border-left: 4px solid var(--accent-amber);
    }
    .clarification-card.resolved {
      border-left-color: var(--accent-green);
      opacity: 0.8;
    }
    .card-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .status-tag {
      font-size: 0.7rem;
      font-weight: 700;
      color: var(--accent-amber);
    }
    .question {
      font-size: 0.95rem;
      color: var(--text-primary);
      font-weight: 500;
      line-height: 1.5;
    }
    .options-container {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .opt-label {
      font-size: 0.72rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }
    .opts-list {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .resolution-box {
      font-size: 0.82rem;
      color: var(--accent-green);
      background: rgba(16, 185, 129, 0.1);
      padding: 8px 12px;
      border-radius: var(--radius-md);
    }
  `]
})
export class DashboardComponent implements OnInit, OnDestroy {
  activeTab = 'inbox';
  emails: Email[] = [];
  selectedEmail: Email | null = null;
  tasks: Task[] = [];
  meetings: MeetingProposal[] = [];
  drafts: Draft[] = [];
  clarifications: ClarificationRequest[] = [];
  eventsLog: WebSocketEvent[] = [];
  recentEvents: WebSocketEvent[] = [];
  systemStatus: SystemStatus | null = null;
  autopilotStatus: AutopilotStatus | null = null;

  isWsConnected = false;
  isProcessing = false;
  isSidebarCollapsed = false;
  currentStepIndex = 0;
  showComposeModal = false;

  private subs = new Subscription();

  constructor(
    private api: ApiService,
    private ws: WebSocketService,
    private toast: ToastService
  ) {}

  ngOnInit() {
    this.loadAllData();
    this.subscribeToWebSocket();
  }

  ngOnDestroy() {
    this.subs.unsubscribe();
  }

  get unreadCount(): number {
    return this.emails.filter(e => !e.is_read).length;
  }

  get pendingTasksCount(): number {
    return this.tasks.filter(t => t.status === 'pending').length;
  }

  get stagedMeetingsCount(): number {
    return this.meetings.filter(m => m.stage === 1).length;
  }

  get pendingClarificationsCount(): number {
    return this.clarifications.filter(c => c.status === 'pending').length;
  }

  get activeMeetingProposal(): MeetingProposal | null {
    if (!this.selectedEmail) return null;
    return this.meetings.find(m => m.email_id === this.selectedEmail?.id) || null;
  }

  get activeTasks(): Task[] {
    if (!this.selectedEmail) return [];
    return this.tasks.filter(t => t.email_id === this.selectedEmail?.id);
  }

  get activeDraft(): Draft | null {
    if (!this.selectedEmail) return null;
    return this.drafts.find(d => d.email_id === this.selectedEmail?.id) || null;
  }

  get activeClarification(): ClarificationRequest | null {
    if (!this.selectedEmail) return null;
    return this.clarifications.find(c => c.email_id === this.selectedEmail?.id && c.status === 'pending') || null;
  }

  loadAllData() {
    // 1. Fetch Emails
    this.api.getEmails().subscribe({
      next: (res) => {
        this.emails = res.emails;
        if (!this.selectedEmail && this.emails.length > 0) {
          this.onSelectEmail(this.emails[0]);
        }
      },
      error: (err) => console.error('Failed to load emails:', err)
    });

    // 2. Fetch Tasks (MSSQL)
    this.api.getTasks().subscribe({
      next: (res) => this.tasks = res.tasks,
      error: (err) => console.error('Failed to load tasks:', err)
    });

    // 3. Fetch Meeting Proposals
    this.api.getMeetings().subscribe({
      next: (res) => {
        this.meetings = res.proposals.map(p => ({
          ...p,
          parsed_slots: p.proposed_slots_json ? JSON.parse(p.proposed_slots_json) : []
        }));
      },
      error: (err) => console.error('Failed to load meetings:', err)
    });

    // 4. Fetch Drafts
    this.api.getDrafts().subscribe({
      next: (res) => this.drafts = res,
      error: (err) => console.error('Failed to load drafts:', err)
    });

    // 5. Fetch Clarifications
    this.api.getClarifications().subscribe({
      next: (res) => {
        this.clarifications = res.map(c => ({
          ...c,
          parsed_options: c.options_json ? JSON.parse(c.options_json) : []
        }));
      },
      error: (err) => console.error('Failed to load clarifications:', err)
    });

    // 6. Fetch System Diagnostic
    this.api.getSystemStatus().subscribe({
      next: (status) => this.systemStatus = status,
      error: (err) => console.warn('Backend status check pending:', err)
    });

    // 7. Fetch Autopilot Live Status
    this.api.getAutopilotStatus().subscribe({
      next: (status) => this.autopilotStatus = status,
      error: (err) => console.warn('Autopilot status pending:', err)
    });
  }

  onManualSync() {
    this.loadAllData();
    this.toast.info('Workspace Synced', 'Refreshed emails, tasks, and calendar proposals from MSSQL.');
  }

  subscribeToWebSocket() {
    this.subs.add(
      this.ws.isConnected$.subscribe(connected => {
        this.isWsConnected = connected;
      })
    );

    this.subs.add(
      this.ws.events$.subscribe((event: WebSocketEvent) => {
        this.eventsLog.unshift(event);
        if (this.eventsLog.length > 50) this.eventsLog.pop();

        // Autopilot event notifications
        if (event.event_type === 'autopilot_action') {
          const actions = event.details['actions'] as string[] | undefined;
          const actionMsg = actions?.join(', ') || 'Autonomous action executed';
          this.toast.success('Autopilot Action', actionMsg);
          this.loadAllData();
        } else if (event.event_type === 'email_ingested') {
          const subject = event.details['subject'] as string | undefined;
          this.toast.info('Autonomous Ingestion', `Auto-ingested: ${subject || 'New message'}`);
          this.loadAllData();
        }

        if (this.selectedEmail && event.email_id === this.selectedEmail.id) {
          this.recentEvents.push(event);
          if (this.recentEvents.length > 8) this.recentEvents.shift();

          // Advance Stepper based on agent step
          switch (event.step?.toLowerCase()) {
            case 'observe': this.currentStepIndex = 1; break;
            case 'think': this.currentStepIndex = 2; break;
            case 'act': this.currentStepIndex = 3; break;
            case 'audit': this.currentStepIndex = 4; break;
            case 'draft': this.currentStepIndex = 5; break;
            case 'finish': this.currentStepIndex = 5; break;
          }
        }
      })
    );
  }

  onSelectEmail(email: Email) {
    this.selectedEmail = email;
    this.recentEvents = [];
    this.currentStepIndex = email.status === 'processed' ? 5 : 0;

    if (!email.is_read) {
      this.api.markEmailAsRead(email.id).subscribe({
        next: (updated) => email.is_read = true
      });
    }
  }

  onRunPipeline(tone: string) {
    if (!this.selectedEmail) return;
    this.isProcessing = true;
    this.currentStepIndex = 1;
    this.recentEvents = [];

    this.toast.info('Agent Loop Started', `Executing Observe -> Think -> Act pattern for Email #${this.selectedEmail.id}`);

    this.api.processEmail(this.selectedEmail.id, tone).subscribe({
      next: (res) => {
        this.isProcessing = false;
        this.currentStepIndex = 5;
        this.toast.success('Agent Workflow Complete', `Processed intent: ${res.intent.toUpperCase()}`);
        this.loadAllData();
      },
      error: (err) => {
        this.isProcessing = false;
        this.toast.error('Workflow Error', err?.error?.detail || 'Failed processing email');
        console.error('Process error:', err);
      }
    });
  }

  onConfirmMeeting(proposalId: number) {
    this.api.confirmMeeting(proposalId).subscribe({
      next: () => {
        this.toast.success('Meeting Confirmed', 'Advanced to Stage 2: Booked on corporate calendar');
        this.loadAllData();
      },
      error: (err) => this.toast.error('Confirmation Failed', 'Could not confirm meeting')
    });
  }

  onToggleTaskStatus(task: Task) {
    const nextStatus = task.status === 'completed' ? 'pending' : 'completed';
    this.api.updateTask(task.id, { status: nextStatus }).subscribe({
      next: (updated) => {
        task.status = updated.status;
        this.toast.success('Task Updated', `Task #${task.id} marked as ${nextStatus}`);
        this.loadAllData();
      }
    });
  }

  onUpdateTask(id: number, updates: Partial<Task>) {
    this.api.updateTask(id, updates).subscribe({
      next: () => {
        this.toast.success('Task Updated', 'Task successfully saved');
        this.loadAllData();
      }
    });
  }

  onCreateTask(task: Partial<Task>) {
    this.api.createTask(task).subscribe({
      next: (created) => {
        this.toast.success('Task Created', `Saved #${created.id} into MSSQL`);
        this.loadAllData();
      }
    });
  }

  onDeleteTask(id: number) {
    this.api.deleteTask(id).subscribe({
      next: () => {
        this.toast.info('Task Deleted', `Removed Task #${id}`);
        this.loadAllData();
      }
    });
  }

  onApproveDraft(draftId: number) {
    this.api.approveDraft(draftId).subscribe({
      next: () => {
        this.toast.success('Draft Approved', 'Response is staged and ready to dispatch');
        this.loadAllData();
      }
    });
  }

  onSendDraft(draftId: number) {
    this.api.sendDraft(draftId).subscribe({
      next: () => {
        this.toast.success('Email Dispatched', 'Response sent via corporate Outlook service');
        this.loadAllData();
      }
    });
  }

  onSubmitClarificationReply(payload: { id: number; answer: string }) {
    this.api.replyClarification(payload.id, payload.answer).subscribe({
      next: () => {
        this.toast.success('Clarification Resolved', 'Pause lifted. Re-analyzing email context.');
        this.loadAllData();
        if (this.selectedEmail) {
          this.onRunPipeline('professional');
        }
      }
    });
  }

  onIngestEmail(payload: { sender: string; subject: string; body: string }) {
    this.api.ingestEmail(payload).subscribe({
      next: (newEmail) => {
        this.showComposeModal = false;
        this.toast.success('Email Ingested', `Email #${newEmail.id} saved to MSSQL`);
        this.loadAllData();
        this.selectedEmail = newEmail;
      },
      error: (err) => this.toast.error('Ingest Failed', 'Could not save email')
    });
  }

  onChangeAutonomyLevel(level: string) {
    this.api.configureAutopilot({ autonomy_level: level }).subscribe({
      next: (res) => {
        this.autopilotStatus = res.current_config;
        this.toast.success('Autonomy Updated', `Switched to ${level} mode`);
      },
      error: (err) => this.toast.error('Config Error', 'Could not update autonomy level')
    });
  }

  onTriggerPollNow() {
    this.toast.info('Autonomous Poll', 'Scanning inbox for incoming emails...');
    this.api.triggerPollNow().subscribe({
      next: (res) => {
        const ingested = res.result?.ingested || 0;
        const processed = res.result?.processed || 0;
        this.toast.success('Poll Complete', `Ingested: ${ingested}, Processed: ${processed}`);
        this.loadAllData();
      },
      error: (err) => this.toast.error('Poll Error', 'Failed to execute autonomous poll')
    });
  }
}
