"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { workflows as workflowsApi } from "@/lib/api";

interface Workflow {
  id: string;
  name: string;
  tags: string[];
  lastRun: string;
  status: "success" | "failed" | "running";
}

const MOCK_WORKFLOWS: Workflow[] = [
  { id: "wf-1", name: "Weekly Revenue Report", tags: ["finance", "weekly"], lastRun: "2h ago", status: "success" },
  { id: "wf-2", name: "Clean Inbox", tags: ["email"], lastRun: "1d ago", status: "success" },
  { id: "wf-3", name: "Meeting Follow-ups", tags: ["meetings", "slack"], lastRun: "3h ago", status: "running" },
  { id: "wf-4", name: "Sales Lead Research", tags: ["sales", "crm"], lastRun: "5h ago", status: "failed" },
  { id: "wf-5", name: "Project Status Rollup", tags: ["projects"], lastRun: "12h ago", status: "success" },
];

const STATUS_STYLES: Record<string, string> = {
  success: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
  running: "bg-blue-100 text-blue-800",
};

export default function WorkflowsPage() {
  const [workflowsList, setWorkflowsList] = useState<Workflow[]>(MOCK_WORKFLOWS);

  useEffect(() => {
    let cancelled = false;
    workflowsApi
      .list()
      .then((data) => {
        if (!cancelled && data.length > 0) {
          setWorkflowsList(
            data.map((w) => ({
              id: w.id,
              name: w.name,
              tags: w.tags ?? [],
              lastRun: w.last_run ?? "—",
              status: (w.status ?? "success") as Workflow["status"],
            }))
          );
        }
      })
      .catch(() => {});
    return () => { cancelled = true; };
  }, []);

  async function handleRun(workflowId: string) {
    try {
      await workflowsApi.run(workflowId);
    } catch {
      // API unavailable
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Workflows</h1>
        <Link
          href="/workflows/new"
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          + New Workflow
        </Link>
      </div>

      <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-700">Name</th>
              <th className="text-left px-4 py-3 font-medium text-gray-700">Tags</th>
              <th className="text-left px-4 py-3 font-medium text-gray-700">Last run</th>
              <th className="text-left px-4 py-3 font-medium text-gray-700">Status</th>
              <th className="text-right px-4 py-3 font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {workflowsList.map((wf) => (
              <tr key={wf.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{wf.name}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-1">
                    {wf.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-500">{wf.lastRun}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_STYLES[wf.status]}`}>
                    {wf.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-right space-x-2">
                  <button
                    type="button"
                    onClick={() => handleRun(wf.id)}
                    className="rounded border border-gray-300 px-3 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Run
                  </button>
                  <Link
                    href={`/workflows/${wf.id}`}
                    className="rounded border border-gray-300 px-3 py-1 text-xs font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Edit
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
