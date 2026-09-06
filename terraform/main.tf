resource "snowflake_database" "ai_lab" {
  name = "AI_ENGINEERING_LAB"
}

resource "snowflake_schema" "raw" {
  database = snowflake_database.ai_lab.name
  name     = "RAW"
}

resource "snowflake_schema" "curated" {
  database = snowflake_database.ai_lab.name
  name     = "CURATED"
}

resource "snowflake_schema" "ai" {
  database = snowflake_database.ai_lab.name
  name     = "AI"
}

resource "snowflake_schema" "analytics" {
  database = snowflake_database.ai_lab.name
  name     = "ANALYTICS"
}