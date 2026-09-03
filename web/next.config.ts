import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === "production";

// Derived from the actual repo, never hardcoded. A hardcoded basePath fails
// silently -- the page still returns 200, but every CSS/JS asset 404s -- the
// moment the site is rebuilt under a different repo name. That is exactly
// what happened moving this off ml-research-pulse: the HTML loaded, nothing
// was styled or interactive, and nothing in the response code said why.
const basePath =
  process.env.NEXT_PUBLIC_BASE_PATH ||
  (process.env.NEXT_PUBLIC_REPO_SLUG
    ? "/" + process.env.NEXT_PUBLIC_REPO_SLUG.split("/").pop()
    : "");

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  basePath: isProd ? basePath : "",
  assetPrefix: isProd ? basePath + "/" : "",
};

export default nextConfig;
