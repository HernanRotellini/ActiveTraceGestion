import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react'
import type { Session, SessionUser } from '@/shared/types/session'
import { readSession, writeSession, clearSession } from '@/shared/services/session'

interface SessionContextValue {
  session: Session | null
  isAuthenticated: boolean
  login: (access_token: string, refresh_token: string, user: SessionUser) => void
  logout: () => void
  hasPermission: (permission: string) => boolean
  updateSession: (session: Session) => void
}

const SessionContext = createContext<SessionContextValue | null>(null)

export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(() => readSession())

  useEffect(() => {
    if (session) {
      writeSession(session)
    }
  }, [session])

  const isAuthenticated = session !== null

  const login = useCallback((access_token: string, refresh_token: string, user: SessionUser) => {
    const newSession: Session = { access_token, refresh_token, user }
    setSession(newSession)
    writeSession(newSession)
  }, [])

  const logout = useCallback(() => {
    setSession(null)
    clearSession()
  }, [])

  const updateSession = useCallback((newSession: Session) => {
    setSession(newSession)
    writeSession(newSession)
  }, [])

  const hasPermission = useCallback(
    (permission: string): boolean => {
      if (session?.user?.roles?.includes('ADMIN')) return true
      if (!session?.user?.permissions) return false
      return session.user.permissions.includes(permission)
    },
    [session],
  )

  return (
    <SessionContext.Provider value={{ session, isAuthenticated, login, logout, hasPermission, updateSession }}>
      {children}
    </SessionContext.Provider>
  )
}

export function useSession(): SessionContextValue {
  const context = useContext(SessionContext)
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider')
  }
  return context
}
