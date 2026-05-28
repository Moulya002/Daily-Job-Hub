import { PageHeader } from "@/components/common/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AdminScrapersPage() {
  return (
    <section className="space-y-6">
      <PageHeader title="Scraper Monitoring" description="Observe source freshness, failure rates, and ingestion throughput." />
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Greenhouse</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xl font-semibold">98%</p>
            <p className="text-xs text-slate-500">Success over last 24h</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Lever</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xl font-semibold">95%</p>
            <p className="text-xs text-slate-500">Success over last 24h</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Ashby</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xl font-semibold">91%</p>
            <p className="text-xs text-slate-500">Success over last 24h</p>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
