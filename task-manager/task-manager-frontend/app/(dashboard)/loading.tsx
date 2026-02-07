import { LoadingSkeleton } from "@/components/ui/loading-skeleton";

export default function DashboardLoading() {
  return (
    <section className="stack-lg">
      <LoadingSkeleton className="h-20 w-full" />
      <div className="grid-4">
        <LoadingSkeleton className="h-28 w-full" />
        <LoadingSkeleton className="h-28 w-full" />
        <LoadingSkeleton className="h-28 w-full" />
        <LoadingSkeleton className="h-28 w-full" />
      </div>
      <div className="grid-2">
        <LoadingSkeleton className="h-[420px] w-full" />
        <LoadingSkeleton className="h-[420px] w-full" />
      </div>
    </section>
  );
}
