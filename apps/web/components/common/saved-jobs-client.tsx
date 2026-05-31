"use client";

import type { JobListItem } from "@daily-job-hub/types";

import { EmptyState } from "@/components/common/empty-state";
import { JobCard } from "@/components/common/job-card";

export function SavedJobsClient({ jobs }: { jobs: JobListItem[] }) {
  if (!jobs.length) {
    return (
      <EmptyState
        title="No saved jobs yet"
        description="Save jobs from listings or AI search to track them here with deadlines and personalized reminders."
      />
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {jobs.map((job) => (
        <JobCard key={job.id} job={job} />
      ))}
    </div>
  );
}
