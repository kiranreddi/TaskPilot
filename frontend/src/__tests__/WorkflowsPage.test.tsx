import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

jest.mock("next/navigation", () => ({
  usePathname: () => "/workflows",
  useParams: () => ({}),
  redirect: jest.fn(),
}));

jest.mock("next/link", () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return React.createElement("a", { href }, children);
  };
});

import WorkflowsPage from "@/app/(dashboard)/workflows/page";

describe("Workflows Page", () => {
  it("renders the heading", () => {
    render(React.createElement(WorkflowsPage));
    expect(screen.getByText("Workflows")).toBeInTheDocument();
  });

  it("renders workflow rows", () => {
    render(React.createElement(WorkflowsPage));
    expect(screen.getByText("Weekly Revenue Report")).toBeInTheDocument();
    expect(screen.getByText("Clean Inbox")).toBeInTheDocument();
  });

  it("renders table headers", () => {
    render(React.createElement(WorkflowsPage));
    ["Name", "Tags", "Last run", "Status", "Actions"].forEach((header) => {
      expect(screen.getByText(header)).toBeInTheDocument();
    });
  });
});
