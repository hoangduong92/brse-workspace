'use client'

import React, { useState, useRef, useEffect } from 'react'
import Avatar from '@/components/ui/avatar'
import LogoutButton from '@/components/auth/logout-button'

interface NavbarProps {
  userName?: string
  userEmail?: string
  userAvatar?: string
}

export default function Navbar({ userName, userEmail, userAvatar }: NavbarProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false)
      }
    }

    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isMenuOpen])

  return (
    <nav className="h-16 bg-white border-b border-border sticky top-0 z-40">
      <div className="h-full flex items-center justify-between px-4 md:px-6">
        {/* Left side - can add search or breadcrumbs */}
        <div className="flex-1">
          {/* Placeholder for future features like search */}
        </div>

        {/* Right side - User menu */}
        <div className="flex items-center gap-4">
          {/* User menu dropdown */}
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-bg-tertiary transition-base cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
            >
              <Avatar
                name={userName || userEmail || 'User'}
                src={userAvatar}
                size="sm"
              />
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium text-text-primary">
                  {userName || 'User'}
                </p>
                {userEmail && (
                  <p className="text-xs text-text-muted truncate max-w-[150px]">
                    {userEmail}
                  </p>
                )}
              </div>
              <svg
                className={`w-4 h-4 text-text-muted transition-transform ${
                  isMenuOpen ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Dropdown menu */}
            {isMenuOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-border py-1">
                <div className="px-4 py-3 border-b border-border">
                  <p className="text-sm font-medium text-text-primary">
                    {userName || 'User'}
                  </p>
                  {userEmail && (
                    <p className="text-xs text-text-muted truncate">
                      {userEmail}
                    </p>
                  )}
                </div>
                <div className="py-1">
                  <a
                    href="/dashboard/settings"
                    className="block px-4 py-2 text-sm text-text-secondary hover:bg-bg-tertiary transition-base cursor-pointer"
                  >
                    Settings
                  </a>
                  <div className="px-4 py-2">
                    <LogoutButton />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
