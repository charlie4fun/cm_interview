# Review of the Original Files

This document reviews the original shell script and Kubernetes manifest from
the assignment. The files are kept unchanged in this directory for reference.

## `script.sh`

The script is intended to write a timestamped message to standard output, but
it does not work as written.

### Problems

1. `LOG_FILE` is assigned with single quotes:

   ```shell
   LOG_FILE='$STDOUT'
   ```

   Single quotes prevent variable expansion, so the value becomes the literal
   string `$STDOUT`, not `/dev/stdout`.

2. The function redirects output to `LOGFILE`, while the declared variable is
   named `LOG_FILE`. `LOGFILE` is therefore empty and the redirection fails.

3. `log_message $LOG_MESSAGE` is unquoted. The shell splits the message into
   separate words, but the function prints only `$1`. Most of the message is
   lost.

4. `echo` is less predictable than `printf` when messages contain options or
   escape sequences.

5. The script has no shebang or strict error handling. Its interpreter is not
   explicit, and failures may be missed.

6. Redirecting to `/dev/stdout` is unnecessary for a simple command-line
   script. Writing normally to standard output is clearer and also works with
   shell redirection, containers, and log collectors.

### Suggested implementation

```shell
#!/usr/bin/env bash
set -euo pipefail

readonly LOG_MESSAGE='is the date, written to standard output'

log_message() {
    printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$1"
}

log_message "${LOG_MESSAGE}"
```

This version preserves the complete message, uses an unambiguous UTC
timestamp, and writes directly to standard output.

## `nginx.yaml`

The manifest is intended to run two nginx replicas and expose them through a
Service, but Kubernetes cannot deploy it successfully as written.

### Blocking problems

1. Resource names such as `myNginx` contain uppercase letters. Kubernetes
   names must follow the lowercase DNS label format.

2. The Deployment selector uses `app: myNginx`, while the Pod template uses
   `app: myNgnx`. A Deployment selector must match the Pod template labels, so
   the API server rejects this Deployment.

3. The Service has no selector. It therefore creates no automatic Endpoints
   and cannot send traffic to the nginx Pods.

4. The Service port defaults `targetPort` to `8080`, but the standard nginx
   image listens on port `80`.

5. `containerPort: 8000` does not configure nginx to listen on that port. It is
   only metadata describing an existing container port.

### Reliability and security problems

1. The unqualified `nginx` image uses the mutable `latest` tag. A fixed version
   or digest is required for repeatable deployments.

2. Readiness and liveness probes are missing, so Kubernetes cannot distinguish
   a ready instance from an unhealthy one.

3. Resource requests and limits are missing. Scheduling is less predictable,
   and a container can consume unbounded resources.

4. The container security context does not disable privilege escalation or
   drop Linux capabilities. The default nginx image also commonly starts as
   root to bind to port 80.

5. The manifest uses only a custom `app` label. Recommended Kubernetes labels
   such as `app.kubernetes.io/name` make ownership and selection clearer.

### Suggested structure

The Deployment and Service should use one consistent lowercase label, for
example `app.kubernetes.io/name: nginx`. The container should expose the port
on which the selected nginx image actually listens. The Service should select
the same label and map its public port explicitly:

```yaml
selector:
  app.kubernetes.io/name: nginx
ports:
  - name: http
    port: 8080
    targetPort: 80
```

A production-oriented version should additionally pin the image, define
probes and resources, and use a hardened image that can run as a non-root
user.
