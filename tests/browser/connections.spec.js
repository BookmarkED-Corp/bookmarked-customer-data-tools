/**
 * Browser tests for Customer Data Tools - Connections Setup
 *
 * Tests connection configuration, defaults loading, and auto-testing features
 */

const { test, expect } = require('@playwright/test');

test.describe('Connections Setup - Page Load and Defaults', () => {
  test('should load the connections setup page', async ({ page }) => {
    await page.goto('/connections/setup');

    // Check header
    await expect(page.locator('.header h1')).toContainText('Connection Setup');
    await expect(page.locator('.header p')).toContainText('Configure and test connections');
  });

  test('should have all connection sections visible', async ({ page }) => {
    await page.goto('/connections/setup');

    // Check all sections exist
    await expect(page.locator('#staging-section')).toBeVisible();
    await expect(page.locator('#production-section')).toBeVisible();
    await expect(page.locator('#hubspot-section')).toBeVisible();
    await expect(page.locator('#clickup-section')).toBeVisible();
    await expect(page.locator('#classlink-section')).toBeVisible();
  });

  test('should auto-load defaults from config/defaults.json', async ({ page }) => {
    await page.goto('/connections/setup');

    // Wait for defaults to load
    await page.waitForTimeout(1500);

    // Check staging DB defaults
    await expect(page.locator('#staging-host')).toHaveValue('bookmarked-stage-db-cluster.cluster-ct7orinaenkn.us-east-1.rds.amazonaws.com');
    await expect(page.locator('#staging-database')).toHaveValue('prod_dump_0925');
    await expect(page.locator('#staging-user')).toHaveValue('postgres');
    await expect(page.locator('#staging-password')).toHaveValue('NndbOD0(Eknj243.V4Cuj9Qxy:E[');

    // Check staging API defaults
    await expect(page.locator('#staging-api-url')).toHaveValue('https://stg.api.bookmarked.com');
    await expect(page.locator('#staging-api-username')).toHaveValue('bkd_stff.bookmarked@hotmail.com');
    await expect(page.locator('#staging-api-password')).toHaveValue('Test.123!');

    console.log('✅ Staging defaults loaded correctly');
  });

  test('should auto-load production defaults', async ({ page }) => {
    await page.goto('/connections/setup');
    await page.waitForTimeout(1500);

    // Check production DB defaults
    await expect(page.locator('#production-host')).toHaveValue('bookmarked-prod-db.cqqw6jilbuwg.us-east-1.rds.amazonaws.com');
    await expect(page.locator('#production-database')).toHaveValue('bookmarked_prod');
    await expect(page.locator('#production-user')).toHaveValue('readonly_user');

    // Check production API defaults
    await expect(page.locator('#production-api-url')).toHaveValue('https://prod.api.bookmarked.com');
    await expect(page.locator('#production-api-username')).toHaveValue('stff.bookmarked@hotmail.com');
    await expect(page.locator('#production-api-password')).toHaveValue('Test.123!');

    console.log('✅ Production defaults loaded correctly');
  });

  test('should auto-load ClickUp API key', async ({ page }) => {
    await page.goto('/connections/setup');
    await page.waitForTimeout(1500);

    await expect(page.locator('#clickup-api-key')).toHaveValue('pk_81574061_6QDK41JNLQJ00WF38UGJRSMN0XV1JEC0');

    console.log('✅ ClickUp API key loaded correctly');
  });

  test('should auto-load ClassLink API key', async ({ page }) => {
    await page.goto('/connections/setup');
    await page.waitForTimeout(1500);

    await expect(page.locator('#classlink-api-key')).toHaveValue('c8ad8b56-7b88-426d-9279-83d7442a54da');

    console.log('✅ ClassLink API key loaded correctly');
  });
});

test.describe('Manual Connection Testing', () => {
  test('should test staging database connection successfully', async ({ page }) => {
    await page.goto('/connections/setup');
    await page.waitForTimeout(1500);

    // Clear localStorage to ensure clean state
    await page.evaluate(() => localStorage.clear());

    // Click the first "Test DB Connection" button (staging)
    const testButton = page.locator('#staging-section button.btn-test').first();
    await testButton.click();

    // Wait for test to complete
    await page.waitForTimeout(5000);

    // Check for success message
    const message = page.locator('#staging-message');
    await expect(message).toBeVisible();
    await expect(message).toHaveClass(/success/);
    await expect(message).toContainText('✓');

    // Check status indicator
    const status = page.locator('#staging-status');
    await expect(status).toHaveClass(/success/);

    console.log('✅ Staging DB connection test passed');
  });

  test('should test staging API connection', async ({ page }) => {
    await page.goto('/connections/setup');
    await page.waitForTimeout(1500);
    await page.evaluate(() => localStorage.clear());

    // Click the second test button in staging section (API test)
    const testButton = page.locator('#staging-section button.btn-test').nth(1);
    await testButton.click();

    // Wait for test to complete
    await page.waitForTimeout(5000);

    // Check for result message
    const message = page.locator('#staging-api-message');
    await expect(message).toBeVisible();

    // Should have either success or error message
    const messageText = await message.textContent();
    expect(messageText).toMatch(/✓|✗/);

    console.log(`✅ Staging API test result: ${messageText}`);
  });

  test('should save successful test to localStorage', async ({ page }) => {
    await page.goto('/connections/setup');
    await page.waitForTimeout(1500);
    await page.evaluate(() => localStorage.clear());

    // Test staging DB
    await page.locator('#staging-section button.btn-test').first().click();
    await page.waitForTimeout(5000);

    // Check localStorage was updated
    const testedConnections = await page.evaluate(() => {
      return localStorage.getItem('testedConnections');
    });

    expect(testedConnections).not.toBeNull();
    const parsed = JSON.parse(testedConnections);
    expect(parsed.staging).toBe(true);

    console.log('✅ Test result saved to localStorage');
  });
});

