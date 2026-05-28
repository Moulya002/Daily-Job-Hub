import { NextResponse } from "next/server";

import { auth } from "@/auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function GET() {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const response = await fetch(`${API_BASE_URL}/users/${encodeURIComponent(session.user.id)}/saved-jobs`);
  if (!response.ok) {
    return NextResponse.json({ error: "Failed to fetch saved jobs" }, { status: response.status });
  }

  const payload = await response.json();
  return NextResponse.json(payload);
}
