/**
 * Single source of truth for hook-text dedupe. Import, generation, manual add,
 * and edit-then-approve all normalize through here before touching
 * Hook.normalizedText.
 */
export function normalizeHookText(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFKC")
    .replace(/[‘’‚‛′]/g, "'")
    .replace(/[“”„‟″]/g, '"')
    .replace(/[^\p{L}\p{N}' ]/gu, "")
    .replace(/\s+/g, " ")
    .trim();
}

const IG_PATH = /^\/(reels?|p)\/([A-Za-z0-9_-]+)/;

/**
 * Canonicalize an Instagram reel/post URL for dedupe: strips share tokens
 * (?stkn=...), trailing slashes, and folds /reel/ vs /reels/ vs /p/ variants
 * down to the shortcode. Returns null if this isn't an Instagram content URL.
 */
export function canonicalizeReelUrl(raw: string): string | null {
  let url: URL;
  try {
    url = new URL(raw.trim());
  } catch {
    return null;
  }
  if (!/(^|\.)instagram\.com$/.test(url.hostname)) return null;
  const match = IG_PATH.exec(url.pathname);
  if (!match) return null;
  return `https://www.instagram.com/reel/${match[2]}/`;
}

export function looksLikeUrl(value: string): boolean {
  return /^https?:\/\//i.test(value.trim());
}
