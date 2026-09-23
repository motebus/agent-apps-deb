# Agent Apps to AGPC Apps

The active composition package is `agpc-apps 0.3.0-1`. Publish the accompanying
`agent-apps 0.3.0-1` transition in the same repository cohort. It depends exactly
on `agpc-apps (= 0.3.0-1)` and has no direct application dependencies or hooks.
Historical `agent-apps` releases and the source repository remain intact.

The new package carries documentation under `/usr/share/doc/agpc-apps`; the
transition retains documentation under `/usr/share/doc/agent-apps`. No payload
paths overlap. `Provides`, `Breaks`, `Conflicts` and `Replaces` are unnecessary
and intentionally absent. Keeping both metapackages installed allows dependents
of the old name and existing manual/automatic installation marks to survive.

Fresh full installations select `agpc-apps=0.3.0-1`. Existing installations also
request `agent-apps=0.3.0-1`, making APT replace the old composition metadata
with the transition and retain all component packages. Validate the exact plan
with `--simulate --no-remove` before the reviewed transaction. Do not remove,
purge or autoremove the old name to accomplish this rename. Ordinary APT
upgrades of the old name also pull in the new package through its exact dependency.

`agpc.sh` selects standard native AGPC, including contextd owned by the core.
`agpc-full.sh` adds the Apps composition and full-profile dependencies. Apps
requires the new `agent-sphere >= 0.3.0-1` composition and the current native
uChat floor; neither this rename nor an Apps package install performs the
separate SQLite Inbox migration required by uchatd 0.5.0.

The core owns AGOS, execution, CX-Mesh, Mote and contextd. Ultra owns local
knowledge and communication services. AGPC Manager/MEdge own management. Apps
owns the Jujue, iAgent, SS-WebOS, MDesk and uChat composition. The rename changes
no protected configuration, transport journal, account, Mote identity, vault,
registration authority or application data.

Before publication, verify native leaf artifacts and the signed full dependency
closure, including the new core/contextd package. Isolated APT simulations and
DEB payload audits are package evidence only; configured runtime acceptance
remains a separate gate. No Docker/OCI image is built for AGPC.
