// Local dev Postgres without Docker: downloads binaries into node_modules and
// runs a server on port 5502 with data in .pgdata/.
// Usage: node scripts/db.mjs start | stop
import EmbeddedPostgres from "embedded-postgres";
import { existsSync } from "node:fs";
import path from "node:path";

const dataDir = path.resolve(".pgdata");
const pg = new EmbeddedPostgres({
  databaseDir: dataDir,
  user: "postgres",
  password: "postgres",
  port: 5502,
  persistent: true,
});

const cmd = process.argv[2];

if (cmd === "start") {
  const fresh = !existsSync(path.join(dataDir, "PG_VERSION"));
  if (fresh) await pg.initialise();
  await pg.start();
  if (fresh) await pg.createDatabase("trial_reels");
  console.log("postgres running on port 5502 (db: trial_reels). Stop with: npm run db:stop");
  // Keep the process alive; ctrl-c stops the server cleanly.
  const stop = async () => {
    await pg.stop();
    process.exit(0);
  };
  process.on("SIGINT", stop);
  process.on("SIGTERM", stop);
} else if (cmd === "stop") {
  await pg.stop();
  console.log("postgres stopped");
} else {
  console.error("usage: node scripts/db.mjs start|stop");
  process.exit(1);
}
