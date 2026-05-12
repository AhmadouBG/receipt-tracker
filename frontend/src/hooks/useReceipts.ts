import { useState, useEffect, useCallback } from "react"
import { fetchReceipts, type Receipt } from "../lib/api"

export function useReceipts() {
  const [receipts, setReceipts] = useState<Receipt[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchReceipts()
      setReceipts(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch receipts")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  return { receipts, loading, error, refresh }
}
