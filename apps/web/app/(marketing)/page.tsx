import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  "AI semantic job search",
  "Resume match scoring with missing skills",
  "Application tracker with deadlines",
  "Cover letter and recruiter message generation"
];

export default function LandingPage() {
  return (
    <section className="space-y-10 py-6 md:py-12">
      <div className="space-y-4">
        <p className="text-sm text-blue-300">Built for internships + new grad recruiting</p>
        <h1 className="max-w-4xl text-4xl font-bold tracking-tight md:text-5xl">
          One platform to discover jobs, optimize your resume, and track every application.
        </h1>
        <p className="max-w-2xl text-slate-300">
          Daily Job Hub combines scraping, semantic search, and AI guidance to help you land opportunities faster.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link href="/jobs">
            <Button>Browse Jobs</Button>
          </Link>
          <Link href="/search">
            <Button variant="outline">Try AI Search</Button>
          </Link>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {features.map((feature) => (
          <Card key={feature}>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{feature}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-400">Production-ready architecture with scalable APIs, queues, and vector retrieval.</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
