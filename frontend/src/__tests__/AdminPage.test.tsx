import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

jest.mock("next/navigation", () => ({
  usePathname: () => "/admin",
  useParams: () => ({}),
  redirect: jest.fn(),
}));

import AdminPage from "@/app/(dashboard)/admin/page";

describe("Admin Page", () => {
  it("renders the heading", () => {
    render(React.createElement(AdminPage));
    expect(screen.getByText("Admin")).toBeInTheDocument();
  });

  it("renders org members table", () => {
    render(React.createElement(AdminPage));
    expect(screen.getByText("Alice Johnson")).toBeInTheDocument();
    expect(screen.getByText("bob@acme.com")).toBeInTheDocument();
  });

  it("renders invite button", () => {
    render(React.createElement(AdminPage));
    expect(screen.getByText("Invite member")).toBeInTheDocument();
  });

  it("renders policy settings", () => {
    render(React.createElement(AdminPage));
    expect(screen.getByText("Require approval for WRITE actions")).toBeInTheDocument();
    expect(screen.getByText("Allowed email domains")).toBeInTheDocument();
  });

  it("renders integration health dashboard", () => {
    render(React.createElement(AdminPage));
    expect(screen.getByText("Integration Health Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Google Workspace")).toBeInTheDocument();
  });
});
