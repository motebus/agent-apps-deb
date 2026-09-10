# Native installer integration boundary

The top-level installer requests `agent-sphere 0.1.0-9`, `agent-apps 0.1.0-3`
and the checksum-verified official Obsidian DEB in one APT transaction. Apps
remains a documentation-only metapackage with 13 dependencies. It performs no
network access, migration, configuration, vault selection or runtime execution.

The MCP rename requires Mote MCPd `3.0.0-3`, CX Agent `0.3.4-3` and Codex Mesh
`1.0.0-2`. The latter two releases replace their old bridge dependency. No
`Provides: mote-bridge-mcp` alias is allowed. The `mote mcp` stdio contract and
legacy provider/helper/configuration/topology/receipt paths remain native
component compatibility identifiers; no daemon is introduced.

The old `mote-bridge-mcp 3.0.0-2` removal hook deletes its managed system Codex
entry. Before downloading or invoking APT, the installer must reject unknown
old package metadata, changed hooks/helper, locked-file ownership hazards and
customized legacy system entries. Its exact reviewed normal migration is
checked again under APT's lock, with the replacement artifact bound to its
reviewed SHA-256. Unrelated Codex configuration, user/project configuration,
locked identity metadata and existing receipt/state files must survive. A
simulation alone does not protect against changes between review and DPKG.
Fresh installation selects only `mote-mcpd`; a residual old package record does
not become an active dependency and must not be purged as an incidental step.

The read-only `scripts/apt_plan.py` accepts a C-locale simulation and a DPKG
snapshot with tab-separated `binary:Package`, `Version`, `db:Status-Abbrev`.
Only configured `ii` records count. It checks 21 canonical package floors,
rejects every removal, purge, resolver error, ambiguous record, missing package
and active retired runtime. It neither authenticates packages nor authorizes
migration. Configuration-only records do not count as running packages.

The exact `mote-chatd 2.0.0-6` documentation guard may retain protected legacy
conffile ownership outside the canonical count. It must not be removed or
purged. The top-level installer also supports the separately reviewed ordinary
`mote-chatd 2.0.0-4` replacement when the locked file has no DPKG ownership.
This generic auditor does not permit either removal and does not certify guard
payloads. Existing CX and vault package renames likewise require exact native
artifact checks in the installer, preserving configuration and user data.

`ultra-mcp-ssh`, `mcp-run`, `model-node` and standalone `model-grid` are not active
dependencies. Retirement does not authorize historical artifact deletion,
configuration purges or unrelated package removal. A successful dependency
plan is not runtime readiness, owner admission, live inference, desktop, local
I/O or reboot acceptance. These remain explicit host-level checks.
