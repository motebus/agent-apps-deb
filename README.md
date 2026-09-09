# Agent Apps

`agent-apps.deb` is the application composition package for an Agent Computer.

```text
Agent Computer = agent-sphere.deb + agent-apps.deb
Agent Sphere   = system infrastructure
Agent Apps     = intelligence and applications
```

Version **0.1.0-2 is an unpublished composition preview**. It selects these
13 direct dependencies through native APT and DPKG:

| Direct dependency | Minimum version | Application role |
| --- | --- | --- |
| `agos` | `2.0.0-2` | Native Agent intelligence runtime. |
| `ss-webos` | `2.0.0-11` | WebOS application runtime. |
| `mdesk` | `3.0.0-6` | Desktop application. |
| `mote-bridge-mcp` | `3.0.0-2` | MCP application bridge. |
| `cx-agent` | `0.3.4-2` | Native CX Agent application package. |
| `uchat` | `2.0.0-3` | Chat application. |
| `mote-vault-sync` | `1.1.0-3` | Obsidian vault sync client. |
| `mote-vault-syncd` | `1.1.0-3` | Vault sync service. |
| `mote-secd` | `1.0.0-2` | Security runtime package. |
| `codex-mesh` | `1.0.0-1` | Codex Mesh application package. |
| `obsidian` | `1.13.7` | Required human desktop editor; official upstream DEB. |
| `model-router` | `0.1.0-1` | Merged routing, admission, scheduling, and dispatch runtime. |
| `model-llm` | `0.1.0-3` | Native inference provider. |

`ultra-mcp-ssh`, `mcp-run`, and `model-node` are retired and excluded. They are not active
standalone or on-demand options. Historical release artifacts are retained;
this metapackage does not remove installed packages or delete releases.

`mote-bridge-mcp` remains the Codex-facing bridge. The Obsidian sync packages
are renamed from `mote-sync`/`mote-syncd` to
`mote-vault-sync`/`mote-vault-syncd`. Their component owner preserves the
existing vault wire and configuration interface. This metapackage supplies
neither old-name aliases nor runtime migration logic.

This Apps profile places the Obsidian desktop application on the Linux Agent
Computer used for local editing, alongside MEdge and AGOS. Obsidian is the
human editor; MEdge owns admitted local vault I/O. AGOS manages Agent and
model resource policy through the merged Model Router, which dispatches to
admitted CX Agent or Model LLM resources. It consumes owner-approved memory interfaces and does not read
a Vault directly. AGOS does not install OS packages or take over model
provider execution.

APT/DPKG and systemd retain installation and service lifecycle. The top-level
Agent Computer installer must acquire a reviewed official upstream Obsidian
DEB and include it in the joint APT transaction. The metapackage must not fetch
packages from a maintainer script or pretend that Obsidian is published in the
MoteBus APT repository. Installing the editor does not create/select a Vault,
activate a plugin, prove vault synchronization, or establish Agent readiness.
The reviewed official Obsidian artifact is version `1.13.7`, architecture
`amd64`; its SHA-256 is recorded in `dependency-contract.json`. It is acquired
from upstream and is not rehosted as a MoteBus package.
The desktop UI runs in the user's graphical session, not inside `agosd` or a
Sphere daemon. A graphical session is required for editor acceptance.

Model Router now incorporates the former Grid admission, scheduling, durable
correlation, and dispatch implementation in one daemon. There is no separate
`model-grid.deb` dependency or Grid service in this composition. AGOS
`2.0.0-2` also declares `model-router >= 0.1.0-1` and `model-llm >= 0.1.0-3`
as its resource dependencies. Both are explicit direct Apps dependencies;
repeated APT dependency edges do not install duplicate packages.

`cx-node.deb` is renamed to `cx-agent.deb`. This package rename preserves the
existing `cx://mms` interface, CX Node semantic role, owner identity/env, and
existing service unit unless a component migration explicitly changes them.
The Router's `cx-node` lane names that semantic role, not the retired package
identity. `model-llm` supplies inference; the old ModelNode package is retired.

