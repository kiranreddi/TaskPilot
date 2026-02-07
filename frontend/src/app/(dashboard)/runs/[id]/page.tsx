"use client";

import { useParams } from "next/navigation";

interface RunStep {
  name: string;
  status: "completed" | "running" | "pending" | "failed";
  output?: string;
}

const STEPS: RunStep[] = [
  { name: "Search Gmail for billing emails", status: "completed", output: "Found 23 emails" },
  { name: "Summarize totals by vendor", status: "completed", output: "5 vendors totaling $12,450" },
  { name: "Post summary to Slack #finance", status: "completed", output: "Message posted" },
];

const ARTIFACTS = [
  { name: "summary.md", url: "#" },
  { name: "report.pdf", url: "#" },
];

const RETRIES = [
  { attempt: 1, status: "failed", at: "2024-01-15 09:01" },
  { attempt: 2, status: "success", at: "2024-01-15 09:02" },
];

const STATUS_ICONS: Record<string, string> = {
  completed: "✅",
  running: "🔄",
  pending: "⏳",
  failed: "❌",
};

export default function RunDetailPage() {
  const params = useParams();
  const runId = params.id as string;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Run {runId}</h1>
        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
          completed
        </span>
      </div>

      {/* Step Timeline */}
      <div className="bg-white rounded-xl border p-5 shadow-sm">
        <h2 className="font-semibold text-sm mb-4">Steps</h2>
        <div className="space-y-3">
          {STEPS.map((step, i) => (
            <div key={i} className="flex items-start gap-3">
              <span className="text-lg">{STATUS_ICONS[step.status]}</span>
              <div>
                <div className="text-sm font-medium">{step.name}</div>
                {step.output && (
                  <div className="text-xs text-gray-500 mt-0.5">{step.output}</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Artifacts */}
      <div className="bg-white rounded-xl border p-5 shadow-sm">
        <h2 className="font-semibold text-sm mb-3">Artifacts</h2>
        <div className="space-y-2">
          {ARTIFACTS.map((artifact) => (
            <a
              key={artifact.name}
              href={artifact.url}
              className="flex items-center gap-2 text-sm text-indigo-600 hover:underline"
            >
              📎 {artifact.name}
            </a>
          ))}
        </div>
      </div>

      {/* Retry History */}
      <div className="bg-white rounded-xl border p-5 shadow-sm">
        <h2 className="font-semibold text-sm mb-3">Retry History</h2>
        <div className="space-y-2">
          {RETRIES.map((retry) => (
            <div key={retry.attempt} className="flex items-center gap-3 text-sm">
              <span className="text-gray-500">Attempt {retry.attempt}</span>
              <span
                className={`px-2 py-0.5 rounded text-xs font-medium ${
                  retry.status === "success"
                    ? "bg-green-100 text-green-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {retry.status}
              </span>
              <span className="text-gray-400 text-xs">{retry.at}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Output Summary */}
      <div className="bg-white rounded-xl border p-5 shadow-sm">
        <h2 className="font-semibold text-sm mb-3">Output Summary</h2>
        <p className="text-sm text-gray-600">
          Successfully processed 23 billing emails, summarized revenue across 5 vendors
          totaling $12,450, and posted the summary to Slack #finance channel.
        </p>
      </div>
    </div>
  );
}
