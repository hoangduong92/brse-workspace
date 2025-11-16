/**
 * Load environment variables từ .env file
 */
import { readFileSync } from 'fs';
import { resolve } from 'path';

export function loadEnv() {
  try {
    const envPath = resolve(process.cwd(), '.env');
    const envContent = readFileSync(envPath, 'utf-8');

    envContent.split('\n').forEach(line => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) return;

      const [key, ...values] = trimmed.split('=');
      const value = values.join('=').trim();

      if (key && value) {
        process.env[key.trim()] = value;
      }
    });
  } catch (error) {
    // .env file không tồn tại - không sao, có thể dùng system env
  }
}
