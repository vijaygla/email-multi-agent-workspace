import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MeetingProposal } from '../../shared/models/agent.interface';

@Component({
  selector: 'app-meetings',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="meetings-view">
      <div class="header">
        <h2>Calendar Proposals (Outlook Integration)</h2>
        <p class="subtitle">Discovered and staged meeting times from incoming email requests.</p>
      </div>

      <div *ngIf="proposals.length === 0" class="empty-state glass-panel">
        <p>No meeting proposals logged yet. Ingest an email asking for a meeting to test Case 1!</p>
      </div>

      <div class="proposals-grid">
        <div *ngFor="let p of proposals" class="proposal-card glass-panel">
          <div class="card-header">
            <div class="title-section">
              <span class="badge badge-meeting">Proposal #{{ p.id }}</span>
              <span class="stage-pill" [class.stage2]="p.stage === 2">
                {{ p.stage === 2 ? 'Stage 2: Auto Coordinated' : 'Stage 1: User Review Required' }}
              </span>
            </div>
            <span class="created-at">{{ p.created_at | date:'medium' }}</span>
          </div>

          <div class="meta-section">
            <div><strong>Participants:</strong> {{ p.participants || 'N/A' }}</div>
            <div><strong>Requested Dates:</strong> {{ p.requested_dates || 'Tomorrow' }}</div>
          </div>

          <div class="slots-box" [class.confirmed-box]="p.stage === 2">
            <div class="slots-heading" [class.confirmed-heading]="p.stage === 2">
              {{ p.stage === 2 ? 'Confirmed Booked Slot:' : 'Available Open Slots:' }}
            </div>
            <div class="slots-container">
              <div *ngFor="let slot of p.parsed_slots" class="slot-pill">
                <span>{{ p.stage === 2 ? '✅' : '🕒' }}</span>
                <span>{{ slot.display || slot.start_time }}</span>
              </div>
            </div>
          </div>

          <div class="card-actions" *ngIf="p.stage === 1">
            <button class="btn btn-success" (click)="confirmMeeting.emit(p.id)">
              Confirm Slot & Advance to Stage 2
            </button>
          </div>
          <div class="card-actions" *ngIf="p.stage === 2">
            <span class="confirmed-text">✓ Confirmed & Booked on Corporate Calendar</span>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .meetings-view {
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
    .proposals-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
      gap: 16px;
    }
    .proposal-card {
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .title-section {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .stage-pill {
      font-size: 0.72rem;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: var(--radius-full);
      background: rgba(245, 158, 11, 0.15);
      color: var(--accent-amber);
    }
    .stage-pill.stage2 {
      background: rgba(16, 185, 129, 0.15);
      color: var(--accent-green);
    }
    .created-at {
      font-size: 0.72rem;
      color: var(--text-muted);
    }
    .meta-section {
      font-size: 0.82rem;
      color: var(--text-secondary);
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .slots-box {
      background: rgba(0, 163, 224, 0.05);
      border: 1px solid rgba(0, 163, 224, 0.2);
      border-radius: var(--radius-md);
      padding: 12px;
    }
    .slots-box.confirmed-box {
      background: rgba(16, 185, 129, 0.08);
      border-color: rgba(16, 185, 129, 0.3);
    }
    .slots-heading {
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--capg-cyan);
      margin-bottom: 8px;
    }
    .slots-heading.confirmed-heading {
      color: var(--accent-green);
    }
    .slots-container {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .slot-pill {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.8rem;
      color: var(--text-primary);
    }
    .confirmed-text {
      color: var(--accent-green);
      font-size: 0.85rem;
      font-weight: 600;
    }
  `]
})
export class MeetingsComponent {
  @Input() proposals: MeetingProposal[] = [];
  @Output() confirmMeeting = new EventEmitter<number>();
}
