use std::collections::HashMap;

use crate::errors::{AgentSDKError, Result};
use crate::models::{AgentIdentityToken, AgentProfile, AuthStrategy, IdentityVerificationResult};
use crate::providers::base::Provider;

pub const MOLTBOOK_BASE_URL: &str = "https://www.moltbook.com/api/v1";

pub struct MoltbookProvider;

impl MoltbookProvider {
    pub fn new() -> Self {
        Self
    }
}

impl Default for MoltbookProvider {
    fn default() -> Self {
        Self::new()
    }
}

impl Provider for MoltbookProvider {
    fn name(&self) -> &str {
        "moltbook"
    }

    fn base_url(&self) -> &str {
        MOLTBOOK_BASE_URL
    }

    fn default_auth_strategy(&self) -> AuthStrategy {
        AuthStrategy::Bearer
    }

    fn build_auth_headers(&self, api_key: &str) -> HashMap<String, String> {
        let mut headers = HashMap::new();
        headers.insert(
            "Authorization".to_string(),
            format!("Bearer {api_key}"),
        );
        headers
    }

    fn build_app_auth_headers(&self, app_key: &str) -> HashMap<String, String> {
        let mut headers = HashMap::new();
        headers.insert("X-Moltbook-App-Key".to_string(), app_key.to_string());
        headers
    }

    fn parse_agent_profile(&self, data: &serde_json::Value) -> Result<AgentProfile> {
        let agent_data = data.get("agent").unwrap_or(data);
        let stats = agent_data
            .get("stats")
            .cloned()
            .unwrap_or(serde_json::json!({}));
        let mut metadata = HashMap::new();
        if let Some(fc) = agent_data.get("follower_count") {
            metadata.insert("follower_count".to_string(), fc.clone());
        }
        if let Some(posts) = stats.get("posts") {
            metadata.insert("posts".to_string(), posts.clone());
        }
        if let Some(comments) = stats.get("comments") {
            metadata.insert("comments".to_string(), comments.clone());
        }
        if let Some(owner) = agent_data.get("owner") {
            metadata.insert("owner".to_string(), owner.clone());
        }

        Ok(AgentProfile {
            id: agent_data
                .get("id")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            name: agent_data
                .get("name")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            description: agent_data
                .get("description")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            avatar_url: agent_data
                .get("avatar_url")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
            karma: agent_data
                .get("karma")
                .and_then(|v| v.as_i64())
                .unwrap_or(0),
            is_verified: agent_data
                .get("is_claimed")
                .and_then(|v| v.as_bool())
                .unwrap_or(false),
            created_at: agent_data
                .get("created_at")
                .and_then(|v| v.as_str())
                .and_then(|s| chrono::DateTime::parse_from_rfc3339(s).ok())
                .map(|dt| dt.with_timezone(&chrono::Utc)),
            metadata,
        })
    }

    fn parse_identity_token(&self, data: &serde_json::Value) -> Result<AgentIdentityToken> {
        serde_json::from_value(data.clone())
            .map_err(|e| AgentSDKError::Validation(format!("Parse identity token error: {e}")))
    }

    fn parse_verification_result(
        &self,
        data: &serde_json::Value,
    ) -> Result<IdentityVerificationResult> {
        let valid = data
            .get("valid")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);
        let agent = if valid && data.get("agent").is_some() {
            Some(self.parse_agent_profile(data)?)
        } else {
            None
        };
        let error = data
            .get("error")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string());

        Ok(IdentityVerificationResult {
            valid,
            agent,
            error,
        })
    }
}
