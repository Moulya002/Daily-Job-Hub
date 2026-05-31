import type { JobListItem, SemanticSearchResult } from "@daily-job-hub/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type JobLevelCounts = {
  ALL: number;
  INTERN: number;
  NEW_GRAD: number;
  FULL_TIME: number;
  CONTRACT: number;
};

export async function getJobStats(): Promise<JobLevelCounts> {
  const response = await fetch(`${API_BASE_URL}/jobs/stats`, {
    next: { revalidate: 300 }
  });
  if (!response.ok) {
    return { ALL: 0, INTERN: 0, NEW_GRAD: 0, FULL_TIME: 0, CONTRACT: 0 };
  }
  return (await response.json()) as JobLevelCounts;
}

export async function getJobs(options?: {
  level?: string;
  limit?: number;
}): Promise<JobListItem[]> {
  const params = new URLSearchParams();
  params.set("limit", String(options?.limit ?? 60));
  if (options?.level && options.level !== "ALL") {
    params.set("level", options.level);
  }
  const response = await fetch(`${API_BASE_URL}/jobs?${params}`, {
    cache: "no-store"
  });
  if (!response.ok) return [];
  return (await response.json()) as JobListItem[];
}

export async function semanticSearch(query: string): Promise<SemanticSearchResult[]> {
  const response = await fetch(`${API_BASE_URL}/search?query=${encodeURIComponent(query)}`, {
    next: { revalidate: 120 }
  });
  if (!response.ok) return [];
  return (await response.json()) as SemanticSearchResult[];
}

export async function getSavedJobsForUser(userId: string): Promise<JobListItem[]> {
  const response = await fetch(
    `${API_BASE_URL}/users/${encodeURIComponent(userId)}/saved-jobs/jobs`,
    { cache: "no-store" }
  );
  if (!response.ok) return [];
  return (await response.json()) as JobListItem[];
}

export async function getAppliedJobsForUser(userId: string): Promise<JobListItem[]> {
  const response = await fetch(
    `${API_BASE_URL}/users/${encodeURIComponent(userId)}/applications/jobs`,
    { cache: "no-store" }
  );
  if (!response.ok) return [];
  return (await response.json()) as JobListItem[];
}

export async function getRecommendations(userId: string): Promise<JobListItem[]> {
  const response = await fetch(`${API_BASE_URL}/recommendations?user_id=${encodeURIComponent(userId)}`, {
    next: { revalidate: 300 }
  });
  if (!response.ok) return [];
  return (await response.json()) as JobListItem[];
}
