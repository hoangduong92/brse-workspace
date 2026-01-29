import { AppLayout } from "@/components/layout/app-layout";
import { MembersContent } from "@/components/members/members-content";

export default function MembersPage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "Backlog UI Pro", href: "/" },
        { label: "Members" },
      ]}
    >
      <MembersContent />
    </AppLayout>
  );
}
