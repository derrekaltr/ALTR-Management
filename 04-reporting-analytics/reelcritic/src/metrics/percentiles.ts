export const MIN_POPULATION = 5;

/** Mid-rank percentile (0..100): (below + 0.5*equal) / n * 100. */
export function percentileRank(value: number, population: number[]): number {
  if (population.length === 0) return 50;
  let below = 0;
  let equal = 0;
  for (const p of population) {
    if (p < value) below++;
    else if (p === value) equal++;
  }
  return ((below + 0.5 * equal) / population.length) * 100;
}

export interface PercentileResult {
  percentile: number | null;
  n: number;
  reason?: "insufficient_history" | "metric_null";
}

/**
 * Percentile of `value` against `others` (the population EXCLUDING null entries).
 * Returns null percentile if the population is too small.
 */
export function percentileOf(value: number | null, others: Array<number | null>): PercentileResult {
  const pop = others.filter((x): x is number => x != null && Number.isFinite(x));
  if (value == null) return { percentile: null, n: pop.length, reason: "metric_null" };
  if (pop.length < MIN_POPULATION) return { percentile: null, n: pop.length, reason: "insufficient_history" };
  return { percentile: round1(percentileRank(value, pop)), n: pop.length };
}

export function round1(x: number): number {
  return Math.round(x * 10) / 10;
}

export function median(xs: number[]): number | null {
  if (xs.length === 0) return null;
  const s = [...xs].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m]! : (s[m - 1]! + s[m]!) / 2;
}
