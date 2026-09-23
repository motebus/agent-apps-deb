AGPC Apps 0.3.0-1 formally renames the application composition to agpc-apps.
The matching agent-apps 0.3.0-1 package is a documentation-only transition with
an exact dependency on agpc-apps. Existing installations upgrade without package
removals, migration hooks or application data changes. Historical releases and
the source repository are preserved.

The new composition requires agent-sphere 0.3.0-1 for standard AGPC including
contextd, and uchat 3.2.0-4 for the Redis-authoritative uchatd 0.5.0 release.
Existing SQLite Inboxes retain their separate mandatory offline migration gate.
The target installer split is agpc.sh for standard AGPC and agpc-full.sh for
standard plus Apps. Linux execution, package builds and tests remain native;
Windows native support is future work, and codd remains a cloud service.

These packages are composition review artifacts until native dependency
artifacts, signed aggregate closure and host acceptance have been verified.
