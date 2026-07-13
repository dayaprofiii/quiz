export const apiBaseUrl = '/api';

export function roomWebSocketUrl(code) {
  const wsBaseUrl = window.__QUIZLEET_WS_URL__ || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
  return `${wsBaseUrl}?code=${encodeURIComponent(code)}`;
}
