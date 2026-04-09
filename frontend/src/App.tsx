import "./index.css"
import { ExpenseChart } from "./components/ExpenseChart"

function App() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Receipt Tracker</h1>
        <ExpenseChart data={[]} timeGranularity="day" />
      </div>
    </div>
  )
}

export default App
