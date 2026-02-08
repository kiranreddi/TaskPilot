import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";

jest.mock("next/navigation", () => ({
  usePathname: () => "/chat",
  useParams: () => ({}),
  redirect: jest.fn(),
}));

jest.mock("next/link", () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return React.createElement("a", { href }, children);
  };
});

jest.mock("@/lib/api", () => ({
  workflows: {
    create: jest.fn().mockRejectedValue(new Error("API unavailable")),
    run: jest.fn().mockRejectedValue(new Error("API unavailable")),
  },
}));

import ChatPage from "@/app/(dashboard)/chat/page";

describe("Chat Page", () => {
  it("renders the prompt textarea", () => {
    render(React.createElement(ChatPage));
    expect(
      screen.getByPlaceholderText("Ask TaskPilot to do something across your apps…")
    ).toBeInTheDocument();
  });

  it("renders the Run button", () => {
    render(React.createElement(ChatPage));
    expect(screen.getByText("Run")).toBeInTheDocument();
  });

  it("renders app chips", () => {
    render(React.createElement(ChatPage));
    ["Google", "Slack", "Notion", "Stripe"].forEach((app) => {
      expect(screen.getByText(app)).toBeInTheDocument();
    });
  });

  it("renders read-only toggle", () => {
    render(React.createElement(ChatPage));
    expect(screen.getByText("Read-only mode")).toBeInTheDocument();
  });

  it("shows plan modal when Run is clicked with prompt", async () => {
    render(React.createElement(ChatPage));
    const textarea = screen.getByPlaceholderText(
      "Ask TaskPilot to do something across your apps…"
    );
    fireEvent.change(textarea, { target: { value: "test prompt" } });
    fireEvent.click(screen.getByText("Run"));
    await waitFor(() => {
      expect(screen.getByText("Here's what I will do")).toBeInTheDocument();
    });
    expect(screen.getByText("Approve & Run")).toBeInTheDocument();
  });
});
