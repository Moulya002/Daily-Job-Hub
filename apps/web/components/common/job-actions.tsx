"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";

import { applyJob, saveJob, unapplyJob, unsaveJob } from "@/lib/client-api";
import { Button } from "@/components/ui/button";
import { useJobStore } from "@/store/useJobStore";

export function JobActions({ jobId }: { jobId: string }) {
  const { data: session, status } = useSession();
  const savedJobIds = useJobStore((state) => state.savedJobIds);
  const appliedJobIds = useJobStore((state) => state.appliedJobIds);
  const toggleSaveJob = useJobStore((state) => state.toggleSaveJob);
  const toggleAppliedJob = useJobStore((state) => state.toggleAppliedJob);
  const [isSaving, setIsSaving] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const isSignedIn = Boolean(session?.user);
  const isSaved = savedJobIds.includes(jobId);
  const isApplied = appliedJobIds.includes(jobId);

  const requireSignIn = (): boolean => {
    if (isSignedIn) return true;
    setMessage("Sign in with GitHub to save and track applications.");
    const params = new URLSearchParams({ callbackUrl: "/jobs" });
    window.location.assign(`/api/auth/signin/github?${params.toString()}`);
    return false;
  };

  const onSaveToggle = async () => {
    if (isSaving || status === "loading") return;
    if (!requireSignIn()) return;

    setIsSaving(true);
    setMessage(null);
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
      setMessage("Could not update saved jobs. Try again.");
    } finally {
      setIsSaving(false);
    }
  };

  const onApplyToggle = async () => {
    if (isApplying || status === "loading") return;
    if (!requireSignIn()) return;

    setIsApplying(true);
    setMessage(null);
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
      setMessage("Could not update application status. Try again.");
    } finally {
      setIsApplying(false);
    }
  };

  return (
    <div className="flex flex-col items-end gap-1">
      <div className="flex gap-2">
        <Button variant={isSaved ? "secondary" : "outline"} size="sm" onClick={onSaveToggle} disabled={isSaving}>
          {isSaved ? "Saved" : "Save"}
        </Button>
        <Button variant={isApplied ? "secondary" : "default"} size="sm" onClick={onApplyToggle} disabled={isApplying}>
          {isApplied ? "Applied" : "Mark Applied"}
        </Button>
      </div>
      {message ? <p className="max-w-[14rem] text-right text-xs text-amber-400">{message}</p> : null}
      {!isSignedIn && status !== "loading" ? (
        <p className="text-right text-xs text-slate-500">Sign in to sync across devices</p>
      ) : null}
    </div>
  );
}
