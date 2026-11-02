import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  template: `
    <aside class="sidebar" [class.collapsed]="isCollapsed">
      <!-- Workspace Brand & Collapse Toggle -->
      <div class="brand">
        <!-- Expanded View: Logo, Title, and Collapse Button -->
        <ng-container *ngIf="!isCollapsed">
          <div class="brand-left">
            <div class="logo-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
            </div>
            <div class="brand-text">
              <div class="brand-title">Email Workspace</div>
              <div class="brand-sub">Nexus AI Engine</div>
            </div>
          </div>

          <button 
            class="collapse-toggle-btn" 
            title="Collapse Sidebar (Free screen space)" 
            (click)="onToggle()"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="11 17 6 12 11 7"></polyline>
              <polyline points="18 17 13 12 18 7"></polyline>
            </svg>
          </button>
        </ng-container>

        <!-- Collapsed View: ONLY a Clean Centered Expand Button (No Overlapping) -->
        <button 
          *ngIf="isCollapsed"
          class="collapse-toggle-btn collapsed-mode-btn" 
          title="Expand Sidebar" 
          (click)="onToggle()"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="13 17 18 12 13 7"></polyline>
            <polyline points="6 17 11 12 6 7"></polyline>
          </svg>
        </button>
      </div>

      <!-- Quick Compose / Demo Ingest Button -->
      <div class="compose-btn-wrapper">
        <button 
          class="btn btn-primary compose-btn" 
          [title]="isCollapsed ? 'Ingest / Compose Email' : ''"
          (click)="openCompose.emit()"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span *ngIf="!isCollapsed">Ingest / Compose</span>
        </button>
      </div>

      <!-- Navigation Links -->
      <nav class="nav-menu">
        <div class="nav-section-title" *ngIf="!isCollapsed">Navigation</div>

        <button 
          class="nav-item" 
          [class.active]="activeTab === 'inbox'"
          [title]="isCollapsed ? 'Inbox (' + unreadCount + ' unread)' : ''"
          (click)="selectTab('inbox')"
        >
          <div class="nav-item-content">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline>
              <path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path>
            </svg>
            <span *ngIf="!isCollapsed">Inbox</span>
          </div>
          <!-- Badge only shown when expanded -->
          <span class="nav-badge" *ngIf="!isCollapsed && unreadCount > 0">{{ unreadCount }}</span>
        </button>

        <button 
          class="nav-item" 
          [class.active]="activeTab === 'tasks'"
          [title]="isCollapsed ? 'Task Board (' + tasksCount + ' pending)' : ''"
          (click)="selectTab('tasks')"
        >
          <div class="nav-item-content">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 11l3 3L22 4"></path>
              <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
            </svg>
            <span *ngIf="!isCollapsed">Task Board (MSSQL)</span>
          </div>
          <!-- Badge only shown when expanded -->
          <span class="nav-badge badge-task" *ngIf="!isCollapsed && tasksCount > 0">{{ tasksCount }}</span>
        </button>

        <button 
          class="nav-item" 
          [class.active]="activeTab === 'meetings'"
          [title]="isCollapsed ? 'Calendar Proposals (' + meetingsCount + ' staged)' : ''"
          (click)="selectTab('meetings')"
        >
          <div class="nav-item-content">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            <span *ngIf="!isCollapsed">Calendar Proposals</span>
          </div>
          <!-- Badge only shown when expanded -->
          <span class="nav-badge badge-meeting" *ngIf="!isCollapsed && meetingsCount > 0">{{ meetingsCount }}</span>
        </button>

        <button 
          class="nav-item" 
          [class.active]="activeTab === 'clarifications'"
          [title]="isCollapsed ? 'Clarifications (' + clarificationsCount + ' pending)' : ''"
          (click)="selectTab('clarifications')"
        >
          <div class="nav-item-content">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <span *ngIf="!isCollapsed">Clarifications (Case 5)</span>
          </div>
          <!-- Badge only shown when expanded -->
          <span class="nav-badge badge-clarification" *ngIf="!isCollapsed && clarificationsCount > 0">{{ clarificationsCount }}</span>
        </button>

        <button 
          class="nav-item" 
          [class.active]="activeTab === 'telemetry'"
          [title]="isCollapsed ? (isWsConnected ? 'Live Agent Spans (Connected)' : 'Live Agent Spans (Disconnected)') : ''"
          (click)="selectTab('telemetry')"
        >
          <div class="nav-item-content">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
            <span *ngIf="!isCollapsed">Live Agent Spans</span>
          </div>
          <!-- Dot only shown when expanded -->
          <span class="pulse-dot" [class.disconnected]="!isWsConnected" *ngIf="!isCollapsed"></span>
        </button>
      </nav>

      <!-- Autopilot Governance Widget -->
      <div class="autopilot-widget" *ngIf="!isCollapsed">
        <div class="autopilot-header">
          <div class="autopilot-title-row">
            <span class="autopilot-label">AUTOPILOT</span>
            <span class="autopilot-badge" [class.badge-l3]="autopilotStatus?.autonomy_level === 'L3'" [class.badge-l2]="autopilotStatus?.autonomy_level === 'L2'">
              {{ autopilotStatus?.autonomy_level || 'L1' }}
            </span>
          </div>
          <div class="autopilot-desc">
            {{ autopilotStatus?.autonomy_level === 'L3' ? 'Full Autopilot' : (autopilotStatus?.autonomy_level === 'L2' ? 'Semi-Autonomous' : (autopilotStatus?.autonomy_level === 'L0' ? 'Manual Only' : 'Assisted Mode')) }}
          </div>
        </div>
        <div class="autopilot-controls">
          <select class="autopilot-select" [value]="autopilotStatus?.autonomy_level || 'L1'" (change)="onAutonomyChange($event)">
            <option value="L0">L0 (Manual)</option>
            <option value="L1">L1 (Assisted)</option>
            <option value="L2">L2 (Semi-Auto)</option>
            <option value="L3">L3 (Full Auto)</option>
          </select>
          <button class="poll-btn" title="Run instant autonomous inbox poll" (click)="triggerPollNow.emit()">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 4 23 10 17 10"></polyline>
              <polyline points="1 20 1 14 7 14"></polyline>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- System Health Indicator Footer -->
      <div class="system-status" *ngIf="!isCollapsed">
        <div class="status-header">
          <span class="pulse-dot" [class.disconnected]="!isWsConnected"></span>
          <span class="status-title">{{ isWsConnected ? 'REAL-TIME LIVE' : 'CONNECTING' }}</span>
        </div>
        <div class="status-detail">
          <div>DB: <span class="highlight">MSSQL Active</span></div>
          <div>AI: <span class="highlight">Nexus v1</span></div>
        </div>
      </div>

      <!-- Collapsed status pip at bottom -->
      <div class="system-status-collapsed" *ngIf="isCollapsed" [title]="isWsConnected ? 'Real-Time Live (MSSQL & AI Active)' : 'Connecting to backend...'">
        <span class="pulse-dot" [class.disconnected]="!isWsConnected"></span>
      </div>
    </aside>
  `,
  styles: [`
    .sidebar {
      width: 235px;
      height: 100vh;
      background: var(--bg-secondary);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      transition: width 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
      z-index: 10;
    }
    .sidebar.collapsed {
      width: 64px;
    }
    .brand {
      padding: 16px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border-subtle);
      height: 68px;
      box-sizing: border-box;
    }
    .sidebar.collapsed .brand {
      padding: 14px 0;
      justify-content: center;
    }
    .brand-left {
      display: flex;
      align-items: center;
      gap: 10px;
      overflow: hidden;
    }
    .logo-icon {
      width: 36px;
      height: 36px;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, var(--capg-blue), var(--capg-cyan));
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      box-shadow: 0 4px 12px rgba(0, 112, 173, 0.4);
      flex-shrink: 0;
    }
    .brand-title {
      font-size: 0.9rem;
      font-weight: 700;
      color: var(--text-primary);
      letter-spacing: -0.01em;
      white-space: nowrap;
    }
    .brand-sub {
      font-size: 0.7rem;
      color: var(--capg-cyan);
      font-weight: 500;
      white-space: nowrap;
    }
    .collapse-toggle-btn {
      width: 30px;
      height: 30px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      flex-shrink: 0;
      transition: all 0.2s;
    }
    .collapse-toggle-btn:hover {
      background: rgba(0, 163, 224, 0.2);
      border-color: var(--capg-cyan);
      color: var(--text-primary);
    }
    .collapsed-mode-btn {
      width: 38px;
      height: 38px;
      border-radius: var(--radius-md);
      background: rgba(0, 163, 224, 0.12);
      border-color: rgba(0, 163, 224, 0.3);
      color: var(--capg-cyan);
    }
    .collapsed-mode-btn:hover {
      background: rgba(0, 163, 224, 0.25);
      color: #ffffff;
      box-shadow: 0 0 12px rgba(0, 163, 224, 0.4);
    }
    .compose-btn-wrapper {
      padding: 14px 12px 10px;
      display: flex;
      justify-content: center;
    }
    .sidebar.collapsed .compose-btn-wrapper {
      padding: 14px 0 10px;
    }
    .compose-btn {
      width: 100%;
      padding: 9px 12px;
      font-weight: 600;
      letter-spacing: 0.02em;
      font-size: 0.85rem;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      white-space: nowrap;
    }
    .sidebar.collapsed .compose-btn {
      width: 42px;
      height: 42px;
      padding: 0;
      border-radius: var(--radius-md);
    }
    .nav-menu {
      flex: 1;
      padding: 6px 10px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      overflow-y: auto;
    }
    .sidebar.collapsed .nav-menu {
      padding: 6px 0;
      align-items: center;
    }
    .nav-section-title {
      font-size: 0.68rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-muted);
      padding: 6px 8px 4px;
      white-space: nowrap;
    }
    .nav-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      padding: 9px 12px;
      border-radius: var(--radius-md);
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-secondary);
      font-size: 0.84rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      outline: none;
    }
    .sidebar.collapsed .nav-item {
      width: 42px;
      height: 42px;
      padding: 0;
      justify-content: center;
      border-radius: var(--radius-md);
    }
    .nav-item-content {
      display: flex;
      align-items: center;
      gap: 10px;
      white-space: nowrap;
    }
    .sidebar.collapsed .nav-item-content {
      gap: 0;
      justify-content: center;
    }
    .nav-item:hover {
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-primary);
    }
    .nav-item.active {
      background: rgba(0, 163, 224, 0.12);
      border-color: rgba(0, 163, 224, 0.3);
      color: var(--capg-cyan);
      font-weight: 600;
    }
    .nav-badge {
      font-size: 0.7rem;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: var(--radius-full);
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-primary);
    }
    .system-status {
      margin: 12px;
      padding: 10px 12px;
      background: rgba(17, 24, 39, 0.6);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
    }
    .system-status-collapsed {
      margin: 16px auto;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .status-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
    }
    .status-title {
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      color: var(--accent-green);
      white-space: nowrap;
    }
    .status-detail {
      font-size: 0.7rem;
      color: var(--text-muted);
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .status-detail .highlight {
      color: var(--text-secondary);
      font-weight: 500;
    }
    /* Autopilot Governance Widget Styles */
    .autopilot-widget {
      margin: 10px 12px 6px;
      padding: 10px 12px;
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
      border: 1px solid rgba(59, 130, 246, 0.25);
      border-radius: var(--radius-md);
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .autopilot-title-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .autopilot-label {
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      color: var(--accent-blue);
    }
    .autopilot-badge {
      font-size: 0.65rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(59, 130, 246, 0.2);
      color: var(--accent-blue);
      border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .autopilot-badge.badge-l2 {
      background: rgba(245, 158, 11, 0.2);
      color: var(--accent-amber);
      border-color: rgba(245, 158, 11, 0.3);
    }
    .autopilot-badge.badge-l3 {
      background: rgba(16, 185, 129, 0.2);
      color: var(--accent-green);
      border-color: rgba(16, 185, 129, 0.3);
    }
    .autopilot-desc {
      font-size: 0.7rem;
      color: var(--text-muted);
      margin-top: -2px;
    }
    .autopilot-controls {
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .autopilot-select {
      flex: 1;
      background: var(--bg-primary);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      color: var(--text-primary);
      font-size: 0.72rem;
      padding: 4px 6px;
      cursor: pointer;
    }
    .autopilot-select:focus {
      outline: none;
      border-color: var(--accent-blue);
    }
    .poll-btn {
      background: var(--bg-tertiary);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      color: var(--text-secondary);
      padding: 5px 7px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s ease;
    }
    .poll-btn:hover {
      background: var(--accent-blue);
      color: #fff;
      border-color: var(--accent-blue);
    }
  `]
})
export class SidebarComponent {
  @Input() activeTab = 'inbox';
  @Input() unreadCount = 0;
  @Input() tasksCount = 0;
  @Input() meetingsCount = 0;
  @Input() clarificationsCount = 0;
  @Input() isWsConnected = false;
  @Input() isCollapsed = false;
  @Input() autopilotStatus: any = null;

  @Output() tabChange = new EventEmitter<string>();
  @Output() openCompose = new EventEmitter<void>();
  @Output() toggleCollapse = new EventEmitter<boolean>();
  @Output() changeAutonomyLevel = new EventEmitter<string>();
  @Output() triggerPollNow = new EventEmitter<void>();

  selectTab(tab: string) {
    this.tabChange.emit(tab);
  }

  onToggle() {
    this.isCollapsed = !this.isCollapsed;
    this.toggleCollapse.emit(this.isCollapsed);
  }

  onAutonomyChange(event: Event) {
    const level = (event.target as HTMLSelectElement).value;
    this.changeAutonomyLevel.emit(level);
  }
}
