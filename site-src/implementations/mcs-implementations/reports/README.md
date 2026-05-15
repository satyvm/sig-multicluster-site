# Submitting a Conformance Report

This directory contains conformance reports submitted by MCS API implementers.

## Directory Structure

```
reports/
  <conformance-version>/
    <impl-name>/
      <impl-version>.yaml
```

For example:

```
reports/
  v0.5.0/
    submariner/
      v0.23.0.yaml
    gke/
      2026-01-01.yaml
      2026-07-01.yaml
```

## How to Submit

1. **Run the conformance suite** against your implementation. Check out a
   tagged release of the [mcs-api repository](https://github.com/kubernetes-sigs/mcs-api)
   (e.g., `git checkout v0.5.0`) and run the suite, providing the following
   flags to identify your implementation:
   - `--organization` — your organization name (e.g., "Google Cloud")
   - `--project` — your project name (e.g., "GKE Multi Cluster Service")
   - `--version` — your implementation version (e.g., "1.2.0")
   - `--url` — link to your project's documentation

2. **Copy the generated `report.yaml`** into the appropriate directory:
   `reports/<conformance-version>/<impl-name>/<impl-version>.yaml`

   - `<conformance-version>` is the released version of the mcs-api conformance suite you ran (e.g., `v0.5.0`)
   - `<impl-name>` is a lowercase identifier for your implementation (e.g., `submariner`, `gke`, `cilium`)
   - Optionally rename the file to your implementation version (e.g., `v0.23.0.yaml`, `2026-01-01.yaml`) — `report.yaml` is also fine

3. **Open a pull request** against the
   [sig-multicluster-site](https://github.com/kubernetes-sigs/sig-multicluster-site) repository.

## Requirements

The YAML report file must contain non-empty values for the following fields under `implementation`:

- `organization`
- `project`
- `version`
- `url`
