# Submodule Security Vetting

This repository treats every entry in `.gitmodules` as a third-party dependency that must pass security and licensing controls before updates are merged.

`bmad-method-wds-expansion` is explicitly covered by this policy.

## Required Controls

1. Source registration
- Add/update submodules only through `.gitmodules` with an explicit tracked branch.
- Keep Dependabot submodule allowlists aligned with `.gitmodules`.

2. Vulnerability and secret scanning
- `linting.yml` runs Trivy on pull requests and pushes with `HIGH,CRITICAL` severity gates.
- `submodule-security-monitoring.yml` runs a scheduled Trivy scan to catch newly disclosed findings even when repo code does not change.

3. License compatibility
- `quality-checks.yml` resolves each submodule repository license from GitHub and fails if the SPDX identifier is outside the allowed set.

4. Periodic monitoring
- `submodule-security-monitoring.yml` checks every configured submodule against its upstream branch and opens/updates an issue when the pinned commit does not match upstream.

## Allowed Submodule SPDX Licenses

`MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `ISC`, `0BSD`, `Unlicense`, `WTFPL`, `CC0-1.0`, `CC-BY-3.0`, `CC-BY-4.0`, `Python-2.0`, `PSF-2.0`, `MPL-2.0`
