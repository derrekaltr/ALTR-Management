import type { RetentionPoint } from "../ingest/types.js";

export type CurveShape = "cliff" | "hump" | "plateau_loop" | "unknown";

export interface CurveResult {
  shape: CurveShape;
  first_15pct_drop: number | null; // retention points lost by t<=15%
  mid_slope: number | null; // retention change per 1% of time across 15%..85%
  tail_retention_pct: number | null; // retention at last point
  rewatch_bump: boolean; // any later point >= 5 pts above an earlier local minimum
  points: number;
}

/**
 * Deterministic retention-curve classifier (Galloway-style Cliff / Hump / Plateau-Loop).
 * Needs >= 3 points; otherwise "unknown".
 */
export function classifyCurve(raw: RetentionPoint[]): CurveResult {
  const pts = [...raw]
    .filter((p) => Number.isFinite(p.t_pct) && Number.isFinite(p.retained_pct))
    .sort((a, b) => a.t_pct - b.t_pct);
  if (pts.length < 3) {
    return { shape: "unknown", first_15pct_drop: null, mid_slope: null, tail_retention_pct: null, rewatch_bump: false, points: pts.length };
  }
  const start = pts[0]!.retained_pct;
  const at = (t: number) => interpolate(pts, t);
  const r15 = at(15);
  const r85 = at(85);
  const tail = pts[pts.length - 1]!.retained_pct;
  const firstDrop = start - r15;
  const midSlope = (r85 - r15) / 70;

  // rewatch bump: a later point at least 5 pts above a prior local minimum
  let runningMin = Infinity;
  let bump = false;
  for (const p of pts) {
    if (p.retained_pct >= runningMin + 5) bump = true;
    runningMin = Math.min(runningMin, p.retained_pct);
  }

  let shape: CurveShape;
  if (firstDrop >= 40) shape = "cliff";
  else if (bump) shape = "hump";
  else if (tail >= 0.6 * r15 && Math.abs(midSlope) <= 0.35) shape = "plateau_loop";
  else shape = "unknown";

  return {
    shape,
    first_15pct_drop: round1(firstDrop),
    mid_slope: round3(midSlope),
    tail_retention_pct: round1(tail),
    rewatch_bump: bump,
    points: pts.length,
  };
}

function interpolate(pts: RetentionPoint[], t: number): number {
  if (t <= pts[0]!.t_pct) return pts[0]!.retained_pct;
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i - 1]!;
    const b = pts[i]!;
    if (t <= b.t_pct) {
      const span = b.t_pct - a.t_pct;
      if (span === 0) return b.retained_pct;
      const f = (t - a.t_pct) / span;
      return a.retained_pct + f * (b.retained_pct - a.retained_pct);
    }
  }
  return pts[pts.length - 1]!.retained_pct;
}

const round1 = (x: number) => Math.round(x * 10) / 10;
const round3 = (x: number) => Math.round(x * 1000) / 1000;
