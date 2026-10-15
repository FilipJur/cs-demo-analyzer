// Formatting helpers shared by the library and replay panels.

const BYTE_UNITS = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB'] as const;

export function formatBytes(value: number | null): string {
  if (value === null || !Number.isFinite(value)) return 'unknown';
  let amount = Math.max(0, value);
  let unit = 0;
  while (amount >= 1024 && unit < BYTE_UNITS.length - 1) {
    amount /= 1024;
    unit += 1;
  }
  const digits = unit === 0 ? 0 : amount >= 100 ? 0 : 1;
  return `${amount.toFixed(digits)} ${BYTE_UNITS[unit]}`;
}

export function formatTimestamp(value: string | null | undefined): string {
  if (!value) return 'unknown';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString();
}

export function formatTickTime(tick: number, startTick: number, tickRateHz: number): string {
  if (!Number.isFinite(tickRateHz) || tickRateHz <= 0) return 'n/a';
  return `${((tick - startTick) / tickRateHz).toFixed(2)}s`;
}

export function shortHash(value: string): string {
  return value.length <= 12 ? value : `${value.slice(0, 8)}…${value.slice(-3)}`;
}

export function sideColor(side: string): string {
  const normalized = side.trim().toLowerCase();
  if (normalized === 'ct') return '#4d9cff';
  if (normalized === 't') return '#f0b23c';
  if (normalized === 'spectator') return '#9aa0a6';
  return '#c8ccd2';
}

export function sideLabel(side: string): string {
  const normalized = side.trim().toLowerCase();
  if (normalized === 'ct') return 'CT';
  if (normalized === 't') return 'T';
  if (normalized === 'spectator') return 'Spectator';
  return side || 'unknown';
}
