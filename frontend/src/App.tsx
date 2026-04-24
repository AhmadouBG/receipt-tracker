import { useState, useEffect, useRef } from "react"
import "./index.css"
import { FileUpload } from "./components/FileUpload"
import { ReceiptTable } from "./components/ReceiptTable"
import { fetchReceipts, type Receipt } from "./lib/api"

function App() {
  const [receipts, setReceipts] = useState<Receipt[]>([])
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

  const hasData = receipts.length > 0
  const totalExpenses = receipts.reduce((sum, r) => sum + (r.total ?? 0), 0)
  const receiptCount = receipts.length

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
            </div>

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