use thiserror::Error;

#[derive(Error, Debug)]
pub enum AgentSDKError {
    #[error("Authentication failed: {0}")]
    Authentication(String),

    #[error("Authorization failed: {0}")]
    Authorization(String),

    #[error("Resource not found: {0}")]
    NotFound(String),

    #[error("Rate limit exceeded (retry after {retry_after:?}s): {message}")]
    RateLimit {
        message: String,
        retry_after: Option<f64>,
    },

    #[error("Validation error: {0}")]
    Validation(String),

    #[error("Transport error: {0}")]
    Transport(String),

    #[error("Provider error ({provider}): {message}")]
    Provider { message: String, provider: String },

    #[error("Configuration error: {0}")]
    Configuration(String),

    #[error("HTTP error ({status}): {body}")]
    Http { status: u16, body: String },
}

impl AgentSDKError {
    pub fn status_code(&self) -> Option<u16> {
        match self {
            Self::Authentication(_) => Some(401),
            Self::Authorization(_) => Some(403),
            Self::NotFound(_) => Some(404),
            Self::Validation(_) => Some(422),
            Self::RateLimit { .. } => Some(429),
            Self::Http { status, .. } => Some(*status),
            _ => None,
        }
    }
}

pub fn raise_for_status(status: u16, body: &str) -> std::result::Result<(), AgentSDKError> {
    match status {
        200..=399 => Ok(()),
        401 => Err(AgentSDKError::Authentication(body.to_string())),
        403 => Err(AgentSDKError::Authorization(body.to_string())),
        404 => Err(AgentSDKError::NotFound(body.to_string())),
        422 => Err(AgentSDKError::Validation(body.to_string())),
        429 => Err(AgentSDKError::RateLimit {
            message: body.to_string(),
            retry_after: None,
        }),
        _ => Err(AgentSDKError::Http {
            status,
            body: body.to_string(),
        }),
    }
}

pub type Result<T> = std::result::Result<T, AgentSDKError>;

impl AgentSDKError {
    pub fn is_retryable(&self) -> bool {
        matches!(
            self,
            Self::RateLimit { .. }
                | Self::Http { status: 500, .. }
                | Self::Http { status: 502, .. }
                | Self::Http { status: 503, .. }
                | Self::Http { status: 504, .. }
        )
    }
}
