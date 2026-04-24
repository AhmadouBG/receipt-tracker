interface ConfidenceBadgeProps {
  confidence: number | null
}

function getConfidenceColor(confidence: number | null): string {
  if (confidence === null) return "bg-gray-200 text-gray-600"
  if (confidence >= 0.8) return "bg-green-100 text-green-800"
  if (confidence >= 0.5) return "bg-yellow-100 text-yellow-800"
  return "bg-red-100 text-red-800"
}

function getConfidenceLabel(confidence: number | null): string {
  if (confidence === null) return "N/A"
  return `${Math.round(confidence * 100)}%`
}

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(confidence)}`}
    >
      {getConfidenceLabel(confidence)}
    </span>
  )
}