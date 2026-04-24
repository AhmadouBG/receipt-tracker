export type TimeGranularity = "day" | "week" | "month" | "year"

interface TimeGranularityToggleProps {
  value: TimeGranularity
  onChange: (value: TimeGranularity) => void
}

const options: { value: TimeGranularity; label: string }[] = [
  { value: "day", label: "Day" },
  { value: "week", label: "Week" },
  { value: "month", label: "Month" },
  { value: "year", label: "Year" },
]

export function TimeGranularityToggle({ value, onChange }: TimeGranularityToggleProps) {
  return (
    <div className="inline-flex rounded-lg border bg-white p-1">
      {options.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
            value === option.value
              ? "bg-primary text-white"
              : "text-gray-600 hover:bg-gray-200 hover:text-gray-900"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}