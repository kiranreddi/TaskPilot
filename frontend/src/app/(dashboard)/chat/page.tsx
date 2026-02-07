"use client";

import { useState } from "react";

const APP_CHIPS = ["Google", "Slack", "Notion", "Stripe"];

interface PlanStep {
  description: string;
  risk: "READ" | "WRITE";
  approval: boolean;
}

export default function ChatPage() {
  const [prompt, setPrompt] = useState("");
  const [readOnly, setReadOnly] = useState(false);
  const [selectedApps, setSelectedApps] = useState<string[]>([]);
  const [showPlan, setShowPlan] = useState(false);

  const samplePlan: PlanStep[] = [
    { description: "Search Gmail for billing emails", risk: "READ", approval: false },
    { description: "Summarize totals by vendor", risk: "READ", approval: false },
    { description: "Post summary to Slack #finance", risk: "WRITE", approval: true },
  ];

  function toggleApp(app: string) {
    setSelectedApps((prev) =>
      prev.includes(app) ? prev.filter((a) => a !== app) : [...prev, app]
    );
  }

  function handleRun() {
    if (!prompt.trim()) return;
    setShowPlan(true);
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Chat</h1>

      <div className="bg-white rounded-xl shadow-sm border p-6 space-y-4">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ask TaskPilot to do something across your apps…"
          rows={4}
          className="w-full rounded-lg border border-gray-300 px-4 py-3 text-sm focus:border-indigo-500 focus:ring-indigo-500 resize-none"
        />

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Read-only mode</span>
            <button
              type="button"
              onClick={() => setReadOnly(!readOnly)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                readOnly ? "bg-indigo-600" : "bg-gray-300"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                  readOnly ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {APP_CHIPS.map((app) => (
            <button
              key={app}
              type="button"
              onClick={() => toggleApp(app)}
              className={`px-3 py-1 rounded-full text-sm font-medium border transition-colors ${
                selectedApps.includes(app)
                  ? "bg-indigo-100 border-indigo-300 text-indigo-700"
                  : "bg-gray-100 border-gray-200 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {app}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={handleRun}
          className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700"
        >
          Run
        </button>
      </div>

      {/* Plan Preview Modal */}
      {showPlan && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 space-y-4">
            <h2 className="text-lg font-bold">Here&apos;s what I will do</h2>

            <ol className="space-y-3">
              {samplePlan.map((step, i) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-xs font-medium">
                    {i + 1}
                  </span>
                  <div className="flex-1">
                    <span>{step.description}</span>
                    <span
                      className={`ml-2 inline-block px-2 py-0.5 rounded text-xs font-medium ${
                        step.risk === "WRITE"
                          ? "bg-amber-100 text-amber-800"
                          : "bg-green-100 text-green-800"
                      }`}
                    >
                      {step.risk}
                    </span>
                    {step.approval && (
                      <span className="ml-1 text-amber-600 text-xs">⚠ requires approval</span>
                    )}
                  </div>
                </li>
              ))}
            </ol>

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowPlan(false)}
                className="flex-1 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
              >
                Approve &amp; Run
              </button>
              <button
                type="button"
                onClick={() => setShowPlan(false)}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Edit
              </button>
              <button
                type="button"
                onClick={() => setShowPlan(false)}
                className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
