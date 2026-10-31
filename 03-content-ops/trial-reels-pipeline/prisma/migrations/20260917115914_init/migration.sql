-- CreateEnum
CREATE TYPE "HookStatus" AS ENUM ('PENDING_REVIEW', 'APPROVED', 'REJECTED', 'RETIRED');

-- CreateEnum
CREATE TYPE "HookSource" AS ENUM ('EXTRACTED', 'IMPORT', 'MANUAL', 'GENERATED');

-- CreateEnum
CREATE TYPE "ExampleStatus" AS ENUM ('NEEDS_VIDEO', 'UPLOADED', 'ANALYZED', 'ANALYSIS_FAILED');

-- CreateEnum
CREATE TYPE "BatchStatus" AS ENUM ('RUNNING', 'COMPLETE', 'FAILED');

-- CreateEnum
CREATE TYPE "VersionStatus" AS ENUM ('PLANNED', 'POSTED', 'SKIPPED');

-- CreateTable
CREATE TABLE "ExampleReel" (
    "id" TEXT NOT NULL,
    "sourceUrl" TEXT,
    "sourceHandle" TEXT,
    "videoUrl" TEXT,
    "thumbUrl" TEXT,
    "frameUrls" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "status" "ExampleStatus" NOT NULL DEFAULT 'NEEDS_VIDEO',
    "analysis" JSONB,
    "backgroundDescription" TEXT,
    "tags" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "whyItWorks" TEXT,
    "notes" TEXT,
    "error" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "analyzedAt" TIMESTAMP(3),

    CONSTRAINT "ExampleReel_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Hook" (
    "id" TEXT NOT NULL,
    "text" TEXT NOT NULL,
    "normalizedText" TEXT NOT NULL,
    "category" TEXT,
    "tags" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "notes" TEXT,
    "status" "HookStatus" NOT NULL DEFAULT 'APPROVED',
    "source" "HookSource" NOT NULL,
    "proven" BOOLEAN NOT NULL DEFAULT false,
    "timesUsed" INTEGER NOT NULL DEFAULT 0,
    "exampleReelId" TEXT,
    "batchId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "reviewedAt" TIMESTAMP(3),

    CONSTRAINT "Hook_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "GenerationBatch" (
    "id" TEXT NOT NULL,
    "status" "BatchStatus" NOT NULL DEFAULT 'RUNNING',
    "seedIds" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "toneGuidance" TEXT,
    "count" INTEGER NOT NULL DEFAULT 10,
    "model" TEXT NOT NULL,
    "rawResponse" JSONB,
    "error" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "GenerationBatch_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Creator" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "handle" TEXT,
    "token" TEXT NOT NULL,
    "tokenRotatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "active" BOOLEAN NOT NULL DEFAULT true,
    "timezone" TEXT NOT NULL DEFAULT 'America/New_York',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Creator_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "DayPlan" (
    "id" TEXT NOT NULL,
    "creatorId" TEXT NOT NULL,
    "date" DATE NOT NULL,
    "notes" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "DayPlan_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Version" (
    "id" TEXT NOT NULL,
    "dayPlanId" TEXT NOT NULL,
    "hookId" TEXT NOT NULL,
    "exampleReelId" TEXT,
    "order" INTEGER NOT NULL,
    "changeAudio" BOOLEAN NOT NULL DEFAULT false,
    "changeSpeed" BOOLEAN NOT NULL DEFAULT false,
    "status" "VersionStatus" NOT NULL DEFAULT 'PLANNED',
    "postedAt" TIMESTAMP(3),

    CONSTRAINT "Version_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "ExampleReel_sourceUrl_key" ON "ExampleReel"("sourceUrl");

-- CreateIndex
CREATE INDEX "ExampleReel_status_idx" ON "ExampleReel"("status");

-- CreateIndex
CREATE UNIQUE INDEX "Hook_normalizedText_key" ON "Hook"("normalizedText");

-- CreateIndex
CREATE INDEX "Hook_status_idx" ON "Hook"("status");

-- CreateIndex
CREATE INDEX "Hook_category_idx" ON "Hook"("category");

-- CreateIndex
CREATE INDEX "Hook_proven_idx" ON "Hook"("proven");

-- CreateIndex
CREATE UNIQUE INDEX "Creator_token_key" ON "Creator"("token");

-- CreateIndex
CREATE UNIQUE INDEX "DayPlan_creatorId_date_key" ON "DayPlan"("creatorId", "date");

-- CreateIndex
CREATE UNIQUE INDEX "Version_dayPlanId_hookId_key" ON "Version"("dayPlanId", "hookId");

-- CreateIndex
CREATE UNIQUE INDEX "Version_dayPlanId_order_key" ON "Version"("dayPlanId", "order");

-- AddForeignKey
ALTER TABLE "Hook" ADD CONSTRAINT "Hook_exampleReelId_fkey" FOREIGN KEY ("exampleReelId") REFERENCES "ExampleReel"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Hook" ADD CONSTRAINT "Hook_batchId_fkey" FOREIGN KEY ("batchId") REFERENCES "GenerationBatch"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "DayPlan" ADD CONSTRAINT "DayPlan_creatorId_fkey" FOREIGN KEY ("creatorId") REFERENCES "Creator"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Version" ADD CONSTRAINT "Version_dayPlanId_fkey" FOREIGN KEY ("dayPlanId") REFERENCES "DayPlan"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Version" ADD CONSTRAINT "Version_hookId_fkey" FOREIGN KEY ("hookId") REFERENCES "Hook"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Version" ADD CONSTRAINT "Version_exampleReelId_fkey" FOREIGN KEY ("exampleReelId") REFERENCES "ExampleReel"("id") ON DELETE SET NULL ON UPDATE CASCADE;
