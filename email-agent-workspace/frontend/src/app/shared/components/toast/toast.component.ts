import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastService, ToastMessage } from './toast.service';

@Component({
  selector: 'app-toast',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="toast-container">
      <div 
        *ngFor="let toast of toasts$ | async" 
        class="toast-item" 
        [ngClass]="'toast-' + toast.type"
        (click)="toastService.remove(toast.id)"
      >
        <div class="toast-icon">
          <span *ngIf="toast.type === 'success'">✓</span>
          <span *ngIf="toast.type === 'info'">ℹ</span>
          <span *ngIf="toast.type === 'warning'">⚠</span>
          <span *ngIf="toast.type === 'error'">✕</span>
        </div>
        <div class="toast-content">
          <div class="toast-title">{{ toast.title }}</div>
          <div class="toast-message">{{ toast.message }}</div>
        </div>
        <button class="toast-close" (click)="toastService.remove(toast.id)">×</button>
      </div>
    </div>
  `,
  styles: [`
    .toast-container {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      pointer-events: none;
    }
    .toast-item {
      pointer-events: auto;
      min-width: 300px;
      max-width: 420px;
      padding: 12px 16px;
      border-radius: var(--radius-md);
      background: rgba(17, 24, 39, 0.95);
      backdrop-filter: blur(12px);
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: flex-start;
      gap: 12px;
      cursor: pointer;
      animation: slideIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      border-left: 4px solid var(--capg-cyan);
    }
    .toast-success { border-left-color: var(--accent-green); }
    .toast-info { border-left-color: var(--capg-cyan); }
    .toast-warning { border-left-color: var(--accent-amber); }
    .toast-error { border-left-color: var(--accent-rose); }
    
    .toast-icon {
      font-size: 1.1rem;
      font-weight: 700;
      line-height: 1;
      margin-top: 2px;
    }
    .toast-success .toast-icon { color: var(--accent-green); }
    .toast-info .toast-icon { color: var(--capg-cyan); }
    .toast-warning .toast-icon { color: var(--accent-amber); }
    .toast-error .toast-icon { color: var(--accent-rose); }

    .toast-content {
      flex: 1;
    }
    .toast-title {
      font-size: 0.875rem;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 2px;
    }
    .toast-message {
      font-size: 0.8rem;
      color: var(--text-secondary);
      line-height: 1.4;
    }
    .toast-close {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 1.2rem;
      cursor: pointer;
      padding: 0 4px;
    }
    .toast-close:hover {
      color: var(--text-primary);
    }
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `]
})
export class ToastComponent {
  public toastService = inject(ToastService);
  toasts$ = this.toastService.toasts$;
}
