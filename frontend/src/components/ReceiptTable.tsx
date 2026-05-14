import { useState, useRef } from "react"
import { ChevronLeft, ChevronRight, AlertTriangle, RefreshCw, Loader2 } from "lucide-react"
import type { Receipt } from "@/lib/api"
import { reuploadReceipt } from "@/lib/api"
import { ConfidenceBadge } from "./ConfidenceBadge"

interface ReceiptTableProps {
  receipts: Receipt[]
  onReuploadComplete?: () => void
}

const PAGE_SIZE = 10

export function ReceiptTable({ receipts, onReuploadComplete }: ReceiptTableProps) {
  const [page, setPage] = useState(0)
  const [reuploadingId, setReuploadingId] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const pendingUploadId = useRef<string | null>(null)

  const handleReuploadClick = (receiptId: string) => {
    pendingUploadId.current = receiptId
    fileInputRef.current?.click()
  }

  const handleFileSelected = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    const receiptId = pendingUploadId.current
    if (!file || !receiptId) return

    setReuploadingId(receiptId)
    try {
      await reuploadReceipt(receiptId, file)
      onReuploadComplete?.()
    } catch {
      // error handled silently — data refresh will show still-failed state
    } finally {
      setReuploadingId(null)
      pendingUploadId.current = null
      if (fileInputRef.current) fileInputRef.current.value = ""
    }
  }

  if (receipts.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No receipts yet. Upload a receipt to get started.
      </div>
    )
  }

  const totalPages = Math.ceil(receipts.length / PAGE_SIZE)
  const paginatedReceipts = receipts.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  return (
    <div className="border rounded-lg overflow-hidden">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelected}
        accept=".png,.jpg,.jpeg,.pdf"
        className="hidden"
      />
      <div className="overflow-y-auto" style={{ maxHeight: "400px" }}>
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-gray-50">
            <tr className="border-b">
              <th className="px-4 py-3 text-left font-medium text-gray-600">Company</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Date</th>
              <th className="px-4 py-3 text-right font-medium text-gray-600">Total</th>
              <th className="px-4 py-3 text-center font-medium text-gray-600">Confidence</th>
              <th className="px-4 py-3 text-center font-medium text-gray-600"></th>
            </tr>
          </thead>
          <tbody>
            {paginatedReceipts.map((receipt) => {
              const isFailed = receipt.status === "failed"
              return (
                <tr key={receipt.id} className={`border-b hover:bg-gray-50 ${isFailed ? "bg-red-50" : ""}`}>
                  <td className="px-4 py-3 font-medium">
                    <div className="flex items-center gap-2">
                      {isFailed && <AlertTriangle className="h-4 w-4 text-red-500 shrink-0" />}
                      <span className={isFailed ? "text-red-600" : ""}>
                        {receipt.company ?? (isFailed ? "Failed" : "-")}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {receipt.date ?? (receipt.datetime ? receipt.datetime.slice(0, 10) : "-")}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {receipt.total != null ? Number(receipt.total.toFixed(2)).toLocaleString("fr-FR", { style: "currency", currency: "EUR" }) : "-"}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {isFailed ? (
                      <span className="text-xs text-red-500 font-medium">Failed</span>
                    ) : (
                      <ConfidenceBadge confidence={receipt.confidence} />
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {isFailed && (
                      <button
                        onClick={() => handleReuploadClick(receipt.receipt_id)}
                        disabled={reuploadingId === receipt.receipt_id}
                        className="inline-flex items-center gap-1 text-xs text-red-600 hover:text-red-700 font-medium disabled:opacity-50"
                        title="Re-upload receipt"
                      >
                        {reuploadingId === receipt.receipt_id ? (
                          <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        ) : (
                          <RefreshCw className="h-3.5 w-3.5" />
                        )}
                        {reuploadingId === receipt.receipt_id ? "Processing..." : "Re-upload"}
                      </button>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="p-1 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <span className="text-sm text-gray-500">
            {page + 1} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page === totalPages - 1}
            className="p-1 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      )}
    </div>
  )
}
