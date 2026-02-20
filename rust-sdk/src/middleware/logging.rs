use std::time::Instant;

use tracing::info;

pub struct LoggingMiddleware {
    enabled: bool,
}

impl LoggingMiddleware {
    pub fn new(enabled: bool) -> Self {
        Self { enabled }
    }

    pub fn log_request(&self, method: &str, path: &str) -> Option<Instant> {
        if self.enabled {
            info!("-> {} {}", method, path);
            Some(Instant::now())
        } else {
            None
        }
    }

    pub fn log_response(&self, method: &str, path: &str, status: u16, start: Option<Instant>) {
        if self.enabled {
            let duration_ms = start.map(|s| s.elapsed().as_millis()).unwrap_or(0);
            info!("<- {} {} [{}] ({}ms)", method, path, status, duration_ms);
        }
    }
}

impl Default for LoggingMiddleware {
    fn default() -> Self {
        Self::new(false)
    }
}