This composition has no optional `Suggests` packages. ModelNode is retired;
its historical process-fixture results are evidence, not a supported runtime
option. The active resource path is AGOS → merged Model Router → admitted CX Agent
or Model LLM. Adding packages to this composition does not move their
runtime, routing, security, or lifecycle authority into Agent Apps. In
particular, installing `mote-secd` does not create a second Sphere trust plane.

Local native AGOS validation work now exists. Compatible public
`agos >= 2.0.0-2`, `cx-agent >= 0.3.4-2`, `mote-vault-sync >= 1.1.0-3`, and
`mote-vault-syncd >= 1.1.0-3` releases and joint installation acceptance
remain unverified. Historical AGOS `1.0.0-16` and the old `cx-node` package identity
do not satisfy this composition. The contract therefore keeps
`installable: false` and `readiness: false`, with six public release gates
(including merged Router and Model LLM) and the external Obsidian provisioning gate explicit. Neither the version floors nor this source preview certify current
APT availability or compatibility of all 13 components.

This package contains only this README and copyright metadata. It supplies
no executable, daemon, systemd unit, maintainer script, runtime configuration,
credentials, AGOS implementation, compatibility alias, or package manager.
It does not depend on `agent-sphere`; the installation request composes the
two top-level packages. Each dependency owns its runtime and lifecycle.

The target installation is one APT transaction containing `agent-sphere`,
`agent-apps`, and the exact reviewed official Obsidian DEB supplied by the
top-level installer. A bare APT request cannot resolve an external dependency
that has not been provisioned. The installer owns upstream acquisition and
verification; Agent Apps owns declaring Obsidian as a required application.

**Public installation is not ready until compatible native releases and the
reviewed external Obsidian package are available to the same transaction, and
the complete dependency plan has passed acceptance.** Do not
force dependencies, create fake runtime providers, use the retired
`agent-app` name, or silently install only part of the requested product.
A separately reviewed local preview may select exact local native artifacts
with explicit version-floor overrides; it is not evidence of public release
availability and must retain the same 13 dependency identities.

Build and audit with Python 3, Git and `dpkg-deb`:

```sh
python3 scripts/package.py build
python3 scripts/package.py verify dist/agent-apps_0.1.0-2_all.deb
python3 scripts/package.py compatibility
python3 -m unittest discover -s tests -v
```

Builds use the committed Git timestamp, or an explicit `SOURCE_DATE_EPOCH`
for an uncommitted local preview. Release manifests require clean committed
source and record its exact commit. The validation workflow builds and tests
the package and has no publication step. Review manifests preserve the
unresolved public installation and readiness gates. Checksums identify bytes;
they do not independently authenticate a release. Public compatibility and
full joint lifecycle, I/O, Agent request, and reboot acceptance remain separate
requirements.

`scripts/apt_plan.py` audits a C-locale joint APT simulation and an installed
package snapshot. It checks all **21 required package/version floors**: two
top-level packages, six Sphere dependencies, and thirteen Apps dependencies.
The native Sphere floor is `0.1.0-5`, with MEdge `3.0.0-2`, MoteD `3.6.0-2`,
MLINK `2.1.0-1`, and Mote Transportd `2.0.0-6`. AGOS resource edges are counted
once. Every removal is rejected. There is no chatd-removal exception: the
exact `mote-chatd 2.0.0-6` documentation guard may remain to retain existing
configuration ownership. Metadata recognition does not verify its payload;
the caller must bind it to the approved artifact and inspect its migration.
Fresh installations require only the 21 canonical packages and no guard.

The auditor never installs packages or establishes runtime readiness. Vault
and CX replacements require the separately reviewed top-level transaction
guard; this read-only tool does not authorize those removals. See
`MIGRATION_PLAN.md` for the current integration boundary.

Public packaging source:
[MoteBus Agent Apps](https://github.com/motebus/agent-apps-deb). Publishing this
source and its CI review artifact does not publish a Debian release or make
missing component dependencies available.
APT publication remains a separate reviewed action. Removing this metapackage
removes its documentation; a separate APT autoremove may affect automatically
installed dependencies and must be reviewed independently.
