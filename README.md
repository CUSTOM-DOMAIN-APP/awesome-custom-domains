# Awesome Custom Domains

A curated list of tools, services, protocols, and reference implementations for **connecting user domains to SaaS platforms**: DNS automation, domain ownership verification, and SSL/TLS issuance for customer-owned hostnames.

If you are building a product where customers bring their own domain (a website builder, email platform, AI agent product, or agency tooling), this list maps the whole solution space: managed services, DIY building blocks, open protocols, and worked examples.

Maintained by [CustomDomain.ai](https://customdomain.ai). Contributions welcome, see [Contributing](#contributing).

## Contents

- [Managed services](#managed-services)
- [DIY building blocks](#diy-building-blocks)
- [Open protocols](#open-protocols)
- [Reference implementations and examples](#reference-implementations-and-examples)
- [Email domain authentication](#email-domain-authentication)
- [MCP servers and AI-agent tooling](#mcp-servers-and-ai-agent-tooling)
- [Reading](#reading)

## Managed services

End-to-end platforms that handle DNS setup, verification, and TLS for your customers' domains.

- [Custom Domain](https://customdomain.ai) - One-click domain connection for SaaS: automatic DNS across 63 providers, CNAME/TXT verification, automatic TLS, embeddable widget, REST API, and a hosted MCP server for AI agents. Free tier. (This list's maintainer.)
- [Entri](https://entri.com) - Domain connection suite with an embeddable modal (Connect), managed hosting/SSL (Power), certificates (Secure), in-app domain sales (Sell), and DNS monitoring.
- [Approximated](https://approximated.app) - Custom domain API and managed reverse proxy for connecting user domains, with per-domain pricing.
- [SaaS Custom Domains](https://saascustomdomains.com) - Managed custom domains with API and dashboard, aimed at SaaS products.
- [Cloudflare for SaaS](https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/) - Custom hostnames on Cloudflare's edge: certificate issuance and routing primitives for platforms already on Cloudflare (you build the onboarding UX).

## DIY building blocks

Pieces you can assemble yourself if you would rather build than buy.

- [Caddy](https://caddyserver.com/docs/automatic-https#on-demand-tls) - On-Demand TLS issues certificates for arbitrary hostnames at handshake time; the canonical DIY answer for serving unknown customer domains.
- [Let's Encrypt](https://letsencrypt.org) - Free ACME certificate authority underlying most custom-domain TLS automation.
- [cert-manager](https://cert-manager.io) - Kubernetes-native certificate automation for per-tenant certs.
- [Traefik](https://doc.traefik.io/traefik/https/acme/) - Reverse proxy with ACME support usable for customer hostname termination.
- [OctoDNS](https://github.com/octodns/octodns) - Infrastructure-as-code style DNS management across providers.
- [VinylDNS](https://github.com/vinyldns/vinyldns) - DNS automation and governance platform for large DNS estates.

## Open protocols

- [Domain Connect](https://www.domainconnect.org) - An open protocol from the Domain Connect Association (initiated at GoDaddy) that lets participating DNS providers apply service templates on a user's behalf. Adoption is limited to participating registrars, which is why managed services layer additional methods (provider APIs, guided flows) on top. See the [spec](https://github.com/Domain-Connect/spec) and [templates](https://github.com/Domain-Connect/Templates).
- [ACME (RFC 8555)](https://datatracker.ietf.org/doc/html/rfc8555) - The protocol behind automated certificate issuance (Let's Encrypt and others).

## Reference implementations and examples

- [vercel/platforms](https://github.com/vercel/platforms) - The widely-cited Next.js multi-tenant example with custom domains on Vercel.
- [Cloudflare platform template](https://github.com/dinasaur404/platform-template) - Workers for Platforms example including custom hostnames.
- [Connect a custom domain, step by step](https://customdomain.ai/guides/how-to-set-up-a-custom-domain) - Vendor-neutral walkthrough of records, verification, TLS, and propagation.
- [Custom domain vs subdomain](https://customdomain.ai/glossary/custom-domain-vs-subdomain) - When a tenant subdomain is enough and when customer domains win.

## Email domain authentication

Connecting a domain for email means DNS records for authentication, not just routing.

- [SPF](https://datatracker.ietf.org/doc/html/rfc7208) - Authorizes sending hosts for a domain (TXT record).
- [DKIM](https://datatracker.ietf.org/doc/html/rfc6376) - Cryptographic signing of mail, verified via DNS-published keys.
- [DMARC](https://datatracker.ietf.org/doc/html/rfc7489) - Policy layer aligning SPF/DKIM with the From domain, with reporting.
- [learndmarc.com](https://www.learndmarc.com) - Interactive SPF/DKIM/DMARC debugging.
- [connect-domain-for-email-platforms](https://github.com/CUSTOM-DOMAIN-APP/connect-domain-for-email-platforms) - Guide repo: onboarding customer sending domains with automated SPF/DKIM/DMARC setup.

## MCP servers and AI-agent tooling

- [customdomain-mcp](https://github.com/ever-just/customdomain-mcp) - Hosted MCP server where agents search, register, and connect domains end to end (DNS, verification, TLS). The provisioning-capable domain MCP.
- [domain-check](https://github.com/saidutt46/domain-check) - Domain availability checking with MCP support.
- [MCP Registry](https://registry.modelcontextprotocol.io) - The official Model Context Protocol server registry.
- [connect-domain-for-ai-agents](https://github.com/CUSTOM-DOMAIN-APP/connect-domain-for-ai-agents) - Guide repo: agents that provision websites and need real domains.

## Reading

- [Why custom domains are hard](https://customdomain.ai/why-custom-domains-are-hard) - The three-party problem between platforms, users, and DNS providers.
- [One-click DNS setup](https://customdomain.ai/one-click-dns-setup) - How provider authorization connects a domain in about 30 seconds.
- [On-demand TLS](https://customdomain.ai/glossary/on-demand-tls) - Certificate issuance at first request, explained.
- [Domain Connect knowledge base](https://github.com/Domain-Connect/knowledge-base) - CC0 background material on the protocol and the problem space.

## Contributing

PRs welcome. One tool per line, format `- [Name](link) - description.`, alphabetical within its section, and keep descriptions factual. Tools must be directly relevant to connecting customer-owned domains to platforms.

## License

[MIT](LICENSE). List curation by [CustomDomain.ai](https://customdomain.ai).
