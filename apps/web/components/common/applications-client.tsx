"use client";

import { useMemo } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useJobStore } from "@/store/useJobStore";

export function ApplicationsClient() {
  const jobs = useJobStore((state) => state.jobs);
  const appliedJobIds = useJobStore((state) => state.appliedJobIds);

  const appliedJobs = useMemo(() => jobs.filter((job) => appliedJobIds.includes(job.id)), [jobs, appliedJobIds]);

  if (!appliedJobs.length) {
    return <p className="text-sm text-slate-400">No applications tracked yet. Mark a job as applied from listings.</p>;
  }

  return (
    <div className="grid gap-4">
      {appliedJobs.map((job) => (
        <Card key={job.id}>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">{job.title}</CardTitle>
            <p className="text-sm text-slate-400">{job.companyName}</p>
          </CardHeader>
          <CardContent className="flex items-center justify-between">
            <Badge variant="secondary">APPLIED</Badge>
            <p className="text-sm text-slate-400">{job.location ?? "Location flexible"}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
