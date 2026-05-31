import { signOut, auth } from "@/auth";
import { Button } from "@/components/ui/button";
import { SignInButton } from "@/components/common/sign-in-button";

export async function AuthActions() {
  const session = await auth();
  const githubConfigured = Boolean(
    process.env.AUTH_GITHUB_ID?.trim() && process.env.AUTH_GITHUB_SECRET?.trim()
  );

  if (!session?.user) {
    return <SignInButton callbackUrl="/jobs" githubConfigured={githubConfigured} />;
  }

  return (
    <form
      action={async () => {
        "use server";
        await signOut({ redirectTo: "/" });
      }}
    >
      <Button size="sm" variant="outline" type="submit">
        Sign out
      </Button>
    </form>
  );
}
