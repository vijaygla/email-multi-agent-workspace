import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface ToastMessage {
  id: string;
  type: 'success' | 'info' | 'warning' | 'error';
  title: string;
  message: string;
  duration?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ToastService {
  private toastsSubject = new BehaviorSubject<ToastMessage[]>([]);
  public toasts$: Observable<ToastMessage[]> = this.toastsSubject.asObservable();

  show(type: 'success' | 'info' | 'warning' | 'error', title: string, message: string, duration = 4000) {
    const id = Math.random().toString(36).substring(2, 9);
    const toast: ToastMessage = { id, type, title, message, duration };
    const current = this.toastsSubject.getValue();
    this.toastsSubject.next([...current, toast]);

    if (duration > 0) {
      setTimeout(() => {
        this.remove(id);
      }, duration);
    }
  }

  success(title: string, message: string) {
    this.show('success', title, message);
  }

  info(title: string, message: string) {
    this.show('info', title, message);
  }

  warning(title: string, message: string) {
    this.show('warning', title, message);
  }

  error(title: string, message: string) {
    this.show('error', title, message, 6000);
  }

  remove(id: string) {
    const updated = this.toastsSubject.getValue().filter(t => t.id !== id);
    this.toastsSubject.next(updated);
  }
}
