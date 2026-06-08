# Guide for Cluster Manager Implementors

This is a step-by-step guide how to get your own implementation of Cluster managers to publish `ClusterProfile` objects for the clusters it manages, and let other consumers consume them like e.g. [Kueue](https://kueue.sigs.k8s.io/), [Knative Operator](https://knative.dev/), or [multicluster-runtime](https://github.com/kubernetes-sigs/multicluster-runtime). For more information on other cluster manager implementations check: [Cluster Inventory API Implementations](./index.md#cluster-managers).

**Prerequisites**

- A `hub cluster` where ClusterProfile objects will be published.
- `Go` 1.21+ for the controller code. Preferably v1.25+.
- `kubectl` access to the hub cluster.

For tinkering, start a [KinD cluster](https://kind.sigs.k8s.io/docs/user/quick-start/).

```bash
kind create cluster --name hub
kind create cluster --name spoke-1
kind create cluster --name spoke-2
kubectl config use-context kind-hub
```

## Step 1: Install the ClusterProfile CRD

The `ClusterProfiles` CRD must be installed on the hub cluster before any controller can create or read profile objects.

If you have cloned [cluster-inventory-api repo](https://github.com/kubernetes-sigs/cluster-inventory-api) locally, use:

```bash
kubectl apply -f config/crd/bases/multicluster.x-k8s.io_clusterprofiles.yaml
```

otherwise,

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/cluster-inventory-api/main/config/crd/bases/multicluster.x-k8s.io_clusterprofiles.yaml
```

now verify it:

```bash
kubectl get crd clusterprofiles.multicluster.x-k8s.io
```

## Step 2: Import the Go Module

```bash
go get sigs.k8s.io/cluster-inventory-api
```

The module provides following important elements:

| Package | Purpose |
| --------- | --------- |
| `sigs.k8s.io/cluster-inventory-api/apis/v1alpha1` | Go types for `ClusterProfile` and related structs |
| `sigs.k8s.io/cluster-inventory-api/client/clientset/versioned` | Generated typed clientset (`ciaclient`) |
| `sigs.k8s.io/cluster-inventory-api/pkg/access` | Consumer-side library for building `rest.Config` from a profile |

In your controller's `main.go`, import and initialize the typed client so that controller code can interact with ClusterProfile resources:

```go
import (
    ciaclient "sigs.k8s.io/cluster-inventory-api/client/clientset/versioned"
)

// hubConfig is your *rest.Config for the hub cluster
cic, err := ciaclient.NewForConfig(hubConfig)
if err != nil {
    log.Fatalf("failed to construct cluster-inventory client: %v", err)
}
```

## 3. Choose a Namespace Strategy

`ClusterProfile` objects are **namespace-scoped**. The namespace you choose should reflect your deployment model:

| Strategy | When to use |
| ---------- | ------------ |
| **Single namespace** | Simple deployments; all clusters in one place. |
| **Per-cluster-manager namespace** | Multiple cluster managers on one hub; each manager owns its namespace. |
| **Namespace = ClusterSet** | The namespace carries the `multicluster.x-k8s.io/clusterset=<name>` label to group clusters into a ClusterSet. |

For this guide, we are going to use single namespace,

```bash
kubectl create namespace cluster-inventory
```

also, to mark a namespace as belonging to a ClusterSet you would run:

```bash
kubectl label namespace cluster-inventory \
  multicluster.x-k8s.io/clusterset=my-fleet
```

## 4. Create a ClusterProfile

The only required field in `spec` is `clusterManager.name`. It is **immutable** after creation, so choose a stable, unique name for your cluster manager instance.

You must also add the `x-k8s.io/cluster-manager` label with the same value to make filtering easier for consumers.

### YAML example

```yaml
apiVersion: multicluster.x-k8s.io/v1alpha1
kind: ClusterProfile
metadata:
  name: cluster-us-west-1
  namespace: cluster-inventory
  labels:
    x-k8s.io/cluster-manager: my-fleet-manager
spec:
  displayName: "US West 1 Production Cluster"
  clusterManager:
    name: my-fleet-manager