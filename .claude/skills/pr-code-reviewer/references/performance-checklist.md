# Performance Review Checklist

Performance anti-patterns and optimization guidelines for code review.

## Database Performance

### Query Optimization

- [ ] No N+1 queries
- [ ] SELECT only needed columns (no `SELECT *`)
- [ ] Proper JOIN usage (not subqueries when JOIN is faster)
- [ ] Pagination for large result sets
- [ ] Indexes on frequently queried columns

### N+1 Query Detection

```python
# BAD: N+1 queries
for order in orders:
    user = db.query(User).get(order.user_id)  # Query per order!
    print(user.name)

# GOOD: Eager loading
orders = db.query(Order).options(joinedload(Order.user)).all()
for order in orders:
    print(order.user.name)  # No additional query
```

```typescript
// BAD: N+1 in ORM
for (const post of posts) {
  const author = await prisma.user.findUnique({ where: { id: post.authorId } });
}

// GOOD: Include relation
const posts = await prisma.post.findMany({
  include: { author: true }
});
```

### Indexing Guidelines

- [ ] Index on foreign keys
- [ ] Index on WHERE clause columns
- [ ] Index on ORDER BY columns
- [ ] Composite indexes for multi-column filters
- [ ] No over-indexing (each index has write cost)

```sql
-- Check missing indexes (PostgreSQL)
SELECT
  schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE n_distinct > 100 AND schemaname = 'public';

-- Find unused indexes
SELECT *
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

### Connection Management

- [ ] Connection pooling configured
- [ ] Connections released properly
- [ ] Transaction scope minimized
- [ ] No connection leaks

## Memory Management

### Memory Leaks

- [ ] Event listeners cleaned up
- [ ] Timers/intervals cleared
- [ ] Large objects released
- [ ] Caches bounded
- [ ] No circular references preventing GC

```javascript
// BAD: Memory leak via event listener
class Component {
  constructor() {
    window.addEventListener('resize', this.handleResize);
  }
  // Missing cleanup!
}

// GOOD: Proper cleanup
class Component {
  constructor() {
    this.handleResize = this.handleResize.bind(this);
    window.addEventListener('resize', this.handleResize);
  }

  destroy() {
    window.removeEventListener('resize', this.handleResize);
  }
}
```

### Object Allocation

- [ ] No unnecessary object creation in hot paths
- [ ] Object pooling for expensive allocations
- [ ] Lazy initialization where appropriate
- [ ] Stream processing for large datasets

```python
# BAD: Create new object in loop
results = []
for item in large_list:
    results.append(ExpensiveObject(item).process())

# GOOD: Reuse or stream
def process_items(items):
    for item in items:
        yield process_item(item)  # Generator, no list allocation
```

## Algorithmic Complexity

### Common Anti-Patterns

| Anti-Pattern | Complexity | Fix |
|--------------|------------|-----|
| Nested loops on same list | O(n²) | Use hash map |
| Repeated list searches | O(n²) | Convert to set |
| Recursive without memoization | O(2^n) | Add memoization |
| String concatenation in loop | O(n²) | Use StringBuilder/join |

```python
# BAD: O(n²)
for i, item1 in enumerate(items):
    for item2 in items[i+1:]:
        if item1.id == item2.related_id:
            # ...

# GOOD: O(n)
item_map = {item.id: item for item in items}
for item in items:
    related = item_map.get(item.related_id)
    if related:
        # ...
```

### Data Structure Selection

| Use Case | Bad Choice | Good Choice |
|----------|------------|-------------|
| Frequent lookups | List | Dict/Set |
| Ordered unique items | List with checks | SortedSet |
| Queue operations | List (pop(0)) | deque |
| Priority access | List sort | heapq |

## Async and Concurrency

### Blocking Operations

- [ ] No blocking I/O in async context
- [ ] CPU-intensive work offloaded
- [ ] Proper async/await usage
- [ ] No sync operations in hot paths

```python
# BAD: Blocking in async
async def get_users():
    time.sleep(1)  # Blocks event loop!
    return users

# GOOD: Non-blocking
async def get_users():
    await asyncio.sleep(1)
    return users
