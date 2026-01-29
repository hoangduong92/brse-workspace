import { AppLayout } from "@/components/layout/app-layout";
import { IssuesPageContent } from "@/components/issues/issues-page-content";

export default function IssuesPage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "Backlog UI Pro", href: "/" },
        { label: "Issues" },
      ]}
    >
      <IssuesPageContent />
    </AppLayout>
  );
}
