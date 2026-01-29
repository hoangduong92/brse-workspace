import { AppLayout } from "@/components/layout/app-layout";
import { DashboardContent } from "@/components/dashboard/dashboard-content";

export default function HomePage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "Backlog UI Pro", href: "/" },
        { label: "Dashboard" },
      ]}
    >
      <DashboardContent />
    </AppLayout>
  );
}
