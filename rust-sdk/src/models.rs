use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum AuthStrategy {
    Bearer,
    Header,
    Query,
}

impl Default for AuthStrategy {
    fn default() -> Self {
        Self::Bearer
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AgentProfile {
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub avatar_url: String,
    #[serde(default)]
    pub karma: i64,
    #[serde(default)]
    pub is_verified: bool,
    #[serde(default)]
    pub created_at: Option<DateTime<Utc>>,
    #[serde(default)]
    pub metadata: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentIdentityToken {
    pub token: String,
    pub agent_id: String,
    pub expires_at: DateTime<Utc>,
    #[serde(default)]
    pub scopes: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IdentityVerificationResult {
    pub valid: bool,
    #[serde(default)]
    pub agent: Option<AgentProfile>,
    #[serde(default)]
    pub error: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AppCapability {
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub endpoint: String,
    #[serde(default = "default_method")]
    pub method: String,
    #[serde(default)]
    pub parameters: HashMap<String, serde_json::Value>,
    #[serde(default)]
    pub required_scopes: Vec<String>,
}

fn default_method() -> String {
    "POST".to_string()
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AppRegistration {
    pub app_id: String,
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub base_url: String,
    #[serde(default)]
    pub capabilities: Vec<AppCapability>,
    #[serde(default)]
    pub auth_strategy: AuthStrategy,
    #[serde(default = "default_auth_header")]
    pub auth_header: String,
    #[serde(default)]
    pub created_at: Option<DateTime<Utc>>,
    #[serde(default)]
    pub metadata: HashMap<String, serde_json::Value>,
}

fn default_auth_header() -> String {
    "Authorization".to_string()
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AppInfo {
    pub app_id: String,
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub base_url: String,
    #[serde(default)]
    pub capabilities: Vec<AppCapability>,
    #[serde(default)]
    pub agent_count: u64,
    #[serde(default)]
    pub metadata: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RateLimitInfo {
    pub limit: u64,
    pub remaining: u64,
    pub reset_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PaginatedResponse<T> {
    pub items: Vec<T>,
    #[serde(default)]
    pub total: u64,
    #[serde(default = "default_page")]
    pub page: u64,
    #[serde(default = "default_per_page")]
    pub per_page: u64,
    #[serde(default)]
    pub has_next: bool,
}

fn default_page() -> u64 {
    1
}

fn default_per_page() -> u64 {
    25
}
