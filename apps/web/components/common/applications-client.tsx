"use client";

import type { JobListItem } from "@daily-job-hub/types";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function ApplicationsClient({ jobs }: { jobs: JobListItem[] }) {
  if (!jobs.length) {
    return (
      <p className="text-sm text-slate-400">
        No applications tracked yet. Mark a job as applied from listings (requires sign-in).
      </p>
    );
  }

  return (
    <div className="grid gap-4">
      {jobs.map((job) => (
        <Card key={job.id}>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">{job.title}</CardTitle>
            <p className="text-sm text-slate-400">
              {job.companyName} · {job.location ?? "Location flexible"}
            </p>
          </CardHeader>
          <CardContent className="flex items-center justify-between">
            <Badge variant="secondary">APPLIED</Badge>
            {job.applyUrl ? (
              <a
                href={job.applyUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-400 hover:text-blue-300"
              >
                View posting ↗
              </a>
            ) : null}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
