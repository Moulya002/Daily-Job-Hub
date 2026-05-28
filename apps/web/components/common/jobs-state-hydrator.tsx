"use client";

import { useEffect } from "react";
import type { JobListItem } from "@daily-job-hub/types";

import { fetchAppliedJobIds, fetchSavedJobIds } from "@/lib/client-api";
import { useJobStore } from "@/store/useJobStore";

export function JobsStateHydrator({ jobs }: { jobs: JobListItem[] }) {
  const setJobs = useJobStore((state) => state.setJobs);
  const setSavedJobIds = useJobStore((state) => state.setSavedJobIds);
  const setAppliedJobIds = useJobStore((state) => state.setAppliedJobIds);

  useEffect(() => {
    setJobs(jobs);
  }, [jobs, setJobs]);

  useEffect(() => {
    let isMounted = true;
    const syncUserState = async () => {
      const [saved, applied] = await Promise.all([fetchSavedJobIds(), fetchAppliedJobIds()]);
      if (!isMounted) return;
      setSavedJobIds(saved);
      setAppliedJobIds(applied);
    };
    void syncUserState();
    return () => {
      isMounted = false;
    };
  }, [setAppliedJobIds, setSavedJobIds]);

  return null;
}
