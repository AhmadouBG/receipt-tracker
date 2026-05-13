import { useState } from "react"
import { uploadReceipt } from "../lib/api"

export function useUpload(onUploadComplete?: () => void) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const upload = async () => {
    if (!file) return

    setUploading(true)
    setError(null)

    try {
      await uploadReceipt(file)
      setFile(null)
      onUploadComplete?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed")
    } finally {
      setUploading(false)
    }
  }

  const removeFile = () => {
    setFile(null)
    setError(null)
  }

  const reset = () => {
    setFile(null)
    setError(null)
    setUploading(false)
  }

  return { file, setFile, uploading, error, upload, removeFile, reset }
}
