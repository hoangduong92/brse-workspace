import { AppLayout } from "@/components/layout/app-layout";
import { ReportsContent } from "@/components/reports/reports-content";

export default function ReportsPage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "Backlog UI Pro", href: "/" },
        { label: "Reports" },
      ]}
    >
      <ReportsContent />
    </AppLayout>
  );
}
