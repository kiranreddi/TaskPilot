import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

jest.mock("next/navigation", () => ({
  usePathname: () => "/runs",
  useParams: () => ({ id: "run-001" }),
  redirect: jest.fn(),
}));

jest.mock("next/link", () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return React.createElement("a", { href }, children);
  };
});

import RunsPage from "@/app/(dashboard)/runs/page";
import RunDetailPage from "@/app/(dashboard)/runs/[id]/page";

describe("Runs Page", () => {
  it("renders the heading", () => {
    render(React.createElement(RunsPage));
    expect(screen.getByText("Runs")).toBeInTheDocument();
  });

  it("renders run rows", () => {
    render(React.createElement(RunsPage));
    expect(screen.getByText("run-001")).toBeInTheDocument();
    expect(screen.getByText("run-004")).toBeInTheDocument();
  });

  it("renders View buttons", () => {
    render(React.createElement(RunsPage));
    const viewButtons = screen.getAllByText("View");
    expect(viewButtons.length).toBeGreaterThan(0);
  });
});

describe("Run Detail Page", () => {
  it("renders the run id", () => {
    render(React.createElement(RunDetailPage));
    expect(screen.getByText("Run run-001")).toBeInTheDocument();
  });

  it("renders steps", () => {
    render(React.createElement(RunDetailPage));
    expect(screen.getByText("Search Gmail for billing emails")).toBeInTheDocument();
  });

  it("renders artifacts", () => {
    render(React.createElement(RunDetailPage));
    expect(screen.getByText("📎 summary.md")).toBeInTheDocument();
    expect(screen.getByText("📎 report.pdf")).toBeInTheDocument();
  });

  it("renders retry history", () => {
    render(React.createElement(RunDetailPage));
    expect(screen.getByText("Attempt 1")).toBeInTheDocument();
    expect(screen.getByText("Attempt 2")).toBeInTheDocument();
  });
});
