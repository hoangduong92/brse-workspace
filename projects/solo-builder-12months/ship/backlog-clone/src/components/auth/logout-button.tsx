'use client'

import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export default function LogoutButton() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)

  const handleLogout = async () => {
    setIsLoading(true)
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/login')
    router.refresh()
  }

  return (
    <button
      onClick={handleLogout}
      disabled={isLoading}
      className="w-full text-left text-sm text-text-secondary hover:text-text-primary transition-base disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
    >
      {isLoading ? 'Logging out...' : 'Logout'}
    </button>
  )
}
