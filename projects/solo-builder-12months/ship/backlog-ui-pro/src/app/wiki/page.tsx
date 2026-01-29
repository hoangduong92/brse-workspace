import { AppLayout } from "@/components/layout/app-layout";
import { WikiContent } from "@/components/wiki/wiki-content";

export default function WikiPage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "Backlog UI Pro", href: "/" },
        { label: "Wiki" },
      ]}
    >
      <WikiContent />
    </AppLayout>
  );
}
