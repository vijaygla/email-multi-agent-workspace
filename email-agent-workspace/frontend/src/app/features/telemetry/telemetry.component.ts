import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebSocketEvent, SystemStatus } from '../../shared/models/agent.interface';

@Component({
  selector: 'app-telemetry',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="telemetry-view">
      <div class="header">
        <div>
          <h2>Agent Telemetry & Real-Time Spans</h2>
          <p class="subtitle">Live event stream piped directly from FastAPI WebSocket (/ws/stream).</p>
        </div>
      </div>

      <!-- System Diagnostic Panel -->
      <div *ngIf="systemStatus" class="sys-grid">
        <div class="sys-card glass-panel">
          <div class="sys-label">Database Engine</div>
          <div class="sys-val">{{ systemStatus.database.engine }}</div>
          <div class="sys-sub">{{ systemStatus.database.database }} ({{ systemStatus.database.server }})</div>
        </div>

        <div class="sys-card glass-panel">
          <div class="sys-label">Router Model</div>
          <div class="sys-val">{{ systemStatus.generative_engine.models.router }}</div>
          <div class="sys-sub">Fast classification</div>
        </div>

        <div class="sys-card glass-panel">
          <div class="sys-label">Drafting & Reasoning</div>
          <div class="sys-val">{{ systemStatus.generative_engine.models.drafting }}</div>
          <div class="sys-sub">High capability</div>
        </div>

        <div class="sys-card glass-panel">
          <div class="sys-label">Fallback Model</div>
          <div class="sys-val">{{ systemStatus.generative_engine.models.fallback }}</div>
          <div class="sys-sub">Failover resilience</div>
        </div>
      </div>

      <!-- Live Stream Events Log -->
      <div class="stream-panel glass-panel">
        <div class="panel-header">
          <div class="header-left">
            <span class="pulse-dot"></span>
            <h3>Live Telemetry Stream</h3>
          </div>
          <span class="events-count">{{ events.length }} Events Captured</span>
        </div>

        <div *ngIf="events.length === 0" class="empty-state">
          <p>Awaiting agent execution events... Trigger analysis on any email to view live spans.</p>
        </div>

        <div class="events-list" *ngIf="events.length > 0">
          <div *ngFor="let ev of events" class="event-row">
            <div class="ev-time">{{ ev.timestamp | date:'HH:mm:ss.SS' }}</div>
            <div class="ev-badge">
              <span class="badge" [ngClass]="getBadgeClass(ev.step)">{{ ev.agent_name }}</span>
            </div>
            <div class="ev-step">{{ ev.step }}</div>
            <div class="ev-details">
              <span class="ev-msg">{{ ev.details.message || '' }}</span>
              <pre class="ev-json" *ngIf="hasExtraData(ev.details)">{{ formatJson(ev.details) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .telemetry-view {
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
    .sys-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }
    .sys-card {
      padding: 16px 18px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .sys-label {
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      font-weight: 600;
    }
    .sys-val {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--capg-cyan);
      font-family: var(--font-mono);
    }
    .sys-sub {
      font-size: 0.75rem;
      color: var(--text-secondary);
    }
    .stream-panel {
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      flex: 1;
    }
    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .header-left {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .events-count {
      font-size: 0.75rem;
      color: var(--text-muted);
      background: rgba(255, 255, 255, 0.05);
      padding: 2px 10px;
      border-radius: var(--radius-full);
    }
    .empty-state {
      padding: 40px;
      text-align: center;
      color: var(--text-muted);
    }
    .events-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      overflow-y: auto;
      flex: 1;
    }
    .event-row {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 10px 14px;
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      font-family: var(--font-mono);
      font-size: 0.78rem;
    }
    .ev-time {
      color: var(--text-muted);
      flex-shrink: 0;
    }
    .ev-step {
      color: #fbbf24;
      font-weight: 600;
      flex-shrink: 0;
      min-width: 60px;
    }
    .ev-details {
      flex: 1;
      color: var(--text-primary);
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .ev-msg {
      color: #e2e8f0;
    }
    .ev-json {
      background: rgba(0, 0, 0, 0.3);
      padding: 6px 10px;
      border-radius: 4px;
      color: #94a3b8;
      font-size: 0.72rem;
      white-space: pre-wrap;
    }
  `]
})
export class TelemetryComponent {
  @Input() events: WebSocketEvent[] = [];
  @Input() systemStatus: SystemStatus | null = null;

  getBadgeClass(step: string): string {
    switch (step?.toLowerCase()) {
      case 'observe': return 'badge-meeting';
      case 'think': return 'badge-mixed';
      case 'act': return 'badge-task';
      case 'finish': return 'badge-task';
      default: return 'badge-clarification';
    }
  }

  hasExtraData(details: any): boolean {
    if (!details) return false;
    const keys = Object.keys(details).filter(k => k !== 'message');
    return keys.length > 0;
  }

  formatJson(details: any): string {
    const clone = { ...details };
    delete clone.message;
    return JSON.stringify(clone, null, 2);
  }
}
