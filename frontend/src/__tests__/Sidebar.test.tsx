import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

// Mock next/navigation
jest.mock("next/navigation", () => ({
  usePathname: () => "/chat",
  useParams: () => ({ id: "test-123" }),
  redirect: jest.fn(),
}));

// Mock next/link
jest.mock("next/link", () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return React.createElement("a", { href }, children);
  };
});

import Sidebar from "@/components/Sidebar";

describe("Sidebar", () => {
  it("renders the TaskPilot brand", () => {
    render(React.createElement(Sidebar));
    expect(screen.getByText("TaskPilot")).toBeInTheDocument();
  });

  it("renders all navigation links", () => {
    render(React.createElement(Sidebar));
    const labels = ["Chat", "Workflows", "Templates", "Runs", "Integrations", "Billing", "Admin"];
    labels.forEach((label) => {
      expect(screen.getByText(label)).toBeInTheDocument();
    });
  });

  it("renders user avatar section", () => {
    render(React.createElement(Sidebar));
    expect(screen.getByText("User")).toBeInTheDocument();
    expect(screen.getByText("user@example.com")).toBeInTheDocument();
  });
});
