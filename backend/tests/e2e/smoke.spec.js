import { test, expect } from '@playwright/test';

test.describe('Hello World Website - E2E Smoke Tests', () => {

  // 1. Page loads without JavaScript errors
  test('page loads without JavaScript errors', async ({ page }) => {
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/');
    
    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
    
    expect(consoleErrors).toHaveLength(0);
  });

  // 2. 'Hello World' heading is visible and centered
  test('Hello World heading is visible and centered', async ({ page }) => {
    await page.goto('/');
    
    const greeting = page.locator('h1#greeting');
    await expect(greeting).toBeVisible();
    await expect(greeting).toHaveText('Hello World');
    
    // Check centering - the card has text-align: center
    const card = page.locator('.card');
    const cardBox = await card.boundingBox();
    const greetingBox = await greeting.boundingBox();
    
    // Greeting should be horizontally centered within the card
    const cardCenterX = cardBox.x + cardBox.width / 2;
    const greetingCenterX = greetingBox.x + greetingBox.width / 2;
    
    expect(Math.abs(cardCenterX - greetingCenterX)).toBeLessThan(2);
  });

  // 3. Date/time display is populated on load
  test('date/time display is populated on load', async ({ page }) => {
    await page.goto('/');
    
    const timestamp = page.locator('#timestamp');
    await expect(timestamp).toBeVisible();
    
    const timestampText = await timestamp.textContent();
    expect(timestampText).toContain('Page loaded at:');
    
    // Should have a formatted date/time (contains weekday, month, day, year, time)
    const datePattern = /Page loaded at:\s*.+/;
    expect(timestampText).toMatch(datePattern);
  });

  // 4. No 404 errors for CSS or JS resources
  test('no 404 errors for CSS or JS resources', async ({ page }) => {
    const failedRequests = [];
    
    page.on('requestfailed', request => {
      failedRequests.push({
        url: request.url(),
        failure: request.failure()?.errorText
      });
    });

    page.on('response', response => {
      if (response.status() === 404) {
        failedRequests.push({
          url: response.url(),
          status: 404
        });
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Filter to only CSS/JS resources
    const cssJsFailures = failedRequests.filter(
      req => req.url.endsWith('.css') || req.url.endsWith('.js')
    );
    
    expect(cssJsFailures).toHaveLength(0);
  });

  // 5. Layout renders correctly at 375px viewport width (mobile)
  test('layout renders correctly at mobile viewport', async ({ page }) => {
    // Set mobile viewport (iPhone SE width)
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Verify the greeting is still visible
    const greeting = page.locator('h1#greeting');
    await expect(greeting).toBeVisible();
    
    // Verify the card renders without horizontal overflow
    const card = page.locator('.card');
    const cardBox = await card.boundingBox();
    
    expect(cardBox.x).toBeGreaterThanOrEqual(0);
    expect(cardBox.x + cardBox.width).toBeLessThanOrEqual(375);
    
    // Verify timestamp is visible at mobile size
    const timestamp = page.locator('#timestamp');
    await expect(timestamp).toBeVisible();
  });

});
