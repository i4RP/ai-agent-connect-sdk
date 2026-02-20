use std::collections::HashMap;
use std::env;

#[derive(Debug, Clone)]
pub struct SDKConfig {
    pub api_key: String,
    pub app_key: String,
    pub base_url: String,
    pub timeout_secs: u64,
    pub retries: u32,
    pub retry_delay_ms: u64,
    pub retry_max_delay_ms: u64,
    pub retry_backoff_factor: f64,
    pub rate_limit_enabled: bool,
    pub rate_limit_max_requests: u64,
    pub rate_limit_window_secs: u64,
    pub log_requests: bool,
    pub log_responses: bool,
    pub custom_headers: HashMap<String, String>,
    pub provider: String,
}

impl Default for SDKConfig {
    fn default() -> Self {
        Self {
            api_key: String::new(),
            app_key: String::new(),
            base_url: String::new(),
            timeout_secs: 30,
            retries: 3,
            retry_delay_ms: 1000,
            retry_max_delay_ms: 60000,
            retry_backoff_factor: 2.0,
            rate_limit_enabled: true,
            rate_limit_max_requests: 100,
            rate_limit_window_secs: 60,
            log_requests: false,
            log_responses: false,
            custom_headers: HashMap::new(),
            provider: "generic".to_string(),
        }
    }
}

impl SDKConfig {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn from_env(prefix: &str) -> Self {
        Self {
            api_key: env::var(format!("{prefix}_API_KEY")).unwrap_or_default(),
            app_key: env::var(format!("{prefix}_APP_KEY")).unwrap_or_default(),
            base_url: env::var(format!("{prefix}_BASE_URL")).unwrap_or_default(),
            timeout_secs: env::var(format!("{prefix}_TIMEOUT"))
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(30),
            retries: env::var(format!("{prefix}_RETRIES"))
                .ok()
                .and_then(|v| v.parse().ok())
                .unwrap_or(3),
            retry_delay_ms: 1000,
            retry_max_delay_ms: 60000,
            retry_backoff_factor: 2.0,
            rate_limit_enabled: env::var(format!("{prefix}_RATE_LIMIT"))
                .map(|v| v.to_lowercase() == "true")
                .unwrap_or(true),
            rate_limit_max_requests: 100,
            rate_limit_window_secs: 60,
            log_requests: env::var(format!("{prefix}_LOG_REQUESTS"))
                .map(|v| v.to_lowercase() == "true")
                .unwrap_or(false),
            log_responses: env::var(format!("{prefix}_LOG_RESPONSES"))
                .map(|v| v.to_lowercase() == "true")
                .unwrap_or(false),
            custom_headers: HashMap::new(),
            provider: env::var(format!("{prefix}_PROVIDER")).unwrap_or_else(|_| "generic".to_string()),
        }
    }

    pub fn with_api_key(mut self, api_key: impl Into<String>) -> Self {
        self.api_key = api_key.into();
        self
    }

    pub fn with_app_key(mut self, app_key: impl Into<String>) -> Self {
        self.app_key = app_key.into();
        self
    }

    pub fn with_base_url(mut self, base_url: impl Into<String>) -> Self {
        self.base_url = base_url.into();
        self
    }

    pub fn with_timeout(mut self, timeout_secs: u64) -> Self {
        self.timeout_secs = timeout_secs;
        self
    }

    pub fn with_retries(mut self, retries: u32) -> Self {
        self.retries = retries;
        self
    }

    pub fn with_provider(mut self, provider: impl Into<String>) -> Self {
        self.provider = provider.into();
        self
    }

    pub fn with_header(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.custom_headers.insert(key.into(), value.into());
        self
    }
}
