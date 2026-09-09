# Native installer integration boundary

This is a review contract. Publishing this source does not execute APT or
claim that the thirteen Apps components are released, installable, configured,
or ready. Compatible public component releases and the full native lifecycle
remain explicit acceptance gates.

The top-level installer owns one complete product request: `agent-sphere`,
`agent-apps`, and the checksum-verified official Obsidian DEB. Native APT
resolves component packages. The metapackage has no network hooks, daemon,
configuration, installer, or migration code. Obsidian is not redistributed;
installing its editor does not create a vault or authorize changes to user data.

The read-only `scripts/apt_plan.py` accepts a C-locale APT simulation and a
DPKG snapshot with tab-separated `binary:Package`, `Version`, and
`db:Status-Abbrev`. Only fully configured `ii` records count as installed.
It verifies all 21 canonical package version floors, with native Sphere >= 0.1.0-5,
MEdge >= 3.0.0-2, MoteD >= 3.6.0-2, MLINK >= 2.1.0-1 and transport >= 2.0.0-6.
It rejects all removals, purges, resolver errors, ambiguous records, missing
components and active retired runtimes. Configuration-only records do not
count as running packages and are not purged.

The earlier proposal to remove `mote-chatd` is retired. Existing deployment
identity may still have obsolete DPKG conffile ownership under that name.
The component owner's exact `mote-chatd 2.0.0-6` documentation guard retains
that ownership while `mote-transportd` owns the runtime. This guard may remain
outside the 21 canonical packages. It must not be removed, purged, or treated as
an active compatibility runtime. The auditor reports its exact metadata
version and `retention_payload_verified: false`; the caller must verify the
approved DEB SHA, documentation-only payload, hooks, ownership preservation,
and dependency closure separately. A version string alone proves none of
those facts. Fresh installation does not add a retention guard.

Vault packages are renamed to `mote-vault-sync`/`mote-vault-syncd >= 1.1.0-3`.
CX is renamed to `cx-agent >= 0.3.4-2`; the `cx://mms` interface and semantic
role remain component-owned. Existing vault and CX package replacements
require the top-level installer's exact-artifact transaction guard. That
guard must run under APT's native lock and admit only reviewed replacement
pairs while preserving identity, configuration, user vaults, and unrelated
packages. A simulated plan alone cannot protect against resolver drift.
This generic auditor deliberately provides no removal bypass.

`ultra-mcp-ssh`, `mcp-run`, and `model-node` are retired. `model-grid` is merged
into Model Router and is not a Debian dependency. Retirement does not authorize
purging configuration-only records, deleting historical artifacts, or broadening
an installation's removal scope. AGOS >= 2.0.0-2 and Apps both require
`model-router >= 0.1.0-1` and `model-llm >= 0.1.0-3`; repeated edges resolve once.

`dependency_plan_valid: true` describes the supplied plan and inventory only.
`runtime_ready` remains false. The auditor does not authenticate APT sources,
verify DEB bytes, prove that the inventory is current, grant owner admission,
execute package transactions, or assert successful migration. The caller owns
those gates and final installed-version verification. Public release acceptance
also requires native dependency/lifecycle tests and owner-configured Mote,
local I/O, Agent request, model dispatch, desktop, and reboot evidence as
applicable. No model downloads, inference backend install, real inference, or
user-vault changes are implied by package composition.
