use std::time::Duration;

use tracing::warn;

const RETRYABLE_STATUS_CODES: &[u16] = &[429, 500, 502, 503, 504];

#[derive(Debug, Clone)]
pub struct RetryMiddleware {
    max_retries: u32,
    base_delay: Duration,
    max_delay: Duration,
    backoff_factor: f64,
}

impl RetryMiddleware {
    pub fn new(max_retries: u32, base_delay_ms: u64, max_delay_ms: u64, backoff_factor: f64) -> Self {
        Self {
            max_retries,
            base_delay: Duration::from_millis(base_delay_ms),
            max_delay: Duration::from_millis(max_delay_ms),
            backoff_factor,
        }
    }

    pub fn should_retry(&self, status: u16, attempt: u32) -> bool {
        RETRYABLE_STATUS_CODES.contains(&status) && attempt < self.max_retries
    }

    pub fn delay_for_attempt(&self, attempt: u32, retry_after: Option<f64>) -> Duration {
        if let Some(secs) = retry_after {
            return Duration::from_secs_f64(secs);
        }
        let delay_ms = self.base_delay.as_millis() as f64 * self.backoff_factor.powi(attempt as i32);
        let delay = Duration::from_millis(delay_ms as u64);
        std::cmp::min(delay, self.max_delay)
    }

    pub fn max_retries(&self) -> u32 {
        self.max_retries
    }

    pub async fn wait_and_log(&self, status: u16, path: &str, attempt: u32, retry_after: Option<f64>) {
        let delay = self.delay_for_attempt(attempt, retry_after);
        warn!(
            "Retryable status {} on {} (attempt {}/{}), waiting {:?}",
            status,
            path,
            attempt + 1,
            self.max_retries,
            delay,
        );
        tokio::time::sleep(delay).await;
    }
}

impl Default for RetryMiddleware {
    fn default() -> Self {
        Self::new(3, 1000, 60000, 2.0)
    }
}
