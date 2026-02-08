# TaskPilot — Frontend Deployment (Cloudflare Pages)

> Deploy the TaskPilot Next.js frontend to Cloudflare Pages.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Option 1: Cloudflare Pages via Git Integration](#option-1-cloudflare-pages-via-git-integration)
3. [Option 2: Cloudflare Pages via Wrangler CLI](#option-2-cloudflare-pages-via-wrangler-cli)
4. [Custom Domain Setup](#custom-domain-setup)
5. [Environment Variables Configuration](#environment-variables-configuration)
6. [Cloudflare Pages Settings & Limits](#cloudflare-pages-settings--limits)
7. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## Prerequisites

| Requirement          | Details                                    |
| -------------------- | ------------------------------------------ |
| Cloudflare account   | Free tier is sufficient                    |
| GitHub repository    | TaskPilot repo pushed to GitHub            |
| Node.js 20+         | Required for local builds                  |
| Custom domain        | Optional — Cloudflare provides a `.pages.dev` subdomain |
| Backend deployed     | The API must be accessible from the internet |

---

## Option 1: Cloudflare Pages via Git Integration

This is the recommended approach. Cloudflare Pages automatically builds and deploys on every push to your main branch.

### Step 1 — Connect Your GitHub Repository

1. Log in to the [Cloudflare Dashboard](https://dash.cloudflare.com).
2. Navigate to **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**.
3. Authorise Cloudflare to access your GitHub account.
4. Select the **TaskPilot** repository.
5. Click **Begin setup**.

### Step 2 — Configure Build Settings

| Setting                | Value                                               |
| ---------------------- | --------------------------------------------------- |
| **Project name**       | `taskpilot` (or your preferred name)                |
| **Production branch**  | `main`                                              |
| **Framework preset**   | `Next.js`                                           |
| **Build command**      | `cd frontend && npm ci && npm run build`            |
| **Build output directory** | `frontend/.next`                                |
| **Root directory**     | `/` (leave as default)                              |

### Step 3 — Set Environment Variables

Before the first build, add these environment variables in the Cloudflare Pages settings:

| Variable              | Value                              | Environment  |
| --------------------- | ---------------------------------- | ------------ |
| `NEXT_PUBLIC_API_URL`  | `https://api.taskpilot.example`   | Production   |
| `NEXT_PUBLIC_API_URL`  | `https://api-staging.taskpilot.example` | Preview |
| `NODE_VERSION`         | `20`                              | All          |

### Step 4 — Deploy

1. Click **Save and Deploy**.
2. Cloudflare Pages clones your repo, runs the build command, and deploys the output.
3. Your site is available at `https://taskpilot.pages.dev` (or your custom project name).

### Automatic Deployments

- **Production:** Every push to `main` triggers a new production deployment.
- **Preview:** Every push to other branches or pull requests gets a unique preview URL (e.g., `https://abc123.taskpilot.pages.dev`).

---

## Option 2: Cloudflare Pages via Wrangler CLI

Use this approach for manual deployments or CI/CD pipelines.

### Step 1 — Install Wrangler

```bash
npm install -g wrangler

# Authenticate with Cloudflare
wrangler login
```

### Step 2 — Build Locally

```bash
cd frontend
npm ci
npm run build
```

### Step 3 — Create the Pages Project (First Time Only)

```bash
wrangler pages project create taskpilot
```

### Step 4 — Deploy

```bash
wrangler pages deploy frontend/.next --project-name taskpilot
```

### Step 5 — Set Environment Variables via CLI

```bash
# Production
wrangler pages secret put NEXT_PUBLIC_API_URL --project-name taskpilot
# When prompted, enter: https://api.taskpilot.example
```

### CI/CD Integration (GitHub Actions Example)

Add this to your `.github/workflows/deploy-frontend.yml`:

```yaml
name: Deploy Frontend to Cloudflare Pages

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: cd frontend && npm ci

      - name: Build
        run: cd frontend && npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ vars.NEXT_PUBLIC_API_URL }}

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy frontend/.next --project-name taskpilot
```

---

## Custom Domain Setup

### Step 1 — Add the Domain to Cloudflare

1. In the Cloudflare Dashboard, go to **Workers & Pages** → your project → **Custom domains**.
2. Click **Set up a custom domain**.
3. Enter your domain (e.g., `app.taskpilot.com`).

### Step 2 — Configure DNS

If your domain is already on Cloudflare DNS:
- Cloudflare automatically creates the required CNAME record.

If your domain is on an external DNS provider:
- Add a CNAME record pointing to `taskpilot.pages.dev`.

```
Type:  CNAME
Name:  app
Value: taskpilot.pages.dev
TTL:   Auto
Proxy: Enabled (orange cloud)
```

### Step 3 — SSL/TLS

Cloudflare automatically provisions an SSL certificate for your custom domain. This typically takes a few minutes.

- **SSL mode:** Full (strict) — recommended
- **Always Use HTTPS:** Enable in the Cloudflare SSL/TLS settings

---

## Environment Variables Configuration

### Build-Time Variables

These are embedded into the JavaScript bundle during build:

| Variable               | Description                        | Required |
| ---------------------- | ---------------------------------- | -------- |
| `NEXT_PUBLIC_API_URL`  | Full URL of the TaskPilot backend API | Yes   |
| `NODE_VERSION`         | Node.js version for the build      | Yes (set to `20`) |

### Setting Variables in Cloudflare Dashboard

1. Go to **Workers & Pages** → your project → **Settings** → **Environment variables**.
2. Add variables for **Production** and/or **Preview** environments.
3. Click **Save**.
4. Trigger a new deployment for changes to take effect (variables are embedded at build time).

### Important Notes

- `NEXT_PUBLIC_` prefixed variables are exposed to the browser. Do NOT put secrets here.
- Backend API URL must be publicly accessible with CORS configured for your frontend domain.
- Changes to environment variables require a new deployment to take effect.

---

## Cloudflare Pages Settings & Limits

### Free Tier Limits

| Resource             | Limit                      |
| -------------------- | -------------------------- |
| Builds per month     | 500                        |
| Concurrent builds    | 1                          |
| Max build time       | 20 minutes                 |
| Max site size        | 25 MiB (per file), 20,000 files |
| Bandwidth            | Unlimited                  |
| Requests             | Unlimited                  |
| Custom domains       | 100 per project            |

### Recommended Settings

| Setting              | Value                      |
| -------------------- | -------------------------- |
| Build system version | v2                         |
| Node.js version      | 20.x                       |
| Build caching        | Enabled (speeds up builds) |

### Build Caching

Cloudflare Pages caches `node_modules` between builds. To bust the cache:

1. Go to **Settings** → **Builds & deployments**.
2. Click **Clear build cache**.
3. Trigger a new deployment.

---

## Troubleshooting Common Issues

### Build Fails: "Cannot find module"

**Cause:** Dependencies not installed or wrong working directory.

**Fix:** Ensure the build command starts with `cd frontend &&`:

```
cd frontend && npm ci && npm run build
```

### Build Fails: "Node.js version too old"

**Cause:** Cloudflare Pages defaults to an older Node.js version.

**Fix:** Set the `NODE_VERSION` environment variable to `20`.

### 404 on Page Refresh (Client-Side Routing)

**Cause:** Next.js uses dynamic routes that Cloudflare Pages doesn't know about.

**Fix:** Next.js on Cloudflare Pages handles this automatically with the `@cloudflare/next-on-pages` adapter. If you're using static export, add a `_redirects` file:

```
/*    /index.html   200
```

### API Calls Fail with CORS Error

**Cause:** The backend doesn't allow requests from the Cloudflare Pages domain.

**Fix:** Add the Cloudflare Pages domain to the backend's CORS configuration:

```python
# In backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://taskpilot.pages.dev",
        "https://app.taskpilot.com",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variable Not Available at Runtime

**Cause:** `NEXT_PUBLIC_` variables are embedded at build time, not runtime.

**Fix:** Redeploy after changing environment variables. Variables without the `NEXT_PUBLIC_` prefix are only available during the build process, not in the browser.

### Build Timeout (>20 minutes)

**Cause:** Large dependency tree or slow network.

**Fix:**
1. Ensure you're using `npm ci` (not `npm install`) for faster installs.
2. Enable build caching in Cloudflare Pages settings.
3. Consider reducing bundle size by analysing with `npm run build -- --analyze`.

### Preview Deployments Not Working

**Cause:** Preview environments may have different or missing environment variables.

**Fix:** Add environment variables for the **Preview** environment separately in Cloudflare Pages settings.
