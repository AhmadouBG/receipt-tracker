import { useState, useEffect, useCallback } from "react"
import { fetchReceipts, type Receipt } from "../lib/api"

export function useReceipts() {
  const [receipts, setReceipts] = useState<Receipt[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  //Prevents React from recreating the function every render usecallback is used to memoize the function

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
  //[] ensures that the effect only runs once when the component mounts

  useEffect(() => {
    refresh()
  }, [refresh])
  console.log("receipts: ", receipts)
  //[refresh] ensures that the effect only runs when refresh changes
  return { receipts, loading, error, refresh }
}
