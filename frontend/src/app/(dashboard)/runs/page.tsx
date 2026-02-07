"use client";

import Link from "next/link";

interface Run {
  id: string;
  workflow: string;
  status: "completed" | "running" | "failed" | "cancelled";
  started: string;
  duration: string;
}

const RUNS: Run[] = [
  { id: "run-001", workflow: "Weekly Revenue Report", status: "completed", started: "2024-01-15 09:00", duration: "2m 14s" },
  { id: "run-002", workflow: "Clean Inbox", status: "completed", started: "2024-01-15 08:30", duration: "45s" },
  { id: "run-003", workflow: "Meeting Follow-ups", status: "running", started: "2024-01-15 10:00", duration: "—" },
  { id: "run-004", workflow: "Sales Lead Research", status: "failed", started: "2024-01-14 14:00", duration: "1m 02s" },
  { id: "run-005", workflow: "Project Status Rollup", status: "cancelled", started: "2024-01-14 09:00", duration: "30s" },
];

const STATUS_STYLES: Record<string, string> = {
  completed: "bg-green-100 text-green-800",
  running: "bg-blue-100 text-blue-800",
  failed: "bg-red-100 text-red-800",
  cancelled: "bg-gray-100 text-gray-800",
};

export default function RunsPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Runs</h1>

      <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-700">Run ID</th>
              <th className="text-left px-4 py-3 font-medium text-gray-700">Workflow</th>
              <th className="text-left px-4 py-3 font-medium text-gray-700">Status</th>
              <th className="text-left px-4 py-3 font-medium text-gray-700">Started</th>
              <th className="text-left px-4 py-3 font-medium text-gray-700">Duration</th>
              <th className="text-right px-4 py-3 font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {RUNS.map((run) => (
              <tr key={run.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-mono text-xs">{run.id}</td>
                <td className="px-4 py-3">{run.workflow}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_STYLES[run.status]}`}>
                    {run.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-500">{run.started}</td>
                <td className="px-4 py-3 text-gray-500">{run.duration}</td>
                <td className="px-4 py-3 text-right">
                  <Link
                    href={`/runs/${run.id}`}
                    className="rounded border border-gray-300 px-3 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50"
                  >
                    View
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
