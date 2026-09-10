# Agent Apps

`agent-apps.deb` composes the applications of an Agent Computer through native
APT and DPKG dependencies:

```text
Agent Computer = agent-sphere.deb + agent-apps.deb
Agent Sphere   = system infrastructure
Agent Apps     = intelligence and applications
```

Version **0.1.0-3** keeps 13 direct dependencies. It replaces the MCP package
name with `mote-mcpd` and requires the corresponding CX Agent and Codex Mesh
releases, whose dependencies use that name.

| Direct dependency | Minimum version | Role |
| --- | --- | --- |
| `agos` | `2.0.0-2` | Native Agent intelligence runtime. |
| `ss-webos` | `2.0.0-11` | WebOS application runtime. |
| `mdesk` | `3.0.0-6` | Desktop application. |
| `mote-mcpd` | `3.0.0-3` | On-demand stdio MCP provider (`mote mcp`); no daemon. |
| `cx-agent` | `0.3.4-3` | Native CX Agent application. |
| `uchat` | `2.0.0-3` | Chat application. |
| `mote-vault-sync` | `1.1.0-3` | Vault sync client. |
| `mote-vault-syncd` | `1.1.0-3` | SSH subsystem vault sync endpoint. |
| `mote-secd` | `1.0.0-2` | Security runtime. |
| `codex-mesh` | `1.0.0-2` | Codex Mesh application. |
| `obsidian` | `1.13.7` | Human desktop vault editor; official upstream DEB. |
| `model-router` | `0.1.0-1` | Merged routing, admission, scheduling and dispatch. |
| `model-llm` | `0.1.0-3` | Native inference provider. |

`mote-mcpd` retains the on-demand stdio `mote mcp` interface. The rename adds no
daemon, listener, persistent Mote identity, or new trust plane. Existing helper,
provider, configuration, locked topology and receipt paths retain their legacy
names where required for compatibility. The canonical managed Codex server
entry uses the new name; its migration belongs to the native component.

The MCP rename cohort must be published together: Mote MCPd `3.0.0-3`, CX Agent
`0.3.4-3` and Codex Mesh `1.0.0-2`. The old `mote-bridge-mcp` package is neither
a dependency nor a virtual provider of this composition. The dependency
contract records these aggregate publication gates and the external Obsidian
acquisition requirement. Its `installable: false` and `readiness: false` mean
that composition metadata alone does not establish availability or runtime
acceptance. The signed aggregate and the installed host are checked separately.

Obsidian `1.13.7` is acquired from its official upstream release by the top-level
installer, verified against the SHA-256 in `dependency-contract.json`, and
supplied to the same APT transaction. It is not redistributed by MoteBus.
Installing the editor does not select a vault or authorize changes to user data.

`ultra-mcp-ssh`, `mcp-run` and `model-node` remain retired. Model Grid is merged
into Model Router. There are no optional `Suggests` packages. AGOS requires
Model Router and Model LLM; repeated dependency edges resolve once. The active
model path is AGOS → merged Model Router → admitted CX Agent or Model LLM.
Runtime configuration, source admission and successful requests remain separate
evidence from installation.

This package contains only this README and copyright metadata. It supplies no
executable, daemon, unit, maintainer script, runtime configuration, credentials,
compatibility alias or package manager. It does not depend on `agent-sphere`;
the installer requests the two top-level packages together. Each component
owns its runtime and lifecycle.

Build and audit with Python 3, Git and `dpkg-deb`:

```sh
python3 scripts/package.py build
python3 scripts/package.py verify dist/agent-apps_0.1.0-3_all.deb
python3 scripts/package.py compatibility
python3 -m unittest discover -s tests -v
```

Builds use the committed timestamp or an explicit `SOURCE_DATE_EPOCH`. Release
manifests require clean source and record the commit, CI ref and run ID. The
validation workflow produces artifacts; APT activation is a separate action.
Checksums identify bytes and do not independently authenticate a release.

`scripts/apt_plan.py` reads a C-locale APT simulation and an installed package
snapshot. It checks **21 required package/version floors**: Sphere `0.1.0-9`,
Apps `0.1.0-3`, six Sphere components and thirteen Apps components. MEdge remains
at `3.0.0-3`. Every removal is rejected by this generic auditor; exact component
renames require the top-level installer's separately reviewed transaction guard.
The `mote-chatd 2.0.0-6` documentation guard may remain outside the canonical
count to retain protected legacy configuration ownership. Recognizing its
metadata is not verification of its payload. Fresh installation needs no guard.
See [MIGRATION_PLAN.md](MIGRATION_PLAN.md) for migration limits.

Removing this metapackage removes its documentation. Product removal and APT
autoremove require an independent plan because component services and retained
identities have their own lifecycle. This source contains no product uninstaller.

Public source: [MoteBus Agent Apps](https://github.com/motebus/agent-apps-deb).
