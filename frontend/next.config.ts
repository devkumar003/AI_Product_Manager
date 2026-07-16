import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async redirects() {
    return [
      {
        source: '/dashboard/idea-analyzer',
        destination: '/dashboard/discovery?tab=idea',
        permanent: false,
      },
      {
        source: '/dashboard/prd-generator',
        destination: '/dashboard/requirements?tab=prd',
        permanent: false,
      },
      {
        source: '/dashboard/requirement-generator',
        destination: '/dashboard/requirements?tab=catalog',
        permanent: false,
      },
      {
        source: '/dashboard/acceptance-criteria',
        destination: '/dashboard/requirements?tab=stories',
        permanent: false,
      },
      {
        source: '/dashboard/wireframe-suggestions',
        destination: '/dashboard/requirements?tab=stories',
        permanent: false,
      },
      {
        source: '/dashboard/roadmap-generator',
        destination: '/dashboard/roadmap?tab=timeline',
        permanent: false,
      },
      {
        source: '/dashboard/executive',
        destination: '/dashboard/reports',
        permanent: false,
      },
      {
        source: '/dashboard/architecture-generator',
        destination: '/dashboard/engineering?tab=architecture',
        permanent: false,
      },
      {
        source: '/dashboard/tech-stack',
        destination: '/dashboard/engineering?tab=techstack',
        permanent: false,
      },
      {
        source: '/dashboard/testing-strategy',
        destination: '/dashboard/engineering?tab=testing',
        permanent: false,
      },
      {
        source: '/dashboard/deployment-guide',
        destination: '/dashboard/engineering?tab=deployment',
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
