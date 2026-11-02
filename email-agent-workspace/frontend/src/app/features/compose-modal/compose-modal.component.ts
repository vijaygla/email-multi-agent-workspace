import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-compose-modal',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="modal-backdrop" (click)="close.emit()">
      <div class="modal-card glass-panel" (click)="$event.stopPropagation()">
        <div class="modal-header">
          <h3>Ingest Email into Workspace</h3>
          <button class="close-btn" (click)="close.emit()">×</button>
        </div>

        <!-- 1-Click Demo Presets -->
        <div class="presets-section">
          <div class="presets-label">⚡ 1-Click Test Scenarios (Cases 1 - 5):</div>
          <div class="presets-grid">
            <button class="preset-btn" (click)="applyPreset('case1')">
              <span class="badge badge-meeting">Case 1</span>
              <span>Calendar Finder (Meeting)</span>
            </button>
            <button class="preset-btn" (click)="applyPreset('case2')">
              <span class="badge badge-task">Case 2</span>
              <span>To-Do Creator (Task)</span>
            </button>
            <button class="preset-btn" (click)="applyPreset('case3')">
              <span class="badge badge-mixed">Case 3</span>
              <span>Mixed Intent (Both)</span>
            </button>
            <button class="preset-btn" (click)="applyPreset('case5')">
              <span class="badge badge-clarification">Case 5</span>
              <span>Clarification (Ambiguous)</span>
            </button>
          </div>
        </div>

        <!-- Email Ingest Form -->
        <div class="form-body">
          <div class="form-group">
            <label>Sender Email:</label>
            <input type="email" class="form-control" [(ngModel)]="sender" placeholder="sarah.connor@nexus.ai" />
          </div>

          <div class="form-group">
            <label>Subject Line:</label>
            <input type="text" class="form-control" [(ngModel)]="subject" placeholder="Project Architecture Discussion" />
          </div>

          <div class="form-group">
            <label>Email Body:</label>
            <textarea 
              class="form-control text-body" 
              rows="6" 
              [(ngModel)]="body"
              placeholder="Type email body or select a preset scenario above..."
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" (click)="close.emit()">Cancel</button>
          <button class="btn btn-primary" (click)="submit()" [disabled]="!subject || !body">
            Ingest & Save to Database
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(8px);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .modal-card {
      width: 100%;
      max-width: 600px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
      animation: modalFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .modal-header h3 {
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-primary);
    }
    .close-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 1.5rem;
      cursor: pointer;
    }
    .close-btn:hover {
      color: var(--text-primary);
    }
    .presets-section {
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .presets-label {
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--capg-cyan);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .presets-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
    }
    .preset-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 10px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      color: var(--text-secondary);
      font-size: 0.75rem;
      font-weight: 500;
      cursor: pointer;
      text-align: left;
      transition: all 0.15s;
    }
    .preset-btn:hover {
      background: rgba(0, 163, 224, 0.15);
      border-color: var(--capg-cyan);
      color: var(--text-primary);
    }
    .form-body {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .form-group label {
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--text-secondary);
    }
    .text-body {
      resize: vertical;
      line-height: 1.5;
    }
    .modal-footer {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 6px;
    }
    @keyframes modalFadeIn {
      from { transform: scale(0.96); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }
  `]
})
export class ComposeModalComponent {
  @Output() close = new EventEmitter<void>();
  @Output() ingest = new EventEmitter<{ sender: string; subject: string; body: string }>();

  sender = 'sarah.connor@nexus.ai';
  subject = 'Quick sync on project roadmap';
  body = "Hi team, let's meet tomorrow afternoon to review the Q3 architecture and sync on timelines.";

  applyPreset(type: string) {
    switch (type) {
      case 'case1':
        this.sender = 'sarah.connor@nexus.ai';
        this.subject = 'Project Architecture Discussion';
        this.body = "Hi, let's meet tomorrow afternoon to review the Q3 architecture and sync on timelines.";
        break;
      case 'case2':
        this.sender = 'alex.turner@nexus.ai';
        this.subject = 'Action items: Budget deck preparation';
        this.body = 'Hi team, please send the revised budget deck by Friday 5 PM. Make sure John reviews the cost breakdown first. This is high priority.';
        break;
      case 'case3':
        this.sender = 'elena.rostova@nexus.ai';
        this.subject = 'Q3 Budget Review and Architecture Discussion';
        this.body = "Hello! Could you please prepare and send the final budget deck by Friday 5 PM EST? Also, let's meet tomorrow afternoon around 2 PM EST to sync on the client feedback.";
        break;
      case 'case5':
        this.sender = 'marcus.vance@nexus.ai';
        this.subject = 'Quick chat sometime';
        this.body = "Hey, let's connect sometime whenever you are free to discuss that thing we talked about.";
        break;
    }
  }

  submit() {
    if (this.subject.trim() && this.body.trim()) {
      this.ingest.emit({
        sender: this.sender || 'colleague@nexus.ai',
        subject: this.subject,
        body: this.body
      });
    }
  }
}
