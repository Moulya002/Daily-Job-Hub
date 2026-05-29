import type { JobListItem, SemanticSearchResult } from "@daily-job-hub/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function getJobs(): Promise<JobListItem[]> {
  const response = await fetch(`${API_BASE_URL}/jobs?limit=5000`, {
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

export async function getRecommendations(userId: string): Promise<JobListItem[]> {
  const response = await fetch(`${API_BASE_URL}/recommendations?user_id=${encodeURIComponent(userId)}`, {
    next: { revalidate: 300 }
  });
  if (!response.ok) return [];
  return (await response.json()) as JobListItem[];
}
