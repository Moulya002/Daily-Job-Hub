import { PageHeader } from "@/components/common/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function JobDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <section className="space-y-6">
      <PageHeader title="Job Details" description="Detailed requirements, skills, and tailored AI actions." />
      <Card>
        <CardHeader>
          <CardTitle>Job ID: {id}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-400">Connect this page to a dedicated `/jobs/:id` API endpoint for full description and matching insights.</p>
        </CardContent>
      </Card>
    </section>
  );
}
