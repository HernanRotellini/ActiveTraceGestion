import { useState, useRef, useEffect, useId } from 'react'

export interface ComboboxItem {
  value: string
  label: string
}

interface ComboboxProps {
  label: string
  items: ComboboxItem[]
  value: string
  onChange: (value: string) => void
  placeholder?: string
  error?: string
  isLoading?: boolean
  searchPlaceholder?: string
  noResultsText?: string
}

export function Combobox({
  label,
  items,
  value,
  onChange,
  placeholder = 'Seleccionar...',
  error,
  isLoading = false,
  searchPlaceholder = 'Buscar...',
  noResultsText = 'Sin resultados',
}: ComboboxProps) {
  const id = useId()
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const containerRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const selectedItem = items.find((i) => i.value === value)

  const filteredItems = search
    ? items.filter(
        (i) =>
          i.label.toLowerCase().includes(search.toLowerCase()) ||
          i.value.toLowerCase().includes(search.toLowerCase()),
      )
    : items

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
        setSearch('')
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  function handleSelect(item: ComboboxItem) {
    onChange(item.value)
    setOpen(false)
    setSearch('')
    inputRef.current?.blur()
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Escape') {
      setOpen(false)
      setSearch('')
    }
    if (e.key === 'Enter' && filteredItems.length === 1) {
      handleSelect(filteredItems[0])
    }
  }

  return (
    <div ref={containerRef} className="relative">
      <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <div className="relative">
        <input
          ref={inputRef}
          id={id}
          type="text"
          value={open ? search : (selectedItem?.label ?? '')}
          onChange={(e) => {
            setSearch(e.target.value)
            if (!open) setOpen(true)
            if (!e.target.value) onChange('')
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={open ? searchPlaceholder : placeholder}
          className={`block w-full rounded-lg border px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 ${
            error
              ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:border-primary-500 focus:ring-primary-500'
          }`}
          autoComplete="off"
        />
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
          <svg
            className={`h-4 w-4 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {open && (
        <div className="absolute z-50 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-gray-200 bg-white shadow-lg">
          {isLoading ? (
            <div className="px-3 py-4 text-center text-sm text-gray-500">Cargando...</div>
          ) : filteredItems.length === 0 ? (
            <div className="px-3 py-4 text-center text-sm text-gray-500">{noResultsText}</div>
          ) : (
            <ul className="py-1" role="listbox">
              {filteredItems.map((item) => (
                <li
                  key={item.value}
                  role="option"
                  aria-selected={item.value === value}
                  onClick={() => handleSelect(item)}
                  onKeyDown={(e) => { if (e.key === 'Enter') handleSelect(item) }}
                  tabIndex={0}
                  className={`cursor-pointer px-3 py-2 text-sm transition-colors hover:bg-primary-50 focus:bg-primary-50 focus:outline-none ${
                    item.value === value ? 'bg-primary-50 font-medium text-primary-700' : 'text-gray-700'
                  }`}
                >
                  {item.label}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {error && (
        <p className="mt-1 text-sm text-red-600" role="alert">{error}</p>
      )}
    </div>
  )
}
