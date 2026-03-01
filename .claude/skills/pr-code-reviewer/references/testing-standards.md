# Testing Standards

Comprehensive testing requirements and best practices for pull request review.

## Test Coverage Requirements

### Minimum Coverage by Change Type

| Change Type | Minimum Coverage | Notes |
|-------------|-----------------|-------|
| New feature | 80% | 100% for critical paths |
| Bug fix | Regression test required | Must cover the fixed case |
| Refactor | Maintain existing | Should not decrease |
| Documentation | N/A | No tests required |
| Configuration | 50% | Validate config loading |

### Coverage Measurement Commands

```bash
# Python (pytest-cov)
pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# JavaScript/TypeScript (Jest/Vitest)
npm test -- --coverage --coverageReporters=text --coverageThreshold='{"global":{"branches":80,"functions":80,"lines":80}}'

# Go
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out

# Rust
cargo tarpaulin --out Stdout --skip-clean -- --test-threads=1
```

## Test Types

### Unit Tests

**Purpose:** Test individual functions/methods in isolation.

**Requirements:**
- [ ] Fast execution (< 100ms per test)
- [ ] No external dependencies (use mocks)
- [ ] Single responsibility (one assertion concept)
- [ ] Descriptive names (should_When_Given)

**Naming Conventions:**
```python
# Python
def test_should_return_error_when_input_is_negative():
def test_calculate_total_applies_discount_correctly():

# JavaScript/TypeScript
describe('UserService', () => {
  it('should return error when email is invalid', () => {})
  it('should hash password before saving', () => {})
})

# Go
func TestCalculateTotal_AppliesDiscount(t *testing.T) {}
func TestValidateEmail_ReturnsErrorForInvalidInput(t *testing.T) {}
```

### Integration Tests

**Purpose:** Test component interactions.

**Requirements:**
- [ ] Uses real or containerized dependencies
- [ ] Tests API contracts
- [ ] Tests database interactions
- [ ] Tests external service integrations (mocked or test instances)

**Best Practices:**
```typescript
// Use test containers or mock servers
describe('UserAPI', () => {
  let app: FastifyInstance;
  let db: TestDatabase;

  beforeAll(async () => {
    db = await TestDatabase.create();
    app = await createApp({ database: db });
  });

  afterAll(async () => {
    await db.close();
    await app.close();
  });

  it('should create user and persist to database', async () => {
    const response = await app.inject({
      method: 'POST',
      url: '/api/users',
      payload: { email: 'test@example.com' }
    });

    expect(response.statusCode).toBe(201);
    const dbUser = await db.users.findById(response.json().id);
    expect(dbUser).toBeDefined();
  });
});
```

### End-to-End Tests

**Purpose:** Test complete user flows.

**Requirements:**
- [ ] Tests critical user journeys
- [ ] Uses realistic test data
- [ ] Independent of other tests
- [ ] Cleanup after execution

**Tools:**
- Playwright (recommended)
- Cypress
- Selenium

```typescript
// Playwright example
test('user can complete checkout', async ({ page }) => {
  await page.goto('/products');
  await page.click('[data-testid="add-to-cart"]');
  await page.click('[data-testid="checkout"]');
  await page.fill('[name="email"]', 'test@example.com');
  await page.click('[data-testid="place-order"]');
  await expect(page.locator('.order-confirmation')).toBeVisible();
});
```

## Test Quality Indicators

### Good Tests Have:
- [ ] Clear arrangement (Given)
- [ ] Single action (When)
- [ ] Clear assertions (Then)
- [ ] Descriptive failure messages
- [ ] No test interdependencies
- [ ] No hardcoded waits (use explicit waits)
- [ ] Proper cleanup

### AAA Pattern
```python
def test_should_calculate_order_total_with_tax():
    # Arrange
    order = Order(items=[
        Item(price=100, quantity=2),
        Item(price=50, quantity=1)
    ])
    tax_rate = 0.1

    # Act
    total = order.calculate_total(tax_rate)

    # Assert
    assert total == 275  # (200 + 50) * 1.1
```

