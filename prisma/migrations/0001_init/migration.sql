-- Extensions
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enums
CREATE TYPE "Role" AS ENUM ('USER', 'ADMIN');
CREATE TYPE "JobType" AS ENUM ('INTERN', 'NEW_GRAD', 'FULL_TIME', 'CONTRACT');
CREATE TYPE "WorkMode" AS ENUM ('REMOTE', 'HYBRID', 'ONSITE');
CREATE TYPE "EmploymentLevel" AS ENUM ('ENTRY', 'ASSOCIATE', 'MID', 'SENIOR');
CREATE TYPE "JobStatus" AS ENUM ('ACTIVE', 'CLOSED', 'EXPIRED');
CREATE TYPE "ApplicationSource" AS ENUM ('PLATFORM', 'COMPANY_SITE', 'REFERRAL', 'RECRUITER');
CREATE TYPE "ApplicationStatus" AS ENUM ('SAVED', 'APPLIED', 'OA', 'PHONE_SCREEN', 'INTERVIEW', 'OFFER', 'REJECTED');
CREATE TYPE "ResumeStatus" AS ENUM ('PROCESSING', 'READY', 'FAILED');
CREATE TYPE "AlertChannel" AS ENUM ('EMAIL', 'IN_APP', 'BOTH');
CREATE TYPE "AlertFrequency" AS ENUM ('INSTANT', 'DAILY', 'WEEKLY');
CREATE TYPE "MessageType" AS ENUM ('COVER_LETTER', 'RECRUITER_OUTREACH', 'REFERRAL_REQUEST', 'THANK_YOU_NOTE');
CREATE TYPE "MessageStatus" AS ENUM ('DRAFT', 'GENERATED', 'EDITED', 'SENT');
CREATE TYPE "EmbeddingEntityType" AS ENUM ('JOB', 'RESUME', 'USER_PROFILE', 'ALERT_QUERY');
CREATE TYPE "ScrapeSourceType" AS ENUM ('GREENHOUSE', 'LEVER', 'ASHBY', 'YC', 'CUSTOM');
CREATE TYPE "ScrapeRunStatus" AS ENUM ('QUEUED', 'RUNNING', 'SUCCEEDED', 'PARTIAL', 'FAILED');

