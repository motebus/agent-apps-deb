# Agent Apps

`agent-apps 0.2.0-1` composes user applications in the four-package Agent Sphere
system:

```text
agent-sphere    headless core, AGOS, model execution, Codex Mesh and Mote
agent-ultra     local Redixs, Comm/Telegram, Obsidian and vault sync
sphere-manager dedicated native management frontend, backed by MEdge
agent-apps     Jujue, iAgent and additional user applications
```

Apps declares Jujue, iAgent, SS-WebOS `2.0.0-11`, MDesk `3.0.0-6`, UChat
`2.0.0-3`, Agent Sphere `0.2.0-1` and Agent Ultra `0.1.0-1` as required
dependencies. There are no `Recommends` or `Suggests`. AGOS, model execution,
Codex Mesh and MCP belong to Core; local knowledge and communication
infrastructure belongs to Ultra. Core has no TUI. The separate manager owns
its frontend and MEdge owns its headless management backend.

This source is an **unreleased composition candidate**. Jujue and iAgent are
approved component names, but their native DEB versions and artifacts have not
been established. They remain explicit unresolved release gates in
`dependency-contract.json`; the manifest command refuses release while those
gates remain. Existing web/OCI source and AGOS's bounded iagent-text profile
are not substitute packages or proof of a standalone iAgent app.

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
