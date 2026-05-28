"use client";

import { useState } from "react";

import { applyJob, saveJob, unapplyJob, unsaveJob } from "@/lib/client-api";
import { Button } from "@/components/ui/button";
import { useJobStore } from "@/store/useJobStore";

export function JobActions({ jobId }: { jobId: string }) {
  const savedJobIds = useJobStore((state) => state.savedJobIds);
  const appliedJobIds = useJobStore((state) => state.appliedJobIds);
  const toggleSaveJob = useJobStore((state) => state.toggleSaveJob);
  const toggleAppliedJob = useJobStore((state) => state.toggleAppliedJob);
  const [isSaving, setIsSaving] = useState(false);
  const [isApplying, setIsApplying] = useState(false);

  const isSaved = savedJobIds.includes(jobId);
  const isApplied = appliedJobIds.includes(jobId);

  const onSaveToggle = async () => {
    if (isSaving) return;
    setIsSaving(true);
    const wasSaved = isSaved;
    toggleSaveJob(jobId);
    try {
      if (wasSaved) {
        await unsaveJob(jobId);
      } else {
        await saveJob(jobId);
      }
    } catch {
      toggleSaveJob(jobId);
    } finally {
      setIsSaving(false);
    }
  };

  const onApplyToggle = async () => {
    if (isApplying) return;
    setIsApplying(true);
    const wasApplied = isApplied;
    toggleAppliedJob(jobId);
    try {
      if (wasApplied) {
        await unapplyJob(jobId);
      } else {
        await applyJob(jobId);
      }
    } catch {
      toggleAppliedJob(jobId);
    } finally {
      setIsApplying(false);
    }
  };

  return (
    <div className="flex gap-2">
      <Button variant={isSaved ? "secondary" : "outline"} size="sm" onClick={onSaveToggle} disabled={isSaving}>
        {isSaved ? "Saved" : "Save"}
      </Button>
      <Button variant={isApplied ? "secondary" : "default"} size="sm" onClick={onApplyToggle} disabled={isApplying}>
        {isApplied ? "Applied" : "Mark Applied"}
      </Button>
    </div>
  );
}
