import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

interface ExpenseData {
  period: string
  total: number
}

interface ExpenseChartProps {
  data: ExpenseData[]
  timeGranularity: "day" | "week" | "month" | "year"
}

const mockData: ExpenseData[] = [
  { period: "Mon", total: 45.50 },
  { period: "Tue", total: 28.75 },
  { period: "Wed", total: 67.30 },
  { period: "Thu", total: 112.20 },
  { period: "Fri", total: 89.00 },
  { period: "Sat", total: 34.90 },
  { period: "Sun", total: 52.15 },
]

export function ExpenseChart({ data = mockData, timeGranularity = "day" }: ExpenseChartProps) {
  const total = data.reduce((sum, item) => sum + item.total, 0)

  return (
    <div className="p-4">
      <div className="w-full max-w-4xl p-6 bg-white rounded-xl shadow-sm border">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Expenses</h2>
          <p className="text-sm text-gray-500">{timeGranularity === "day" ? "Daily" : timeGranularity + "ly"} breakdown</p>
        </div>
        <div className="h-[250px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200" />
              <XAxis
                dataKey="period"
                tick={{ fill: "#6b7280", fontSize: 12 }}
                tickLine={{ stroke: "#d1d5db" }}
              />
              <YAxis
                tick={{ fill: "#6b7280", fontSize: 12 }}
                tickLine={{ stroke: "#d1d5db" }}
                tickFormatter={(value) => `€${value}`}
              />
              <Tooltip
                formatter={(value) => [`€${Number(value).toFixed(2)}`, "Total"]}
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                }}
              />
              <Bar dataKey="total" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-500">Total</span>
            <span className="text-lg font-semibold text-gray-900">€{total.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export type { ExpenseData }
