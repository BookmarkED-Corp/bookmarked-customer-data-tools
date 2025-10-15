/**
 * Browser tests for Customer Data Tools - Student Search
 *
 * Tests district selection, student search, and side-by-side data comparison
 */

const { test, expect } = require('@playwright/test');

test.describe('District Selection', () => {
  test('should load the district select page', async ({ page }) => {
    await page.goto('/district-select');

    // Check header
    await expect(page.locator('h1')).toContainText('Select District');
    await expect(page.locator('p')).toContainText('Choose an environment and district');
  });

  test('should have environment selector with staging and production', async ({ page }) => {
    await page.goto('/district-select');

    const envSelect = page.locator('#environment-select');
    await expect(envSelect).toBeVisible();

    // Check options
    await expect(envSelect.locator('option[value="staging"]')).toBeVisible();
    await expect(envSelect.locator('option[value="production"]')).toBeVisible();
  });

  test('should load districts from API when environment is selected', async ({ page }) => {
    await page.goto('/district-select');

    // Select staging environment
    await page.locator('#environment-select').selectOption('staging');

    // Wait for districts to load
    await page.waitForTimeout(3000);

    // Check that district list is visible
    const districtList = page.locator('#district-list');
    await expect(districtList).toBeVisible();

    // Should have at least one district
    const districts = page.locator('.district-item');
    await expect(districts.first()).toBeVisible();

    console.log('✅ Districts loaded from staging');
  });

  test('should display district information correctly', async ({ page }) => {
    await page.goto('/district-select');
    await page.locator('#environment-select').selectOption('staging');
    await page.waitForTimeout(3000);

    // Check first district item has name
    const firstDistrict = page.locator('.district-item').first();
    await expect(firstDistrict.locator('.district-name')).not.toBeEmpty();

    console.log('✅ District information displayed');
  });

  test('should select a district and proceed to search', async ({ page }) => {
    await page.goto('/district-select');
    await page.locator('#environment-select').selectOption('staging');
    await page.waitForTimeout(3000);

    // Click first district
    await page.locator('.district-item').first().click();

    // Should navigate to student search page
    await page.waitForURL('**/tools/student-search');
    await expect(page).toHaveURL(/\/tools\/student-search/);

    console.log('✅ District selected, navigated to search page');
  });
});

test.describe('Student Search Page', () => {
  test('should load the student search page', async ({ page }) => {
    await page.goto('/tools/student-search');

    // Check header
    await expect(page.locator('h1')).toContainText('Student Search');
  });

  test('should have search input and button', async ({ page }) => {
    await page.goto('/tools/student-search');

    await expect(page.locator('#search-input')).toBeVisible();
    await expect(page.locator('#search-button')).toBeVisible();
  });

  test('should show selected district information', async ({ page, context }) => {
    await page.goto('/tools/student-search');

    // Inject district info into localStorage
    await page.evaluate(() => {
      localStorage.setItem('selectedDistrict', JSON.stringify({
        id: 123,
        name: 'Test District',
        environment: 'staging'
      }));
    });

    await page.reload();
    await page.waitForTimeout(500);

    // Should display district name
    await expect(page.locator('#selected-district-name')).toContainText('Test District');
    await expect(page.locator('#selected-environment')).toContainText('staging');

    console.log('✅ District information displayed on search page');
  });
});

