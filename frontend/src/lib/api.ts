const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

export function setToken(token: string) {
  localStorage.setItem("token", token);
}

export function clearToken() {
  localStorage.removeItem("token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || res.statusText);
  }
  return res.json() as Promise<T>;
}

// Auth
export const auth = {
  signup: (data: { email: string; password: string; name: string }) =>
    request<{ token: string }>("/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  login: (data: { email: string; password: string }) =>
    request<{ token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  me: () => request<{ id: string; email: string; name: string; role: string }>("/me"),
};

// Integrations
export const integrations = {
  list: () =>
    request<
      { provider: string; name: string; description: string; icon: string }[]
    >("/integrations"),
  connections: () =>
    request<
      {
        provider: string;
        status: string;
        scopes: string[];
        last_healthy: string;
      }[]
    >("/connections"),
  connect: (provider: string) =>
    request<{ redirect_url: string }>(`/connections/${provider}/start`, {
      method: "POST",
    }),
};

// Workflows
export const workflows = {
  list: () =>
    request<
      {
        id: string;
        name: string;
        tags: string[];
        last_run: string;
        status: string;
      }[]
    >("/workflows"),
  create: (data: {
    source: "nl" | "template";
    prompt?: string;
    template_id?: string;
  }) =>
    request<{ id: string }>("/workflows", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  run: (workflowId: string, data?: { inputs?: Record<string, unknown>; approvals?: Record<string, unknown> }) =>
    request<{ run_id: string }>(`/workflows/${workflowId}/run`, {
      method: "POST",
      body: JSON.stringify(data ?? {}),
    }),
};

// Runs
export const runs = {
  get: (runId: string) =>
    request<{
      id: string;
      workflow: string;
      status: string;
      started: string;
      duration: string;
      steps: { name: string; status: string; output?: string }[];
      artifacts: { name: string; url: string }[];
      retries: { attempt: number; status: string; at: string }[];
    }>(`/runs/${runId}`),
  cancel: (runId: string) =>
    request<{ ok: boolean }>(`/runs/${runId}/cancel`, { method: "POST" }),
};

// Templates
export const templates = {
  list: () =>
    request<
      { id: string; name: string; description: string; tags: string[] }[]
    >("/templates"),
};

// Billing
export const billing = {
  webhook: (payload: unknown) =>
    request<{ ok: boolean }>("/billing/webhook", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
