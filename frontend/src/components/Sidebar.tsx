"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/chat", label: "Chat", icon: "💬" },
  { href: "/workflows", label: "Workflows", icon: "⚙️" },
  { href: "/templates", label: "Templates", icon: "📄" },
  { href: "/runs", label: "Runs", icon: "▶️" },
  { href: "/integrations", label: "Integrations", icon: "🔌" },
  { href: "/billing", label: "Billing", icon: "💳" },
  { href: "/admin", label: "Admin", icon: "🛡️" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex flex-col w-56 min-h-screen bg-gray-900 text-white">
      <div className="px-5 py-6 text-xl font-bold tracking-tight">
        TaskPilot
      </div>

      <nav className="flex-1 px-3 space-y-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? "bg-indigo-600 text-white"
                  : "text-gray-300 hover:bg-gray-800 hover:text-white"
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="px-5 py-4 border-t border-gray-700 flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-sm font-bold">
          U
        </div>
        <div className="text-sm">
          <div className="font-medium">User</div>
          <div className="text-gray-400 text-xs">user@example.com</div>
        </div>
      </div>
    </aside>
  );
}
