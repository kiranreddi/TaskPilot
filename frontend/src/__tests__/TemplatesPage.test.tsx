import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

jest.mock("next/navigation", () => ({
  usePathname: () => "/templates",
  useParams: () => ({}),
  redirect: jest.fn(),
}));

jest.mock("next/link", () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return React.createElement("a", { href }, children);
  };
});

import TemplatesPage from "@/app/(dashboard)/templates/page";

describe("Templates Page", () => {
  it("renders the heading", () => {
    render(React.createElement(TemplatesPage));
    expect(screen.getByText("Templates")).toBeInTheDocument();
  });

  it("renders all template cards", () => {
    render(React.createElement(TemplatesPage));
    [
      "Weekly Revenue Report",
      "Clean Inbox",
      "Meeting Follow-ups",
      "Sales Lead Research",
      "Project Status Rollup",
    ].forEach((name) => {
      expect(screen.getByText(name)).toBeInTheDocument();
    });
  });

  it("renders Use buttons for each template", () => {
    render(React.createElement(TemplatesPage));
    const useButtons = screen.getAllByText("Use");
    expect(useButtons).toHaveLength(5);
  });
});
