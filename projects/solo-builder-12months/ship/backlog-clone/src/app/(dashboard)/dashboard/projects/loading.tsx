import { SkeletonCard } from '@/components/ui/skeleton'

export default function ProjectsLoading() {
  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="h-9 w-40 bg-gray-200 rounded animate-pulse-slow mb-2" />
          <div className="h-5 w-64 bg-gray-200 rounded animate-pulse-slow" />
        </div>
        <div className="h-10 w-32 bg-gray-200 rounded-lg animate-pulse-slow" />
      </div>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  )
}
