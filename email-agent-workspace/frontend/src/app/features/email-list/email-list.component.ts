import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Email } from '../../shared/models/agent.interface';

@Component({
  selector: 'app-email-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="email-list-panel">
      <!-- Search & Filters Header -->
      <div class="deck-header">
        <div class="search-box">
          <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input 
            type="text" 
            class="form-control search-input" 
            placeholder="Search emails, sender, tasks..."
            [(ngModel)]="searchQuery"
          />
          <button 
            class="icon-btn sync-btn" 
            [class.syncing]="isSyncing"
            [disabled]="isSyncing"
            title="Sync & Refresh Workspace" 
            (click)="onSyncClick()"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 4 23 10 17 10"></polyline>
              <polyline points="1 20 1 14 7 14"></polyline>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
          </button>
        </div>

        <!-- Filter Chips -->
        <div class="filter-chips">
          <button 
            class="chip" 
            [class.active]="selectedFilter === 'all'" 
            (click)="setFilter('all')"
          >
            All
          </button>
          <button 
            class="chip" 
            [class.active]="selectedFilter === 'unread'" 
            (click)="setFilter('unread')"
          >
            Unread
          </button>
          <button 
            class="chip" 
            [class.active]="selectedFilter === 'meeting'" 
            (click)="setFilter('meeting')"
          >
            Meetings
          </button>
          <button 
            class="chip" 
            [class.active]="selectedFilter === 'task'" 
            (click)="setFilter('task')"
          >
            Tasks
          </button>
          <button 
            class="chip" 
            [class.active]="selectedFilter === 'mixed_intent'" 
            (click)="setFilter('mixed_intent')"
          >
            Mixed
          </button>
        </div>
      </div>

      <!-- Email Deck List -->
      <div class="deck-scroll">
        <div *ngIf="filteredEmails.length === 0" class="empty-state">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
            <polyline points="22,6 12,13 2,6"/>
          </svg>
          <p>No matching emails found</p>
        </div>

        <div 
          *ngFor="let email of filteredEmails" 
          class="email-card"
          [class.selected]="selectedEmail?.id === email.id"
          [class.unread]="!email.is_read"
          (click)="selectEmail(email)"
        >
          <div class="card-top">
            <div class="sender-info">
              <div class="avatar" [ngStyle]="{'background': getAvatarColor(email.sender)}">
                {{ email.sender[0].toUpperCase() }}
              </div>
              <div class="sender-details">
                <span class="sender-name">{{ email.sender.split('@')[0] }}</span>
                <span class="received-time">{{ formatTime(email.received_at) }}</span>
              </div>
            </div>
            
            <div class="card-badges">
              <span *ngIf="email.intent === 'meeting'" class="badge badge-meeting">Meeting</span>
              <span *ngIf="email.intent === 'task'" class="badge badge-task">Task</span>
              <span *ngIf="email.intent === 'mixed_intent'" class="badge badge-mixed">Mixed</span>
              <span *ngIf="email.status === 'clarification_needed'" class="badge badge-clarification">Clarify</span>
            </div>
          </div>

          <div class="card-subject" [class.unread-text]="!email.is_read">
            {{ email.subject }}
          </div>

          <div class="card-snippet">
            {{ email.body }}
          </div>

          <div class="card-footer">
            <span class="status-indicator" [ngClass]="'status-' + email.status">
              {{ email.status }}
            </span>
            <span *ngIf="email.confidence" class="confidence-tag">
              Confidence: {{ (email.confidence * 100).toFixed(0) }}%
            </span>
          </div>
        </div>
      </div>
    </section>
  `,
  styles: [`
    .email-list-panel {
      width: 315px;
      height: 100vh;
      background: var(--bg-primary);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }
    .deck-header {
      padding: 16px 16px 12px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: var(--bg-secondary);
    }
    .search-box {
      display: flex;
      align-items: center;
      gap: 8px;
      position: relative;
    }
    .search-icon {
      position: absolute;
      left: 12px;
      color: var(--text-muted);
      pointer-events: none;
    }
    .search-input {
      padding-left: 36px;
      padding-right: 12px;
      height: 38px;
    }
    .icon-btn {
      width: 38px;
      height: 38px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.2s;
      flex-shrink: 0;
    }
    .icon-btn:hover {
      background: rgba(255, 255, 255, 0.12);
      color: var(--text-primary);
    }
    .sync-btn {
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .sync-btn.syncing {
      background: rgba(0, 163, 224, 0.2) !important;
      border-color: var(--capg-cyan) !important;
      box-shadow: 0 0 14px rgba(0, 163, 224, 0.4);
    }
    .sync-btn.syncing svg {
      animation: sync-spin 0.75s cubic-bezier(0.4, 0, 0.2, 1) infinite;
      color: var(--capg-cyan);
    }
    @keyframes sync-spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    .filter-chips {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 2px;
    }
    .chip {
      padding: 4px 10px;
      font-size: 0.75rem;
      font-weight: 500;
      border-radius: var(--radius-full);
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s;
    }
    .chip:hover {
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-primary);
    }
    .chip.active {
      background: var(--capg-blue);
      border-color: var(--capg-cyan);
      color: #ffffff;
      font-weight: 600;
    }
    .deck-scroll {
      flex: 1;
      overflow-y: auto;
      padding: 8px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .empty-state {
      padding: 48px 16px;
      text-align: center;
      color: var(--text-muted);
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
    }
    .email-card {
      padding: 14px;
      border-radius: var(--radius-md);
      background: rgba(17, 24, 39, 0.6);
      border: 1px solid var(--border-subtle);
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .email-card:hover {
      background: rgba(30, 41, 59, 0.7);
      border-color: rgba(255, 255, 255, 0.15);
      transform: translateY(-1px);
    }
    .email-card.selected {
      background: rgba(0, 112, 173, 0.15);
      border-color: var(--capg-cyan);
      box-shadow: 0 0 12px rgba(0, 163, 224, 0.2);
    }
    .email-card.unread {
      border-left: 3px solid var(--capg-cyan);
    }
    .card-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }
    .sender-info {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }
    .avatar {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      font-weight: 700;
      color: #ffffff;
      flex-shrink: 0;
    }
    .sender-details {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    .sender-name {
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--text-primary);
      text-transform: capitalize;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .received-time {
      font-size: 0.7rem;
      color: var(--text-muted);
    }
    .card-subject {
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--text-secondary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .card-subject.unread-text {
      color: var(--text-primary);
      font-weight: 600;
    }
    .card-snippet {
      font-size: 0.78rem;
      color: var(--text-muted);
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      line-height: 1.35;
    }
    .card-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 4px;
      font-size: 0.7rem;
    }
    .status-indicator {
      text-transform: capitalize;
      font-weight: 600;
    }
    .status-unread { color: var(--text-muted); }
    .status-processing { color: var(--accent-amber); }
    .status-processed { color: var(--accent-green); }
    .status-clarification_needed { color: var(--accent-amber); }
    .confidence-tag {
      color: var(--capg-cyan);
      font-family: var(--font-mono);
      font-size: 0.68rem;
    }
  `]
})
export class EmailListComponent {
  @Input() emails: Email[] = [];
  @Input() selectedEmail: Email | null = null;
  @Output() emailSelect = new EventEmitter<Email>();
  @Output() refresh = new EventEmitter<void>();

  searchQuery = '';
  selectedFilter = 'all';
  isSyncing = false;

  onSyncClick() {
    this.isSyncing = true;
    this.refresh.emit();
    setTimeout(() => {
      this.isSyncing = false;
    }, 850);
  }

  get filteredEmails(): Email[] {
    return this.emails.filter(e => {
      // Intent/Status Filter
      if (this.selectedFilter === 'unread' && e.is_read) return false;
      if (this.selectedFilter === 'meeting' && e.intent !== 'meeting') return false;
      if (this.selectedFilter === 'task' && e.intent !== 'task') return false;
      if (this.selectedFilter === 'mixed_intent' && e.intent !== 'mixed_intent') return false;

      // Text Query Search
      if (this.searchQuery.trim()) {
        const q = this.searchQuery.toLowerCase();
        const matchSubject = e.subject.toLowerCase().includes(q);
        const matchSender = e.sender.toLowerCase().includes(q);
        const matchBody = e.body.toLowerCase().includes(q);
        return matchSubject || matchSender || matchBody;
      }
      return true;
    });
  }

  setFilter(filter: string) {
    this.selectedFilter = filter;
  }

  selectEmail(email: Email) {
    this.emailSelect.emit(email);
  }

  formatTime(isoString: string): string {
    if (!isoString) return '';
    try {
      const d = new Date(isoString);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  }

  getAvatarColor(sender: string): string {
    const colors = ['#0070ad', '#8b5cf6', '#059669', '#d97706', '#dc2626', '#4f46e5'];
    let hash = 0;
    for (let i = 0; i < sender.length; i++) {
      hash = sender.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  }
}
