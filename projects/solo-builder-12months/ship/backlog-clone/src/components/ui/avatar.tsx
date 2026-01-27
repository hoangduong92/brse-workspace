import React from 'react'

interface AvatarProps {
  name?: string
  src?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export default function Avatar({ name, src, size = 'md', className = '' }: AvatarProps) {
  const sizeStyles = {
    sm: 'h-8 w-8 text-xs',
    md: 'h-10 w-10 text-sm',
    lg: 'h-12 w-12 text-base',
  }

  const getInitials = (name: string) => {
    const parts = name.trim().split(' ')
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase()
    }
    return name.substring(0, 2).toUpperCase()
  }

  const getBackgroundColor = (name: string) => {
    const colors = [
      'bg-blue-500',
      'bg-green-500',
      'bg-yellow-500',
      'bg-purple-500',
      'bg-pink-500',
      'bg-indigo-500',
      'bg-red-500',
      'bg-teal-500',
    ]
    const index = name.charCodeAt(0) % colors.length
    return colors[index]
  }

  return (
    <div className={`inline-flex items-center justify-center rounded-full ${sizeStyles[size]} ${className}`}>
      {src ? (
        <img
          src={src}
          alt={name || 'User avatar'}
          className={`rounded-full object-cover ${sizeStyles[size]}`}
        />
      ) : name ? (
        <div className={`flex items-center justify-center rounded-full ${sizeStyles[size]} ${getBackgroundColor(name)} text-white font-medium`}>
          {getInitials(name)}
        </div>
      ) : (
        <div className={`flex items-center justify-center rounded-full ${sizeStyles[size]} bg-gray-300 text-gray-600`}>
          <svg
            className="h-1/2 w-1/2"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
              clipRule="evenodd"
            />
          </svg>
        </div>
      )}
    </div>
  )
}
