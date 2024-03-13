terraform {
  required_version = "~> 1.6.3"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.79.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "2.45.0"
    }
  }
  backend "azurerm" {
    resource_group_name  = "bravo-api-terraformstate-rg"
    storage_account_name = "bravoapitfstate"
    container_name       = "tfstate"
  }
}

provider "azurerm" {
  features {
  }
  skip_provider_registration = true
}

provider "azuread" {
  use_cli = true
  use_msi = false
}
