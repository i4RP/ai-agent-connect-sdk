use std::collections::HashMap;

use crate::errors::Result;
use crate::models::{
    AgentIdentityToken, AgentProfile, AppCapability, AppInfo, AppRegistration, AuthStrategy,
    IdentityVerificationResult, PaginatedResponse,
};

pub trait Provider: Send + Sync {
    fn name(&self) -> &str;
    fn base_url(&self) -> &str;

    fn default_auth_strategy(&self) -> AuthStrategy {
        AuthStrategy::Bearer
    }

    fn identity_token_endpoint(&self) -> &str {
        "/agents/me/identity-token"
    }

    fn verify_identity_endpoint(&self) -> &str {
        "/agents/verify-identity"
    }

    fn agent_profile_endpoint(&self) -> &str {
        "/agents/me"
    }

    fn app_register_endpoint(&self) -> &str {
        "/apps/register"
    }

    fn app_list_endpoint(&self) -> &str {
        "/apps"
    }

    fn app_detail_endpoint(&self, app_id: &str) -> String {
        format!("/apps/{app_id}")
    }

    fn build_auth_headers(&self, api_key: &str) -> HashMap<String, String>;
    fn build_app_auth_headers(&self, app_key: &str) -> HashMap<String, String>;

    fn parse_agent_profile(&self, data: &serde_json::Value) -> Result<AgentProfile>;
    fn parse_identity_token(&self, data: &serde_json::Value) -> Result<AgentIdentityToken>;
    fn parse_verification_result(
        &self,
        data: &serde_json::Value,
    ) -> Result<IdentityVerificationResult>;

    fn parse_app_registration(&self, data: &serde_json::Value) -> Result<AppRegistration> {
        serde_json::from_value(data.clone())
            .map_err(|e| crate::errors::AgentSDKError::Validation(format!("Parse error: {e}")))
    }

    fn parse_app_info(&self, data: &serde_json::Value) -> Result<AppInfo> {
        serde_json::from_value(data.clone())
            .map_err(|e| crate::errors::AgentSDKError::Validation(format!("Parse error: {e}")))
    }

    fn parse_app_list(&self, data: &serde_json::Value) -> Result<PaginatedResponse<AppInfo>> {
        serde_json::from_value(data.clone())
            .map_err(|e| crate::errors::AgentSDKError::Validation(format!("Parse error: {e}")))
    }

    fn format_register_payload(
        &self,
        name: &str,
        description: &str,
        base_url: &str,
        capabilities: &[AppCapability],
        metadata: Option<&HashMap<String, serde_json::Value>>,
    ) -> serde_json::Value {
        let mut payload = serde_json::json!({
            "name": name,
            "description": description,
            "base_url": base_url,
            "capabilities": capabilities,
        });
        if let Some(meta) = metadata {
            payload["metadata"] = serde_json::json!(meta);
        }
        payload
    }
}
