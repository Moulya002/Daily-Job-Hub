import { PageHeader } from "@/components/common/page-header";
import { ResumeAnalyzer } from "@/components/common/resume-analyzer";

export default function ResumeAnalysisPage() {
  return (
    <section className="space-y-6">
      <PageHeader title="Resume Analysis" description="Upload your resume and score fit against target roles." />
      <ResumeAnalyzer />
    </section>
  );
}