test.describe('Student Search Functionality', () => {
  test('should search for a student and display results', async ({ page, context }) => {
    // Mock the API response
    await context.route('**/api/students/search', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          student: true,
          bookmarked_data: {
            id: 1,
            sourcedId: 'S12345',
            givenName: 'John',
            familyName: 'Doe',
            email: 'john.doe@test.com',
            grade: '9',
            campus: 'Test High School',
            enrollments: [
              {
                className: 'Algebra I',
                classCode: 'MATH-101',
                period: '1',
                subject: 'Mathematics'
              }
            ]
          },
          classlink_data: {
            sourcedId: 'S12345',
            givenName: 'John',
            familyName: 'Doe',
            email: 'john.doe@test.com',
            grade: '9'
          }
        })
      });
    });

    await page.goto('/tools/student-search');

    // Set district in localStorage
    await page.evaluate(() => {
      localStorage.setItem('selectedDistrict', JSON.stringify({
        id: 123,
        name: 'Test District',
        environment: 'staging'
      }));
    });

    // Enter search term
    await page.locator('#search-input').fill('John Doe');

    // Click search button
    await page.locator('#search-button').click();

    // Wait for results
    await page.waitForTimeout(2000);

    // Should show comparison view
    await expect(page.locator('#comparison-container')).toBeVisible();

    // Should show Bookmarked data
    await expect(page.locator('#bookmarked-column')).toContainText('John');
    await expect(page.locator('#bookmarked-column')).toContainText('Doe');

    // Should show ClassLink data
    await expect(page.locator('#classlink-column')).toContainText('John');
    await expect(page.locator('#classlink-column')).toContainText('Doe');

    console.log('✅ Student search returned results and displayed comparison');
  });

  test('should handle student not found', async ({ page, context }) => {
    // Mock API response for no student
    await context.route('**/api/students/search', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          message: 'No student found in Bookmarked database',
          student: false
        })
      });
    });

    await page.goto('/tools/student-search');

    await page.evaluate(() => {
      localStorage.setItem('selectedDistrict', JSON.stringify({
        id: 123,
        name: 'Test District',
        environment: 'staging'
      }));
    });

    await page.locator('#search-input').fill('Nonexistent Student');
    await page.locator('#search-button').click();

    await page.waitForTimeout(2000);

    // Should show error message
    await expect(page.locator('#error-message')).toBeVisible();
    await expect(page.locator('#error-message')).toContainText('No student found');

    console.log('✅ No student found handled correctly');
  });

  test('should handle ClassLink not available for district', async ({ page, context }) => {
    // Mock API response with ClassLink error
    await context.route('**/api/students/search', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          student: true,
          bookmarked_data: {
            id: 1,
            sourcedId: 'S12345',
            givenName: 'John',
            familyName: 'Doe',
            email: 'john.doe@test.com',
            grade: '9'
          },
          classlink_data: null,
          classlink_error: 'District does not have ClassLink integration'
        })
      });
    });

    await page.goto('/tools/student-search');

    await page.evaluate(() => {
      localStorage.setItem('selectedDistrict', JSON.stringify({
        id: 123,
        name: 'Test District',
        environment: 'staging'
      }));
    });

    await page.locator('#search-input').fill('John Doe');
    await page.locator('#search-button').click();

    await page.waitForTimeout(2000);

    // Should show Bookmarked data
    await expect(page.locator('#bookmarked-column')).toBeVisible();

    // Should show ClassLink error
    await expect(page.locator('#classlink-error')).toBeVisible();
    await expect(page.locator('#classlink-error')).toContainText('ClassLink integration');

    console.log('✅ ClassLink unavailable handled correctly');
  });
});

