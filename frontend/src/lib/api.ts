const API_BASE = "http://localhost:8000/api"

export interface Receipt {
  id: number
  receipt_id: string
  filename: string
  company: string | null
  date: string | null
  total: number | null
  address: string | null
  confidence: number | null
  datetime: string
  status: string
}

export interface UploadResponse {
  receipt_id: string
  status: string
  filename: string
  error?: string
}

export async function fetchReceipts(): Promise<Receipt[]> {
  const res = await fetch(`${API_BASE}/receipts`)
  if (!res.ok) throw new Error("Failed to fetch receipts")
  return res.json()
}

export async function uploadReceipt(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append("file", file)

  const res = await fetch(`${API_BASE}/uploadReceipt`, {
    method: "POST",
    body: formData,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || "Upload failed")
  }

  return res.json()
}