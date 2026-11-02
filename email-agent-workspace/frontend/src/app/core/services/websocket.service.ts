import { Injectable, NgZone } from '@angular/core';
import { Observable, Subject, BehaviorSubject } from 'rxjs';
import { WebSocketEvent } from '../../shared/models/agent.interface';

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: WebSocket | null = null;
  private readonly wsUrl = 'ws://127.0.0.1:8000/ws/stream';
  
  private eventSubject = new Subject<WebSocketEvent>();
  public events$: Observable<WebSocketEvent> = this.eventSubject.asObservable();

  private isConnectedSubject = new BehaviorSubject<boolean>(false);
  public isConnected$: Observable<boolean> = this.isConnectedSubject.asObservable();

  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectInterval = 3000;

  constructor(private zone: NgZone) {
    this.connect();
  }

  public connect(): void {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      this.socket = new WebSocket(this.wsUrl);

      this.socket.onopen = () => {
        this.zone.run(() => {
          this.isConnectedSubject.next(true);
          this.reconnectAttempts = 0;
          console.log('[WebSocket] Connected to Real-time Stream:', this.wsUrl);
        });
      };

      this.socket.onmessage = (event) => {
        this.zone.run(() => {
          try {
            const data: WebSocketEvent = JSON.parse(event.data);
            this.eventSubject.next(data);
          } catch (e) {
            // Ignore non-json ping/pong responses
          }
        });
      };

      this.socket.onclose = () => {
        this.zone.run(() => {
          this.isConnectedSubject.next(false);
          this.scheduleReconnect();
        });
      };

      this.socket.onerror = (error) => {
        this.zone.run(() => {
          console.warn('[WebSocket] Error on stream connection:', error);
          this.isConnectedSubject.next(false);
        });
      };
    } catch (err) {
      console.error('[WebSocket] Setup exception:', err);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        this.connect();
      }, this.reconnectInterval);
    }
  }

  public send(msg: string): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(msg);
    }
  }
}
