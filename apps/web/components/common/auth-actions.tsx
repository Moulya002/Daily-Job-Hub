import { signOut, auth } from "@/auth";
import { Button } from "@/components/ui/button";
import { SignInButton } from "@/components/common/sign-in-button";

export async function AuthActions() {
  const session = await auth();

  if (!session?.user) {
    return <SignInButton callbackUrl="/jobs" />;
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
