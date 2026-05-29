import { JobsBrowser } from "@/components/common/jobs-browser";
import { PageHeader } from "@/components/common/page-header";
import { getJobs } from "@/lib/api";
import { JobsStateHydrator } from "@/components/common/jobs-state-hydrator";

export default async function JobsPage() {
  const jobs = await getJobs();

  return (
    <section className="space-y-6">
      <JobsStateHydrator jobs={jobs} />
      <PageHeader
        title="Internship and New Grad Jobs"
        description="Fresh listings from Greenhouse, Lever, Ashby, YC Jobs, and curated company career pages."
      />
      <JobsBrowser jobs={jobs} />
    </section>
  );
}
