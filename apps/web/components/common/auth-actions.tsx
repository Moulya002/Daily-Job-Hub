import { signIn, signOut, auth } from "@/auth";
import { Button } from "@/components/ui/button";

export async function AuthActions() {
  const session = await auth();

  if (!session?.user) {
    return (
      <form
        action={async () => {
          "use server";
          await signIn("github");
        }}
      >
        <Button size="sm">Sign in</Button>
      </form>
    );
  }

  return (
    <form
      action={async () => {
        "use server";
        await signOut();
      }}
    >
      <Button size="sm" variant="outline">
        Sign out
      </Button>
    </form>
  );
}
