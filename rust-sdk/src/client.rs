use std::collections::HashMap;
use std::sync::Arc;

use crate::config::SDKConfig;
use crate::errors::{AgentSDKError, Result};
use crate::middleware::logging::LoggingMiddleware;
use crate::middleware::rate_limit::RateLimitMiddleware;
use crate::middleware::retry::RetryMiddleware;
use crate::models::{
    AgentIdentityToken, AgentProfile, AppCapability, AppInfo, AppRegistration,
    IdentityVerificationResult, PaginatedResponse, RateLimitInfo,
};
use crate::providers::base::Provider;
use crate::providers::custom::CustomProvider;
use crate::providers::moltbook::MoltbookProvider;
use crate::transport::Transport;

pub struct AgentConnectClient {
    transport: Transport,
    provider: Arc<dyn Provider>,
    config: SDKConfig,
    retry: RetryMiddleware,
    rate_limiter: Option<RateLimitMiddleware>,
    logger: LoggingMiddleware,
}

impl AgentConnectClient {
    pub fn new(config: SDKConfig, provider: Arc<dyn Provider>) -> Result<Self> {
        let mut cfg = config;
        if cfg.base_url.is_empty() {
            cfg.base_url = provider.base_url().to_string();
        }

        let auth_headers = provider.build_auth_headers(&cfg.api_key);
        for (k, v) in auth_headers {
            cfg.custom_headers.insert(k, v);
        }

        let transport = Transport::new(&cfg)?;
        let retry = RetryMiddleware::new(
            cfg.retries,
            cfg.retry_delay_ms,
            cfg.retry_max_delay_ms,
            cfg.retry_backoff_factor,
        );
        let rate_limiter = if cfg.rate_limit_enabled {
            Some(RateLimitMiddleware::new(
                cfg.rate_limit_max_requests,
                cfg.rate_limit_window_secs,
            ))
        } else {
            None
        };
        let logger = LoggingMiddleware::new(cfg.log_requests);

        Ok(Self {
            transport,
            provider,
            config: cfg,
            retry,
            rate_limiter,
            logger,
        })
    }

    pub fn with_moltbook(api_key: impl Into<String>) -> Result<Self> {
        let config = SDKConfig::new().with_api_key(api_key);
        let provider = Arc::new(MoltbookProvider::new());
        Self::new(config, provider)
    }

    pub fn with_custom(
        api_key: impl Into<String>,
        provider_name: impl Into<String>,
        base_url: impl Into<String>,
    ) -> Result<Self> {
        let base = base_url.into();
        let config = SDKConfig::new().with_api_key(api_key).with_base_url(&base);
        let provider = Arc::new(CustomProvider::new(provider_name, base));
        Self::new(config, provider)
    }

    pub fn from_env(prefix: &str) -> Result<Self> {
        let config = SDKConfig::from_env(prefix);
        let provider: Arc<dyn Provider> = match config.provider.as_str() {
            "moltbook" => Arc::new(MoltbookProvider::new()),
            _ => {
                if config.base_url.is_empty() {
                    return Err(AgentSDKError::Configuration(
                        "Base URL required for non-moltbook providers".to_string(),
                    ));
                }
                Arc::new(CustomProvider::new(
                    config.provider.clone(),
                    config.base_url.clone(),
                ))
            }
        };
        Self::new(config, provider)
    }

    pub fn provider(&self) -> &dyn Provider {
        self.provider.as_ref()
    }

    pub fn rate_limit_info(&self) -> Option<RateLimitInfo> {
        self.transport.last_rate_limit()
    }

