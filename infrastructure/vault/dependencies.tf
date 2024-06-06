terraform {
  required_version = ">= 1.5.0, <2.0.0"

  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "~> 4.2.0"
    }
  }
}

provider "vault" {
  # Take auth from ~/.vault-token by default
  # Need `vault login`
  address = var.vault_address
}
