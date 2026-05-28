import Link from "next/link";
import type { JobListItem } from "@daily-job-hub/types";

import { JobActions } from "@/components/common/job-actions";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function JobCard({ job }: { job: JobListItem }) {
  return (
    <Card className="transition hover:border-slate-700">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="text-base">{job.title}</CardTitle>
          <Badge variant="secondary">{job.workMode ?? "FLEX"}</Badge>
        </div>
        <p className="text-sm text-slate-400">
          {job.companyName} · {job.location ?? "Location flexible"}
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-slate-300">{job.summary}</p>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <Link href={`/jobs/${job.id}`} className="text-sm text-blue-400 hover:text-blue-300">
            View details
          </Link>
          <JobActions jobId={job.id} />
        </div>
      </CardContent>
    </Card>
  );
}
