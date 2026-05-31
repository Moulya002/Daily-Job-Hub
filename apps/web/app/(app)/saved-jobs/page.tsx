import { auth } from "@/auth";
import { PageHeader } from "@/components/common/page-header";
import { SavedJobsClient } from "@/components/common/saved-jobs-client";
import { getSavedJobsForUser } from "@/lib/api";

export default async function SavedJobsPage() {
  const session = await auth();
  const jobs = session?.user?.id ? await getSavedJobsForUser(session.user.id) : [];

  return (
    <section className="space-y-6">
      <PageHeader
        title="Saved Jobs"
        description="Shortlist roles for follow-up, referrals, and interview preparation."
        actionLabel="Create Alert"
      />
      <SavedJobsClient jobs={jobs} />
    </section>
  );
}
