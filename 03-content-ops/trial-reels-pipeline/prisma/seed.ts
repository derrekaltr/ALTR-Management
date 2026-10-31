import { PrismaClient } from "@prisma/client";
import { randomBytes } from "node:crypto";

const prisma = new PrismaClient();

function normalize(text: string): string {
  return text
    .toLowerCase()
    .normalize("NFKC")
    .replace(/[‘’‚‛′]/g, "'")
    .replace(/[“”„‟″]/g, '"')
    .replace(/[^\p{L}\p{N}' ]/gu, "")
    .replace(/\s+/g, " ")
    .trim();
}

const HOOKS: { text: string; category: string; proven?: boolean }[] = [
  { text: "POV: you texted him first again", category: "goofy", proven: true },
  { text: "he said he likes natural girls. anyway", category: "funny", proven: true },
  { text: "my toxic trait? this outfit on a Tuesday", category: "sexy", proven: true },
  { text: "rating my self control around iced coffee: 1/10", category: "goofy" },
  { text: "when the gym fit does more work than the workout", category: "funny" },
  { text: "day 3 of pretending I woke up like this", category: "goofy" },
  { text: "she's not mad, she's just recording", category: "funny" },
  { text: "warning: main character energy ahead", category: "sexy" },
  { text: "nobody warned me adulthood was just laundry", category: "goofy" },
  { text: "tell me why groceries cost a whole paycheck", category: "funny" },
  { text: "it's giving 'don't text your ex' energy", category: "goofy" },
  { text: "me pretending the camera isn't right there", category: "funny", proven: true },
  { text: "the audacity of this dress. anyway, hi", category: "sexy" },
  { text: "5am club? never met her", category: "goofy" },
  { text: "if lost, return to the coffee shop", category: "funny" },
];

async function main() {
  for (const hook of HOOKS) {
    await prisma.hook.createMany({
      data: [
        {
          text: hook.text,
          normalizedText: normalize(hook.text),
          category: hook.category,
          status: "APPROVED",
          source: "IMPORT",
          proven: hook.proven ?? false,
        },
      ],
      skipDuplicates: true,
    });
  }

  const creators = [
    { name: "Demo Creator One", handle: "@demo.one", timezone: "America/New_York" },
    { name: "Demo Creator Two", handle: "@demo.two", timezone: "America/Los_Angeles" },
  ];
  for (const creator of creators) {
    const existing = await prisma.creator.findFirst({ where: { name: creator.name } });
    if (!existing) {
      await prisma.creator.create({
        data: { ...creator, token: randomBytes(24).toString("base64url") },
      });
    }
  }

  await prisma.exampleReel.createMany({
    data: [
      { sourceUrl: "https://www.instagram.com/reel/SEEDAAA111/" },
      { sourceUrl: "https://www.instagram.com/reel/SEEDBBB222/" },
      { sourceUrl: "https://www.instagram.com/reel/SEEDCCC333/" },
    ],
    skipDuplicates: true,
  });

  const tokens = await prisma.creator.findMany({ select: { name: true, token: true } });
  console.log("Seeded. Creator links:");
  for (const t of tokens) console.log(`  ${t.name}: /c/${t.token}`);
}

main()
  .then(() => prisma.$disconnect())
  .catch(async (e) => {
    console.error(e);
    await prisma.$disconnect();
    process.exit(1);
  });
