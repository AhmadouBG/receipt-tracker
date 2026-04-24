import { useState } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import type { Receipt } from "@/lib/api"
import { ConfidenceBadge } from "./ConfidenceBadge"

interface ReceiptTableProps {
  receipts: Receipt[]
}

const PAGE_SIZE = 10

export function ReceiptTable({ receipts }: ReceiptTableProps) {
  const [page, setPage] = useState(0)

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
      <div className="overflow-y-auto" style={{ maxHeight: "400px" }}>
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-gray-50">
            <tr className="border-b">
              <th className="px-4 py-3 text-left font-medium text-gray-600">Company</th>
              <th className="px-4 py-3 text-left font-medium text-gray-600">Date</th>
              <th className="px-4 py-3 text-right font-medium text-gray-600">Total</th>
              <th className="px-4 py-3 text-center font-medium text-gray-600">Confidence</th>
            </tr>
          </thead>
          <tbody>
            {paginatedReceipts.map((receipt) => (
              <tr key={receipt.id} className="border-b hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">
                  {receipt.company ?? "-"}
                </td>
                <td className="px-4 py-3">
                  {receipt.date ?? receipt.datetime.slice(0, 10)}
                </td>
                <td className="px-4 py-3 text-right">
                  {receipt.total != null ? `${receipt.total.toFixed(2)} €` : "-"}
                </td>
                <td className="px-4 py-3 text-center">
                  <ConfidenceBadge confidence={receipt.confidence} />
                </td>
              </tr>
            ))}
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