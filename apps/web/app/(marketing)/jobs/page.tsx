import { JobCard } from "@/components/common/job-card";
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
      <div className="grid gap-4 md:grid-cols-2">
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </div>
    </section>
  );
}
