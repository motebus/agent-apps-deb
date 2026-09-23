# AGPC Apps

`agpc-apps 0.3.0-1` is the native user-application composition for the full AGPC
profile. It formally replaces the product/package name Agent Apps. The existing
source repository and old immutable release history remain at `agent-apps-deb`.

```text
agpc.sh        standard native AGPC, including contextd through agent-sphere
agpc-full.sh   standard native AGPC plus agpc-apps and the full applications
agpc-apps     Jujue, iAgent, SS-WebOS, MDesk and uChat; requires Core and Ultra
agent-apps    legacy-name transition, depends exactly on agpc-apps 0.3.0-1
```

The standard profile owns its core runtime dependencies, including `contextd`.
Apps requires `agent-sphere >= 0.3.0-1` so it cannot select the older core
composition. It does not duplicate the contextd runtime dependency. The full
profile includes `agent-ultra` local knowledge/communication infrastructure and
its owner-managed Obsidian provisioning. The separate `agpc-manager` package
owns the management frontend; MEdge owns its headless management backend.

Apps requires Jujue `0.2.0-1`, iAgent `1.0.0-1`, SS-WebOS `2.0.0-12`, MDesk
`3.0.0-6`, uChat `3.2.0-4`, Agent Sphere `0.3.0-1` and Agent Ultra `0.1.0-1`.
There are no `Recommends` or `Suggests`. The uChat floor requires uchatd 0.5.0
and its durable Redis profile. Upgrading a SQLite-backed uchatd still requires
that package's explicit offline migration before installation; this metapackage
does not bypass its pre-install checks. Redis is independent infrastructure;
clients use the uChat protocol, and `mote-transportd` owns D/MSG transport.

AGPC executes natively on Linux and is distributed as Debian packages. Windows
native support is future work. `contextd` belongs inside AGPC; CoD Server/codd
is a cloud service outside this package. Docker/OCI may be used for cloud/server
services and is not an AGPC runtime or package-build path.

The local application profile uses compiled Jujue Vue assets in the root-owned
SS-WebOS catalog. Its desktop bridge invokes the fixed native iAgent client;
iAgent uses admitted local AGOS APIs. AGOS owns caller grants and model execution.
Installing Apps grants no model/tool permission, identity or execution authority.

Both DEBs contain README and copyright files only, under their own distinct
`/usr/share/doc/<package>/` directories. They install no runtime, configuration,
daemon or maintainer hook. They declare no `Provides`, `Conflicts`, `Breaks` or
`Replaces`: no files overlap, and the transition must coexist with the new
package. APT/DPKG and each component own lifecycle; the rename never purges
configuration or removes an application. Removing either metapackage removes
only its documentation. Do not run autoremove as part of this rename.

For a fresh full installation, select `agpc-apps=0.3.0-1`. If `agent-apps` is
already installed, upgrade it to `agent-apps=0.3.0-1` in the same reviewed APT
transaction; its exact dependency selects `agpc-apps=0.3.0-1`. Existing manual
installation marks remain attached to the old name, whose dependency keeps the
new applications selected. Merely adding the new package does not guarantee
APT upgrades the old metapackage, so the installer must request the transition
when an old installation is present. No removal of the old name is required.

Version floors and source tests do not establish release or runtime acceptance.
The dependency contract deliberately records `installable: false` and
`readiness: false`: exact native leaf artifacts (including the new core), a
signed aggregate closure, migration checks and configured-host acceptance
remain necessary before activation. The two installer profiles are the target
integration contract; building this repository alone does not publish them.

Build and validate directly on native Linux with Python 3, Git, dpkg tools and
APT; CI uses an Ubuntu shell environment and no containers:

```sh
python3 scripts/package.py build
python3 scripts/package.py compatibility
python3 -m unittest discover -s tests -v
```

The build emits both `agpc-apps_0.3.0-1_all.deb` and the transitional
`agent-apps_0.3.0-1_all.deb`. The audits enforce documentation-only payloads,
exact package metadata and native dependency ownership. Isolated APT simulations
exercise fresh installation, legacy-name upgrade and missing-dependency refusal
without changing the host package database or starting services.

After committing and reviewing a clean source tree, `python3 scripts/package.py
manifest` binds both artifacts and their hashes to that source commit. This is
an unpublished composition review record, not a signed deployment approval.
