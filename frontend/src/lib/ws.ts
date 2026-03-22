const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/v1/ws";

export function createWebSocket(sessionId: string): WebSocket {
  return new WebSocket(`${WS_URL}/${sessionId}`);
}