test.describe('Side-by-Side Comparison Display', () => {
  test('should display matching data with green indicators', async ({ page, context }) => {
    await context.route('**/api/students/search', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          student: true,
          bookmarked_data: {
            sourcedId: 'S12345',
            givenName: 'John',
            familyName: 'Doe',
            email: 'john.doe@test.com',
            grade: '9'
          },
          classlink_data: {
            sourcedId: 'S12345',
            givenName: 'John',
            familyName: 'Doe',
            email: 'john.doe@test.com',
            grade: '9'
          }
        })
      });
    });

    await page.goto('/tools/student-search');

    await page.evaluate(() => {
      localStorage.setItem('selectedDistrict', JSON.stringify({
        id: 123,
        name: 'Test District',
        environment: 'staging'
      }));
    });

    await page.locator('#search-input').fill('John Doe');
    await page.locator('#search-button').click();
    await page.waitForTimeout(2000);

    // Check for match indicators (green checkmarks)
    const matchIndicators = page.locator('.match-indicator.match');
    await expect(matchIndicators.first()).toBeVisible();

    console.log('✅ Matching data highlighted with green indicators');
  });

  test('should display mismatched data with red indicators', async ({ page, context }) => {
    await context.route('**/api/students/search', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          student: true,
          bookmarked_data: {
            sourcedId: 'S12345',
            givenName: 'John',
            email: 'john.doe@test.com',
            grade: '9'
          },
          classlink_data: {
            sourcedId: 'S12345',
            givenName: 'Johnny',  // Different name
            email: 'johnny.doe@test.com',  // Different email
            grade: '9'
          }
        })
      });
    });

    await page.goto('/tools/student-search');

    await page.evaluate(() => {
      localStorage.setItem('selectedDistrict', JSON.stringify({
        id: 123,
        name: 'Test District',
        environment: 'staging'
      }));
    });

    await page.locator('#search-input').fill('John');
    await page.locator('#search-button').click();
    await page.waitForTimeout(2000);

    // Check for mismatch indicators (red X)
    const mismatchIndicators = page.locator('.match-indicator.mismatch');
    await expect(mismatchIndicators.first()).toBeVisible();

    console.log('✅ Mismatched data highlighted with red indicators');
  });

  test('should display enrollment data', async ({ page, context }) => {
    await context.route('**/api/students/search', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          student: true,
          bookmarked_data: {
            sourcedId: 'S12345',
            givenName: 'John',
            familyName: 'Doe',
            enrollments: [
              {
                className: 'Algebra I',
                classCode: 'MATH-101',
                period: '1',
                subject: 'Mathematics'
              },
              {
                className: 'English 9',
                classCode: 'ENG-101',
                period: '2',
                subject: 'English'
              }
            ]
          },
          classlink_data: {
            sourcedId: 'S12345',
            givenName: 'John',
            familyName: 'Doe'
          }
        })
      });
    });

    await page.goto('/tools/student-search');

    await page.evaluate(() => {
      localStorage.setItem('selectedDistrict', JSON.stringify({
        id: 123,
        name: 'Test District',
        environment: 'staging'
      }));
    });

    await page.locator('#search-input').fill('John Doe');
    await page.locator('#search-button').click();
    await page.waitForTimeout(2000);

    // Should display enrollment section
    await expect(page.locator('#enrollments-section')).toBeVisible();

    // Should show class names
    await expect(page.locator('#enrollments-section')).toContainText('Algebra I');
    await expect(page.locator('#enrollments-section')).toContainText('English 9');

    console.log('✅ Enrollment data displayed correctly');
  });
});

test.describe('Loading and Error States', () => {
  test('should show loading indicator during search', async ({ page, context }) => {
    // Delay the API response
    await context.route('**/api/students/search', route => {
      setTimeout(() => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            student: true,
            bookmarked_data: { sourcedId: 'S12345' }
          })
        });
      }, 2000);
    });

    await page.goto('/tools/student-search');

    await page.evaluate(() => {
      localStorage.setItem('selectedDistrict', JSON.stringify({
        id: 123,
        name: 'Test District',
        environment: 'staging'
      }));
    });

    await page.locator('#search-input').fill('John Doe');
    await page.locator('#search-button').click();

    // Loading indicator should be visible
    await expect(page.locator('#loading-indicator')).toBeVisible();

    // Wait for response
    await page.waitForTimeout(3000);

    // Loading indicator should be hidden
    await expect(page.locator('#loading-indicator')).not.toBeVisible();

    console.log('✅ Loading indicator works correctly');
  });

  test('should handle API error gracefully', async ({ page, context }) => {
    // Mock API error
    await context.route('**/api/students/search', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          success: false,
          message: 'Internal server error'
        })
      });
    });

    await page.goto('/tools/student-search');

    await page.evaluate(() => {
      localStorage.setItem('selectedDistrict', JSON.stringify({
        id: 123,
        name: 'Test District',
        environment: 'staging'
      }));
    });

    await page.locator('#search-input').fill('John Doe');
    await page.locator('#search-button').click();
    await page.waitForTimeout(2000);

    // Should show error message
    await expect(page.locator('#error-message')).toBeVisible();
    await expect(page.locator('#error-message')).toContainText('error');

    console.log('✅ API error handled gracefully');
  });

  test('should require district selection before search', async ({ page }) => {
    await page.goto('/tools/student-search');

    // Clear localStorage
    await page.evaluate(() => localStorage.clear());
    await page.reload();

    // Try to search without district
    await page.locator('#search-input').fill('John Doe');
    await page.locator('#search-button').click();

    // Should show warning or be disabled
    const button = page.locator('#search-button');
    const isDisabled = await button.isDisabled();

    if (!isDisabled) {
      // Should show error message
      await expect(page.locator('#error-message')).toBeVisible();
      await expect(page.locator('#error-message')).toContainText('Select a district');
    }

    console.log('✅ District selection required before search');
  });
});
