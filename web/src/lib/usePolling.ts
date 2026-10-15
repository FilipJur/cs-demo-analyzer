import { useCallback, useEffect, useRef, useState } from 'react';
import { isAbortError, toApiError, type ApiError } from '../api/client';

export type Polled<T> = {
  data: T | null;
  error: ApiError | null;
  loading: boolean;
  updatedAt: number | null;
  refresh: () => void;
};

export type PollOptions = {
  /** Polling is suspended while false; the request is aborted. */
  enabled?: boolean;
  /** Changing this key resets the data and restarts polling (new selection). */
  key?: string | number | null;
};

/**
 * Durable-state polling: sequential requests, the previous one aborted and
 * every stale response dropped, paused while the tab is hidden.
 */
export function usePolled<T>(load: (signal: AbortSignal) => Promise<T>, intervalMs: number, options: PollOptions = {}): Polled<T> {
  const { enabled = true, key = null } = options;
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(enabled);
  const [updatedAt, setUpdatedAt] = useState<number | null>(null);
  const [nonce, setNonce] = useState(0);
  const loadRef = useRef(load);
  loadRef.current = load;
  const keyRef = useRef(key);

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      return;
    }
    const keyChanged = keyRef.current !== key;
    keyRef.current = key;
    if (keyChanged) {
      setData(null);
      setError(null);
    }
    let active = true;
    let inFlight: AbortController | null = null;
    const run = async () => {
      inFlight?.abort();
      const controller = new AbortController();
      inFlight = controller;
      let value: T;
      try {
        value = await loadRef.current(controller.signal);
      } catch (exc) {
        if (!active || controller.signal.aborted || isAbortError(exc)) return;
        setError(toApiError(exc));
        setLoading(false);
        return;
      }
      if (!active || controller.signal.aborted) return;
      setData(value);
      setError(null);
      setUpdatedAt(Date.now());
      setLoading(false);
    };
    void run();
    const timer = window.setInterval(() => {
      if (document.visibilityState === 'visible') void run();
    }, intervalMs);
    return () => {
      active = false;
      window.clearInterval(timer);
      inFlight?.abort();
    };
  }, [enabled, intervalMs, nonce, key]);

  const refresh = useCallback(() => setNonce((value) => value + 1), []);
  return { data, error, loading, updatedAt, refresh };
}
