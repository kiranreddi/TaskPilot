"use client";

interface Template {
  id: string;
  name: string;
  description: string;
  tags: string[];
}

const TEMPLATES: Template[] = [
  {
    id: "tpl-1",
    name: "Weekly Revenue Report",
    description: "Pull Stripe data → Google Sheets → PDF → Post to Slack",
    tags: ["finance", "stripe", "slack"],
  },
  {
    id: "tpl-2",
    name: "Clean Inbox",
    description: "Archive, label, and summarize Gmail messages",
    tags: ["email", "gmail"],
  },
  {
    id: "tpl-3",
    name: "Meeting Follow-ups",
    description: "Calendar events → Notion action items → Slack reminders",
    tags: ["meetings", "notion", "slack"],
  },
  {
    id: "tpl-4",
    name: "Sales Lead Research",
    description: "Enrich HubSpot leads with web research and summaries",
    tags: ["sales", "hubspot"],
  },
  {
    id: "tpl-5",
    name: "Project Status Rollup",
    description: "Aggregate task statuses from Notion → Slack summary",
    tags: ["projects", "notion", "slack"],
  },
];

export default function TemplatesPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Templates</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {TEMPLATES.map((tpl) => (
          <div
            key={tpl.id}
            className="bg-white rounded-xl border p-5 flex flex-col gap-3 shadow-sm"
          >
            <h3 className="font-semibold text-sm">{tpl.name}</h3>
            <p className="text-xs text-gray-500 flex-1">{tpl.description}</p>
            <div className="flex flex-wrap gap-1">
              {tpl.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600"
                >
                  {tag}
                </span>
              ))}
            </div>
            <button
              type="button"
              className="w-full rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700"
            >
              Use
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
