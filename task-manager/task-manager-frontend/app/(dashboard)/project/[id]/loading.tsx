import { LoadingSkeleton } from "@/components/ui/loading-skeleton";

export default function ProjectLoading() {
  return (
    <section className="stack-lg">
      <LoadingSkeleton className="h-36 w-full" />
      <LoadingSkeleton className="h-64 w-full" />
      <LoadingSkeleton className="h-80 w-full" />
    </section>
  );
}
