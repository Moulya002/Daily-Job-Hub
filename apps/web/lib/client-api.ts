type SavedJobItem = { job_id: string };
type ApplicationItem = { job_id: string; status: string };

export async function saveJob(jobId: string): Promise<void> {
  const response = await fetch(`/api/jobs/${jobId}/save`, {
    method: "POST"
  });
  if (!response.ok) {
    throw new Error("Failed to save job.");
  }
}

export async function unsaveJob(jobId: string): Promise<void> {
  const response = await fetch(`/api/jobs/${jobId}/save`, {
    method: "DELETE"
  });
  if (!response.ok) {
    throw new Error("Failed to unsave job.");
  }
}

export async function applyJob(jobId: string): Promise<void> {
  const response = await fetch(`/api/jobs/${jobId}/apply`, {
    method: "POST"
  });
  if (!response.ok) {
    throw new Error("Failed to mark job as applied.");
  }
}

export async function unapplyJob(jobId: string): Promise<void> {
  const response = await fetch(`/api/jobs/${jobId}/apply`, {
    method: "DELETE"
  });
  if (!response.ok) {
    throw new Error("Failed to unmark application.");
  }
}

export async function fetchSavedJobIds(): Promise<string[]> {
  const response = await fetch("/api/user-activity/saved-jobs");
  if (!response.ok) return [];
  const payload = (await response.json()) as SavedJobItem[];
  return payload.map((item) => item.job_id);
}

export async function fetchAppliedJobIds(): Promise<string[]> {
  const response = await fetch("/api/user-activity/applications");
  if (!response.ok) return [];
  const payload = (await response.json()) as ApplicationItem[];
  return payload.map((item) => item.job_id);
}
