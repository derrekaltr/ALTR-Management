import fs from "node:fs";
import { FIXTURE_FILE } from "../config.js";
import { DatasetSchema, type Dataset } from "./types.js";

export function loadFixture(file: string = FIXTURE_FILE): Dataset {
  return DatasetSchema.parse(JSON.parse(fs.readFileSync(file, "utf8")));
}
