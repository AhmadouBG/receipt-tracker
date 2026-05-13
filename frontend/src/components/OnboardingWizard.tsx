import { Upload, Loader2, BarChart3, CheckCircle2, ArrowRight } from "lucide-react"
import { Button } from "./ui/button"

interface OnboardingWizardProps {
  step: 1 | 2 | 3
  onComplete: () => void
  onSkip: () => void
}

const steps = [
  { number: 1, title: "Upload your first receipt", icon: Upload },
  { number: 2, title: "Watch the AI work", icon: Loader2 },
  { number: 3, title: "See your data appear", icon: BarChart3 },
]

export function OnboardingWizard({ step, onComplete, onSkip }: OnboardingWizardProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg mx-4 bg-white rounded-2xl shadow-2xl border overflow-hidden">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Welcome to Receipt Tracker</h2>
            <button
              onClick={onSkip}
              className="text-sm text-gray-400 hover:text-gray-600 transition-colors"
            >
              Skip
            </button>
          </div>

          <div className="flex justify-center gap-2 mb-6">
            {steps.map((s) => (
              <div
                key={s.number}
                className={`h-2 w-16 rounded-full transition-colors ${
                  s.number <= step ? "bg-teal-500" : "bg-gray-200"
                }`}
              />
            ))}
          </div>

          {step === 1 && <Step1Content />}
          {step === 2 && <Step2Content />}
          {step === 3 && <Step3Content onComplete={onComplete} />}
        </div>
      </div>
    </div>
  )
}

function Step1Content() {
  return (
    <div className="text-center space-y-4">
      <div className="mx-auto w-16 h-16 rounded-full bg-teal-50 flex items-center justify-center">
        <Upload className="h-7 w-7 text-teal-500" />
      </div>
      <div>
        <p className="text-gray-900 font-medium text-base">
          Drop your first receipt
        </p>
        <p className="text-gray-500 text-sm mt-1">
          Drag and drop a receipt image or PDF below to get started.
        </p>
      </div>
      <div className="border-2 border-dashed border-teal-200 bg-teal-50/50 rounded-xl p-6">
        <Upload className="mx-auto h-8 w-8 text-teal-400 mb-2" />
        <p className="text-sm text-teal-700 font-medium">Use the upload section below</p>
        <p className="text-xs text-teal-500 mt-1">PNG, JPG, or PDF</p>
      </div>
    </div>
  )
}

function Step2Content() {
  return (
    <div className="text-center space-y-4">
      <div className="mx-auto w-16 h-16 rounded-full bg-amber-50 flex items-center justify-center">
        <Loader2 className="h-7 w-7 text-amber-500 animate-spin" />
      </div>
      <div>
        <p className="text-gray-900 font-medium text-base">
          Scanning your receipt...
        </p>
        <p className="text-gray-500 text-sm mt-1">
          The AI is extracting company, date, total, and address from your receipt.
        </p>
      </div>
      <div className="bg-amber-50 rounded-xl p-4 space-y-2">
        <div className="flex items-center gap-3 text-sm">
          <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
          <span className="text-amber-800">Extracting fields...</span>
        </div>
        <div className="flex items-center gap-3 text-sm text-gray-400">
          <div className="w-2 h-2 rounded-full bg-gray-300" />
          <span>Parsing results</span>
        </div>
        <div className="flex items-center gap-3 text-sm text-gray-400">
          <div className="w-2 h-2 rounded-full bg-gray-300" />
          <span>Updating chart</span>
        </div>
      </div>
    </div>
  )
}

function Step3Content({ onComplete }: { onComplete: () => void }) {
  return (
    <div className="text-center space-y-4">
      <div className="mx-auto w-16 h-16 rounded-full bg-green-50 flex items-center justify-center">
        <CheckCircle2 className="h-7 w-7 text-green-500" />
      </div>
      <div>
        <p className="text-gray-900 font-medium text-base">
          Your expense chart is live!
        </p>
        <p className="text-gray-500 text-sm mt-1">
          Your receipt data appears in the chart below. Add more receipts to track your spending.
        </p>
      </div>
      <div className="bg-teal-50 rounded-xl p-4">
        <BarChart3 className="mx-auto h-10 w-10 text-teal-500 mb-2" />
        <p className="text-sm text-teal-700 font-medium">Receipt processed successfully</p>
      </div>
      <Button onClick={onComplete} className="w-full">
        See my chart
        <ArrowRight className="ml-2 h-4 w-4" />
      </Button>
    </div>
  )
}
