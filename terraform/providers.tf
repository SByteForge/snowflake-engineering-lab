terraform {
  required_providers {
    snowflake = {
      source = "snowflakedb/snowflake"
    }
  }

  backend "gcs" {
    bucket = "snowflake-tf-state-shubham-2026"
    prefix = "snowflake-engineering-lab/state"
  }
}

provider "snowflake" {
  organization_name = var.snowflake_organization
  account_name      = var.snowflake_account
  user              = var.snowflake_user
  password          = var.snowflake_password
}