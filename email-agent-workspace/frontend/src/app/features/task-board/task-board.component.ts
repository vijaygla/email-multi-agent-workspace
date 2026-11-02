import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Task } from '../../shared/models/agent.interface';

@Component({
  selector: 'app-task-board',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="task-board-view">
      <div class="board-header">
        <div>
          <h2>To-Do Board (MSSQL Persistence)</h2>
          <p class="subtitle">Action items extracted by the Task Extractor Agent and saved directly in Microsoft SQL Server.</p>
        </div>
        <button class="btn btn-primary" (click)="showNewTaskForm = !showNewTaskForm">
          + Add Task
        </button>
      </div>

      <!-- Add Task Inline Form -->
      <div *ngIf="showNewTaskForm" class="new-task-card glass-panel">
        <h3>Create New Action Item</h3>
        <div class="form-row">
          <input type="text" class="form-control" placeholder="Task title..." [(ngModel)]="newTaskTitle" />
          <input type="text" class="form-control" placeholder="Assignee (e.g. Me)" [(ngModel)]="newTaskOwner" style="max-width: 140px;" />
          <input type="text" class="form-control" placeholder="Due date (e.g. Friday 5 PM)" [(ngModel)]="newTaskDue" style="max-width: 180px;" />
          <select class="form-control" [(ngModel)]="newTaskUrgency" style="max-width: 130px;">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
          <button class="btn btn-success" (click)="onCreateTask()" [disabled]="!newTaskTitle">Save</button>
          <button class="btn btn-secondary" (click)="showNewTaskForm = false">Cancel</button>
        </div>
      </div>

      <!-- 3-Column Kanban Board -->
      <div class="kanban-grid">
        <!-- Pending Column -->
        <div class="kanban-col">
          <div class="col-header">
            <span class="col-title">Pending</span>
            <span class="count-badge">{{ pendingTasks.length }}</span>
          </div>
          <div class="tasks-container">
            <div *ngFor="let t of pendingTasks" class="kanban-card glass-panel">
              <div class="card-top">
                <span class="badge" [ngClass]="'badge-' + t.urgency">{{ t.urgency }}</span>
                <button class="delete-btn" (click)="deleteTask.emit(t.id)">×</button>
              </div>
              <div class="task-title">{{ t.title }}</div>
              <div class="task-desc" *ngIf="t.description">{{ t.description }}</div>
              <div class="task-footer">
                <span>👤 {{ t.owner }}</span>
                <span *ngIf="t.due_date">📅 {{ t.due_date }}</span>
              </div>
              <div class="action-row">
                <button class="btn-micro" (click)="updateStatus(t, 'in_progress')">Start →</button>
                <button class="btn-micro green" (click)="updateStatus(t, 'completed')">Complete ✓</button>
              </div>
            </div>
          </div>
        </div>

        <!-- In Progress Column -->
        <div class="kanban-col">
          <div class="col-header">
            <span class="col-title">In Progress</span>
            <span class="count-badge">{{ inProgressTasks.length }}</span>
          </div>
          <div class="tasks-container">
            <div *ngFor="let t of inProgressTasks" class="kanban-card glass-panel">
              <div class="card-top">
                <span class="badge" [ngClass]="'badge-' + t.urgency">{{ t.urgency }}</span>
                <button class="delete-btn" (click)="deleteTask.emit(t.id)">×</button>
              </div>
              <div class="task-title">{{ t.title }}</div>
              <div class="task-desc" *ngIf="t.description">{{ t.description }}</div>
              <div class="task-footer">
                <span>👤 {{ t.owner }}</span>
                <span *ngIf="t.due_date">📅 {{ t.due_date }}</span>
              </div>
              <div class="action-row">
                <button class="btn-micro" (click)="updateStatus(t, 'pending')">← Pending</button>
                <button class="btn-micro green" (click)="updateStatus(t, 'completed')">Complete ✓</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Completed Column -->
        <div class="kanban-col">
          <div class="col-header">
            <span class="col-title">Completed</span>
            <span class="count-badge completed-badge">{{ completedTasks.length }}</span>
          </div>
          <div class="tasks-container">
            <div *ngFor="let t of completedTasks" class="kanban-card glass-panel completed-card">
              <div class="card-top">
                <span class="badge" [ngClass]="'badge-' + t.urgency">{{ t.urgency }}</span>
                <button class="delete-btn" (click)="deleteTask.emit(t.id)">×</button>
              </div>
              <div class="task-title line-through">{{ t.title }}</div>
              <div class="task-footer">
                <span>👤 {{ t.owner }}</span>
                <span *ngIf="t.due_date">📅 {{ t.due_date }}</span>
              </div>
              <div class="action-row">
                <button class="btn-micro" (click)="updateStatus(t, 'pending')">↺ Reopen</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .task-board-view {
      flex: 1;
      height: 100vh;
      overflow-y: auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }
    .board-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .board-header h2 {
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--text-primary);
    }
    .subtitle {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-top: 4px;
    }
    .new-task-card {
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .form-row {
      display: flex;
      gap: 10px;
    }
    .kanban-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
      flex: 1;
    }
    .kanban-col {
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: rgba(15, 23, 42, 0.4);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 16px;
    }
    .col-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--border-subtle);
    }
    .col-title {
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-primary);
    }
    .count-badge {
      font-size: 0.72rem;
      font-weight: 700;
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-primary);
      padding: 2px 8px;
      border-radius: var(--radius-full);
    }
    .completed-badge {
      background: rgba(16, 185, 129, 0.2);
      color: var(--accent-green);
    }
    .tasks-container {
      display: flex;
      flex-direction: column;
      gap: 10px;
      overflow-y: auto;
      flex: 1;
    }
    .kanban-card {
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      transition: all 0.2s;
    }
    .kanban-card:hover {
      border-color: rgba(255, 255, 255, 0.2);
      transform: translateY(-2px);
    }
    .completed-card {
      opacity: 0.7;
    }
    .card-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .delete-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 1.2rem;
      cursor: pointer;
    }
    .delete-btn:hover {
      color: var(--accent-rose);
    }
    .task-title {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--text-primary);
    }
    .line-through {
      text-decoration: line-through;
      color: var(--text-muted);
    }
    .task-desc {
      font-size: 0.78rem;
      color: var(--text-muted);
      line-height: 1.35;
    }
    .task-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.72rem;
      color: var(--text-secondary);
      margin-top: 4px;
    }
    .action-row {
      display: flex;
      gap: 6px;
      margin-top: 6px;
    }
    .btn-micro {
      padding: 3px 8px;
      font-size: 0.7rem;
      border-radius: var(--radius-sm);
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid var(--border-subtle);
      color: var(--text-secondary);
      cursor: pointer;
    }
    .btn-micro:hover {
      background: rgba(255, 255, 255, 0.16);
      color: var(--text-primary);
    }
    .btn-micro.green:hover {
      background: rgba(16, 185, 129, 0.2);
      color: var(--accent-green);
      border-color: var(--accent-green);
    }
  `]
})
export class TaskBoardComponent {
  @Input() tasks: Task[] = [];
  @Output() taskUpdate = new EventEmitter<{ id: number; updates: Partial<Task> }>();
  @Output() taskCreate = new EventEmitter<Partial<Task>>();
  @Output() deleteTask = new EventEmitter<number>();

  showNewTaskForm = false;
  newTaskTitle = '';
  newTaskOwner = 'Me';
  newTaskDue = '';
  newTaskUrgency: 'low' | 'medium' | 'high' | 'urgent' = 'medium';

  get pendingTasks(): Task[] {
    return this.tasks.filter(t => t.status === 'pending');
  }

  get inProgressTasks(): Task[] {
    return this.tasks.filter(t => t.status === 'in_progress');
  }

  get completedTasks(): Task[] {
    return this.tasks.filter(t => t.status === 'completed');
  }

  updateStatus(task: Task, status: 'pending' | 'in_progress' | 'completed') {
    this.taskUpdate.emit({ id: task.id, updates: { status } });
  }

  onCreateTask() {
    if (!this.newTaskTitle.trim()) return;
    this.taskCreate.emit({
      title: this.newTaskTitle,
      owner: this.newTaskOwner || 'Me',
      due_date: this.newTaskDue || undefined,
      urgency: this.newTaskUrgency,
      status: 'pending'
    });
    this.newTaskTitle = '';
    this.newTaskDue = '';
    this.showNewTaskForm = false;
  }
}
