/**
 * Translation Service - Translate Vietnamese/English to Japanese
 * Uses AI for translation and caches results
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';

interface TranslationCache {
  [key: string]: string;
}

export class Translator {
  private cache: TranslationCache = {};
  private cacheFile = 'workflow/translation-cache.json';

  constructor(enableCache: boolean = true) {
    if (enableCache && existsSync(this.cacheFile)) {
      try {
        this.cache = JSON.parse(readFileSync(this.cacheFile, 'utf-8'));
        console.log(`📦 Loaded ${Object.keys(this.cache).length} cached translations`);
      } catch (error) {
        console.warn('⚠️  Failed to load translation cache, starting fresh');
        this.cache = {};
      }
    }
  }

  /**
   * Translate VN/EN text to Japanese
   */
  async translate(text: string): Promise<string> {
    // Check cache first
    if (this.cache[text]) {
      return this.cache[text];
    }

    // Perform translation
    const translated = await this.performTranslation(text);

    // Cache the result
    this.cache[text] = translated;
    this.saveCache();

    return translated;
  }

  /**
   * AI-based translation (placeholder - will use predefined mappings)
   */
  private async performTranslation(text: string): Promise<string> {
    // Common translations dictionary
    const commonTranslations: { [key: string]: string } = {
      // Status & Process
      'UAT': 'UAT',
      'Release': 'リリース',
      'Chốt Release': 'リリース確定',
      'Coding': 'コーディング',
      'Test trên dev': '開発環境でテスト',
      'Thực thi test': 'テスト実行',

      // Documentation
      'Làm user manual': 'ユーザーマニュアル作成',
      'Tạo user manual': 'ユーザーマニュアル作成',
      'Viết test case': 'テストケース作成',
      'Tạo test case': 'テストケース作成',
      'Tạo test casse': 'テストケース作成',
      'Làm file spec': '仕様書作成',
      'Review file spec': '仕様書レビュー',
      'Review file thiết kế': '設計書レビュー',
      'Tìm hiểu spec': '仕様書調査',
      'Tìm hiểu spec hiện tại': '現在の仕様書を調査',

      // Meetings & Demos
      'Demo với KH': 'お客様向けデモ',
      'Làm manual và MTG giải thích cho user': 'マニュアル作成とユーザー説明会議',

      // Monitoring
      'Monitoring RPA': 'RPA監視'
    };

    // Check if exact match exists
    if (commonTranslations[text]) {
      return commonTranslations[text];
    }

    // Pattern-based translation
    if (text.includes('Update') && text.includes('scenario')) {
      return text.replace(/Update (\d+) scenario.*/, '$1つのシナリオを更新');
    }

    // For complex text, you can integrate with Claude API here
    // For now, return a basic translation indicator
    console.warn(`⚠️  No translation found for: "${text}"`);
    return `[要翻訳] ${text}`;
  }

  /**
   * Save cache to file
   */
  private saveCache(): void {
    try {
      writeFileSync(this.cacheFile, JSON.stringify(this.cache, null, 2), 'utf-8');
    } catch (error) {
      console.warn('⚠️  Failed to save translation cache');
    }
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { count: number; items: string[] } {
    return {
      count: Object.keys(this.cache).length,
      items: Object.keys(this.cache)
    };
  }
}
