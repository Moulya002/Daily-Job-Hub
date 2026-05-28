import { auth } from "@/auth";
import { JobCard } from "@/components/common/job-card";
import { MetricCard } from "@/components/common/metric-card";
import { PageHeader } from "@/components/common/page-header";
import { getRecommendations } from "@/lib/api";

export default async function DashboardPage() {
  const session = await auth();
  const userId = session?.user?.id ?? "";
  const recommendations = userId ? await getRecommendations(userId) : [];

  return (
    <section className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Track your pipeline, deadlines, and AI-ranked opportunities in one place."
      />
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Saved Jobs" value="42" helper="+6 this week" />
        <MetricCard label="Applied" value="13" helper="5 awaiting response" />
        <MetricCard label="Interviews" value="4" helper="2 scheduled" />
        <MetricCard label="Offer Rate" value="8%" helper="based on total applications" />
      </div>
      <div className="space-y-3">
        <h2 className="text-lg font-semibold">Recommended for you</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {recommendations.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      </div>
    </section>
  );
}
