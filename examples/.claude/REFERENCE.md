# Example Project - Reference Documentation

## Architecture Overview

This example project demonstrates a typical structure for using the Enhanced RLM MCP server.

### Directory Structure

```
project/
├── CLAUDE.md           # Essential rules (always loaded)
├── .claude/
│   ├── REFERENCE.md    # This file - detailed documentation
│   └── code_examples/  # Reusable code patterns
├── src/                # Source code
└── tests/              # Test files
```

---

## Common Patterns

### Adding a New Feature

1. **Create the feature file:**
   ```javascript
   // src/features/myFeature.js
   export function myFeature(input) {
     return input.toUpperCase();
   }
   ```

2. **Add tests:**
   ```javascript
   // tests/myFeature.test.js
   import { myFeature } from '../src/features/myFeature';

   test('converts to uppercase', () => {
     expect(myFeature('hello')).toBe('HELLO');
   });
   ```

3. **Update exports:**
   ```javascript
   // src/index.js
   export { myFeature } from './features/myFeature';
   ```

### Configuration Options

Options are stored in `config.json`:

```json
{
  "debug": false,
  "maxRetries": 3,
  "timeout": 5000
}
```

To add a new option:
1. Add the key to `config.json`
2. Update the TypeScript types in `src/types.ts`
3. Document the option in this file

---

## Gotchas and Warnings

### Critical: Environment Variables

**NEVER** commit `.env` files. Always use `.env.example` as a template.

### Important: Async Handling

Always use `try/catch` with async functions:

```javascript
// WRONG
async function fetchData() {
  const data = await api.get('/data');
  return data;
}

// CORRECT
async function fetchData() {
  try {
    const data = await api.get('/data');
    return data;
  } catch (error) {
    console.error('Failed to fetch:', error);
    throw error;
  }
}
```

---

## API Reference

### `processData(input: string): string`

Processes input data and returns the result.

**Parameters:**
- `input` - The input string to process

**Returns:**
- Processed string

**Example:**
```javascript
const result = processData('hello');
console.log(result); // "HELLO"
```

---

*This is an example REFERENCE.md for testing the Enhanced RLM MCP server.*
