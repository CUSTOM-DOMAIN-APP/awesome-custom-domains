# Contribution guidelines

Thanks for helping keep this list accurate. A pull request is the fastest way to add or correct an entry.

## What belongs here

Entries must be directly relevant to letting a platform's users connect domains they own: managed services, DIY building blocks, protocols, provider APIs, diagnostics, examples and field notes. Adjacent categories (idea validation, general SEO tooling, registrar resale) are out of scope regardless of quality. Competitors of the maintainer are in scope and are listed; the list is maintained by CustomDomain™ and says so wherever that matters.

## Adding an entry

- One entry per line, in the form `- [Name](link) - Description.`
- Keep entries alphabetical within their section. The email authentication section is the exception: it follows the order the records are deployed.
- Write a factual description that starts with a capital letter and ends with a period. No marketing adjectives.
- Link the final target of any redirect, and prefer a project's repository or documentation over a landing page.
- Check every link and put the HTTP status in the pull request. A 403 from GitHub or npm to an anonymous fetch is a bot block, not a dead link, so say so rather than dropping the entry.
- Every number must trace to something a reviewer can open. Provider counts come from `https://api.customdomain.ai/v1/providers/census`; prices come from the vendor's own pricing page, with the date it was read.
- Run `npx awesome-lint` before you open the pull request. It should report no errors.

## Corrections

If an entry is wrong, out of date or dead, open an issue or a pull request with the line and the source you checked. Corrections to the maintainer's own entries are as welcome as any other.

## License

By contributing, you dedicate your contribution to the public domain under [CC0 1.0](LICENSE), like the rest of the list.
