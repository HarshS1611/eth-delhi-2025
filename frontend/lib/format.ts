// Use a fixed locale so SSR and client match.
export const nf = new Intl.NumberFormat("en-US");

export function formatInt(n: number) {
  // Avoid locale differences by fixing the locale above.
  return nf.format(Math.floor(Number.isFinite(n) ? n : 0));
}
