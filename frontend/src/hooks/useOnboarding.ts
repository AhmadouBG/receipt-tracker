import { useState, useEffect, useCallback } from "react"

const STORAGE_KEY = "bmad_onboarding_complete"

export function useOnboarding() {
  const [step, setStep] = useState<1 | 2 | 3 | null>(null)

  useEffect(() => {
    const done = localStorage.getItem(STORAGE_KEY) === "true"
    if (!done) setStep(1)
  }, [])

  const nextStep = useCallback(() => {
    setStep((prev) => {
      if (!prev || prev >= 3) return prev
      return (prev + 1) as 1 | 2 | 3
    })
  }, [])

  const complete = useCallback(() => {
    localStorage.setItem(STORAGE_KEY, "true")
    setStep(null)
  }, [])

  const skip = useCallback(() => {
    complete()
  }, [complete])

  return { isOnboarding: step !== null, step, nextStep, complete, skip }
}
