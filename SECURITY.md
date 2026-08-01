# Security policy

## Supported versions

Only the latest released version and the default branch receive security fixes during the alpha phase.

## Reporting

Do not open public issues for vulnerabilities. Use GitHub private vulnerability reporting when enabled,
or contact the repository owner privately.

Include the affected version, reproduction steps, impact, and any suggested mitigation. Do not include
secrets or unrelated personal data.

## Trust model

Hermes Python, Dashboard, and Desktop plugins execute with the authority of the host process or app.
Review source and release checksums before installation. This plugin intentionally has no network client,
no telemetry, and no secret requirements. Project state remains in the repository under `.sdd/`; the
visual-source registry stores only repository paths in the user's Hermes home.
