variable "vault_address" {
  type        = string
  description = "Vault URL"
  default     = "http://vault.kubernetes.fr:30000"
}

variable "kubernetes_host" {
  type        = string
  description = "Kubernetes control plane endpoint"
  # kubectl config view --raw --minify --flatten --output 'jsonpath={.clusters[].cluster.server}'
  default     = "https://127.0.0.1:37717"
}
