import { MarketingHeader } from "../../components/layout/marketing-header";

export default async function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <MarketingHeader />
      <div className="mx-auto max-w-7xl px-4 py-8 md:px-6">{children}</div>
    </div>
  );
}
