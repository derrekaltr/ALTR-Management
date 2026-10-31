import { NextRequest, NextResponse } from "next/server";

// Edge runtime: verify the session cookie with WebCrypto. This is a first
// gate for /admin pages; server actions and pages re-verify via requireAdmin().
async function verifySession(value: string | undefined, secret: string): Promise<boolean> {
  if (!value) return false;
  const dot = value.indexOf(".");
  if (dot === -1) return false;
  const expiry = value.slice(0, dot);
  const sig = value.slice(dot + 1);
  if (!/^\d+$/.test(expiry) || Number(expiry) < Date.now()) return false;

  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const mac = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(expiry));
  const expected = Array.from(new Uint8Array(mac))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  if (sig.length !== expected.length) return false;
  let diff = 0;
  for (let i = 0; i < sig.length; i++) diff |= sig.charCodeAt(i) ^ expected.charCodeAt(i);
  return diff === 0;
}

export async function middleware(request: NextRequest) {
  const secret = process.env.SESSION_SECRET;
  const cookie = request.cookies.get("trp_session")?.value;
  if (!secret || !(await verifySession(cookie, secret))) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*"],
};
