"use client";

import { useMemo, useState } from "react";
import type { JobCategory, JobLevel, JobListItem } from "@daily-job-hub/types";

import { JobCard } from "@/components/common/job-card";
import { EmptyState } from "@/components/common/empty-state";

type LevelFilter = "ALL" | JobLevel;
type CategoryFilter = "ALL" | JobCategory;

const LEVELS: { id: LevelFilter; label: string }[] = [
  { id: "ALL", label: "All" },
  { id: "INTERN", label: "Internship" },
  { id: "NEW_GRAD", label: "New Grad" },
  { id: "FULL_TIME", label: "Full-time" }
];

const CATEGORIES: { id: CategoryFilter; label: string }[] = [
  { id: "ALL", label: "All" },
  { id: "FAANG+", label: "FAANG+" },
  { id: "Quant", label: "Quant" },
  { id: "Other", label: "Other" }
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
  const [category, setCategory] = useState<CategoryFilter>("ALL");

  const byLevel = useMemo(
    () => (level === "ALL" ? jobs : jobs.filter((j) => j.jobType === level)),
    [jobs, level]
  );

  const visible = useMemo(
    () => (category === "ALL" ? byLevel : byLevel.filter((j) => (j.category ?? "Other") === category)),
    [byLevel, category]
  );

  const levelCount = (id: LevelFilter) =>
    id === "ALL" ? jobs.length : jobs.filter((j) => j.jobType === id).length;

  const categoryCount = (id: CategoryFilter) =>
    id === "ALL" ? byLevel.length : byLevel.filter((j) => (j.category ?? "Other") === id).length;

  return (
    <div className="space-y-5">
      <div className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="mr-1 text-xs uppercase tracking-wide text-slate-500">Level</span>
          {LEVELS.map((l) => (
            <Pill
              key={l.id}
              active={level === l.id}
              label={l.label}
              count={levelCount(l.id)}
              onClick={() => setLevel(l.id)}
            />
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="mr-1 text-xs uppercase tracking-wide text-slate-500">Company</span>
          {CATEGORIES.map((c) => (
            <Pill
              key={c.id}
              active={category === c.id}
              label={c.label}
              count={categoryCount(c.id)}
              onClick={() => setCategory(c.id)}
            />
          ))}
        </div>
      </div>

      <p className="text-sm text-slate-400">{visible.length} matching roles</p>

      {visible.length === 0 ? (
        <EmptyState
          title="No jobs match these filters"
          description="Try a different level or company group."
        />
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
