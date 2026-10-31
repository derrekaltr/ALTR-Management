export type LengthBand = "7-15" | "15-30" | "30-60" | "60+" | "over-3min" | "unknown";

export function lengthBand(duration_s: number | null): LengthBand {
  if (duration_s == null || !Number.isFinite(duration_s) || duration_s <= 0) return "unknown";
  if (duration_s > 180) return "over-3min";
  if (duration_s <= 15) return "7-15";
  if (duration_s <= 30) return "15-30";
  if (duration_s <= 60) return "30-60";
  return "60+";
}

/**
 * Soft completion reference by band (CreatorHouse synthesis of Dash Social / Socialinsider / Metricool, 2026).
 * REFERENCE ONLY — not a threshold. Sources disagree 2–5x; the creator's own percentile is the scored signal.
 */
export const SOFT_COMPLETION_REFERENCE: Record<Exclude<LengthBand, "unknown" | "over-3min">, number> = {
  "7-15": 0.74,
  "15-30": 0.6,
  "30-60": 0.49,
  "60+": 0.46,
};

/** hold_rate minus the soft reference for the band; null when either side is unknown. */
export function completionVsBand(hold_rate: number | null, band: LengthBand): number | null {
  if (hold_rate == null) return null;
  if (band === "unknown") return null;
  const ref = band === "over-3min" ? SOFT_COMPLETION_REFERENCE["60+"] : SOFT_COMPLETION_REFERENCE[band];
  return hold_rate - ref;
}
