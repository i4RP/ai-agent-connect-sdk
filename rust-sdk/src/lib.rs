pub mod client;
pub mod config;
pub mod errors;
pub mod middleware;
pub mod models;
pub mod providers;
pub mod transport;

pub use client::AgentConnectClient;
pub use config::SDKConfig;
pub use errors::{AgentSDKError, Result};
pub use middleware::{LoggingMiddleware, RateLimitMiddleware, RetryMiddleware};
pub use models::{
    AgentIdentityToken, AgentProfile, AppCapability, AppInfo, AppRegistration, AuthStrategy,
    IdentityVerificationResult, PaginatedResponse, RateLimitInfo,
};
pub use providers::{CustomProvider, MoltbookProvider, Provider};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = SDKConfig::new();
        assert_eq!(config.timeout_secs, 30);
        assert_eq!(config.retries, 3);
        assert!(config.rate_limit_enabled);
        assert_eq!(config.provider, "generic");
    }

    #[test]
    fn test_config_builder() {
        let config = SDKConfig::new()
            .with_api_key("test-key")
            .with_base_url("https://api.example.com")
            .with_timeout(10)
            .with_retries(5)
            .with_provider("moltbook");

        assert_eq!(config.api_key, "test-key");
        assert_eq!(config.base_url, "https://api.example.com");
        assert_eq!(config.timeout_secs, 10);
        assert_eq!(config.retries, 5);
        assert_eq!(config.provider, "moltbook");
    }

    #[test]
    fn test_moltbook_provider_name() {
        let provider = MoltbookProvider::new();
        assert_eq!(provider.name(), "moltbook");
        assert!(provider.base_url().contains("moltbook.com"));
    }

    #[test]
    fn test_moltbook_auth_headers() {
        let provider = MoltbookProvider::new();
        let headers = provider.build_auth_headers("moltbook_xxx");
        assert_eq!(
            headers.get("Authorization").unwrap(),
            "Bearer moltbook_xxx"
        );
    }

    #[test]
    fn test_moltbook_app_auth_headers() {
        let provider = MoltbookProvider::new();
        let headers = provider.build_app_auth_headers("moltdev_xxx");
        assert_eq!(
            headers.get("X-Moltbook-App-Key").unwrap(),
            "moltdev_xxx"
        );
    }

    #[test]
    fn test_moltbook_parse_agent_profile() {
        let provider = MoltbookProvider::new();
        let data = serde_json::json!({
            "agent": {
                "id": "uuid-1",
                "name": "TestBot",
                "description": "A test bot",
                "karma": 100,
                "avatar_url": "https://example.com/avatar.png",
                "is_claimed": true,
                "follower_count": 42,
                "stats": {"posts": 10, "comments": 20}
            }
        });
        let profile = provider.parse_agent_profile(&data).unwrap();
        assert_eq!(profile.id, "uuid-1");
        assert_eq!(profile.name, "TestBot");
        assert_eq!(profile.karma, 100);
        assert!(profile.is_verified);
    }

    #[test]
    fn test_moltbook_parse_verification_valid() {
        let provider = MoltbookProvider::new();
        let data = serde_json::json!({
            "valid": true,
            "agent": {
                "id": "uuid-1",
                "name": "TestBot",
                "description": "",
                "karma": 50
            }
        });
        let result = provider.parse_verification_result(&data).unwrap();
        assert!(result.valid);
        assert!(result.agent.is_some());
        assert_eq!(result.agent.unwrap().name, "TestBot");
    }

    #[test]
    fn test_moltbook_parse_verification_invalid() {
        let provider = MoltbookProvider::new();
        let data = serde_json::json!({
            "valid": false,
            "error": "Token expired"
        });
        let result = provider.parse_verification_result(&data).unwrap();
        assert!(!result.valid);
        assert!(result.agent.is_none());
        assert_eq!(result.error.unwrap(), "Token expired");
    }

    #[test]
    fn test_custom_provider_basic() {
        let provider = CustomProvider::new("myplatform", "https://api.example.com");
        assert_eq!(provider.name(), "myplatform");
        assert_eq!(provider.base_url(), "https://api.example.com");
    }

    #[test]
    fn test_custom_provider_auth_bearer() {
        let provider = CustomProvider::new("test", "https://api.test.com");
        let headers = provider.build_auth_headers("my-key");
        assert_eq!(headers.get("Authorization").unwrap(), "Bearer my-key");
    }

    #[test]
    fn test_custom_provider_auth_header() {
        let provider = CustomProvider::new("test", "https://api.test.com")
            .with_auth_strategy(AuthStrategy::Header)
            .with_auth_header("X-API-Key");
        let headers = provider.build_auth_headers("my-key");
        assert_eq!(headers.get("X-API-Key").unwrap(), "my-key");
    }

    #[test]
    fn test_custom_provider_endpoints() {
        let provider = CustomProvider::new("test", "https://api.test.com")
            .with_identity_token_path("/auth/token")
            .with_verify_identity_path("/auth/verify")
            .with_agent_profile_path("/me");
        assert_eq!(provider.identity_token_endpoint(), "/auth/token");
        assert_eq!(provider.verify_identity_endpoint(), "/auth/verify");
        assert_eq!(provider.agent_profile_endpoint(), "/me");
    }

    #[test]
    fn test_custom_provider_parse_profile() {
        let provider = CustomProvider::new("test", "https://api.test.com");
        let data = serde_json::json!({
            "id": "agent-1",
            "name": "Bot",
            "description": "test"
        });
        let profile = provider.parse_agent_profile(&data).unwrap();
        assert_eq!(profile.id, "agent-1");
        assert_eq!(profile.name, "Bot");
    }

    #[test]
    fn test_custom_provider_parse_verification() {
        let provider = CustomProvider::new("test", "https://api.test.com");
        let data = serde_json::json!({
            "valid": true,
            "agent": {"id": "1", "name": "Bot"}
        });
        let result = provider.parse_verification_result(&data).unwrap();
        assert!(result.valid);
        assert!(result.agent.is_some());
    }

    #[test]
    fn test_raise_for_status_ok() {
        assert!(errors::raise_for_status(200, "ok").is_ok());
        assert!(errors::raise_for_status(201, "created").is_ok());
    }

    #[test]
    fn test_raise_for_status_401() {
        let err = errors::raise_for_status(401, "unauthorized").unwrap_err();
        assert!(matches!(err, AgentSDKError::Authentication(_)));
    }

    #[test]
    fn test_raise_for_status_404() {
        let err = errors::raise_for_status(404, "not found").unwrap_err();
        assert!(matches!(err, AgentSDKError::NotFound(_)));
    }

    #[test]
    fn test_raise_for_status_429() {
        let err = errors::raise_for_status(429, "too many").unwrap_err();
        assert!(matches!(err, AgentSDKError::RateLimit { .. }));
    }

    #[test]
    fn test_raise_for_status_500() {
        let err = errors::raise_for_status(500, "server error").unwrap_err();
        assert!(matches!(err, AgentSDKError::Http { status: 500, .. }));
    }

    #[test]
    fn test_auth_strategy_default() {
        assert_eq!(AuthStrategy::default(), AuthStrategy::Bearer);
    }

    #[test]
    fn test_agent_profile_defaults() {
        let profile = AgentProfile::default();
        assert_eq!(profile.id, "");
        assert_eq!(profile.karma, 0);
        assert!(!profile.is_verified);
    }

    #[test]
    fn test_retry_middleware_should_retry() {
        let retry = RetryMiddleware::new(3, 1000, 60000, 2.0);
        assert!(retry.should_retry(429, 0));
        assert!(retry.should_retry(500, 2));
        assert!(!retry.should_retry(500, 3));
        assert!(!retry.should_retry(200, 0));
        assert!(!retry.should_retry(404, 0));
    }

    #[test]
    fn test_rate_limit_middleware() {
        let rl = RateLimitMiddleware::new(3, 60);
        assert_eq!(rl.remaining(), 3);
        assert!(!rl.is_rate_limited());

        rl.check().unwrap();
        rl.check().unwrap();
        rl.check().unwrap();

        assert_eq!(rl.remaining(), 0);
        assert!(rl.is_rate_limited());
        assert!(rl.check().is_err());
    }

    #[test]
    fn test_client_with_moltbook() {
        let client = AgentConnectClient::with_moltbook("moltbook_xxx").unwrap();
        assert_eq!(client.provider().name(), "moltbook");
    }

    #[test]
    fn test_client_with_custom() {
        let client =
            AgentConnectClient::with_custom("key", "myplatform", "https://api.example.com")
                .unwrap();
        assert_eq!(client.provider().name(), "myplatform");
    }

    #[test]
    fn test_app_capability_serde() {
        let cap = AppCapability {
            name: "search".to_string(),
            description: "Search items".to_string(),
            endpoint: "/search".to_string(),
            method: "GET".to_string(),
            ..Default::default()
        };
        let json = serde_json::to_value(&cap).unwrap();
        assert_eq!(json["name"], "search");
        assert_eq!(json["method"], "GET");
    }
}
