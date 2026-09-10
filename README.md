# Agent Apps

`agent-apps 0.2.0-1` composes user applications in the four-package Agent Sphere
system:

```text
agent-sphere    headless core, AGOS, model execution, CX-Mesh and Mote
agent-ultra     local Redixs, Comm/Telegram, Obsidian and vault sync
sphere-manager dedicated native management frontend, backed by MEdge
agent-apps     Jujue, iAgent and additional user applications
```

Apps declares Jujue `0.2.0-1`, iAgent `1.0.0-1`, SS-WebOS `2.0.0-12`, MDesk `3.0.0-6`, UChat
`2.0.0-3`, Agent Sphere `0.2.0-1` and Agent Ultra `0.1.0-1` as required
dependencies. There are no `Recommends` or `Suggests`. AGOS, model execution,
CX-Mesh and MCP belong to Core; local knowledge and communication
infrastructure belongs to Ultra. Core has no TUI. The separate manager owns
its frontend and MEdge owns its headless management backend.

The local profile uses compiled Jujue Vue assets in a root-owned SS-WebOS
catalog. Its isolated desktop bridge invokes the fixed native iAgent client;
iAgent is a separate domain application that uses admitted local AGOS APIs.
It has no Mote identity, direct model route, Telegram adapter or system manager.
Unknown turns recover through get without blind retry. AGOS owns the actual
local caller grants and model execution boundary.

These dependency floors identify the native local implementations. A version
floor alone is not artifact acceptance: exact committed-main packages, signed
aggregate closure and native application-chain checks remain release gates.
The composition contract makes no installation or readiness claim by itself.

The metapackage contains this README and copyright metadata only. It provides
no runtime, configuration, daemon, maintainer hook, migration, provider alias
or package manager. APT/DPKG and each dependency own lifecycle. Installing
this package does not provision identity, grant model or tool access, send
Telegram messages, select a vault, or establish runtime readiness.

The permanent plural installer requests all four entry packages in one
transaction, with the verified official Obsidian DEB owned by Ultra's
provisioning contract. It preserves existing configuration and identity
metadata and uses exact migration guards for renamed packages. Removing
this metapackage removes its documentation; complete product removal requires
a separate reviewed component lifecycle/data-preservation plan.

Local review:

```sh
python3 scripts/package.py build
python3 scripts/package.py compatibility
python3 -m unittest discover -s tests -v
```

Build and source tests do not establish native runtime availability. Signed
aggregate dependency resolution, package migration and configured host
acceptance must pass before this candidate is activated.
