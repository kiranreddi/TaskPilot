import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";

jest.mock("next/navigation", () => ({
  usePathname: () => "/integrations",
  useParams: () => ({}),
  redirect: jest.fn(),
}));

jest.mock("next/link", () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return React.createElement("a", { href }, children);
  };
});

import IntegrationsPage from "@/app/(dashboard)/integrations/page";

describe("Integrations Page", () => {
  it("renders the heading", () => {
    render(React.createElement(IntegrationsPage));
    expect(screen.getByText("Integrations")).toBeInTheDocument();
  });

  it("renders search input", () => {
    render(React.createElement(IntegrationsPage));
    expect(screen.getByPlaceholderText("Search integrations…")).toBeInTheDocument();
  });

  it("renders all integration cards", () => {
    render(React.createElement(IntegrationsPage));
    ["Google Workspace", "Slack", "Notion", "Stripe", "HubSpot"].forEach((name) => {
      expect(screen.getByText(name)).toBeInTheDocument();
    });
  });

  it("filters integrations by search", () => {
    render(React.createElement(IntegrationsPage));
    const input = screen.getByPlaceholderText("Search integrations…");
    fireEvent.change(input, { target: { value: "slack" } });
    expect(screen.getByText("Slack")).toBeInTheDocument();
    expect(screen.queryByText("Notion")).not.toBeInTheDocument();
  });

  it("shows connection details modal for connected integrations", () => {
    render(React.createElement(IntegrationsPage));
    const connectedButtons = screen.getAllByText("Connected ✅");
    fireEvent.click(connectedButtons[0]);
    expect(screen.getByText("Reconnect")).toBeInTheDocument();
    expect(screen.getByText("Disconnect")).toBeInTheDocument();
  });
});
