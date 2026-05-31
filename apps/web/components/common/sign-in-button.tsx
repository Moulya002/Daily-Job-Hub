"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";

type SignInButtonProps = {
  callbackUrl?: string;
  size?: "sm" | "default";
  githubConfigured: boolean;
};

/** Navigate directly to the Auth.js GitHub sign-in route (most reliable redirect). */
export function SignInButton({
  callbackUrl = "/jobs",
  size = "sm",
  githubConfigured
}: SignInButtonProps) {
  const [loading, setLoading] = useState(false);

  if (!githubConfigured) {
    return (
      <p className="max-w-xs text-right text-xs text-amber-400">
        GitHub OAuth is not configured. Set AUTH_GITHUB_ID and AUTH_GITHUB_SECRET in apps/web/.env.local
        (see README).
      </p>
    );
  }

  const startSignIn = () => {
    setLoading(true);
    const params = new URLSearchParams({ callbackUrl });
    window.location.assign(`/api/auth/signin/github?${params.toString()}`);
  };

  return (
    <Button type="button" size={size} disabled={loading} onClick={startSignIn}>
      {loading ? "Redirecting to GitHub…" : "Sign in with GitHub"}
    </Button>
  );
}
