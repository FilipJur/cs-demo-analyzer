import { useEffect, useRef, useState } from 'react';
import { isAbortError, toApiError, type ApiError } from '../api/client';

export type AnalyticsQuery<T> = {
  data: T | null;
  error: ApiError | null;
  loading: boolean;
};

/**
 * One-shot query keyed by `key`, for reads driven by the replay tick rather
 * than by a wall-clock interval. Changing `key` aborts the in-flight request
 * and keeps the previous value until the new one lands, so the inspector does
 * not blank out between ticks. `load` is read from a ref, so an inline closure
 * does not restart the request on every render.
 */
export function useAnalyticsQuery<T>(load: (signal: AbortSignal) => Promise<T>, key: string, enabled = true): AnalyticsQuery<T> {
  const loadRef = useRef(load);
  loadRef.current = load;
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(enabled);

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      return;
    }
    const controller = new AbortController();
    let active = true;
    setLoading(true);
    void (async () => {
      try {
        const value = await loadRef.current(controller.signal);
        if (!active || controller.signal.aborted) return;
        setData(value);
        setError(null);
      } catch (exc) {
        if (!active || controller.signal.aborted || isAbortError(exc)) return;
        setError(toApiError(exc));
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
      controller.abort();
    };
  }, [enabled, key]);

  return { data, error, loading };
}
