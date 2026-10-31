import { describe, expect, it } from "vitest";
import { parseCsv } from "../../src/ingest/csv.js";

describe("csv", () => {
  it("handles quotes, escaped quotes, CRLF and BOM", () => {
    const rows = parseCsv('﻿a,b,c\r\n1,"x, y","he said ""hi"""\n2,,\n');
    expect(rows).toEqual([["a", "b", "c"], ["1", "x, y", 'he said "hi"'], ["2", "", ""]]);
  });
  it("multiline quoted field", () => {
    expect(parseCsv('a\n"line1\nline2"')).toEqual([["a"], ["line1\nline2"]]);
  });
});
