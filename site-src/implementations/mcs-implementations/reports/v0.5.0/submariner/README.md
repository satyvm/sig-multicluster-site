To reproduce these results:

* Clone Lighthouse (the Submariner component that implements MCS):

  ```
  git clone https://github.com/submariner-io/lighthouse
  cd lighthouse
  ```

* Check out the appropriate tag

* Deploy the test clusters:

  ```
  make deploy using=clusterset-ip
  export KUBECONFIG=$(find $(git rev-parse --show-toplevel)/output/kubeconfigs/ -type f -printf %p:)
  ```

* Run the conformance suite using the `cluster1` and `cluster2`
  contexts; from `mcs-api`:
  
  ```
  go -C conformance run github.com/onsi/ginkgo/v2/ginkgo . -- \
     --contexts=cluster1,cluster2
  ```
