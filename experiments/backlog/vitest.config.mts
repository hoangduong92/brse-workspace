import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.ts'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.config.*',
        '**/*.d.ts',
        '**/*.test.ts',
        '**/test-*.ts',
        '**/demo.ts',
        'src/fetch-*.ts',
        'src/filter-*.ts',
        'src/process-*.ts'
      ]
    }
  }
});
