import type { ReactNode, MouseEvent } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  onClick?: (e: MouseEvent<HTMLDivElement>) => void
}

export function Card({ children, className = '', onClick }: CardProps) {
  return (
    <div
      className={`rounded-xl border border-gray-200 bg-white shadow-sm ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  )
}