```

### Concurrency Patterns

- [ ] Rate limiting for external calls
- [ ] Batching for bulk operations
- [ ] Circuit breakers for failing services
- [ ] Timeouts on all external calls

```typescript
// GOOD: Batch API calls
async function fetchUsers(ids: string[]): Promise<User[]> {
  const chunks = chunk(ids, 50); // Batch size
  const results = await Promise.all(
    chunks.map(chunk => api.post('/users/batch', { ids: chunk }))
  );
  return results.flat();
}
```

## Caching

### When to Cache

- [ ] Frequently accessed, rarely changed data
- [ ] Expensive computations
- [ ] External API responses
- [ ] Database query results

### Cache Considerations

- [ ] Cache invalidation strategy defined
- [ ] TTL set appropriately
- [ ] Cache key includes relevant parameters
- [ ] Fallback for cache misses
- [ ] No sensitive data in cache

```python
# Cache with proper invalidation
@cache(ttl=300, key=lambda user_id: f"user:{user_id}")
async def get_user(user_id: str):
    return await db.users.find(user_id)

async def update_user(user_id: str, data: dict):
    result = await db.users.update(user_id, data)
    await cache.delete(f"user:{user_id}")  # Invalidate
    return result
```

## Network Performance

### API Calls

- [ ] Minimal payload sizes
- [ ] Compression enabled
- [ ] Connection reuse (keep-alive)
- [ ] Request batching where possible
- [ ] Response streaming for large data

### Payload Optimization

```typescript
// BAD: Over-fetching
const user = await api.get('/users/123');

// GOOD: Field selection
const user = await api.get('/users/123', {
  params: { fields: 'id,name,email' }
});
```

## Frontend Performance

### Bundle Size

- [ ] Tree shaking enabled
- [ ] Code splitting implemented
- [ ] Lazy loading for routes
- [ ] No duplicate dependencies
- [ ] Assets optimized (images, fonts)

### Render Performance

- [ ] No unnecessary re-renders
- [ ] Virtualization for long lists
- [ ] Debouncing for rapid events
- [ ] Memoization for expensive computations
- [ ] Web Workers for CPU-intensive tasks

```typescript
// GOOD: Memoize expensive computation
const sortedItems = useMemo(
  () => items.sort((a, b) => a.name.localeCompare(b.name)),
  [items]
);

// GOOD: Virtualize long lists
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={10000}
  itemSize={35}
>
  {Row}
</FixedSizeList>
```

## Performance Testing Commands

### Profiling

```bash
# Python
python -m cProfile -s cumtime script.py

# Node.js
node --prof app.js
node --prof-process isolate-*.log

# Go
go test -cpuprofile=cpu.out -memprofile=mem.out
go tool pprof cpu.out
```

### Load Testing

```bash
# k6
k6 run --vus 100 --duration 30s script.js

# ab (Apache Bench)
ab -n 1000 -c 100 https://api.example.com/endpoint

# wrk
wrk -t4 -c100 -d30s https://api.example.com/endpoint
```

## Performance Review Checklist

### Database
- [ ] No N+1 queries
- [ ] Proper indexing
- [ ] Connection pooling
- [ ] Query analysis done

### Memory
- [ ] No memory leaks
- [ ] Bounded caches
- [ ] Efficient data structures
- [ ] Large datasets streamed

### Algorithm
- [ ] Optimal complexity
- [ ] No unnecessary iterations
- [ ] Appropriate data structures

### Async
- [ ] No blocking in async
- [ ] Proper concurrency limits
- [ ] Timeouts configured

### Caching
- [ ] Cache strategy defined
- [ ] Invalidation handled
- [ ] TTL appropriate

### Network
- [ ] Minimal payloads
- [ ] Request batching
- [ ] Compression enabled

### Frontend (if applicable)
- [ ] Bundle size acceptable
- [ ] Lazy loading implemented
- [ ] No unnecessary re-renders

## Red Flags for Reviewer

| Pattern | Severity | Action |
|---------|----------|--------|
| N+1 queries | HIGH | Must fix |
| Unbounded loop | HIGH | Must fix |
| Missing pagination | HIGH | Must fix |
| Blocking in async | MEDIUM | Should fix |
| Large object in memory | MEDIUM | Should fix |
| No caching for hot path | MEDIUM | Consider |
| Missing connection pool | MEDIUM | Should fix |
| Excessive re-renders | LOW | Suggest |
