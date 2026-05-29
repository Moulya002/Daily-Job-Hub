import Link from "next/link";
import type { JobListItem } from "@daily-job-hub/types";

import { JobActions } from "@/components/common/job-actions";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const LEVEL_LABELS: Record<string, string> = {
  INTERN: "Internship",
  NEW_GRAD: "New Grad",
  FULL_TIME: "Full-time",
  CONTRACT: "Contract"
};

function formatSalary(min?: number | null, max?: number | null, currency?: string | null): string | null {
  if (!min && !max) return null;
  const symbol = currency === "USD" || !currency ? "$" : `${currency} `;
  const k = (n: number) => `${symbol}${Math.round(n / 1000)}k`;
  if (min && max) return min === max ? `${k(min)}/yr` : `${k(min)}–${k(max)}/yr`;
  return `${k((min ?? max) as number)}/yr`;
}

function formatAge(postedAt?: string | null): string | null {
  if (!postedAt) return null;
  const posted = new Date(postedAt).getTime();
  if (Number.isNaN(posted)) return null;
  const days = Math.floor((Date.now() - posted) / 86_400_000);
  if (days <= 0) return "Today";
  if (days === 1) return "1d ago";
  return `${days}d ago`;
}

export function JobCard({ job }: { job: JobListItem }) {
  const salary = formatSalary(job.salaryMin, job.salaryMax, job.currency);
  const age = formatAge(job.postedAt);
  const level = job.jobType ? LEVEL_LABELS[job.jobType] ?? job.jobType : null;

  return (
    <Card className="transition hover:border-slate-700">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-base">{job.title}</CardTitle>
          <Badge variant="secondary">{job.workMode ?? "FLEX"}</Badge>
        </div>
        <p className="text-sm text-slate-400">
          {job.companyName} · {job.location ?? "Location flexible"}
        </p>
        <div className="flex flex-wrap items-center gap-2 pt-1">
          {job.category && job.category !== "Other" && (
            <Badge variant="default">{job.category}</Badge>
          )}
          {level && <Badge variant="outline">{level}</Badge>}
          {salary && <span className="text-sm font-medium text-emerald-400">{salary}</span>}
          {age && <span className="text-xs text-slate-500">{age}</span>}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-slate-300">{job.summary}</p>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-3">
            <Link href={`/jobs/${job.id}`} className="text-sm text-blue-400 hover:text-blue-300">
              View details
            </Link>
            {job.applyUrl && (
              <a
                href={job.applyUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium text-blue-400 hover:text-blue-300"
              >
                Apply ↗
              </a>
            )}
          </div>
          <JobActions jobId={job.id} />
        </div>
      </CardContent>
    </Card>
  );
}
