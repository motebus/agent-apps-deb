# Four-package migration

The previous Apps package selected thirteen applications and runtimes. Version
0.2.0-1 reassigns ownership through dependencies without removing installed
runtime files or their configuration:

- Core owns AGOS, Codex Mesh, model execution, MCP and Mote/security/local I/O.
- Ultra owns Redixs, local Comm/Telegram, Obsidian and the vault sync pair.
- Sphere Manager owns the dedicated frontend and requires the MEdge backend.
- Apps owns Jujue, iAgent, SS-WebOS, MDesk and UChat, and requires Core and Ultra.

The installer requests all four entries. Dropping a direct dependency does
not authorize removal or autoremove. Existing protected transport ownership
and exact bridge/CX/vault rename checks remain in the installer under APT's
lock. No configuration-only record is purged incidentally.

Jujue and iAgent require actual owner-built Debian artifacts before their
versions are fixed and release is allowed. No empty wrapper, virtual provider
or AGOS alias may satisfy this requirement. All old immutable release tags and
artifacts remain historical evidence.
