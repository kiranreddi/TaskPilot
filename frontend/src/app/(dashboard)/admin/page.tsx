"use client";

import { useState, useEffect } from "react";
import { admin as adminApi } from "@/lib/api";

interface Member {
  name: string;
  email: string;
  role: "admin" | "member" | "viewer";
}

const MOCK_MEMBERS: Member[] = [
  { name: "Alice Johnson", email: "alice@acme.com", role: "admin" },
  { name: "Bob Smith", email: "bob@acme.com", role: "member" },
  { name: "Carol Lee", email: "carol@acme.com", role: "viewer" },
];

interface IntegrationHealth {
  name: string;
  status: "healthy" | "degraded" | "down";
  lastCheck: string;
}

const MOCK_INTEGRATION_HEALTH: IntegrationHealth[] = [
  { name: "Google Workspace", status: "healthy", lastCheck: "2 mins ago" },
  { name: "Slack", status: "healthy", lastCheck: "1 min ago" },
  { name: "Stripe", status: "degraded", lastCheck: "5 mins ago" },
  { name: "Notion", status: "down", lastCheck: "10 mins ago" },
];

const HEALTH_STYLES: Record<string, string> = {
  healthy: "bg-green-100 text-green-800",
  degraded: "bg-amber-100 text-amber-800",
  down: "bg-red-100 text-red-800",
};

export default function AdminPage() {
  const [members, setMembers] = useState<Member[]>(MOCK_MEMBERS);
  const [approvalRequired, setApprovalRequired] = useState(true);
  const [allowedDomains, setAllowedDomains] = useState("acme.com");
  const [integrationHealth] = useState<IntegrationHealth[]>(MOCK_INTEGRATION_HEALTH);

  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        const [membersData, policiesData] = await Promise.all([
          adminApi.members().catch(() => null),
          adminApi.policies().catch(() => null),
        ]);

        if (cancelled) return;

        if (membersData && membersData.length > 0) {
          setMembers(membersData as Member[]);
        }
        if (policiesData) {
          setApprovalRequired(policiesData.require_approval_for_write);
          setAllowedDomains(policiesData.allowed_domains ?? "acme.com");
        }
      } catch {
        // API unavailable – keep mock data
      }
    }

    fetchData();
    return () => { cancelled = true; };
  }, []);

  async function handleToggleApproval() {
    const newValue = !approvalRequired;
    setApprovalRequired(newValue);
    try {
      await adminApi.updatePolicies({ require_approval_for_write: newValue });
    } catch {
      // API unavailable
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold">Admin</h1>

      {/* Org Members */}
      <div className="bg-white rounded-xl border shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b flex items-center justify-between">
          <h2 className="font-semibold text-sm">Organization Members</h2>
          <button
            type="button"
            className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700"
          >
            Invite member
          </button>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-700">Name</th>
              <th className="text-left px-4 py-3 font-medium text-gray-700">Email</th>
              <th className="text-left px-4 py-3 font-medium text-gray-700">Role</th>
              <th className="text-right px-4 py-3 font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {members.map((member) => (
              <tr key={member.email} className="hover:bg-gray-50">
                <td className="px-4 py-3">{member.name}</td>
                <td className="px-4 py-3 text-gray-500">{member.email}</td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 bg-gray-100 rounded text-xs font-medium">
                    {member.role}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    type="button"
                    className="rounded border border-red-300 px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
                  >
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Policy Settings */}
      <div className="bg-white rounded-xl border p-5 space-y-5 shadow-sm">
        <h2 className="font-semibold text-sm">Policy Settings</h2>

        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium">Require approval for WRITE actions</div>
            <div className="text-xs text-gray-500">All write operations need manual approval</div>
          </div>
          <button
            type="button"
            onClick={handleToggleApproval}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              approvalRequired ? "bg-indigo-600" : "bg-gray-300"
            }`}
          >
            <span
              className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
                approvalRequired ? "translate-x-6" : "translate-x-1"
              }`}
            />
          </button>
        </div>

        <div>
          <label htmlFor="domains" className="block text-sm font-medium text-gray-700 mb-1">
            Allowed email domains
          </label>
          <input
            id="domains"
            value={allowedDomains}
            onChange={(e) => setAllowedDomains(e.target.value)}
            placeholder="acme.com, partner.io"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
          />
          <p className="text-xs text-gray-400 mt-1">Comma-separated list of allowed domains</p>
        </div>
      </div>

      {/* Integration Health */}
      <div className="bg-white rounded-xl border p-5 shadow-sm">
        <h2 className="font-semibold text-sm mb-4">Integration Health Dashboard</h2>
        <div className="space-y-3">
          {integrationHealth.map((ih) => (
            <div key={ih.name} className="flex items-center justify-between">
              <span className="text-sm">{ih.name}</span>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-400">{ih.lastCheck}</span>
                <span
                  className={`px-2 py-0.5 rounded text-xs font-medium ${HEALTH_STYLES[ih.status]}`}
                >
                  {ih.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
