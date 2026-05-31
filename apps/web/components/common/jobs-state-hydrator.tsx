"use client";

import { useEffect } from "react";
import { useSession } from "next-auth/react";
import type { JobListItem } from "@daily-job-hub/types";

import { fetchAppliedJobIds, fetchSavedJobIds } from "@/lib/client-api";
import { useJobStore } from "@/store/useJobStore";

export function JobsStateHydrator({ jobs }: { jobs: JobListItem[] }) {
  const { data: session, status } = useSession();
  const setJobs = useJobStore((state) => state.setJobs);
  const setSavedJobIds = useJobStore((state) => state.setSavedJobIds);
  const setAppliedJobIds = useJobStore((state) => state.setAppliedJobIds);

  useEffect(() => {
    setJobs(jobs);
  }, [jobs, setJobs]);

  useEffect(() => {
    if (status !== "authenticated" || !session?.user) {
      setSavedJobIds([]);
      setAppliedJobIds([]);
      return;
    }

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
  }, [session?.user, setAppliedJobIds, setSavedJobIds, status]);

  return null;
}
