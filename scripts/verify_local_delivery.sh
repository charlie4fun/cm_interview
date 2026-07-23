#!/usr/bin/env bash
set -euo pipefail

cluster_name="${CLUSTER_NAME:-interview-dev}"
release_name="${RELEASE_NAME:-interview}"
namespace="${NAMESPACE:-interview}"
chart="${CHART:-charts/interview-app}"
timeout="${TIMEOUT:-90s}"
deployment="${release_name}-interview-app"
service="${release_name}-interview-app"

kubectl config use-context "kind-${cluster_name}" >/dev/null
kubectl -n "${namespace}" rollout status "deployment/${deployment}" --timeout="${timeout}"

root_response="$(kubectl get --raw \
  "/api/v1/namespaces/${namespace}/services/http:${service}:http/proxy/")"
python3 -c \
  'import json,sys; data=json.loads(sys.argv[1]); assert {"name","version","commit"} <= data.keys()' \
  "${root_response}"
kubectl get --raw \
  "/api/v1/namespaces/${namespace}/services/http:${service}:http/proxy/healthz" \
  | python3 -c 'import json,sys; assert json.load(sys.stdin)["status"] == "ok"'
kubectl get --raw \
  "/api/v1/namespaces/${namespace}/services/http:${service}:http/proxy/readyz" \
  | python3 -c 'import json,sys; assert json.load(sys.stdin)["status"] == "ready"'

old_revision="$(kubectl -n "${namespace}" get "deployment/${deployment}" \
  -o jsonpath='{.metadata.generation}')"
verification_revision="verify-$(date +%s)"
helm upgrade "${release_name}" "${chart}" \
  --namespace "${namespace}" \
  --reuse-values \
  --set-string "deploymentRevision=${verification_revision}" \
  --wait --timeout "${timeout}" >/dev/null
new_revision="$(kubectl -n "${namespace}" get "deployment/${deployment}" \
  -o jsonpath='{.metadata.generation}')"
if [[ "${old_revision}" == "${new_revision}" ]]; then
  echo "Rolling update did not create a new Deployment generation" >&2
  exit 1
fi

pod="$(kubectl -n "${namespace}" get pods \
  -l "app.kubernetes.io/name=interview-app,app.kubernetes.io/instance=${release_name}" \
  -o jsonpath='{.items[0].metadata.name}')"
restarts_before="$(kubectl -n "${namespace}" get "pod/${pod}" \
  -o jsonpath='{.status.containerStatuses[0].restartCount}')"
kubectl -n "${namespace}" exec "${pod}" -- \
  python -c 'import os,signal; os.kill(1, signal.SIGTERM)'

for _ in {1..30}; do
  restarts_after="$(kubectl -n "${namespace}" get "pod/${pod}" \
    -o jsonpath='{.status.containerStatuses[0].restartCount}' 2>/dev/null || true)"
  if [[ -n "${restarts_after}" && "${restarts_after}" -gt "${restarts_before}" ]]; then
    break
  fi
  sleep 1
done
if [[ -z "${restarts_after:-}" || "${restarts_after}" -le "${restarts_before}" ]]; then
  echo "Container did not restart after SIGTERM" >&2
  exit 1
fi
kubectl -n "${namespace}" logs "${pod}" --previous \
  | grep -q '"message":"shutdown requested"'
kubectl -n "${namespace}" rollout status "deployment/${deployment}" --timeout="${timeout}"

echo "Local delivery verified: endpoints, probes, rolling update, and graceful shutdown"
