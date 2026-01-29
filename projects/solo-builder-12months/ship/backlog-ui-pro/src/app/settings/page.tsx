import { AppLayout } from "@/components/layout/app-layout";
import { SettingsContent } from "@/components/settings/settings-content";

export default function SettingsPage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "Backlog UI Pro", href: "/" },
        { label: "Settings" },
      ]}
    >
      <SettingsContent />
    </AppLayout>
  );
}
