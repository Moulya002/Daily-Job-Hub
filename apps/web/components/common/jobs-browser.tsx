"use client";

import { useCallback, useState } from "react";
import type { JobLevel, JobListItem } from "@daily-job-hub/types";

import { JobCard } from "@/components/common/job-card";
import { EmptyState } from "@/components/common/empty-state";
import type { JobLevelCounts } from "@/lib/api";

type LevelFilter = "ALL" | JobLevel;

const LEVELS: { id: LevelFilter; label: string }[] = [
  { id: "ALL", label: "All" },
  { id: "INTERN", label: "Internship" },
  { id: "NEW_GRAD", label: "New Grad" },
  { id: "FULL_TIME", label: "Full-time" },
  { id: "CONTRACT", label: "Contract" }
];

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const PAGE_SIZE = 60;

function Pill({
  active,
  label,
  count,
  onClick,
  disabled
}: {
  active: boolean;
  label: string;
  count: number;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`rounded-full border px-3 py-1 text-sm transition disabled:opacity-50 ${
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

async function fetchJobsForLevel(level: LevelFilter): Promise<JobListItem[]> {
  const params = new URLSearchParams({ limit: String(PAGE_SIZE) });
  if (level !== "ALL") params.set("level", level);
  const response = await fetch(`${API_BASE}/jobs?${params}`);
  if (!response.ok) return [];
  return (await response.json()) as JobListItem[];
}

export function JobsBrowser({
  initialJobs,
  stats
}: {
  initialJobs: JobListItem[];
  stats: JobLevelCounts;
}) {
  const [level, setLevel] = useState<LevelFilter>("ALL");
  const [jobs, setJobs] = useState(initialJobs);
  const [loading, setLoading] = useState(false);

  const onLevelChange = useCallback(async (next: LevelFilter) => {
    setLevel(next);
    setLoading(true);
    try {
      setJobs(await fetchJobsForLevel(next));
    } finally {
      setLoading(false);
    }
  }, []);

  const totalForLevel = stats[level] ?? 0;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-2">
        <span className="mr-1 text-xs uppercase tracking-wide text-slate-500">Level</span>
        {LEVELS.map((l) => (
          <Pill
            key={l.id}
            active={level === l.id}
            label={l.label}
            count={stats[l.id] ?? 0}
            disabled={loading}
            onClick={() => void onLevelChange(l.id)}
          />
        ))}
      </div>

      <p className="text-sm text-slate-400">
        {loading
          ? "Loading…"
          : `Showing ${jobs.length} of ${totalForLevel.toLocaleString()} roles (newest first)`}
      </p>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-40 animate-pulse rounded-xl border border-slate-800 bg-slate-900/40" />
          ))}
        </div>
      ) : jobs.length === 0 ? (
        <EmptyState title="No jobs at this level yet" description="Try a different level." />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </div>
  );
}
