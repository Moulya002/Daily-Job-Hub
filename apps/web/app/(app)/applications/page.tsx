import { auth } from "@/auth";
import { ApplicationsClient } from "@/components/common/applications-client";
import { PageHeader } from "@/components/common/page-header";
import { getAppliedJobsForUser } from "@/lib/api";

export default async function ApplicationsPage() {
  const session = await auth();
  const jobs = session?.user?.id ? await getAppliedJobsForUser(session.user.id) : [];

  return (
    <section className="space-y-6">
      <PageHeader
        title="Applications"
        description="Track every stage from saved to offer with notes and reminders."
      />
      <ApplicationsClient jobs={jobs} />
    </section>
  );
}
