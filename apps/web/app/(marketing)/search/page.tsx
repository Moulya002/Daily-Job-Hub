import { PageHeader } from "@/components/common/page-header";
import { JobCard } from "@/components/common/job-card";
import { SearchForm } from "@/components/common/search-form";
import { JobsStateHydrator } from "@/components/common/jobs-state-hydrator";
import { semanticSearch } from "@/lib/api";

export default async function SearchPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q = "remote AI internships with sponsorship" } = await searchParams;
  const results = await semanticSearch(q);

  return (
    <section className="space-y-6">
      <JobsStateHydrator jobs={results} />
      <PageHeader title="Semantic AI Search" description={`Query: ${q}`} />
      <SearchForm />
      <div className="grid gap-4 md:grid-cols-2">
        {results.map((result) => (
          <JobCard key={result.id} job={result} />
        ))}
      </div>
    </section>
  );
}
