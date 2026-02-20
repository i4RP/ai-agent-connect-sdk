use std::collections::HashMap;

use crate::errors::{AgentSDKError, Result};
use crate::models::{
    AgentIdentityToken, AgentProfile, AuthStrategy, IdentityVerificationResult,
};
use crate::providers::base::Provider;

pub struct CustomProvider {
    provider_name: String,
    provider_base_url: String,
    auth_strategy: AuthStrategy,
    auth_header: String,
    app_auth_header: String,
    identity_token_path: String,
    verify_identity_path: String,
    agent_profile_path: String,
    app_register_path: String,
    app_list_path: String,
}

impl CustomProvider {
    pub fn new(name: impl Into<String>, base_url: impl Into<String>) -> Self {
        Self {
            provider_name: name.into(),
            provider_base_url: base_url.into(),
            auth_strategy: AuthStrategy::Bearer,
            auth_header: "Authorization".to_string(),
            app_auth_header: "X-App-Key".to_string(),
            identity_token_path: "/agents/me/identity-token".to_string(),
            verify_identity_path: "/agents/verify-identity".to_string(),
            agent_profile_path: "/agents/me".to_string(),
            app_register_path: "/apps/register".to_string(),
            app_list_path: "/apps".to_string(),
        }
    }

    pub fn with_auth_strategy(mut self, strategy: AuthStrategy) -> Self {
        self.auth_strategy = strategy;
        self
    }

    pub fn with_auth_header(mut self, header: impl Into<String>) -> Self {
        self.auth_header = header.into();
        self
    }

    pub fn with_app_auth_header(mut self, header: impl Into<String>) -> Self {
        self.app_auth_header = header.into();
        self
    }

    pub fn with_identity_token_path(mut self, path: impl Into<String>) -> Self {
        self.identity_token_path = path.into();
        self
    }

    pub fn with_verify_identity_path(mut self, path: impl Into<String>) -> Self {
        self.verify_identity_path = path.into();
        self
    }

    pub fn with_agent_profile_path(mut self, path: impl Into<String>) -> Self {
        self.agent_profile_path = path.into();
        self
    }

    pub fn with_app_register_path(mut self, path: impl Into<String>) -> Self {
        self.app_register_path = path.into();
        self
    }

    pub fn with_app_list_path(mut self, path: impl Into<String>) -> Self {
        self.app_list_path = path.into();
        self
    }
}

impl Provider for CustomProvider {
    fn name(&self) -> &str {
        &self.provider_name
    }

    fn base_url(&self) -> &str {
        &self.provider_base_url
    }

    fn default_auth_strategy(&self) -> AuthStrategy {
        self.auth_strategy.clone()
    }

    fn identity_token_endpoint(&self) -> &str {
        &self.identity_token_path
    }

    fn verify_identity_endpoint(&self) -> &str {
        &self.verify_identity_path
    }

    fn agent_profile_endpoint(&self) -> &str {
        &self.agent_profile_path
    }

    fn app_register_endpoint(&self) -> &str {
        &self.app_register_path
    }

    fn app_list_endpoint(&self) -> &str {
        &self.app_list_path
    }

    fn build_auth_headers(&self, api_key: &str) -> HashMap<String, String> {
        let mut headers = HashMap::new();
        match self.auth_strategy {
            AuthStrategy::Bearer => {
                headers.insert(
                    self.auth_header.clone(),
                    format!("Bearer {api_key}"),
                );
            }
            AuthStrategy::Header | AuthStrategy::Query => {
                headers.insert(self.auth_header.clone(), api_key.to_string());
            }
        }
        headers
    }

    fn build_app_auth_headers(&self, app_key: &str) -> HashMap<String, String> {
        let mut headers = HashMap::new();
        headers.insert(self.app_auth_header.clone(), app_key.to_string());
        headers
    }

    fn parse_agent_profile(&self, data: &serde_json::Value) -> Result<AgentProfile> {
        serde_json::from_value(data.clone())
            .map_err(|e| AgentSDKError::Validation(format!("Parse error: {e}")))
    }

    fn parse_identity_token(&self, data: &serde_json::Value) -> Result<AgentIdentityToken> {
        serde_json::from_value(data.clone())
            .map_err(|e| AgentSDKError::Validation(format!("Parse error: {e}")))
    }

    fn parse_verification_result(
        &self,
        data: &serde_json::Value,
    ) -> Result<IdentityVerificationResult> {
        let valid = data
            .get("valid")
            .and_then(|v| v.as_bool())
            .unwrap_or(false);
        let agent = if valid {
            data.get("agent")
                .and_then(|a| serde_json::from_value(a.clone()).ok())
        } else {
            None
        };
        Ok(IdentityVerificationResult {
            valid,
            agent,
            error: data
                .get("error")
                .and_then(|v| v.as_str())
                .map(|s| s.to_string()),
        })
    }
}
