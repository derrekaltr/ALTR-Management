import { afterEach, describe, expect, it } from "vitest";
import { P, currentAccount, dataDir, outDir, setCurrentAccount } from "../src/config.js";

describe("account-scoped paths", () => {
  afterEach(() => delete process.env.REELCRITIC_ACCOUNT);
  it("default account uses data/ and out/", () => {
    expect(currentAccount()).toBe("default");
    expect(dataDir()).toMatch(/\/data$/);
    expect(P().reels).toMatch(/\/data\/reels\.json$/);
  });
  it("named account is slugged and nested", () => {
    setCurrentAccount("Sarah H!");
    expect(currentAccount()).toBe("sarah-h-");
    expect(dataDir()).toMatch(/\/data\/sarah-h-$/);
    expect(outDir()).toMatch(/\/out\/sarah-h-$/);
    expect(P().critiques).toMatch(/\/out\/sarah-h-\/critiques\.json$/);
  });
});