### Bad Test Smells

| Smell | Problem | Fix |
|-------|---------|-----|
| Multiple assertions | Testing too much | Split into multiple tests |
| Hardcoded waits | Flaky, slow | Use explicit waits/events |
| Shared mutable state | Order-dependent | Use fresh fixtures |
| No assertions | What's being tested? | Add meaningful assertions |
| Excessive mocking | Tests implementation | Test behavior, not code |
| Mystery guest | External dependency | Use fixtures or mocks |

## Mocking Guidelines

### When to Mock
- External API calls
- Database operations (in unit tests)
- File system operations
- Time-dependent code
- Random values

### When NOT to Mock
- Simple value objects
- Standard library functions
- Code you own (test it directly)

### Mock Best Practices
```typescript
// Good: Mock at the boundary
jest.mock('../api/external-service');
// Don't mock internal implementation details

// Good: Verify behavior, not implementation
expect(mockApi.createUser).toHaveBeenCalledWith({
  email: 'test@example.com'
});
// Don't check internal state of the mock

// Good: Reset mocks between tests
beforeEach(() => {
  jest.clearAllMocks();
});
```

## Test Data Management

### Fixtures
```python
# conftest.py
@pytest.fixture
def sample_user():
    return User(
        id=uuid4(),
        email='test@example.com',
        created_at=datetime.utcnow()
    )

@pytest.fixture
def authenticated_client(client, sample_user):
    token = create_jwt_token(sample_user)
    client.headers['Authorization'] = f'Bearer {token}'
    return client
```

### Factory Pattern
```typescript
// test-factories.ts
export const createUser = (overrides: Partial<User> = {}): User => ({
  id: uuid(),
  email: `test-${Date.now()}@example.com`,
  role: 'user',
  ...overrides
});

// Usage
const admin = createUser({ role: 'admin' });
```

## Edge Cases to Test

### Input Validation
- [ ] Null/undefined values
- [ ] Empty strings/collections
- [ ] Boundary values (min, max)
- [ ] Invalid types
- [ ] Malformed data

### Error Conditions
- [ ] Network failures
- [ ] Timeout scenarios
- [ ] Rate limiting
- [ ] Invalid responses
- [ ] Concurrent access

### State Transitions
- [ ] Initial state
- [ ] Terminal state
- [ ] Invalid transitions
- [ ] Idempotency

## Regression Test Requirements

For bug fixes, include:
1. **Failing test before fix:** Demonstrates the bug
2. **Passing test after fix:** Confirms the fix
3. **Root cause comment:** Explains why the bug occurred

```python
def test_should_handle_concurrent_updates_without_race_condition():
    """
    Regression test for #1234: Concurrent updates caused data loss.

    Root cause: Missing transaction isolation in update handler.
    Fix: Added optimistic locking with version field.
    """
    # Test that would have failed before the fix
```

## Performance Testing

### When Required
- New endpoints expected to handle > 100 RPS
- Changes to hot paths
- Database query changes
- Caching implementations

### Tools
- k6 for load testing
- Locust for Python
- Artillery for Node.js

```javascript
// k6 script example
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '1m', target: 20 },
    { duration: '30s', target: 0 }
  ],
  thresholds: {
    http_req_duration: ['p(95)<500']
  }
};

export default function() {
  const res = http.get('https://api.example.com/users');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 500
  });
}
```

## Test Review Checklist

- [ ] Tests exist for new functionality
- [ ] Test names describe expected behavior
- [ ] Tests are independent and can run in any order
- [ ] No hardcoded credentials or secrets in tests
- [ ] Mocks are appropriate and not excessive
- [ ] Assertions are specific and meaningful
- [ ] Edge cases are covered
- [ ] Error paths are tested
- [ ] Tests run fast (< 5s for unit tests)
- [ ] Cleanup is proper (no test pollution)
- [ ] Regression tests for bug fixes included
