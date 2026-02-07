import { FlaskConical } from "lucide-react";
import { DEMO_MODE } from "@/lib/config";
import { cn } from "@/lib/utils";

export function DemoModeBadge({ compact = false }: { compact?: boolean }) {
  if (!DEMO_MODE) {
    return null;
  }

  return (
    <span className={cn("demo-badge", compact && "compact")}>
      <FlaskConical size={compact ? 12 : 14} />
      DemoMode
    </span>
  );
}
