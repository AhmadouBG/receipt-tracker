import { expect, test } from 'vitest';

test('Frontend basic sanity test', () => {
  expect(1 + 1).toBe(2);
});

test('Environment check', () => {
  expect(true).toBe(true);
});
