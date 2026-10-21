# Security policy

PhysLab QA processes local data files and does not intentionally transmit experiment data over the network.

## Supported versions

Until the first stable release, only the current `main` branch and the latest tagged release candidate are actively maintained.

## Reporting a vulnerability

For ordinary correctness bugs, malformed-input crashes, or numerical discrepancies that are safe to discuss publicly, open a GitHub issue with a minimal reproducible example.

For a security-sensitive report, do not post secrets, private datasets, credentials, unpublished research data, or exploit details in a public issue. Contact the maintainer using a private contact method listed on the maintainer's GitHub profile and include the affected version or commit, reproduction steps, and expected impact.

## Scope

Security reports may include unsafe file handling, unintended disclosure of local data, dependency-related vulnerabilities, or behavior that could execute untrusted content unexpectedly. Scientific or numerical correctness problems are also important, but should normally be reported as regular issues unless disclosure itself would create a security risk.
