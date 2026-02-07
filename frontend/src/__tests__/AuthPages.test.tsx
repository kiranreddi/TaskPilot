import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";

jest.mock("next/navigation", () => ({
  usePathname: () => "/login",
  useParams: () => ({}),
  redirect: jest.fn(),
}));

jest.mock("next/link", () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return React.createElement("a", { href }, children);
  };
});

import LoginPage from "@/app/(auth)/login/page";
import SignupPage from "@/app/(auth)/signup/page";

describe("Login Page", () => {
  it("renders login form", () => {
    render(React.createElement(LoginPage));
    expect(screen.getByText("Sign in to your account")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
  });

  it("renders sign in button", () => {
    render(React.createElement(LoginPage));
    expect(screen.getByText("Sign in")).toBeInTheDocument();
  });

  it("renders Google button", () => {
    render(React.createElement(LoginPage));
    expect(screen.getByText("Continue with Google")).toBeInTheDocument();
  });

  it("renders signup link", () => {
    render(React.createElement(LoginPage));
    expect(screen.getByText("Sign up")).toBeInTheDocument();
  });
});

describe("Signup Page", () => {
  it("renders signup form", () => {
    render(React.createElement(SignupPage));
    expect(screen.getByText("Create your account")).toBeInTheDocument();
    expect(screen.getByLabelText("Name")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
  });

  it("renders create account button", () => {
    render(React.createElement(SignupPage));
    expect(screen.getByText("Create account")).toBeInTheDocument();
  });

  it("renders Google button", () => {
    render(React.createElement(SignupPage));
    expect(screen.getByText("Continue with Google")).toBeInTheDocument();
  });
});
