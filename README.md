# Awesome Custom Domains

A curated list of tools, services, protocols, and reference implementations for **connecting user domains to SaaS platforms**: DNS automation, domain ownership verification, and SSL/TLS issuance for customer-owned hostnames.

If you are building a product where customers bring their own domain (a website builder, email platform, AI agent product, or agency tooling), this list covers managed services, DIY building blocks, open protocols, and worked examples. It does not cover registrar shopping, general web hosting, or DNS hosting chosen for your own zone rather than your customers'.

Maintained by [CustomDomain.ai](https://customdomain.ai). Contributions welcome, see [Contributing](#contributing).

## Contents

- [Managed services](#managed-services)
- [How the managed services compare](#how-the-managed-services-compare)
- [DIY building blocks](#diy-building-blocks)
- [ACME clients and certificate limits](#acme-clients-and-certificate-limits)
- [DNS provider APIs](#dns-provider-apis)
- [Platform custom-domain docs](#platform-custom-domain-docs)
- [Open protocols](#open-protocols)
- [Reference implementations and examples](#reference-implementations-and-examples)
- [Email domain authentication](#email-domain-authentication)
- [MCP servers and AI-agent tooling](#mcp-servers-and-ai-agent-tooling)
- [Diagnostics](#diagnostics)
- [Field guides by vertical](#field-guides-by-vertical)
- [Reading](#reading)

## Managed services

End-to-end platforms that handle DNS setup, verification, and TLS for your customers' domains.

- [Approximated](https://approximated.app) - Custom domain API and managed reverse proxy for connecting user domains, with per-domain pricing.
- [Cloudflare for SaaS](https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/) - Custom hostnames on Cloudflare's edge: certificate issuance and routing primitives for platforms already on Cloudflare (you build the onboarding UX).
- [CustomDomain](https://customdomain.ai) - Domain connection for SaaS: 63 DNS providers catalogued, 25 of them configured automatically (17 by provider API token, 6 by one-click OAuth, 2 by Domain Connect) and the remaining 38 through a guided manual flow. Embeddable widget, REST API, [documentation](https://docs.customdomain.ai/docs), and a hosted MCP server. Free Starter tier ($0, 10 domain connections/yr); paid plans from $149/mo. (This list's maintainer.)
- [Entri](https://www.entri.com) - Domain connection suite with an embeddable modal (Connect), managed hosting/SSL (Power), certificates (Secure), in-app domain sales (Sell), and DNS monitoring.
- [SaaS Custom Domains](https://saascustomdomains.com) - Managed custom domains with API and dashboard, aimed at SaaS products.

The provider split above comes from the live census endpoint, `https://api.customdomain.ai/v1/providers/census`, counted 2026-08-19: 63 catalogued, 17 `api`, 6 `oauth`, 2 `dc`, 38 `manual`. The three numbers worth keeping straight are 63 catalogued, 25 with an automatic path, and 38 that still need a human in a DNS dashboard.

## How the managed services compare

Published list prices, all fetched 2026-08-19. Quota units differ between vendors, so the columns are not directly divisible into each other.

| Service | Published entry price | Free tier | Billed per |
|---|---|---|---|
| [Approximated](https://approximated.app) | $0.20 per custom domain per month, $20/mo minimum below 100 domains, 400 GB bandwidth included | 7-day trial only | domain per month |
| [Cloudflare for SaaS](https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/plans/) | 100 custom hostnames included on Free, Pro, and Business; $0.10 per additional hostname | 100 hostnames on the free Cloudflare plan | hostname per month |
| [CustomDomain](https://customdomain.ai/pricing) | $149/mo (Startup, 600 domain connections/yr) | Starter, $0, 10 domain connections/yr | connection per year |
| [Entri](https://www.entri.com/plans) | $249/mo (Startup, 600 domains/yr) | none | domain per year |
| [SaaS Custom Domains](https://saascustomdomains.com) | $29/mo for 100 domains ($0.29 per domain) | free trial, no card required | domain per month |

Limitations of this table, stated plainly:

- It is one axis. Approximated and Cloudflare for SaaS sell edge primitives and expect you to build the onboarding flow; the others sell the onboarding flow itself. A per-hostname rate and a per-connection annual quota are not the same product.
- Entri's Growth, Premium, and Enterprise tiers are all "Talk to Sales", so the only Entri number anyone can compare is the Startup tier.
- CustomDomain's free Starter tier is not the whole product. The Power and Secure/SSL API groups are gated entitlements and return `402 plan_upgrade_required` to a tenant without them.
- This list is maintained by CustomDomain. Read the vendor pages before deciding, and treat every price here as a snapshot that will drift.

## DIY building blocks

Pieces you can assemble yourself if you would rather build than buy.

- [Caddy](https://caddyserver.com/docs/automatic-https#on-demand-tls) - On-Demand TLS issues certificates for arbitrary hostnames at handshake time; the canonical DIY answer for serving unknown customer domains.
- [cert-manager](https://cert-manager.io) - Kubernetes-native certificate automation for per-tenant certs.
- [Let's Encrypt](https://letsencrypt.org) - Free ACME certificate authority underlying most custom-domain TLS automation.
- [OctoDNS](https://github.com/octodns/octodns) - Infrastructure-as-code style DNS management across providers.
- [Traefik](https://doc.traefik.io/traefik/https/acme/) - Reverse proxy with ACME support usable for customer hostname termination.
- [VinylDNS](https://github.com/vinyldns/vinyldns) - DNS automation and governance platform for large DNS estates.

## ACME clients and certificate limits

One certificate per customer domain means issuance is a runtime path, not a deploy step, and rate limits become a capacity question.

- [acme.sh](https://github.com/acmesh-official/acme.sh) - Shell ACME client, widely used for DNS-01 and wildcard issuance.
- [Certbot](https://certbot.eff.org) - EFF's ACME client, the usual starting point for HTTP-01 and DNS-01.
- [lego](https://go-acme.github.io/lego/) - Go ACME client and library with DNS-01 solvers for most provider APIs, embeddable directly in a control plane.
- [Let's Encrypt rate limits](https://letsencrypt.org/docs/rate-limits/) - The limits that decide whether per-customer issuance scales, including certificates per registered domain, duplicate certificates, and failed validations.

## DNS provider APIs

Provider APIs are the mechanism behind the API-token path: 17 of the 25 automatic providers in the census are configured this way. These four are the ones you will meet first.

- [Cloudflare DNS API](https://developers.cloudflare.com/api/resources/dns/) - Record CRUD, including the proxied-record and CNAME-flattening behavior that affects apex setup.
- [DigitalOcean API](https://docs.digitalocean.com/reference/api/digitalocean/) - Domain and domain-record endpoints.
- [GoDaddy Domains API](https://developer.godaddy.com/en/docs/references/rest/domains/v3) - Record replace and patch endpoints; note the API-key tiers and the record-type-scoped replace semantics.
- [Route 53 API](https://docs.aws.amazon.com/Route53/latest/APIReference/Welcome.html) - `ChangeResourceRecordSets` plus alias records, and IAM scoping if a customer delegates access.

Read each one's write semantics before you automate it. Some providers replace a whole zone rather than a single record, which turns a naive write into data loss for the customer.

## Platform custom-domain docs

How the platforms your customers already use expect a custom domain to be pointed. Useful both as prior art and as the documentation your support team ends up reading.

- [Fly.io](https://fly.io/docs/networking/custom-domain/) - Certificate issuance for customer hostnames on Fly.
- [Heroku](https://devcenter.heroku.com/articles/custom-domains) - Long-standing DNS target model, including the apex problem and ALIAS/ANAME workarounds.
- [Netlify](https://docs.netlify.com/manage/domains/domains-fundamentals/domains-glossary/) - Domains glossary, a clear plain-language reference for apex, subdomain, and delegation terms.
- [Railway](https://docs.railway.com/networking/public-networking) - Public networking and custom domain configuration.
- [Render](https://render.com/docs/custom-domains) - Custom domain setup and verification.
- [Vercel](https://vercel.com/docs/domains) - Domain configuration for projects, including nameserver delegation versus record pointing.

## Open protocols

- [ACME (RFC 8555)](https://datatracker.ietf.org/doc/html/rfc8555) - The protocol behind automated certificate issuance (Let's Encrypt and others).
- [CAA (RFC 8659)](https://datatracker.ietf.org/doc/html/rfc8659) - The DNS record that restricts which CAs may issue for a domain. A customer CAA record that does not list your CA will block issuance, and the failure looks like a TLS problem rather than a DNS one.
- [Domain Connect](https://www.domainconnect.org) - An open protocol from the Domain Connect project (initiated at GoDaddy) that lets participating DNS providers apply service templates on a user's behalf. Adoption is limited to participating registrars, which is why managed services layer additional methods (provider APIs, guided flows) on top. See the [spec](https://github.com/Domain-Connect/spec) and [templates](https://github.com/Domain-Connect/Templates). The template repository holds 1,120 templates across 696 provider domains (counted 2026-08-19); goentri.com contributes 77 and customdomain.ai 18, the two largest sets.

## Reference implementations and examples

- [Cloudflare platform template](https://github.com/dinasaur404/platform-template) - Workers for Platforms example including custom hostnames.
- [Connect a custom domain, step by step](https://customdomain.ai/guides/how-to-set-up-a-custom-domain) - Vendor-neutral walkthrough of records, verification, TLS, and propagation.
- [Custom domain vs subdomain](https://customdomain.ai/glossary/custom-domain-vs-subdomain) - When a tenant subdomain is enough and when customer domains win.
- [vercel/platforms](https://github.com/vercel/platforms) - The widely-cited Next.js multi-tenant example with custom domains on Vercel.

## Email domain authentication

Connecting a domain for email means DNS records for authentication, not just routing. Listed in deployment order rather than alphabetically.

- [SPF](https://datatracker.ietf.org/doc/html/rfc7208) - Authorizes sending hosts for a domain (TXT record).
- [DKIM](https://datatracker.ietf.org/doc/html/rfc6376) - Cryptographic signing of mail, verified via DNS-published keys.
- [DMARC](https://datatracker.ietf.org/doc/html/rfc7489) - Policy layer aligning SPF/DKIM with the From domain, with reporting.
- [learndmarc.com](https://www.learndmarc.com) - Interactive SPF/DKIM/DMARC debugging.

## MCP servers and AI-agent tooling

- [customdomain-mcp](https://github.com/CUSTOM-DOMAIN-APP/customdomain-mcp) - Hosted MCP server covering domain search, registration, connection creation, verification, and TLS status in one server. Registered in the official MCP registry as `ai.customdomain/mcp`; streamable HTTP endpoint at `https://mcp.customdomain.ai/mcp` (authenticated, so a bare GET returns 401). No tool accepts raw DNS records as input: record values are computed server-side from vetted templates.
- [domain-check](https://github.com/saidutt46/domain-check) - Domain availability checking with MCP support.
- [MCP Registry](https://registry.modelcontextprotocol.io) - The official Model Context Protocol server registry.

## Diagnostics

What you reach for when a connection is stuck and you need to know whether the problem is the record, the resolver cache, or the certificate.

- [DNSChecker](https://dnschecker.org) - Propagation view of a record across resolvers worldwide.
- [Google Admin Toolbox Dig](https://toolbox.googleapps.com/apps/dig/) - Browser dig for A, CNAME, TXT, and CAA lookups against authoritative servers.
- [Google Public DNS](https://dns.google) - Resolver-side lookup, useful for confirming what a large public resolver currently returns and for how long.
- [SSL Labs Server Test](https://www.ssllabs.com/ssltest/) - Certificate chain and TLS configuration check once the hostname is serving.

A record that resolves from the authoritative server but not from a public resolver is a TTL problem, not a configuration problem. Check the old record's TTL before changing anything a second time.

## Field guides by vertical

Longer-form guides maintained by CustomDomain, one per vertical. Vendor-authored, so read them as field notes rather than neutral surveys.

- [connect-domain-for-agencies](https://github.com/CUSTOM-DOMAIN-APP/connect-domain-for-agencies) - Managing domain connection across many client accounts, white-label considerations.
- [connect-domain-for-ai-agents](https://github.com/CUSTOM-DOMAIN-APP/connect-domain-for-ai-agents) - Agents that provision websites and need real domains, and what an agent-safe DNS surface looks like.
- [connect-domain-for-email-platforms](https://github.com/CUSTOM-DOMAIN-APP/connect-domain-for-email-platforms) - Onboarding customer sending domains with automated SPF/DKIM/DMARC setup.
- [connect-domain-for-website-builders](https://github.com/CUSTOM-DOMAIN-APP/connect-domain-for-website-builders) - Apex versus subdomain, CNAME flattening, and the records a site builder has to write.

## Reading

- [Domain Connect knowledge base](https://github.com/Domain-Connect/knowledge-base) - CC0 background material on the protocol and the problem space, and the source for the often-quoted finding that roughly half of users who attempt manual DNS configuration fail and abandon it.
- [On-demand TLS](https://customdomain.ai/glossary/on-demand-tls) - Certificate issuance at first request, explained.
- [One-click DNS setup](https://customdomain.ai/one-click-dns-setup) - How provider authorization connects a domain in about 30 seconds. The 30 seconds applies to the authorization and API-token paths, not to the guided manual flow.
- [Why custom domains are hard](https://customdomain.ai/why-custom-domains-are-hard) - The three-party problem between platforms, users, and DNS providers.

## Contributing

PRs welcome. One tool per line, format `- [Name](link) - description.`, alphabetical within its section, and keep descriptions factual. The email authentication section is the one exception to alphabetical order: it follows the order the records are deployed.

Tools must be directly relevant to connecting customer-owned domains to platforms. Submissions for adjacent categories (idea validation, general SEO tooling, registrar resale) are out of scope regardless of quality.

Check every link before you submit and put the HTTP status in the PR description. A 403 from GitHub or npm to an anonymous fetch is a bot block, not a dead link, so say so rather than dropping the entry. If a URL redirects, link the final target.

Numbers in descriptions must be traceable to a source a reviewer can open. Provider counts here come from `https://api.customdomain.ai/v1/providers/census`; prices come from the vendor's own pricing page with the date it was read.

## License

[MIT](LICENSE). List curation by [CustomDomain.ai](https://customdomain.ai).
