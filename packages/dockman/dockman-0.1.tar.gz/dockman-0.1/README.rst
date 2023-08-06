README
======

*A webservice that runs docker builds/deployments on docker webhooks*

Rationale: Be able to construct and run docker containers with sensitive
configs when the unconfigured parent docker image builds.

Super dangerous-ish as it needs to run with access to the docker socket
