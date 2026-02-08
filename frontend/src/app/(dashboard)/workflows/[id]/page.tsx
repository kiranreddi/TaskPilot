"use client";

import { useState } from "react";
import { useParams } from "next/navigation";

interface Step {
  id: string;
  tool: string;
  args: string;
  risk: "READ" | "WRITE";
  retryPolicy: string;
}

export default function WorkflowEditorPage() {
  const params = useParams();
  const workflowId = params.id as string;
  const isNew = workflowId === "new";

  const [name, setName] = useState(isNew ? "" : "Weekly Revenue Report");
  const [description, setDescription] = useState(
    isNew ? "" : "Collects Stripe revenue data and posts to Slack"
  );
  const [inputs, setInputs] = useState<{ key: string; value: string }[]>([
    { key: "channel", value: "#finance" },
  ]);
  const [steps, setSteps] = useState<Step[]>([
    { id: "s1", tool: "stripe.listCharges", args: '{"period":"week"}', risk: "READ", retryPolicy: "3x" },
    { id: "s2", tool: "sheets.appendRow", args: '{"sheet":"Revenue"}', risk: "WRITE", retryPolicy: "2x" },
    { id: "s3", tool: "slack.postMessage", args: '{"channel":"#finance"}', risk: "WRITE", retryPolicy: "1x" },
  ]);
  const [cron, setCron] = useState("0 9 * * 1");
  const [timezone, setTimezone] = useState("America/New_York");
  const [scheduleEnabled, setScheduleEnabled] = useState(true);

  function addInput() {
    setInputs([...inputs, { key: "", value: "" }]);
  }

  function removeStep(id: string) {
    setSteps(steps.filter((s) => s.id !== id));
  }

  function moveStep(index: number, direction: -1 | 1) {
    const newSteps = [...steps];
    const target = index + direction;
    if (target < 0 || target >= newSteps.length) return;
    [newSteps[index], newSteps[target]] = [newSteps[target], newSteps[index]];
    setSteps(newSteps);
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">
        {isNew ? "New Workflow" : "Edit Workflow"}
      </h1>

      {/* Basic Info */}
      <div className="bg-white rounded-xl border p-5 space-y-4 shadow-sm">
        <div>
          <label htmlFor="wf-name" className="block text-sm font-medium text-gray-700">Name</label>
          <input
            id="wf-name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label htmlFor="wf-desc" className="block text-sm font-medium text-gray-700">Description</label>
          <textarea
            id="wf-desc"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={2}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm resize-none"
          />
        </div>
      </div>

      {/* Inputs */}
      <div className="bg-white rounded-xl border p-5 space-y-3 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-sm">Inputs</h2>
          <button
            type="button"
            onClick={addInput}
            className="text-xs text-indigo-600 hover:underline"
          >
            + Add input
          </button>
        </div>
        {inputs.map((input, i) => (
          <div key={i} className="flex gap-2">
            <input
              placeholder="Key"
              value={input.key}
              onChange={(e) => {
                const updated = [...inputs];
                updated[i] = { ...updated[i], key: e.target.value };
                setInputs(updated);
              }}
              className="flex-1 rounded-lg border border-gray-300 px-3 py-1.5 text-sm"
            />
            <input
              placeholder="Value"
              value={input.value}
              onChange={(e) => {
                const updated = [...inputs];
                updated[i] = { ...updated[i], value: e.target.value };
                setInputs(updated);
              }}
              className="flex-1 rounded-lg border border-gray-300 px-3 py-1.5 text-sm"
            />
          </div>
        ))}
      </div>

      {/* Steps */}
      <div className="bg-white rounded-xl border p-5 space-y-3 shadow-sm">
        <h2 className="font-semibold text-sm">Steps</h2>
        {steps.map((step, i) => (
          <div
            key={step.id}
            className="border rounded-lg p-4 space-y-2 bg-gray-50"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">
                Step {i + 1}: {step.tool}
              </span>
              <div className="flex gap-1">
                <button type="button" onClick={() => moveStep(i, -1)} className="text-xs px-2 py-1 border rounded hover:bg-white">↑</button>
                <button type="button" onClick={() => moveStep(i, 1)} className="text-xs px-2 py-1 border rounded hover:bg-white">↓</button>
                <button type="button" onClick={() => removeStep(step.id)} className="text-xs px-2 py-1 border rounded text-red-600 hover:bg-red-50">✕</button>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div>
                <span className="text-gray-500">Args:</span>
                <code className="ml-1 bg-white px-1 rounded">{step.args}</code>
              </div>
              <div>
                <span className="text-gray-500">Risk:</span>
                <span
                  className={`ml-1 px-1.5 py-0.5 rounded font-medium ${
                    step.risk === "WRITE"
                      ? "bg-amber-100 text-amber-800"
                      : "bg-green-100 text-green-800"
                  }`}
                >
                  {step.risk}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Retry:</span>
                <span className="ml-1">{step.retryPolicy}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Scheduling */}
      <div className="bg-white rounded-xl border p-5 space-y-4 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-sm">Schedule</h2>
          <button
            type="button"
            onClick={() => setScheduleEnabled(!scheduleEnabled)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              scheduleEnabled ? "bg-indigo-600" : "bg-gray-300"
            }`}
          >
            <span
              className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                scheduleEnabled ? "translate-x-6" : "translate-x-1"
              }`}
            />
          </button>
        </div>
        {scheduleEnabled && (
          <div className="flex gap-4">
            <div className="flex-1">
              <label htmlFor="cron" className="block text-xs text-gray-500 mb-1">Cron expression</label>
              <input
                id="cron"
                value={cron}
                onChange={(e) => setCron(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-mono"
              />
            </div>
            <div className="flex-1">
              <label htmlFor="tz" className="block text-xs text-gray-500 mb-1">Timezone</label>
              <input
                id="tz"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-1.5 text-sm"
              />
            </div>
          </div>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex gap-3">
        <button
          type="button"
          className="flex-1 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700"
        >
          Save new version
        </button>
        <button
          type="button"
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Test run
        </button>
      </div>
    </div>
  );
}
