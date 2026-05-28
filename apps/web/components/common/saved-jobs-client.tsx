"use client";

import { useMemo } from "react";

import { EmptyState } from "@/components/common/empty-state";
import { JobCard } from "@/components/common/job-card";
import { useJobStore } from "@/store/useJobStore";

export function SavedJobsClient() {
  const jobs = useJobStore((state) => state.jobs);
  const savedJobIds = useJobStore((state) => state.savedJobIds);

  const savedJobs = useMemo(() => jobs.filter((job) => savedJobIds.includes(job.id)), [jobs, savedJobIds]);

  if (!savedJobs.length) {
    return (
      <EmptyState
        title="No saved jobs yet"
        description="Save jobs from listings or AI search to track them here with deadlines and personalized reminders."
      />
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {savedJobs.map((job) => (
        <JobCard key={job.id} job={job} />
      ))}
    </div>
  );
}
