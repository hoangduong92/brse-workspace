import React from 'react'

interface BadgeProps {
  variant?: 'status' | 'type'
  value: string
  className?: string
}

export default function Badge({ variant = 'status', value, className = '' }: BadgeProps) {
  const baseStyles = 'inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium'

  const getStatusStyles = (status: string) => {
    const normalized = status.toLowerCase().replace(/[_\s]/g, '-')
    switch (normalized) {
      case 'open':
        return 'bg-gray-100 text-gray-800 border border-gray-300'
      case 'in-progress':
      case 'inprogress':
        return 'bg-blue-100 text-blue-800 border border-blue-300'
      case 'resolved':
        return 'bg-green-100 text-green-800 border border-green-300'
      case 'closed':
        return 'bg-gray-100 text-gray-600 border border-gray-200'
      default:
        return 'bg-gray-100 text-gray-800 border border-gray-300'
    }
  }

  const getTypeStyles = (type: string) => {
    const normalized = type.toLowerCase()
    switch (normalized) {
      case 'bug':
        return 'bg-red-100 text-red-800 border border-red-300'
      case 'feature':
        return 'bg-purple-100 text-purple-800 border border-purple-300'
      case 'task':
        return 'bg-cyan-100 text-cyan-800 border border-cyan-300'
      case 'improvement':
        return 'bg-emerald-100 text-emerald-800 border border-emerald-300'
      default:
        return 'bg-gray-100 text-gray-800 border border-gray-300'
    }
  }

  const variantStyles = variant === 'status' ? getStatusStyles(value) : getTypeStyles(value)

  return (
    <span className={`${baseStyles} ${variantStyles} ${className}`}>
      {value}
    </span>
  )
}
