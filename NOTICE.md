Third-Party Notices for amphimixis
==================================

This distribution of `amphimixis` declares the following direct runtime
dependencies in `pyproject.toml`:

- `pandas` — BSD-3-Clause
- `PyYAML` — MIT
- `paramiko` — LGPL-2.1
- `openai` — Apache-2.0

Compliance material included in this repository
-----------------------------------------------

To preserve the upstream license notices that accompany these direct
dependencies, this repository includes:

- this `NOTICE` summary file
- the project's own [LICENSE](LICENSE)
- full upstream license texts in `third_party_licenses/`

Included third-party license texts
----------------------------------

- `third_party_licenses/pandas.LICENSE`
- `third_party_licenses/pyyaml.LICENSE`
- `third_party_licenses/paramiko.LICENSE`
- `third_party_licenses/openai.LICENSE`

Notes
-----

- The list above is intentionally limited to direct runtime dependencies, not
  development-only tools or transitive packages installed in a local virtual
  environment.
- No separate upstream `NOTICE` file was found in the installed metadata for
  these four direct dependencies on 2026-03-29.
- `paramiko` is distributed under LGPL-2.1. If `amphimixis` is ever shipped as
  a bundled executable or in another form that embeds Python dependencies
  directly, review LGPL redistribution obligations for that packaging model.
- Because the project does not pin exact runtime dependency versions, refresh
  the files in `third_party_licenses/` whenever any direct dependency is
  upgraded.
