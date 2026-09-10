Agent Apps 0.1.0-3 replaces `mote-bridge-mcp` with `mote-mcpd >= 3.0.0-3`
in the unchanged 13-application composition. CX Agent now requires `0.3.4-3`
and Codex Mesh `1.0.0-2` so neither dependent reintroduces the old package.
The MCP runtime remains on-demand stdio through `mote mcp`; no daemon or
compatibility provider alias is added.

The documentation-only metapackage has no hooks or runtime payload. Its
read-only joint plan auditor checks Sphere `0.1.0-9`, Apps `0.1.0-3` and the
21 canonical package floors, rejecting all removals. Exact legacy package
replacement belongs to the separately reviewed top-level installer. Existing
identity/configuration/state paths remain component-owned and preserved.

Obsidian remains a required official upstream dependency acquired by that
installer. No vault is selected, imported or modified. The signed aggregate
must publish the three MCP cohort artifacts together; composition publication
alone does not establish installation availability or runtime readiness.
