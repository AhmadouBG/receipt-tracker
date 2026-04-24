import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Upload, Loader2, FileIcon, X } from "lucide-react"
import { Button } from "./ui/button"
import { uploadReceipt } from "@/lib/api"

interface FileUploadProps {
  onUploadComplete: () => void
}

export function FileUpload({ onUploadComplete }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFile(acceptedFiles[0] ?? null)
    setError(null)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".png", ".jpg", ".jpeg"],
      "application/pdf": [".pdf"],
    },
    maxFiles: 1,
  })

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError(null)

    try {
      await uploadReceipt(file)
      setFile(null)
      onUploadComplete()
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

  return (
    <div className="flex flex-col gap-4">
      {file ? (
        <div className="flex items-center justify-between p-4 border rounded-lg bg-gray-50">
          <div className="flex items-center gap-3">
            <FileIcon className="h-5 w-5 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">{file.name}</span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={removeFile}
              disabled={uploading}
            >
              <X className="h-4 w-4" />
            </Button>
            <Button
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload
                </>
              )}
            </Button>
          </div>
        </div>
      ) : (
        <div
          {...getRootProps()}
          className={`cursor-pointer border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragActive
              ? "border-primary bg-primary/5"
              : "border-gray-300 hover:border-gray-400"
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center gap-3">
            <Upload className="h-8 w-8 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">
                Glissez-d&eacute;posez un fichier ici
              </p>
              <p className="text-xs text-gray-500">ou</p>
            </div>
            <Button variant="secondary" size="sm">
              Choisir un fichier
            </Button>
            <p className="text-xs text-gray-400">
              PNG, JPG, PDF jusqu&apos;&agrave; 10MB
            </p>
          </div>
        </div>
      )}
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  )
}