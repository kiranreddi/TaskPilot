"use client";

import { useState, useEffect } from "react";
import {
  integrations as integrationsApi,
} from "@/lib/api";

interface Integration {
  provider: string;
  name: string;
  description: string;
  icon: string;
  connected: boolean;
  scopes?: string[];
  lastHealthy?: string;
}

const MOCK_INTEGRATIONS: Integration[] = [
  {
    provider: "google",
    name: "Google Workspace",
    description: "Gmail, Calendar, Drive, Sheets",
    icon: "🔵",
    connected: true,
    scopes: ["gmail.read", "calendar.write", "drive.read"],
    lastHealthy: "2 mins ago",
  },
  {
    provider: "slack",
    name: "Slack",
    description: "Messaging, channels, notifications",
    icon: "💜",
    connected: false,
  },
  {
    provider: "notion",
    name: "Notion",
    description: "Docs, databases, wikis",
    icon: "⬛",
    connected: false,
  },
  {
    provider: "stripe",
    name: "Stripe",
    description: "Payments, invoices, subscriptions",
    icon: "🟣",
    connected: true,
    scopes: ["read_write"],
    lastHealthy: "5 mins ago",
  },
  {
    provider: "hubspot",
    name: "HubSpot",
    description: "CRM, contacts, deals",
    icon: "🟠",
    connected: false,
  },
];

export default function IntegrationsPage() {
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Integration | null>(null);
  const [integrationsList, setIntegrationsList] = useState<Integration[]>(MOCK_INTEGRATIONS);

  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        const [available, connections] = await Promise.all([
          integrationsApi.list(),
          integrationsApi.connections().catch(() => []),
        ]);

        if (cancelled) return;

        const connMap = new Map(
          connections.map((c) => [c.provider, c])
        );

        if (available.length > 0) {
          setIntegrationsList(
            available.map((a) => {
              const conn = connMap.get(a.provider);
              return {
                provider: a.provider,
                name: a.name,
                description: a.description,
                icon: a.icon,
                connected: !!conn,
                scopes: conn?.scopes,
                lastHealthy: conn?.last_healthy,
              };
            })
          );
        }
      } catch {
        // API unavailable – keep mock data
      }
    }

    fetchData();
    return () => { cancelled = true; };
  }, []);

  async function handleConnect(provider: string) {
    try {
      const result = await integrationsApi.connect(provider);
      window.location.href = result.redirect_url;
    } catch {
      // API unavailable
    }
  }

  const filtered = integrationsList.filter(
    (i) =>
      i.name.toLowerCase().includes(search.toLowerCase()) ||
      i.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Integrations</h1>

      <input
        type="text"
        placeholder="Search integrations…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full max-w-md rounded-lg border border-gray-300 px-4 py-2 text-sm mb-6 focus:border-indigo-500 focus:ring-indigo-500"
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((integration) => (
          <div
            key={integration.provider}
            className="bg-white rounded-xl border p-5 flex flex-col gap-3 shadow-sm"
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{integration.icon}</span>
              <div>
                <h3 className="font-semibold text-sm">{integration.name}</h3>
                <p className="text-xs text-gray-500">{integration.description}</p>
              </div>
            </div>
            <div className="flex gap-2 mt-auto">
              {integration.connected ? (
                <button
                  type="button"
                  onClick={() => setSelected(integration)}
                  className="flex-1 rounded-lg bg-green-50 border border-green-200 px-3 py-1.5 text-xs font-medium text-green-700"
                >
                  Connected ✅
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => handleConnect(integration.provider)}
                  className="flex-1 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700"
                >
                  Connect
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Connection Details Modal */}
      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold">
                {selected.name} — Connected ✅
              </h2>
              <button
                type="button"
                onClick={() => setSelected(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-1">Scopes</h3>
              <div className="flex flex-wrap gap-1">
                {selected.scopes?.map((scope) => (
                  <span
                    key={scope}
                    className="px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600"
                  >
                    {scope}
                  </span>
                ))}
              </div>
            </div>

            <div className="text-sm text-gray-500">
              Last healthy: {selected.lastHealthy}
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => { handleConnect(selected.provider); setSelected(null); }}
                className="flex-1 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
              >
                Reconnect
              </button>
              <button
                type="button"
                onClick={() => setSelected(null)}
                className="flex-1 rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
              >
                Disconnect
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
