"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";

import { Button } from "@/components/ui/button";

type SignInButtonProps = {
  callbackUrl?: string;
  size?: "sm" | "default";
};

/** Client redirect to GitHub — faster than a server-action sign-in round-trip. */
export function SignInButton({ callbackUrl = "/jobs", size = "sm" }: SignInButtonProps) {
  const [loading, setLoading] = useState(false);

  return (
    <Button
      type="button"
      size={size}
      disabled={loading}
      onClick={() => {
        setLoading(true);
        void signIn("github", { callbackUrl });
      }}
    >
      {loading ? "Redirecting to GitHub…" : "Sign in with GitHub"}
    </Button>
  );
}
