import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

jest.mock("next/navigation", () => ({
  usePathname: () => "/billing",
  useParams: () => ({}),
  redirect: jest.fn(),
}));

import BillingPage from "@/app/(dashboard)/billing/page";

describe("Billing Page", () => {
  it("renders the heading", () => {
    render(React.createElement(BillingPage));
    expect(screen.getByText("Billing")).toBeInTheDocument();
  });

  it("renders plan info", () => {
    render(React.createElement(BillingPage));
    expect(screen.getByText("Pro Plan")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("renders usage meters", () => {
    render(React.createElement(BillingPage));
    expect(screen.getByText("142 / 500")).toBeInTheDocument();
    expect(screen.getByText("1.2M / 3M")).toBeInTheDocument();
  });

  it("renders action buttons", () => {
    render(React.createElement(BillingPage));
    expect(screen.getByText("Upgrade")).toBeInTheDocument();
    expect(screen.getByText("Manage billing")).toBeInTheDocument();
  });
});
