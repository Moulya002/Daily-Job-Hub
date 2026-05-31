import { PageHeader } from "@/components/common/page-header";
import { JobsStateHydrator } from "@/components/common/jobs-state-hydrator";
import { SavedJobsClient } from "@/components/common/saved-jobs-client";
import { getJobs } from "@/lib/api";

export default async function SavedJobsPage() {
  const jobs = await getJobs({ limit: 100 });

  return (
    <section className="space-y-6">
      <JobsStateHydrator jobs={jobs} />
      <PageHeader
        title="Saved Jobs"
        description="Shortlist roles for follow-up, referrals, and interview preparation."
        actionLabel="Create Alert"
      />
      <SavedJobsClient />
    </section>
  );
}
