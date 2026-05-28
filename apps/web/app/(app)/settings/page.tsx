import { PageHeader } from "@/components/common/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  return (
    <section className="space-y-6">
      <PageHeader title="Settings" description="Manage profile, alert channels, and recommendation preferences." />
      <Card>
        <CardHeader>
          <CardTitle>Job Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Input placeholder="Target roles (e.g. Backend, AI Engineer)" />
          <Input placeholder="Preferred locations" />
          <Button variant="secondary">Save preferences</Button>
        </CardContent>
      </Card>
    </section>
  );
}
