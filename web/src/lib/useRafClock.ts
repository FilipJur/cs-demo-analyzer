import { useCallback, useEffect, useRef, useState } from 'react';

export type ClockBounds = { min: number; max: number };

export type RafClock = {
  tick: number;
  playing: boolean;
  play: () => void;
  pause: () => void;
  toggle: () => void;
  seek: (tick: number) => void;
  step: (deltaTicks: number) => void;
};

/**
 * The single tick clock for replay. Exactly one requestAnimationFrame loop runs
 * while playing; seeking resets it. Ticks advance from wall-clock elapsed time
 * scaled by the demo's tick rate (never a hardcoded rate).
 */
export function useRafClock(bounds: ClockBounds | null, tickRateHz: number): RafClock {
  const [tick, setTick] = useState(bounds?.min ?? 0);
  const [playing, setPlaying] = useState(false);
  const tickRef = useRef(bounds?.min ?? 0);
  const boundsRef = useRef(bounds);
  boundsRef.current = bounds;
  const rateRef = useRef(tickRateHz);
  rateRef.current = tickRateHz;
  const fractionRef = useRef(0);
  const frameRef = useRef<number | null>(null);
  const min = bounds?.min ?? null;
  const max = bounds?.max ?? null;

  useEffect(() => {
    // A new window or round resets the clock rather than jumping across it.
    setPlaying(false);
    fractionRef.current = 0;
    const start = min ?? 0;
    tickRef.current = start;
    setTick(start);
  }, [min, max]);

  const apply = useCallback((value: number) => {
    const current = boundsRef.current;
    const rounded = Math.round(value);
    const clamped = current === null ? rounded : Math.min(current.max, Math.max(current.min, rounded));
    tickRef.current = clamped;
    setTick(clamped);
  }, []);

  useEffect(() => {
    if (!playing || min === null || max === null) return;
    let last = performance.now();
    const frame = (now: number) => {
      const current = boundsRef.current;
      if (current === null) return;
      const elapsed = Math.min(250, Math.max(0, now - last));
      last = now;
      const advance = fractionRef.current + (elapsed / 1000) * rateRef.current;
      const whole = Math.floor(advance);
      fractionRef.current = advance - whole;
      if (whole > 0) {
        const next = Math.min(current.max, tickRef.current + whole);
        apply(next);
        if (next >= current.max) {
          fractionRef.current = 0;
          setPlaying(false);
          frameRef.current = null;
          return;
        }
      }
      frameRef.current = requestAnimationFrame(frame);
    };
    frameRef.current = requestAnimationFrame(frame);
    return () => {
      if (frameRef.current !== null) cancelAnimationFrame(frameRef.current);
      frameRef.current = null;
    };
  }, [playing, min, max, apply]);

  const seek = useCallback(
    (value: number) => {
      setPlaying(false);
      fractionRef.current = 0;
      apply(value);
    },
    [apply],
  );

  const step = useCallback(
    (delta: number) => {
      setPlaying(false);
      fractionRef.current = 0;
      apply(tickRef.current + delta);
    },
    [apply],
  );

  return {
    tick,
    playing,
    play: () => setPlaying(true),
    pause: () => setPlaying(false),
    toggle: () => setPlaying((value) => !value),
    seek,
    step,
  };
}
