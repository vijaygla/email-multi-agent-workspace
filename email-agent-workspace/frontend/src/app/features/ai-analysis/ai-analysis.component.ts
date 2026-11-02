import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  Email,
  Task,
  MeetingProposal,
  Draft,
  ClarificationRequest,
  WebSocketEvent
} from '../../shared/models/agent.interface';

@Component({
  selector: 'app-ai-analysis',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <main class="analysis-panel">
      <!-- Empty State when no email selected -->
      <div *ngIf="!email" class="no-selection-state">
        <div class="hero-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
          </svg>
        </div>
        <h2>Enterprise Email Agent Workspace</h2>
        <p class="hero-desc">
          Select an incoming email from the deck to trigger the Nexus Multi-Agent System (Observe -> Think -> Act).
        </p>

        <div class="capabilities-grid">
          <div class="cap-card">
            <div class="cap-tag badge-meeting">Case 1</div>
            <h4>Calendar Finder</h4>
            <p>Discovers open schedule slots via Outlook Calendar and stages proposal drafts.</p>
          </div>

          <div class="cap-card">
            <div class="cap-tag badge-task">Case 2</div>
            <h4>To-Do Creator</h4>
            <p>Scans actionable work items and records tasks directly into Microsoft SQL Server.</p>
          </div>

          <div class="cap-card">
            <div class="cap-tag badge-mixed">Case 3</div>
            <h4>Mixed Intent Router</h4>
            <p>Concurrently splits compound emails to coordinate slots and log tasks simultaneously.</p>
          </div>

          <div class="cap-card">
            <div class="cap-tag badge-clarification">Case 5</div>
            <h4>Double-Checker</h4>
            <p>Pauses workflow when crucial data is missing and drafts clarifying questions.</p>
          </div>
        </div>
      </div>

      <!-- Email Analysis View -->
      <div *ngIf="email" class="analysis-content">
        <!-- Top Toolbar -->
        <header class="analysis-header glass-panel">
          <div class="header-main">
            <div class="header-titles">
              <div class="intent-row">
                <span *ngIf="email.intent === 'meeting'" class="badge badge-meeting">Case 1: Meeting</span>
                <span *ngIf="email.intent === 'task'" class="badge badge-task">Case 2: Task</span>
                <span *ngIf="email.intent === 'mixed_intent'" class="badge badge-mixed">Case 3: Mixed Intent</span>
                <span *ngIf="email.status === 'clarification_needed'" class="badge badge-clarification">Case 5: Clarification</span>
                <span *ngIf="email.confidence" class="confidence-pill">
                  {{ (email.confidence * 100).toFixed(0) }}% Confidence
                </span>
              </div>
              <h2 class="email-subject-title">{{ email.subject }}</h2>
              <div class="meta-row">
                <span>From: <strong>{{ email.sender }}</strong></span>
                <span>To: <strong>{{ email.recipient }}</strong></span>
                <span>Received: {{ email.received_at | date:'medium' }}</span>
              </div>
            </div>

            <!-- Run Agent Pipeline Actions -->
            <div class="header-actions">
              <div class="tone-select-group">
                <label>Tone:</label>
                <select class="form-control tone-select" [(ngModel)]="selectedTone">
                  <option value="professional">Professional</option>
                  <option value="friendly">Friendly</option>
                  <option value="executive">Executive</option>
                  <option value="concise">Concise</option>
                </select>
              </div>

              <button 
                class="btn btn-primary run-btn" 
                [disabled]="isProcessing"
                (click)="onRunPipeline()"
              >
                <svg *ngIf="!isProcessing" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                <div *ngIf="isProcessing" class="spinner-small"></div>
                <span>{{ isProcessing ? 'Running Agents...' : 'Run AI Analysis' }}</span>
              </button>
            </div>
          </div>
        </header>

        <!-- Multi-Agent Stepper (Observe -> Think -> Act) -->
        <div class="agent-stepper glass-panel">
          <div class="stepper-title">
            <div class="pulse-dot"></div>
            <span>Agent Execution Pipeline</span>
          </div>

          <div class="steps-row">
            <div class="step-node" [class.active]="currentStepIndex >= 1" [class.running]="isProcessing && currentStepIndex === 1">
              <div class="node-circle">1</div>
              <div class="node-label">
                <span class="agent-role">Reader Agent</span>
                <span class="agent-phase">Observe</span>
              </div>
            </div>

            <div class="step-line" [class.filled]="currentStepIndex >= 2"></div>

            <div class="step-node" [class.active]="currentStepIndex >= 2" [class.running]="isProcessing && currentStepIndex === 2">
              <div class="node-circle">2</div>
              <div class="node-label">
                <span class="agent-role">Router Agent</span>
                <span class="agent-phase">Think</span>
              </div>
            </div>

            <div class="step-line" [class.filled]="currentStepIndex >= 3"></div>

            <div class="step-node" [class.active]="currentStepIndex >= 3" [class.running]="isProcessing && currentStepIndex === 3">
              <div class="node-circle">3</div>
              <div class="node-label">
                <span class="agent-role">Calendar / Task</span>
                <span class="agent-phase">Act</span>
              </div>
            </div>

            <div class="step-line" [class.filled]="currentStepIndex >= 4"></div>

            <div class="step-node" [class.active]="currentStepIndex >= 4" [class.running]="isProcessing && currentStepIndex === 4">
              <div class="node-circle">4</div>
              <div class="node-label">
                <span class="agent-role">Supervisor</span>
                <span class="agent-phase">Audit</span>
              </div>
            </div>

            <div class="step-line" [class.filled]="currentStepIndex >= 5"></div>

            <div class="step-node" [class.active]="currentStepIndex >= 5" [class.running]="isProcessing && currentStepIndex === 5">
              <div class="node-circle">5</div>
              <div class="node-label">
                <span class="agent-role">Smart Replier</span>
                <span class="agent-phase">Draft</span>
              </div>
            </div>
          </div>

          <!-- Live Real-Time Socket Terminal Feed -->
          <div *ngIf="recentEvents.length > 0" class="realtime-terminal">
            <div class="terminal-bar">
              <span class="terminal-dot red"></span>
              <span class="terminal-dot yellow"></span>
              <span class="terminal-dot green"></span>
              <span class="terminal-title">Real-Time WebSocket Stream (/ws/stream)</span>
            </div>
            <div class="terminal-body">
              <div *ngFor="let ev of recentEvents" class="log-line">
                <span class="log-time">{{ ev.timestamp | date:'HH:mm:ss.SS' }}</span>
                <span class="log-agent">[{{ ev.agent_name }}]</span>
                <span class="log-step">{{ ev.step }}:</span>
                <span class="log-msg">{{ ev.details.message || (ev.details | json) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Cards Layout -->
        <div class="cards-grid">
          <!-- Left Column: Email Body -->
          <div class="card-column">
            <div class="insight-card glass-panel">
              <div class="card-header">
                <h3>Original Email Content</h3>
                <span class="body-tag">{{ email.body.length }} chars</span>
              </div>
              <div class="email-body-content">
                {{ email.body }}
              </div>
            </div>

            <!-- Case 5: Supervisor Clarification Card (If triggered) -->
            <div *ngIf="clarification" class="insight-card glass-panel card-alert">
              <div class="card-header">
                <div class="header-with-badge">
                  <span class="badge badge-clarification">Case 5: Paused</span>
                  <h3>Clarification Needed</h3>
                </div>
              </div>
              <div class="clarification-body">
                <p class="question-text">{{ clarification.question }}</p>
                
                <div class="options-group">
                  <div class="options-label">Select a clarifying option:</div>
                  <button 
                    *ngFor="let opt of clarification.parsed_options" 
                    class="option-pill"
                    (click)="submitClarification(opt)"
                  >
                    {{ opt }}
                  </button>
                </div>

                <div class="custom-reply-group">
                  <input 
                    type="text" 
                    class="form-control" 
                    placeholder="Or type custom clarification..." 
                    [(ngModel)]="customClarificationText"
                  />
                  <button 
                    class="btn btn-amber"
                    [disabled]="!customClarificationText"
                    (click)="submitClarification(customClarificationText)"
                  >
                    Resolve
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column: Case 1, 2, 4 Insights -->
          <div class="card-column">
            <!-- Case 1: Calendar Slots Card -->
            <div *ngIf="meetingProposal" class="insight-card glass-panel">
              <div class="card-header">
                <div class="header-with-badge">
                  <span class="badge badge-meeting">Case 1</span>
                  <h3>Outlook Calendar Suggestions</h3>
                </div>
                <span class="stage-tag" [class.confirmed]="meetingProposal.stage === 2">
                  {{ meetingProposal.stage === 2 ? 'Stage 2: Auto Coordinated' : 'Stage 1: Draft Review' }}
                </span>
              </div>
              <div class="card-body">
                <div class="slots-list">
                  <div *ngFor="let slot of meetingProposal.parsed_slots" class="slot-item">
                    <div class="slot-icon">📅</div>
                    <div class="slot-info">
                      <div class="slot-time">{{ slot.display || slot.start_time }}</div>
                      <div class="slot-meta">
                        {{ meetingProposal.stage === 2 ? 'Booked & confirmed on corporate calendar' : 'Free slot from corporate calendar' }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="card-actions" *ngIf="meetingProposal.stage === 1">
                  <button class="btn btn-success" (click)="confirmMeeting.emit(meetingProposal.id)">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                    <span>Confirm Slot (Advance to Stage 2)</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Case 2: Tasks Card (MSSQL) -->
            <div *ngIf="tasks.length > 0" class="insight-card glass-panel">
              <div class="card-header">
                <div class="header-with-badge">
                  <span class="badge badge-task">Case 2</span>
                  <h3>Logged Tasks (MSSQL Database)</h3>
                </div>
                <span class="count-tag">{{ tasks.length }} Tracked</span>
              </div>
              <div class="card-body">
                <div class="tasks-list">
                  <div *ngFor="let t of tasks" class="task-item">
                    <div class="task-checkbox" (click)="toggleTaskStatus(t)">
                      <div class="checkbox-circle" [class.checked]="t.status === 'completed'">
                        <span *ngIf="t.status === 'completed'">✓</span>
                      </div>
                    </div>
                    <div class="task-content">
                      <div class="task-title" [class.completed-text]="t.status === 'completed'">
                        {{ t.title }}
                      </div>
                      <div class="task-meta">
                        <span>Owner: <strong>{{ t.owner }}</strong></span>
                        <span *ngIf="t.due_date">Due: <strong>{{ t.due_date }}</strong></span>
                        <span class="badge" [ngClass]="'badge-' + t.urgency">{{ t.urgency }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Case 4: Staged Response Draft Card -->
            <div *ngIf="draft" class="insight-card glass-panel card-draft">
              <div class="card-header">
                <div class="header-with-badge">
                  <span class="badge badge-mixed">Case 4</span>
                  <h3>Staged Context-Aware Response</h3>
                </div>
                <span class="draft-status" [ngClass]="'status-' + draft.status">
                  {{ draft.status | uppercase }}
                </span>
              </div>
              <div class="card-body">
                <div class="draft-meta">
                  <div>To: <strong>{{ draft.recipient }}</strong></div>
                  <div>Subject: <strong>{{ draft.subject }}</strong></div>
                  <div>Tone Profile: <span class="tone-badge">{{ draft.tone }}</span></div>
                </div>

                <div class="draft-body-wrapper">
                  <textarea 
                    class="form-control draft-textarea" 
                    [(ngModel)]="draft.body"
                    rows="6"
                  ></textarea>
                </div>

                <div class="card-actions">
                  <button 
                    *ngIf="draft.status === 'staged'" 
                    class="btn btn-primary"
                    (click)="approveDraft.emit(draft.id)"
                  >
                    Approve Draft
                  </button>
                  <button 
                    *ngIf="draft.status === 'approved'" 
                    class="btn btn-success"
                    (click)="sendDraft.emit(draft.id)"
                  >
                    Send via Outlook Mail
                  </button>
                  <span *ngIf="draft.status === 'sent'" class="sent-notice">
                    ✓ Email Dispatched via Outlook Mail Service
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  `,
  styles: [`
    :host {
      flex: 1;
      min-width: 0;
      display: flex;
      height: 100vh;
      overflow: hidden;
    }
    .analysis-panel {
      flex: 1;
      min-width: 0;
      height: 100vh;
      overflow-y: auto;
      overflow-x: hidden;
      background: var(--bg-primary);
      padding: 20px 24px;
      display: flex;
      flex-direction: column;
    }
    .no-selection-state {
      max-width: 820px;
      margin: 60px auto;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;
    }
    .hero-icon {
      width: 72px;
      height: 72px;
      border-radius: var(--radius-lg);
      background: linear-gradient(135deg, rgba(0, 112, 173, 0.2), rgba(0, 163, 224, 0.2));
      border: 1px solid var(--border-accent);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--capg-cyan);
      box-shadow: var(--shadow-glow);
    }
    .hero-desc {
      color: var(--text-secondary);
      font-size: 0.95rem;
      max-width: 580px;
      line-height: 1.5;
    }
    .capabilities-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      margin-top: 32px;
      width: 100%;
    }
    .cap-card {
      padding: 20px;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      text-align: left;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .cap-card h4 {
      font-size: 0.95rem;
      color: var(--text-primary);
    }
    .cap-card p {
      font-size: 0.8rem;
      color: var(--text-muted);
      line-height: 1.4;
    }
    .cap-tag {
      align-self: flex-start;
    }
    .analysis-content {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .analysis-header {
      padding: 20px 24px;
    }
    .header-main {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }
    .header-titles {
      display: flex;
      flex-direction: column;
      gap: 8px;
      min-width: 0;
      flex: 1;
    }
    .intent-row {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .confidence-pill {
      font-size: 0.72rem;
      color: var(--capg-cyan);
      background: rgba(0, 163, 224, 0.1);
      padding: 2px 8px;
      border-radius: var(--radius-full);
      font-family: var(--font-mono);
    }
    .email-subject-title {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--text-primary);
      word-break: break-word;
      line-height: 1.3;
    }
    .meta-row {
      display: flex;
      gap: 14px;
      font-size: 0.78rem;
      color: var(--text-secondary);
      flex-wrap: wrap;
    }
    .header-actions {
      display: flex;
      align-items: center;
      gap: 14px;
      flex-shrink: 0;
    }
    .tone-select-group {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.82rem;
      color: var(--text-secondary);
    }
    .tone-select {
      width: 130px;
      height: 38px;
      padding: 6px 10px;
    }
    .run-btn {
      height: 38px;
      padding: 0 18px;
      font-weight: 600;
    }
    .spinner-small {
      width: 14px;
      height: 14px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-radius: 50%;
      border-top-color: #ffffff;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    /* Stepper */
    .agent-stepper {
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .stepper-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .steps-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: relative;
      gap: 4px;
      overflow-x: auto;
      padding-bottom: 4px;
    }
    .step-node {
      display: flex;
      align-items: center;
      gap: 6px;
      opacity: 0.45;
      transition: all 0.3s;
      flex-shrink: 0;
    }
    .step-node.active {
      opacity: 1;
    }
    .step-node.running .node-circle {
      border-color: var(--capg-cyan);
      box-shadow: 0 0 10px var(--capg-cyan);
      animation: pulse 1.2s infinite;
    }
    .node-circle {
      width: 26px;
      height: 26px;
      border-radius: 50%;
      background: var(--bg-secondary);
      border: 2px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--text-primary);
      flex-shrink: 0;
    }
    .step-node.active .node-circle {
      border-color: var(--capg-cyan);
      background: rgba(0, 163, 224, 0.15);
      color: var(--capg-cyan);
    }
    .node-label {
      display: flex;
      flex-direction: column;
    }
    .agent-role {
      font-size: 0.76rem;
      font-weight: 600;
      color: var(--text-primary);
      white-space: nowrap;
    }
    .agent-phase {
      font-size: 0.65rem;
      color: var(--text-muted);
      text-transform: uppercase;
      white-space: nowrap;
    }
    .step-line {
      flex: 1;
      min-width: 8px;
      height: 2px;
      background: var(--border-subtle);
      margin: 0 4px;
    }
    .step-line.filled {
      background: var(--capg-cyan);
    }

    /* Terminal */
    .realtime-terminal {
      background: #060910;
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      overflow: hidden;
      margin-top: 6px;
    }
    .terminal-bar {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 12px;
      background: #0d131f;
      border-bottom: 1px solid var(--border-subtle);
    }
    .terminal-dot {
      width: 9px;
      height: 9px;
      border-radius: 50%;
    }
    .terminal-dot.red { background: #ef4444; }
    .terminal-dot.yellow { background: #f59e0b; }
    .terminal-dot.green { background: #10b981; }
    .terminal-title {
      font-size: 0.7rem;
      font-family: var(--font-mono);
      color: var(--text-muted);
      margin-left: 6px;
    }
    .terminal-body {
      padding: 10px 14px;
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: #38bdf8;
      max-height: 110px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .log-line {
      display: flex;
      gap: 8px;
    }
    .log-time { color: var(--text-muted); }
    .log-agent { color: #a78bfa; font-weight: 600; }
    .log-step { color: #fbbf24; }
    .log-msg { color: #e2e8f0; }

    /* Cards Grid */
    .cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
    }
    @media (max-width: 1180px) {
      .cards-grid {
        grid-template-columns: 1fr;
      }
    }
    .card-column {
      display: flex;
      flex-direction: column;
      gap: 16px;
      min-width: 0;
    }
    .insight-card {
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      min-width: 0;
      word-break: break-word;
      overflow-wrap: break-word;
    }
    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .header-with-badge {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .insight-card h3 {
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--text-primary);
    }
    .body-tag, .count-tag {
      font-size: 0.7rem;
      color: var(--text-muted);
      background: rgba(255, 255, 255, 0.05);
      padding: 2px 8px;
      border-radius: var(--radius-full);
    }
    .email-body-content {
      font-size: 0.85rem;
      line-height: 1.6;
      color: var(--text-secondary);
      white-space: pre-wrap;
    }

    /* Slots */
    .slots-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .slot-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      background: rgba(0, 163, 224, 0.08);
      border: 1px solid rgba(0, 163, 224, 0.25);
      border-radius: var(--radius-md);
    }
    .slot-icon { font-size: 1.1rem; }
    .slot-time { font-size: 0.85rem; font-weight: 600; color: #38bdf8; }
    .slot-meta { font-size: 0.7rem; color: var(--text-muted); }
    .stage-tag {
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--accent-amber);
      background: rgba(245, 158, 11, 0.1);
      padding: 2px 8px;
      border-radius: var(--radius-full);
    }
    .stage-tag.confirmed {
      color: var(--accent-green);
      background: rgba(16, 185, 129, 0.1);
    }

    /* Tasks */
    .tasks-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .task-item {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 10px 12px;
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
    }
    .task-checkbox {
      cursor: pointer;
      margin-top: 2px;
    }
    .checkbox-circle {
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: 2px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.7rem;
      color: #ffffff;
      transition: all 0.2s;
    }
    .checkbox-circle.checked {
      background: var(--accent-green);
      border-color: var(--accent-green);
    }
    .task-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .task-title {
      font-size: 0.82rem;
      font-weight: 500;
      color: var(--text-primary);
    }
    .task-title.completed-text {
      text-decoration: line-through;
      color: var(--text-muted);
    }
    .task-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 0.7rem;
      color: var(--text-secondary);
    }

    /* Draft */
    .draft-meta {
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 0.78rem;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }
    .tone-badge {
      text-transform: capitalize;
      color: var(--capg-cyan);
      font-weight: 600;
    }
    .draft-textarea {
      resize: vertical;
      font-family: var(--font-sans);
      line-height: 1.5;
    }
    .card-actions {
      display: flex;
      gap: 10px;
      margin-top: 10px;
    }
    .sent-notice {
      color: var(--accent-green);
      font-size: 0.82rem;
      font-weight: 600;
    }
    .draft-status {
      font-size: 0.7rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: var(--radius-full);
    }
    .draft-status.status-staged { color: var(--accent-amber); background: rgba(245, 158, 11, 0.1); }
    .draft-status.status-approved { color: var(--accent-green); background: rgba(16, 185, 129, 0.1); }
    .draft-status.status-sent { color: var(--capg-cyan); background: rgba(0, 163, 224, 0.1); }

    /* Clarification Alert */
    .card-alert {
      border: 1px solid rgba(245, 158, 11, 0.35);
      background: rgba(245, 158, 11, 0.05);
    }
    .clarification-body {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .question-text {
      font-size: 0.875rem;
      color: #fde68a;
      font-weight: 500;
      line-height: 1.5;
    }
    .options-group {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .options-label {
      font-size: 0.72rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }
    .option-pill {
      text-align: left;
      padding: 8px 12px;
      border-radius: var(--radius-md);
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--border-subtle);
      color: var(--text-primary);
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.2s;
    }
    .option-pill:hover {
      background: rgba(245, 158, 11, 0.2);
      border-color: var(--accent-amber);
    }
    .custom-reply-group {
      display: flex;
      gap: 8px;
      margin-top: 4px;
    }
  `]
})
export class AiAnalysisComponent {
  @Input() email: Email | null = null;
  @Input() isProcessing = false;
  @Input() currentStepIndex = 0;
  @Input() meetingProposal: MeetingProposal | null = null;
  @Input() tasks: Task[] = [];
  @Input() draft: Draft | null = null;
  @Input() clarification: ClarificationRequest | null = null;
  @Input() recentEvents: WebSocketEvent[] = [];

  @Output() runPipeline = new EventEmitter<string>();
  @Output() confirmMeeting = new EventEmitter<number>();
  @Output() taskStatusToggle = new EventEmitter<Task>();
  @Output() approveDraft = new EventEmitter<number>();
  @Output() sendDraft = new EventEmitter<number>();
  @Output() submitClarificationReply = new EventEmitter<{ id: number; answer: string }>();

  selectedTone = 'professional';
  customClarificationText = '';

  onRunPipeline() {
    this.runPipeline.emit(this.selectedTone);
  }

  toggleTaskStatus(task: Task) {
    this.taskStatusToggle.emit(task);
  }

  submitClarification(answer: string) {
    if (this.clarification && answer) {
      this.submitClarificationReply.emit({ id: this.clarification.id, answer });
      this.customClarificationText = '';
    }
  }
}