-- Core auth and user tables
CREATE TABLE "User" (
  "id" TEXT PRIMARY KEY,
  "email" TEXT NOT NULL,
  "normalizedEmail" TEXT NOT NULL,
  "name" TEXT,
  "image" TEXT,
  "role" "Role" NOT NULL DEFAULT 'USER',
  "headline" TEXT,
  "university" TEXT,
  "graduationYear" INTEGER,
  "targetRoles" TEXT[] NOT NULL DEFAULT '{}',
  "targetLocations" TEXT[] NOT NULL DEFAULT '{}',
  "needsSponsorship" BOOLEAN NOT NULL DEFAULT FALSE,
  "isOnboarded" BOOLEAN NOT NULL DEFAULT FALSE,
  "preferences" JSONB,
  "lastActiveAt" TIMESTAMP(3),
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "Account" (
  "id" TEXT PRIMARY KEY,
  "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "type" TEXT NOT NULL,
  "provider" TEXT NOT NULL,
  "providerAccountId" TEXT NOT NULL,
  "refresh_token" TEXT,
  "access_token" TEXT,
  "expires_at" INTEGER,
  "token_type" TEXT,
  "scope" TEXT,
  "id_token" TEXT,
  "session_state" TEXT
);

CREATE TABLE "Session" (
  "id" TEXT PRIMARY KEY,
  "sessionToken" TEXT NOT NULL,
  "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "expires" TIMESTAMP(3) NOT NULL
);

CREATE TABLE "VerificationToken" (
  "identifier" TEXT NOT NULL,
  "token" TEXT NOT NULL,
  "expires" TIMESTAMP(3) NOT NULL
);

-- Domain tables
CREATE TABLE "Company" (
  "id" TEXT PRIMARY KEY,
  "name" TEXT NOT NULL,
  "normalizedName" TEXT NOT NULL,
  "website" TEXT,
  "careersPageUrl" TEXT,
  "logoUrl" TEXT,
  "description" TEXT,
  "headquarters" TEXT,
  "sizeRange" TEXT,
  "sponsorshipPolicy" TEXT,
  "techStack" TEXT[] NOT NULL DEFAULT '{}',
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "Job" (
  "id" TEXT PRIMARY KEY,
  "externalId" TEXT,
  "sourceType" "ScrapeSourceType" NOT NULL,
  "sourceName" TEXT NOT NULL,
  "sourceUrl" TEXT NOT NULL,
  "applicationUrl" TEXT NOT NULL,
  "title" TEXT NOT NULL,
  "normalizedTitle" TEXT NOT NULL,
  "description" TEXT NOT NULL,
  "descriptionHtml" TEXT,
  "location" TEXT,
  "locationRegion" TEXT,
  "salaryMin" INTEGER,
  "salaryMax" INTEGER,
  "currency" TEXT DEFAULT 'USD',
  "equity" TEXT,
  "workMode" "WorkMode",
  "employmentLevel" "EmploymentLevel",
  "visaSponsorship" BOOLEAN,
  "requiresClearance" BOOLEAN NOT NULL DEFAULT FALSE,
  "techStack" TEXT[] NOT NULL DEFAULT '{}',
  "keywords" TEXT[] NOT NULL DEFAULT '{}',
  "jobType" "JobType" NOT NULL,
  "status" "JobStatus" NOT NULL DEFAULT 'ACTIVE',
  "postedAt" TIMESTAMP(3),
  "expiresAt" TIMESTAMP(3),
  "lastSeenAt" TIMESTAMP(3),
  "dedupeHash" TEXT NOT NULL,
  "searchTsv" tsvector,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "companyId" TEXT NOT NULL REFERENCES "Company"("id") ON DELETE CASCADE
);

CREATE TABLE "Resume" (
  "id" TEXT PRIMARY KEY,
  "fileName" TEXT NOT NULL,
  "fileUrl" TEXT NOT NULL,
  "fileSizeBytes" INTEGER NOT NULL,
  "mimeType" TEXT NOT NULL DEFAULT 'application/pdf',
  "checksumSha256" TEXT NOT NULL,
  "status" "ResumeStatus" NOT NULL DEFAULT 'PROCESSING',
  "parsedText" TEXT,
  "parsedTextVersion" TEXT,
  "extractedSkills" TEXT[] NOT NULL DEFAULT '{}',
  "extractedProjects" JSONB,
  "extractedEducation" JSONB,
  "extractedExperience" JSONB,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE
);

CREATE TABLE "Application" (
  "id" TEXT PRIMARY KEY,
  "status" "ApplicationStatus" NOT NULL DEFAULT 'SAVED',
  "source" "ApplicationSource" NOT NULL DEFAULT 'PLATFORM',
  "notes" TEXT,
  "appliedAt" TIMESTAMP(3),
  "deadline" TIMESTAMP(3),
  "nextStepAt" TIMESTAMP(3),
  "rejectionReason" TEXT,
  "compensationOffered" INTEGER,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "jobId" TEXT NOT NULL REFERENCES "Job"("id") ON DELETE CASCADE
);

CREATE TABLE "SavedJob" (
  "id" TEXT PRIMARY KEY,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "preferenceScore" DOUBLE PRECISION,
  "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "jobId" TEXT NOT NULL REFERENCES "Job"("id") ON DELETE CASCADE
);

CREATE TABLE "Alert" (
  "id" TEXT PRIMARY KEY,
  "name" TEXT NOT NULL,
  "query" TEXT NOT NULL,
  "channel" "AlertChannel" NOT NULL DEFAULT 'BOTH',
  "frequency" "AlertFrequency" NOT NULL DEFAULT 'DAILY',
  "minMatchScore" DOUBLE PRECISION NOT NULL DEFAULT 0.65,
  "isEnabled" BOOLEAN NOT NULL DEFAULT TRUE,
  "lastTriggeredAt" TIMESTAMP(3),
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE
);

CREATE TABLE "RecruiterMessage" (
  "id" TEXT PRIMARY KEY,
  "type" "MessageType" NOT NULL,
  "status" "MessageStatus" NOT NULL DEFAULT 'GENERATED',
  "companyName" TEXT,
  "roleTitle" TEXT,
  "promptInput" TEXT NOT NULL,
  "outputText" TEXT NOT NULL,
  "modelName" TEXT,
  "tokensPrompt" INTEGER,
  "tokensOutput" INTEGER,
  "qualityScore" DOUBLE PRECISION,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE
);

CREATE TABLE "Embedding" (
  "id" TEXT PRIMARY KEY,
  "entityType" "EmbeddingEntityType" NOT NULL,
  "modelName" TEXT NOT NULL,
  "dimensions" INTEGER NOT NULL DEFAULT 1536,
  "vector" vector(1536) NOT NULL,
  "metadata" JSONB,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "jobId" TEXT REFERENCES "Job"("id") ON DELETE CASCADE,
  "resumeId" TEXT REFERENCES "Resume"("id") ON DELETE CASCADE,
  "userId" TEXT REFERENCES "User"("id") ON DELETE CASCADE,
  "alertId" TEXT REFERENCES "Alert"("id") ON DELETE CASCADE
);

CREATE TABLE "ResumeAnalysis" (
  "id" TEXT PRIMARY KEY,
  "atsScore" INTEGER NOT NULL,
  "matchPercentage" INTEGER NOT NULL,
  "missingSkills" TEXT[] NOT NULL DEFAULT '{}',
  "suggestions" TEXT[] NOT NULL DEFAULT '{}',
  "strengths" TEXT[] NOT NULL DEFAULT '{}',
  "modelName" TEXT NOT NULL,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "resumeId" TEXT NOT NULL REFERENCES "Resume"("id") ON DELETE CASCADE,
  "jobId" TEXT REFERENCES "Job"("id") ON DELETE SET NULL
);

CREATE TABLE "Interview" (
  "id" TEXT PRIMARY KEY,
  "roundName" TEXT NOT NULL,
  "interviewer" TEXT,
  "scheduledAt" TIMESTAMP(3),
  "completedAt" TIMESTAMP(3),
  "feedback" TEXT,
  "rating" INTEGER,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "applicationId" TEXT NOT NULL REFERENCES "Application"("id") ON DELETE CASCADE
);

CREATE TABLE "ApplicationStatusHistory" (
  "id" TEXT PRIMARY KEY,
  "fromStatus" "ApplicationStatus",
  "toStatus" "ApplicationStatus" NOT NULL,
  "changedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "reason" TEXT,
  "applicationId" TEXT NOT NULL REFERENCES "Application"("id") ON DELETE CASCADE
);

CREATE TABLE "UserNote" (
  "id" TEXT PRIMARY KEY,
  "title" TEXT,
  "body" TEXT NOT NULL,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
  "jobId" TEXT REFERENCES "Job"("id") ON DELETE SET NULL,
  "companyId" TEXT REFERENCES "Company"("id") ON DELETE SET NULL
);

CREATE TABLE "ScrapeRun" (
  "id" TEXT PRIMARY KEY,
  "sourceType" "ScrapeSourceType" NOT NULL,
  "sourceName" TEXT NOT NULL,
  "status" "ScrapeRunStatus" NOT NULL DEFAULT 'QUEUED',
  "startedAt" TIMESTAMP(3),
  "completedAt" TIMESTAMP(3),
  "jobsSeen" INTEGER NOT NULL DEFAULT 0,
  "jobsInserted" INTEGER NOT NULL DEFAULT 0,
  "jobsUpdated" INTEGER NOT NULL DEFAULT 0,
  "jobsArchived" INTEGER NOT NULL DEFAULT 0,
  "errorMessage" TEXT,
  "traceId" TEXT,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "JobScrapeEvent" (
  "id" TEXT PRIMARY KEY,
  "eventType" TEXT NOT NULL,
  "sourceUrl" TEXT,
  "payload" JSONB,
  "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "jobId" TEXT NOT NULL REFERENCES "Job"("id") ON DELETE CASCADE,
  "scrapeRunId" TEXT REFERENCES "ScrapeRun"("id") ON DELETE SET NULL
);

CREATE TABLE "AlertDelivery" (
  "id" TEXT PRIMARY KEY,
  "deliveredAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "channel" "AlertChannel" NOT NULL,
  "jobsCount" INTEGER NOT NULL DEFAULT 0,
  "openedAt" TIMESTAMP(3),
  "clickedAt" TIMESTAMP(3),
  "alertId" TEXT NOT NULL REFERENCES "Alert"("id") ON DELETE CASCADE,
  "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE
);

CREATE TABLE "RecommendationLog" (
  "id" TEXT PRIMARY KEY,
  "strategy" TEXT NOT NULL,
  "requestedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "latencyMs" INTEGER,
  "resultCount" INTEGER NOT NULL DEFAULT 0,
  "userId" TEXT NOT NULL REFERENCES "User"("id") ON DELETE CASCADE
);

-- Uniques
CREATE UNIQUE INDEX "User_email_key" ON "User" ("email");
CREATE UNIQUE INDEX "User_normalizedEmail_key" ON "User" ("normalizedEmail");
CREATE UNIQUE INDEX "Company_normalizedName_key" ON "Company" ("normalizedName");
CREATE UNIQUE INDEX "Job_dedupeHash_key" ON "Job" ("dedupeHash");
CREATE UNIQUE INDEX "Job_sourceName_externalId_key" ON "Job" ("sourceName", "externalId");
CREATE UNIQUE INDEX "Resume_checksumSha256_key" ON "Resume" ("checksumSha256");
CREATE UNIQUE INDEX "Application_userId_jobId_key" ON "Application" ("userId", "jobId");
CREATE UNIQUE INDEX "SavedJob_userId_jobId_key" ON "SavedJob" ("userId", "jobId");
CREATE UNIQUE INDEX "Account_provider_providerAccountId_key" ON "Account" ("provider", "providerAccountId");
CREATE UNIQUE INDEX "Session_sessionToken_key" ON "Session" ("sessionToken");
CREATE UNIQUE INDEX "VerificationToken_token_key" ON "VerificationToken" ("token");
CREATE UNIQUE INDEX "VerificationToken_identifier_token_key" ON "VerificationToken" ("identifier", "token");

-- Operational indexes
CREATE INDEX "User_role_createdAt_idx" ON "User" ("role", "createdAt");
CREATE INDEX "User_graduationYear_needsSponsorship_idx" ON "User" ("graduationYear", "needsSponsorship");
CREATE INDEX "User_lastActiveAt_idx" ON "User" ("lastActiveAt");
CREATE INDEX "Company_name_idx" ON "Company" ("name");
CREATE INDEX "Job_companyId_status_postedAt_idx" ON "Job" ("companyId", "status", "postedAt");
CREATE INDEX "Job_jobType_workMode_postedAt_idx" ON "Job" ("jobType", "workMode", "postedAt");
CREATE INDEX "Job_locationRegion_postedAt_idx" ON "Job" ("locationRegion", "postedAt");
CREATE INDEX "Job_visaSponsorship_workMode_idx" ON "Job" ("visaSponsorship", "workMode");
CREATE INDEX "Job_status_expiresAt_idx" ON "Job" ("status", "expiresAt");
CREATE INDEX "Job_lastSeenAt_idx" ON "Job" ("lastSeenAt");
CREATE INDEX "Resume_userId_createdAt_idx" ON "Resume" ("userId", "createdAt");
CREATE INDEX "Resume_status_updatedAt_idx" ON "Resume" ("status", "updatedAt");
CREATE INDEX "Application_userId_status_updatedAt_idx" ON "Application" ("userId", "status", "updatedAt");
CREATE INDEX "Application_jobId_status_idx" ON "Application" ("jobId", "status");
CREATE INDEX "SavedJob_userId_createdAt_idx" ON "SavedJob" ("userId", "createdAt");
CREATE INDEX "Alert_userId_isEnabled_updatedAt_idx" ON "Alert" ("userId", "isEnabled", "updatedAt");
CREATE INDEX "Alert_lastTriggeredAt_idx" ON "Alert" ("lastTriggeredAt");
CREATE INDEX "RecruiterMessage_userId_type_createdAt_idx" ON "RecruiterMessage" ("userId", "type", "createdAt");
CREATE INDEX "Embedding_entityType_modelName_createdAt_idx" ON "Embedding" ("entityType", "modelName", "createdAt");
CREATE INDEX "Embedding_jobId_idx" ON "Embedding" ("jobId");
CREATE INDEX "Embedding_resumeId_idx" ON "Embedding" ("resumeId");
CREATE INDEX "Embedding_userId_idx" ON "Embedding" ("userId");
CREATE INDEX "Embedding_alertId_idx" ON "Embedding" ("alertId");
CREATE INDEX "ResumeAnalysis_userId_createdAt_idx" ON "ResumeAnalysis" ("userId", "createdAt");
CREATE INDEX "ResumeAnalysis_resumeId_createdAt_idx" ON "ResumeAnalysis" ("resumeId", "createdAt");
CREATE INDEX "Interview_applicationId_scheduledAt_idx" ON "Interview" ("applicationId", "scheduledAt");
CREATE INDEX "ApplicationStatusHistory_applicationId_changedAt_idx" ON "ApplicationStatusHistory" ("applicationId", "changedAt");
CREATE INDEX "UserNote_userId_updatedAt_idx" ON "UserNote" ("userId", "updatedAt");
CREATE INDEX "ScrapeRun_sourceType_createdAt_idx" ON "ScrapeRun" ("sourceType", "createdAt");
CREATE INDEX "ScrapeRun_status_createdAt_idx" ON "ScrapeRun" ("status", "createdAt");
CREATE INDEX "JobScrapeEvent_jobId_createdAt_idx" ON "JobScrapeEvent" ("jobId", "createdAt");
CREATE INDEX "JobScrapeEvent_scrapeRunId_createdAt_idx" ON "JobScrapeEvent" ("scrapeRunId", "createdAt");
CREATE INDEX "AlertDelivery_alertId_deliveredAt_idx" ON "AlertDelivery" ("alertId", "deliveredAt");
CREATE INDEX "AlertDelivery_userId_deliveredAt_idx" ON "AlertDelivery" ("userId", "deliveredAt");
CREATE INDEX "RecommendationLog_userId_requestedAt_idx" ON "RecommendationLog" ("userId", "requestedAt");

-- Search/vector indexes
CREATE INDEX "Embedding_vector_ivfflat_idx"
ON "Embedding" USING ivfflat ("vector" vector_cosine_ops) WITH (lists = 200);

CREATE INDEX "Job_searchTsv_gin_idx" ON "Job" USING GIN ("searchTsv");
CREATE INDEX "Job_keywords_gin_idx" ON "Job" USING GIN ("keywords");
CREATE INDEX "Job_techStack_gin_idx" ON "Job" USING GIN ("techStack");
