use std::collections::HashMap;
use std::sync::Mutex;
use std::time::Duration;

use reqwest::header::{HeaderMap, HeaderName, HeaderValue};
use reqwest::{Client, Method, Response};
use tracing::debug;

use crate::config::SDKConfig;
use crate::errors::{raise_for_status, AgentSDKError, Result};
use crate::models::RateLimitInfo;

pub struct Transport {
    client: Client,
    config: SDKConfig,
    last_rate_limit: Mutex<Option<RateLimitInfo>>,
}

impl Transport {
    pub fn new(config: &SDKConfig) -> Result<Self> {
        let mut default_headers = HeaderMap::new();
        if !config.api_key.is_empty() {
            let val = format!("Bearer {}", config.api_key);
            default_headers.insert(
                reqwest::header::AUTHORIZATION,
                HeaderValue::from_str(&val).map_err(|e| {
                    AgentSDKError::Configuration(format!("Invalid API key header: {e}"))
                })?,
            );
        }
        for (k, v) in &config.custom_headers {
            let name = HeaderName::from_bytes(k.as_bytes())
                .map_err(|e| AgentSDKError::Configuration(format!("Invalid header name: {e}")))?;
            let value = HeaderValue::from_str(v)
                .map_err(|e| AgentSDKError::Configuration(format!("Invalid header value: {e}")))?;
            default_headers.insert(name, value);
        }

        let client = Client::builder()
            .timeout(Duration::from_secs(config.timeout_secs))
            .default_headers(default_headers)
            .build()
            .map_err(|e| AgentSDKError::Transport(format!("Failed to build HTTP client: {e}")))?;

        Ok(Self {
            client,
            config: config.clone(),
            last_rate_limit: Mutex::new(None),
        })
    }

    fn parse_rate_limit(&self, response: &Response) -> Option<RateLimitInfo> {
        let limit = response
            .headers()
            .get("X-RateLimit-Limit")
            .and_then(|v| v.to_str().ok())
            .and_then(|v| v.parse::<u64>().ok());
        let remaining = response
            .headers()
            .get("X-RateLimit-Remaining")
            .and_then(|v| v.to_str().ok())
            .and_then(|v| v.parse::<u64>().ok());

        if let (Some(limit), Some(remaining)) = (limit, remaining) {
            let info = RateLimitInfo {
                limit,
                remaining,
                reset_at: None,
            };
            if let Ok(mut guard) = self.last_rate_limit.lock() {
                *guard = Some(info.clone());
            }
            Some(info)
        } else {
            None
        }
    }

    pub fn last_rate_limit(&self) -> Option<RateLimitInfo> {
        self.last_rate_limit
            .lock()
            .ok()
            .and_then(|guard| guard.clone())
    }

    pub async fn request(
        &self,
        method: Method,
        path: &str,
        json_body: Option<&serde_json::Value>,
        params: Option<&HashMap<String, String>>,
        extra_headers: Option<&HashMap<String, String>>,
    ) -> Result<Response> {
        let url = format!("{}{}", self.config.base_url.trim_end_matches('/'), path);

        if self.config.log_requests {
            debug!("-> {} {} params={:?}", method, url, params);
        }

        let mut req = self.client.request(method.clone(), &url);

        if let Some(p) = params {
            req = req.query(p);
        }
        if let Some(body) = json_body {
            req = req.json(body);
        }
        if let Some(headers) = extra_headers {
            for (k, v) in headers {
                req = req.header(k.as_str(), v.as_str());
            }
        }

        let response = req.send().await.map_err(|e| {
            AgentSDKError::Transport(format!("Request failed: {e}"))
        })?;

        self.parse_rate_limit(&response);

        let status = response.status().as_u16();

        if self.config.log_responses {
            debug!("<- {} [{}]", url, status);
        }

        if status >= 400 {
            let body_text = response.text().await.unwrap_or_default();
            raise_for_status(status, &body_text)?;
            unreachable!();
        }

        Ok(response)
    }

    pub async fn get(
        &self,
        path: &str,
        params: Option<&HashMap<String, String>>,
        headers: Option<&HashMap<String, String>>,
    ) -> Result<Response> {
        self.request(Method::GET, path, None, params, headers).await
    }

    pub async fn post(
        &self,
        path: &str,
        json_body: Option<&serde_json::Value>,
        headers: Option<&HashMap<String, String>>,
    ) -> Result<Response> {
        self.request(Method::POST, path, json_body, None, headers)
            .await
    }

    pub async fn put(
        &self,
        path: &str,
        json_body: Option<&serde_json::Value>,
        headers: Option<&HashMap<String, String>>,
    ) -> Result<Response> {
        self.request(Method::PUT, path, json_body, None, headers)
            .await
    }

    pub async fn delete(
        &self,
        path: &str,
        headers: Option<&HashMap<String, String>>,
    ) -> Result<Response> {
        self.request(Method::DELETE, path, None, None, headers)
            .await
    }
}
