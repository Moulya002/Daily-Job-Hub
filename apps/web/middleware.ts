export { auth as middleware } from "@/auth";

export const config = {
  matcher: ["/dashboard/:path*", "/saved-jobs/:path*", "/resume-analysis/:path*", "/applications/:path*", "/settings/:path*", "/admin/:path*"]
};
