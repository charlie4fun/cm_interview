{{- define "interview-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "interview-app.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "interview-app.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "interview-app.labels" -}}
app.kubernetes.io/name: {{ include "interview-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end }}

{{- define "interview-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "interview-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
