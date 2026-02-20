use std::collections::VecDeque;
use std::sync::Mutex;
use std::time::{Duration, Instant};

use crate::errors::{AgentSDKError, Result};

pub struct RateLimitMiddleware {
    max_requests: u64,
    window: Duration,
    timestamps: Mutex<VecDeque<Instant>>,
}

impl RateLimitMiddleware {
    pub fn new(max_requests: u64, window_secs: u64) -> Self {
        Self {
            max_requests,
            window: Duration::from_secs(window_secs),
            timestamps: Mutex::new(VecDeque::new()),
        }
    }

    fn clean_old(&self, timestamps: &mut VecDeque<Instant>) {
        let now = Instant::now();
        while timestamps.front().is_some_and(|t| now.duration_since(*t) > self.window) {
            timestamps.pop_front();
        }
    }

    pub fn check(&self) -> Result<()> {
        let mut timestamps = self
            .timestamps
            .lock()
            .map_err(|_| AgentSDKError::Transport("Rate limit lock poisoned".to_string()))?;
        self.clean_old(&mut timestamps);

        if timestamps.len() as u64 >= self.max_requests {
            let wait_time = timestamps
                .front()
                .map(|t| {
                    let elapsed = Instant::now().duration_since(*t);
                    if elapsed < self.window {
                        self.window - elapsed
                    } else {
                        Duration::ZERO
                    }
                })
                .unwrap_or(Duration::ZERO);

            return Err(AgentSDKError::RateLimit {
                message: format!(
                    "Client-side rate limit: {} requests per {}s window exceeded",
                    self.max_requests,
                    self.window.as_secs()
                ),
                retry_after: Some(wait_time.as_secs_f64()),
            });
        }

        timestamps.push_back(Instant::now());
        Ok(())
    }

    pub fn remaining(&self) -> u64 {
        let mut timestamps = match self.timestamps.lock() {
            Ok(t) => t,
            Err(_) => return 0,
        };
        self.clean_old(&mut timestamps);
        self.max_requests.saturating_sub(timestamps.len() as u64)
    }

    pub fn is_rate_limited(&self) -> bool {
        self.remaining() == 0
    }
}
