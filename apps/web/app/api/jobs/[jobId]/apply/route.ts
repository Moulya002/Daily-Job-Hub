import { NextResponse } from "next/server";

import { auth } from "@/auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type RouteContext = {
  params: Promise<{ jobId: string }>;
};

export async function POST(_request: Request, context: RouteContext) {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { jobId } = await context.params;
  const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/apply?user_id=${encodeURIComponent(session.user.id)}`, {
    method: "POST"
  });

  if (!response.ok) {
    return NextResponse.json({ error: "Failed to apply job" }, { status: response.status });
  }
  return NextResponse.json({ success: true });
}

export async function DELETE(_request: Request, context: RouteContext) {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { jobId } = await context.params;
  const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/apply?user_id=${encodeURIComponent(session.user.id)}`, {
    method: "DELETE"
  });

  if (!response.ok) {
    return NextResponse.json({ error: "Failed to unapply job" }, { status: response.status });
  }
  return NextResponse.json({ success: true });
}