test.describe('Auto-Testing Feature', () => {
  test('should auto-test previously successful connections on page load', async ({ page }) => {
    // First visit - test a connection manually
    await page.goto('/connections/setup');
    await page.waitForTimeout(1500);
    await page.evaluate(() => localStorage.clear());

    // Test staging DB
    await page.locator('#staging-section button.btn-test').first().click();
    await page.waitForTimeout(5000);

    // Verify success
    await expect(page.locator('#staging-message')).toHaveClass(/success/);

    // Reload the page to trigger auto-test
    await page.reload();
    await page.waitForTimeout(3000);

    // Check for auto-test indicator
    const message = page.locator('#staging-message');
    const messageText = await message.textContent();
    expect(messageText).toContain('auto-test');

    console.log('✅ Auto-test triggered on page reload');
  });

  test('should NOT auto-test connections that were never tested', async ({ page }) => {
    await page.goto('/connections/setup');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    await page.waitForTimeout(2000);

    // Production message should not be visible or should not contain "auto-test"
    const productionMessage = page.locator('#production-message');
    const isVisible = await productionMessage.isVisible();

    if (isVisible) {
      const messageText = await productionMessage.textContent();
      expect(messageText).not.toContain('auto-test');
    }

    console.log('✅ Untested connections not auto-tested');
  });

  test('should auto-test multiple connections sequentially', async ({ page }) => {
    await page.goto('/connections/setup');
    await page.waitForTimeout(1500);
    await page.evaluate(() => localStorage.clear());

    // Test staging DB (should succeed) and ClickUp (should succeed)
    await page.locator('#staging-section button.btn-test').first().click();
    await page.waitForTimeout(5000);

    await page.locator('#clickup-section button.btn-test').click();
    await page.waitForTimeout(5000);

    // Reload page
    await page.reload();
    // Wait longer for sequential auto-tests (staging test ~3s + 500ms delay + clickup test ~3s)
    await page.waitForTimeout(8000);

    // Both should show auto-test messages
    const stagingMsg = await page.locator('#staging-message').textContent();
    const clickupMsg = await page.locator('#clickup-message').textContent();

    expect(stagingMsg).toContain('auto-test');
    expect(clickupMsg).toContain('auto-test');

    console.log('✅ Multiple connections auto-tested sequentially');
  });
});

test.describe('UI Elements and Status Indicators', () => {
  test('should have all status indicators in DOM', async ({ page }) => {
    await page.goto('/connections/setup');

    // Check all status indicators exist
    await expect(page.locator('#staging-status')).toBeAttached();
    await expect(page.locator('#production-status')).toBeAttached();
    await expect(page.locator('#hubspot-status')).toBeAttached();
    await expect(page.locator('#clickup-status')).toBeAttached();
    await expect(page.locator('#classlink-status')).toBeAttached();

    console.log('✅ All status indicators present');
  });

  test('should have save button visible and enabled', async ({ page }) => {
    await page.goto('/connections/setup');

    const saveButton = page.locator('text=Save All Connections');
    await expect(saveButton).toBeVisible();
    await expect(saveButton).toBeEnabled();
  });

  test('should update status indicator after successful test', async ({ page, context }) => {
    // Use a fresh context with no localStorage
    await context.clearCookies();

    await page.goto('/connections/setup');

    // Clear localStorage before defaults/auto-tests load
    await page.evaluate(() => localStorage.clear());

    // Wait a bit for page to settle
    await page.waitForTimeout(500);

    // Test connection - this should update the status indicator to success
    await page.locator('#staging-section button.btn-test').first().click();
    await page.waitForTimeout(5000);

    // After test - indicator should have success class
    await expect(page.locator('#staging-status')).toHaveClass(/success/);

    // And message should show success
    const message = page.locator('#staging-message');
    await expect(message).toHaveClass(/success/);

    console.log('✅ Status indicator updated after successful test');
  });
});

test.describe('Error Handling', () => {
  test('should handle failed connection gracefully', async ({ page }) => {
    await page.goto('/connections/setup');
    await page.waitForTimeout(1500);

    // Modify host to invalid value
    await page.locator('#production-host').fill('invalid-host-name.com');

    // Test connection
    await page.locator('#production-section button.btn-test').first().click();
    await page.waitForTimeout(10000);

    // Should show error message
    const message = page.locator('#production-message');
    await expect(message).toBeVisible();
    await expect(message).toHaveClass(/error/);
    await expect(message).toContainText('✗');

    console.log('✅ Failed connection handled gracefully');
  });

  test('should handle missing API response gracefully', async ({ page, context }) => {
    // Block the API endpoint
    await context.route('**/api/connections/test/**', route => {
      route.abort();
    });

    await page.goto('/connections/setup');
    await page.waitForTimeout(1500);

    await page.locator('#staging-section button.btn-test').first().click();
    await page.waitForTimeout(5000);

    // Should show error message or keep original state
    // (Don't crash the page)
    await expect(page.locator('.header')).toBeVisible();

    console.log('✅ Missing API response handled gracefully');
  });
});
