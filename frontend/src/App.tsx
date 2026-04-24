import { useState, useEffect, useRef } from "react"
import "./index.css"
import { FileUpload } from "./components/FileUpload"
import { ReceiptTable } from "./components/ReceiptTable"
import { ExpenseChart, type ExpenseData } from "./components/ExpenseChart"
import { TimeGranularityToggle, type TimeGranularity } from "./components/TimeGranularityToggle"
import { ConfidenceBadge } from "./components/ConfidenceBadge"
import { fetchReceipts, type Receipt } from "./lib/api"

function App() {
  const [receipts, setReceipts] = useState<Receipt[]>([])
  const [granularity, setGranularity] = useState<TimeGranularity>("day")
  const [loading, setLoading] = useState(true)
  const uploadRef = useRef<HTMLDivElement>(null)

  const loadReceipts = async () => {
    try {
      const data = await fetchReceipts()
      setReceipts(data)
    } catch (err) {
      console.error("Failed to fetch receipts:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadReceipts()
  }, [])

  const receiptsToChartData = (receipts: Receipt[], granularity: TimeGranularity): ExpenseData[] => {
    const grouped: Record<string, number> = {}

    for (const receipt of receipts) {
      if (!receipt.total) continue
      const date = new Date(receipt.date ?? receipt.datetime)
      let key: string
      if (granularity === "day") {
        key = date.toLocaleDateString("fr-FR", { weekday: "short" })
      } else if (granularity === "week") {
        const weekStart = new Date(date)
        weekStart.setDate(date.getDate() - date.getDay())
        key = weekStart.toLocaleDateString("fr-FR", { month: "short", day: "numeric" })
      } else if (granularity === "month") {
        key = date.toLocaleDateString("fr-FR", { month: "short" })
      } else {
        key = date.getFullYear().toString()
      }
      grouped[key] = (grouped[key] ?? 0) + receipt.total
    }

    return Object.entries(grouped).map(([period, total]) => ({ period, total }))
  }

  const chartData = receiptsToChartData(receipts, granularity)
  const hasData = receipts.length > 0 && chartData.length > 0
  const totalExpenses = receipts.reduce((sum, r) => sum + (r.total ?? 0), 0)
  const receiptCount = receipts.length
  const avgConfidence = receipts.length > 0
    ? receipts.reduce((sum, r) => sum + (r.confidence ?? 0), 0) / receipts.length
    : null

  const scrollToUpload = () => {
    uploadRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  return (
    <div className="bg-gray-50 p-5">
      <div className="max-w-6xl mx-auto space-y-8">
        <header className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Receipt Tracker</h1>
          <p className="text-gray-500 mt-1">Track your expenses with AI-powered receipt scanning</p>
        </header>

        <section ref={uploadRef} className="space-y-3">
          <h2 className="text-lg font-semibold text-gray-900">Upload Receipt</h2>
          <FileUpload onUploadComplete={loadReceipts} />
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Expenses</h2>
              {hasData && <TimeGranularityToggle value={granularity} onChange={setGranularity} />}
            </div>
            {hasData ? (
              <ExpenseChart data={chartData} timeGranularity={granularity} />
            ) : (
              <div className="text-center py-12 border rounded-lg bg-white">
                <p className="text-gray-500 mb-4">
                  No expense data yet. Upload your first receipt to get started.
                </p>
                <button
                  onClick={scrollToUpload}
                  className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors"
                >
                  Upload a receipt
                </button>
              </div>
            )}
            {hasData && (
              <div className="grid grid-cols-2 gap-3">
                <div className="p-4 bg-white rounded-lg border">
                  <p className="text-sm text-gray-500">Total</p>
                  <p className="text-xl font-bold text-gray-900">{totalExpenses.toFixed(2)} €</p>
                </div>
                <div className="p-4 bg-white rounded-lg border">
                  <p className="text-sm text-gray-500">Receipts</p>
                  <p className="text-xl font-bold text-gray-900">{receiptCount}</p>
                </div>
                <div className="p-4 bg-white rounded-lg border col-span-2">
                  <p className="text-sm text-gray-500 mb-2">Avg. Confidence</p>
                  <ConfidenceBadge confidence={avgConfidence} />
                </div>
              </div>
            )}
          </div>

          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-900">Receipts</h2>
            {loading ? (
              <div className="text-center py-8 text-gray-500">Loading...</div>
            ) : (
              <ReceiptTable receipts={receipts} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App