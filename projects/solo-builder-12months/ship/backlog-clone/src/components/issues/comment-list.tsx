'use client'

import { useState } from 'react'
import { updateComment, deleteComment } from '@/lib/api/comments'

interface Comment {
  id: number
  content: string
  created_at: string
  updated_at: string
  user: {
    id: string
    full_name: string | null
    avatar_url: string | null
  } | null
}

interface CommentListProps {
  comments: Comment[]
  currentUserId?: string
  onUpdate?: () => void
}

export function CommentList({ comments, currentUserId, onUpdate }: CommentListProps) {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editContent, setEditContent] = useState('')
  const [isUpdating, setIsUpdating] = useState(false)

  const handleEdit = (comment: Comment) => {
    setEditingId(comment.id)
    setEditContent(comment.content)
  }

  const handleSave = async (commentId: number) => {
    if (!editContent.trim()) return

    setIsUpdating(true)
    try {
      await updateComment(commentId, editContent.trim())
      setEditingId(null)
      onUpdate?.()
    } catch (error) {
      console.error('Failed to update comment:', error)
      alert('Failed to update comment')
    } finally {
      setIsUpdating(false)
    }
  }

  const handleDelete = async (commentId: number) => {
    if (!confirm('Are you sure you want to delete this comment?')) return

    try {
      await deleteComment(commentId)
      onUpdate?.()
    } catch (error) {
      console.error('Failed to delete comment:', error)
      alert('Failed to delete comment')
    }
  }

  const handleCancel = () => {
    setEditingId(null)
    setEditContent('')
  }

  if (comments.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 text-sm">
        No comments yet
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {comments.map((comment) => {
        const isOwner = currentUserId && comment.user?.id === currentUserId
        const isEditing = editingId === comment.id

        return (
          <div key={comment.id} className="border border-gray-200 rounded-lg p-4">
            {/* Comment header */}
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                {comment.user?.avatar_url ? (
                  <img
                    src={comment.user.avatar_url}
                    alt={comment.user.full_name || 'User'}
                    className="w-8 h-8 rounded-full"
                  />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
                    <span className="text-sm text-gray-600">
                      {comment.user?.full_name?.charAt(0) || '?'}
                    </span>
                  </div>
                )}
                <div>
                  <div className="font-medium text-sm text-gray-900">
                    {comment.user?.full_name || 'Unknown User'}
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(comment.created_at).toLocaleString()}
                    {comment.updated_at !== comment.created_at && ' (edited)'}
                  </div>
                </div>
              </div>

              {isOwner && !isEditing && (
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(comment)}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(comment.id)}
                    className="text-xs text-red-600 hover:underline"
                  >
                    Delete
                  </button>
                </div>
              )}
            </div>

            {/* Comment content */}
            {!isEditing ? (
              <p className="text-gray-900 whitespace-pre-wrap">{comment.content}</p>
            ) : (
              <div className="space-y-2">
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <div className="flex gap-2">
                  <button
                    onClick={() => handleSave(comment.id)}
                    disabled={isUpdating || !editContent.trim()}
                    className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isUpdating ? 'Saving...' : 'Save'}
                  </button>
                  <button
                    onClick={handleCancel}
                    className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
