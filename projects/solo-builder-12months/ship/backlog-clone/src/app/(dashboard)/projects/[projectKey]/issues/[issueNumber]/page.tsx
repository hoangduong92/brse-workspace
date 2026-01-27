'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { getProject } from '@/lib/api/projects'
import { getIssue } from '@/lib/api/issues'
import { getComments, createComment } from '@/lib/api/comments'
import { IssueDetail } from '@/components/issues/issue-detail'
import { CommentList } from '@/components/issues/comment-list'
import { CommentForm } from '@/components/issues/comment-form'
import { createClient } from '@/lib/supabase/client'

export default function IssueDetailPage() {
  const params = useParams()
  const projectKey = params.projectKey as string
  const issueNumber = Number(params.issueNumber)

  const [project, setProject] = useState<any>(null)
  const [issue, setIssue] = useState<any>(null)
  const [comments, setComments] = useState<any[]>([])
  const [members, setMembers] = useState<any[]>([])
  const [currentUserId, setCurrentUserId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadData()
    loadCurrentUser()
  }, [projectKey, issueNumber])

  const loadCurrentUser = async () => {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()
    setCurrentUserId(user?.id || null)
  }

  const loadData = async () => {
    try {
      setIsLoading(true)
      const projectData = await getProject(projectKey)
      setProject(projectData)

      const issueData = await getIssue(projectKey, issueNumber)
      setIssue(issueData)

      const commentsData = await getComments(issueData.id)
      setComments(commentsData)

      // TODO: Load project members from API
      // For now using empty array
      setMembers([])
    } catch (error) {
      console.error('Failed to load data:', error)
      alert('Failed to load data')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddComment = async (content: string) => {
    try {
      await createComment(issue.id, content)
      await loadData()
    } catch (error) {
      console.error('Failed to add comment:', error)
      throw error
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  if (!project || !issue) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Issue not found</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-6 py-8 max-w-5xl">
      {/* Header */}
      <div className="mb-8">
        <div className="text-sm text-gray-500 mb-1">
          <Link href={`/projects/${projectKey}`} className="hover:underline">
            {project.name}
          </Link>
          {' / '}
          <Link href={`/projects/${projectKey}/issues`} className="hover:underline">
            Issues
          </Link>
          {' / '}
          <span>{projectKey}-{issueNumber}</span>
        </div>
      </div>

      {/* Issue Detail */}
      <div className="mb-8">
        <IssueDetail
          issue={issue}
          projectKey={projectKey}
          statuses={project.statuses || []}
          types={project.issue_types || []}
          members={members}
          onUpdate={loadData}
        />
      </div>

      {/* Comments Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Comments ({comments.length})
        </h2>

        <div className="space-y-6">
          <CommentList
            comments={comments}
            currentUserId={currentUserId || undefined}
            onUpdate={loadData}
          />

          <div className="pt-4 border-t border-gray-200">
            <CommentForm onSubmit={handleAddComment} />
          </div>
        </div>
      </div>
    </div>
  )
}
