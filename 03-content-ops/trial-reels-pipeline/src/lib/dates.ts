/**
 * "Today" is always a calendar date in the creator's timezone — never the
 * server's UTC clock. DayPlan.date is a Postgres DATE; Prisma reads/writes it
 * as a Date at UTC midnight, so we convert calendar strings <-> UTC midnight.
 */

/** Calendar date (YYYY-MM-DD) right now in the given IANA timezone. */
export function todayInTimezone(timezone: string): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: timezone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}

/** YYYY-MM-DD -> Date at UTC midnight, matching Prisma's @db.Date handling. */
export function dateStringToUtc(dateString: string): Date {
  return new Date(`${dateString}T00:00:00.000Z`);
}

/** Date at UTC midnight -> YYYY-MM-DD. */
export function utcToDateString(date: Date): string {
  return date.toISOString().slice(0, 10);
}

export function addDays(dateString: string, days: number): string {
  const d = dateStringToUtc(dateString);
  d.setUTCDate(d.getUTCDate() + days);
  return utcToDateString(d);
}

export function formatDisplayDate(dateString: string): string {
  // Pure calendar date: always format at UTC so the day never shifts.
  return new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    timeZone: "UTC",
  }).format(dateStringToUtc(dateString));
}