    async fn request_with_retry(
        &self,
        method: reqwest::Method,
        path: &str,
        json_body: Option<&serde_json::Value>,
        params: Option<&HashMap<String, String>>,
        extra_headers: Option<&HashMap<String, String>>,
    ) -> Result<serde_json::Value> {
        if let Some(ref rl) = self.rate_limiter {
            rl.check()?;
        }

        let start = self.logger.log_request(method.as_str(), path);

        for attempt in 0..=self.retry.max_retries() {
            let result = self
                .transport
                .request(method.clone(), path, json_body, params, extra_headers)
                .await;

            match result {
                Ok(response) => {
                    let status = response.status().as_u16();
                    self.logger
                        .log_response(method.as_str(), path, status, start);
                    let body: serde_json::Value = response.json().await.map_err(|e| {
                        AgentSDKError::Transport(format!("Failed to parse response: {e}"))
                    })?;
                    return Ok(body);
                }
                Err(AgentSDKError::Http { status, ref body }) => {
                    self.logger
                        .log_response(method.as_str(), path, status, start);
                    if self.retry.should_retry(status, attempt) {
                        let retry_after = None;
                        self.retry
                            .wait_and_log(status, path, attempt, retry_after)
                            .await;
                        continue;
                    }
                    return Err(AgentSDKError::Http {
                        status,
                        body: body.clone(),
                    });
                }
                Err(AgentSDKError::RateLimit {
                    ref message,
                    retry_after,
                }) => {
                    self.logger
                        .log_response(method.as_str(), path, 429, start);
                    if self.retry.should_retry(429, attempt) {
                        self.retry
                            .wait_and_log(429, path, attempt, retry_after)
                            .await;
                        continue;
                    }
                    return Err(AgentSDKError::RateLimit {
                        message: message.clone(),
                        retry_after,
                    });
                }
                Err(e) => return Err(e),
            }
        }

        Err(AgentSDKError::Transport(
            "Max retries exceeded".to_string(),
        ))
    }

    pub async fn get_agent_profile(&self) -> Result<AgentProfile> {
        let path = self.provider.agent_profile_endpoint().to_string();
        let data = self
            .request_with_retry(reqwest::Method::GET, &path, None, None, None)
            .await?;
        self.provider.parse_agent_profile(&data)
    }

    pub async fn generate_identity_token(
        &self,
        scopes: Option<&[String]>,
    ) -> Result<AgentIdentityToken> {
        let path = self.provider.identity_token_endpoint().to_string();
        let mut payload = serde_json::json!({});
        if let Some(s) = scopes {
            payload["scopes"] = serde_json::json!(s);
        }
        let data = self
            .request_with_retry(reqwest::Method::POST, &path, Some(&payload), None, None)
            .await?;
        self.provider.parse_identity_token(&data)
    }

    pub async fn verify_identity(&self, token: &str) -> Result<IdentityVerificationResult> {
        let path = self.provider.verify_identity_endpoint().to_string();
        let app_headers = self
            .provider
            .build_app_auth_headers(&self.config.app_key);
        let payload = serde_json::json!({"token": token});
        let data = self
            .request_with_retry(
                reqwest::Method::POST,
                &path,
                Some(&payload),
                None,
                Some(&app_headers),
            )
            .await?;
        self.provider.parse_verification_result(&data)
    }

    pub async fn register_app(
        &self,
        name: &str,
        description: &str,
        base_url: &str,
        capabilities: &[AppCapability],
        metadata: Option<&HashMap<String, serde_json::Value>>,
    ) -> Result<AppRegistration> {
        let path = self.provider.app_register_endpoint().to_string();
        let payload =
            self.provider
                .format_register_payload(name, description, base_url, capabilities, metadata);
        let data = self
            .request_with_retry(reqwest::Method::POST, &path, Some(&payload), None, None)
            .await?;
        self.provider.parse_app_registration(&data)
    }

    pub async fn get_app(&self, app_id: &str) -> Result<AppInfo> {
        let path = self.provider.app_detail_endpoint(app_id);
        let data = self
            .request_with_retry(reqwest::Method::GET, &path, None, None, None)
            .await?;
        self.provider.parse_app_info(&data)
    }

    pub async fn list_apps(
        &self,
        page: u64,
        per_page: u64,
        sort: &str,
    ) -> Result<PaginatedResponse<AppInfo>> {
        let path = self.provider.app_list_endpoint().to_string();
        let mut params = HashMap::new();
        params.insert("page".to_string(), page.to_string());
        params.insert("per_page".to_string(), per_page.to_string());
        params.insert("sort".to_string(), sort.to_string());
        let data = self
            .request_with_retry(reqwest::Method::GET, &path, None, Some(&params), None)
            .await?;
        self.provider.parse_app_list(&data)
    }

    pub async fn request(
        &self,
        method: &str,
        path: &str,
        json_body: Option<&serde_json::Value>,
        params: Option<&HashMap<String, String>>,
    ) -> Result<serde_json::Value> {
        let m = method
            .parse::<reqwest::Method>()
            .map_err(|e| AgentSDKError::Configuration(format!("Invalid HTTP method: {e}")))?;
        self.request_with_retry(m, path, json_body, params, None)
            .await
    }
}
