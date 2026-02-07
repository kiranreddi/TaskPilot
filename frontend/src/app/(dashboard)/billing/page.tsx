"use client";

export default function BillingPage() {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Billing</h1>

      {/* Plan Card */}
      <div className="bg-white rounded-xl border p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-semibold">Pro Plan</h2>
            <p className="text-sm text-gray-500 mt-1">$49/month · Billed monthly</p>
          </div>
          <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium">
            Active
          </span>
        </div>
      </div>

      {/* Usage Meters */}
      <div className="bg-white rounded-xl border p-6 shadow-sm space-y-5">
        <h2 className="font-semibold">Usage this month</h2>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-700">Runs</span>
            <span className="text-gray-500">142 / 500</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-600 rounded-full"
              style={{ width: "28.4%" }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-700">Tokens</span>
            <span className="text-gray-500">1.2M / 3M</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-600 rounded-full"
              style={{ width: "40%" }}
            />
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <button
          type="button"
          className="flex-1 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700"
        >
          Upgrade
        </button>
        <button
          type="button"
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Manage billing
        </button>
      </div>
    </div>
  );
}
