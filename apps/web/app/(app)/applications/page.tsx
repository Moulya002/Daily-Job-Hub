import { JobsStateHydrator } from "@/components/common/jobs-state-hydrator";
import { PageHeader } from "@/components/common/page-header";
import { ApplicationsClient } from "@/components/common/applications-client";
import { getJobs } from "@/lib/api";

export default async function ApplicationsPage() {
  const jobs = await getJobs();

  return (
    <section className="space-y-6">
      <JobsStateHydrator jobs={jobs} />
      <PageHeader title="Applications" description="Track every stage from saved to offer with notes and reminders." />
      <ApplicationsClient />
    </section>
  );
}
