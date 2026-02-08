"use client";

import { useEffect, useState } from "react";
import { auth } from "./api";

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    const token =
      typeof window !== "undefined" ? localStorage.getItem("token") : null;

    if (!token) {
      setLoading(false);
      return;
    }

    auth
      .me()
      .then((data) => {
        if (!cancelled) setUser(data);
      })
      .catch(() => {
        // token invalid – clear it
        if (!cancelled && typeof window !== "undefined") {
          localStorage.removeItem("token");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const isAuthenticated = !!user;

  return { user, loading, isAuthenticated };
}
