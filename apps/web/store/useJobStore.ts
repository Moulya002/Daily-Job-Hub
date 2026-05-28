import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { JobListItem } from "@daily-job-hub/types";

type JobState = {
  savedJobIds: string[];
  appliedJobIds: string[];
  jobs: JobListItem[];
  setJobs: (jobs: JobListItem[]) => void;
  setSavedJobIds: (jobIds: string[]) => void;
  setAppliedJobIds: (jobIds: string[]) => void;
  toggleSaveJob: (jobId: string) => void;
  toggleAppliedJob: (jobId: string) => void;
};

export const useJobStore = create<JobState>()(
  persist(
    (set) => ({
      savedJobIds: [],
      appliedJobIds: [],
      jobs: [],
      setJobs: (jobs) => set({ jobs }),
      setSavedJobIds: (jobIds) => set({ savedJobIds: jobIds }),
      setAppliedJobIds: (jobIds) => set({ appliedJobIds: jobIds }),
      toggleSaveJob: (jobId) =>
        set((state) => ({
          savedJobIds: state.savedJobIds.includes(jobId)
            ? state.savedJobIds.filter((id) => id !== jobId)
            : [...state.savedJobIds, jobId]
        })),
      toggleAppliedJob: (jobId) =>
        set((state) => ({
          appliedJobIds: state.appliedJobIds.includes(jobId)
            ? state.appliedJobIds.filter((id) => id !== jobId)
            : [...state.appliedJobIds, jobId]
        }))
    }),
    {
      name: "daily-job-hub-store"
    }
  )
);
