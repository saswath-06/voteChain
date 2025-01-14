const RATE_LIMIT_WINDOW = 60000; // 1 minute
const MAX_REQUESTS = 10; // 10 requests per minute

class RateLimiter {
  private requests: number[] = [];

  canMakeRequest(): boolean {
    const now = Date.now();
    this.requests = this.requests.filter(
      timestamp => now - timestamp < RATE_LIMIT_WINDOW
    );
    return this.requests.length < MAX_REQUESTS;
  }

  addRequest(): void {
    this.requests.push(Date.now());
  }
}

export const rateLimiter = new RateLimiter();
