Draft Agent Apps 0.1.0-2 composes 13 direct packages: AGOS, SS-WebOS, MDesk,
Mote Bridge MCP, CX Agent, UChat, Mote Vault Sync, Mote Vault Syncd, Mote Secd,
Codex Mesh, Obsidian, Model Router, and Model LLM. No optional packages are
suggested.

`ultra-mcp-ssh`, `mcp-run`, and `model-node` are retired and excluded. Their
historical artifacts remain evidence and are not active installation options.
`model-llm` is the native inference provider. Model Router combines the former
Router and Grid admission/scheduling/dispatch implementation in one daemon;
there is no separate Model Grid Debian dependency.

AGOS >= 2.0.0-2 manages Agent/model resource policy through the merged Router.
It requires model-router >= 0.1.0-1 and model-llm >= 0.1.0-3. Apps also lists
both explicitly; the full product has 21 unique required packages.
`cx-node` becomes `cx-agent >= 0.3.4-2` while preserving its existing
`cx://mms` contract, node role, identity/env, and service unit unless its
component migration explicitly changes them. The Router's cx-node lane remains
a semantic role. `mote-sync`/`mote-syncd` become
`mote-vault-sync`/`mote-vault-syncd >= 1.1.0-3`, preserving vault wire/config.

Obsidian >= 1.13.7 is required on the editing host. The top-level installer
acquires its reviewed official amd64 DEB and supplies it to the joint APT
transaction. Its exact SHA-256 is in the dependency contract; it is not
rehosted on MoteBus. MEdge owns local vault I/O and Obsidian is the human editor.
AGOS does not install OS packages or access a Vault directly.

The Debian release remains unpublished and documentation-only: no service,
network-fetch hook, configuration, alias, or fallback implementation. Six
public native release gates plus external Obsidian provisioning remain
explicit; installable/readiness stay false until the actual release and
runtime evidence satisfy their contracts. Historical artifacts are not deleted
and host packages are not removed by this metapackage.

An explicitly reviewed local preview may use exact local native version-floor
overrides for the same 13 package identities. It is not public compatibility
or live readiness evidence.
