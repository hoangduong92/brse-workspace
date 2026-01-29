import { AppLayout } from "@/components/layout/app-layout";
import { BoardContent } from "@/components/board/board-content";

export default function BoardPage() {
  return (
    <AppLayout
      breadcrumbs={[
        { label: "Backlog UI Pro", href: "/" },
        { label: "Board" },
      ]}
    >
      <BoardContent />
    </AppLayout>
  );
}
