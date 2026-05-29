"use client";

import { useMemo, useState } from "react";
import type { JobLevel, JobListItem } from "@daily-job-hub/types";

import { JobCard } from "@/components/common/job-card";
import { EmptyState } from "@/components/common/empty-state";

type LevelFilter = "ALL" | JobLevel;

const LEVELS: { id: LevelFilter; label: string }[] = [
  { id: "ALL", label: "All" },
  { id: "INTERN", label: "Internship" },
  { id: "NEW_GRAD", label: "New Grad" },
  { id: "FULL_TIME", label: "Full-time" },
  { id: "CONTRACT", label: "Contract" }
];

function Pill({
  active,
  label,
  count,
  onClick
}: {
  active: boolean;
  label: string;
  count: number;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full border px-3 py-1 text-sm transition ${
        active
          ? "border-blue-500 bg-blue-600 text-white"
          : "border-slate-700 text-slate-300 hover:border-slate-500"
      }`}
    >
      {label}
      <span className={`ml-1.5 text-xs ${active ? "text-blue-100" : "text-slate-500"}`}>{count}</span>
    </button>
  );
}

export function JobsBrowser({ jobs }: { jobs: JobListItem[] }) {
  const [level, setLevel] = useState<LevelFilter>("ALL");

  const counts = useMemo(() => {
    const c: Record<string, number> = { ALL: jobs.length };
    for (const job of jobs) {
      const key = job.jobType ?? "UNKNOWN";
      c[key] = (c[key] ?? 0) + 1;
    }
    return c;
  }, [jobs]);

  const visible = useMemo(
    () => (level === "ALL" ? jobs : jobs.filter((j) => j.jobType === level)),
    [jobs, level]
  );

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2">
        <span className="mr-1 text-xs uppercase tracking-wide text-slate-500">Level</span>
        {LEVELS.map((l) => (
          <Pill
            key={l.id}
            active={level === l.id}
            label={l.label}
            count={counts[l.id] ?? 0}
            onClick={() => setLevel(l.id)}
          />
        ))}
      </div>

      <p className="text-sm text-slate-400">{visible.length} matching roles</p>

      {visible.length === 0 ? (
        <EmptyState title="No jobs at this level yet" description="Try a different level." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {visible.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </div>
  );
}
