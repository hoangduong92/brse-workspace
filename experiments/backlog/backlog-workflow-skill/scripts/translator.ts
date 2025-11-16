/**
 * Translation Service (User-Config Compatible)
 * Translates source language to Japanese using dictionaries
 * Supports multiple language pairs: vi-ja, en-ja, custom
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';

interface TranslationCache {
  [key: string]: string;
}

export class Translator {
  private cache: TranslationCache = {};
  private cacheFile = 'workflow/translation-cache.json';
  private languagePair: string;
  private customDictionary: { [key: string]: string };
  private dictionaryPhrases: { [key: string]: string } = {};

  constructor(
    enableCache: boolean = true,
    languagePair: string = 'vi-ja',
    customDictionary: { [key: string]: string } = {}
  ) {
    this.languagePair = languagePair;
    this.customDictionary = customDictionary;

    // Load dictionary for language pair
    this.loadDictionary();

    // Load cache
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
   * Load translation dictionary for the specified language pair
   */
  private loadDictionary() {
    const dictionaryPath = `backlog/backlog-workflow-skill/references/translation-dictionaries/${this.languagePair}.json`;

    if (existsSync(dictionaryPath)) {
      try {
        const dictionary = JSON.parse(readFileSync(dictionaryPath, 'utf-8'));
        this.dictionaryPhrases = dictionary.commonPhrases || {};
        console.log(`📚 Loaded ${Object.keys(this.dictionaryPhrases).length} phrases from ${this.languagePair} dictionary`);
      } catch (error) {
        console.warn(`⚠️  Failed to load dictionary: ${this.languagePair}`);
        console.warn(`   Creating empty dictionary`);
        this.dictionaryPhrases = {};
      }
    } else if (this.languagePair === 'custom') {
      console.log(`📝 Using custom language pair (no pre-built dictionary)`);
      this.dictionaryPhrases = {};
    } else {
      console.warn(`⚠️  Dictionary not found: ${this.languagePair}`);
      console.warn(`   Available: vi-ja, en-ja, or use 'custom'`);
      this.dictionaryPhrases = {};
    }

    // Merge custom dictionary (overrides pre-built)
    if (this.customDictionary && Object.keys(this.customDictionary).length > 0) {
      this.dictionaryPhrases = { ...this.dictionaryPhrases, ...this.customDictionary };
      console.log(`➕ Added ${Object.keys(this.customDictionary).length} custom translations`);
    }
  }

  /**
   * Translate text from source language to Japanese
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
   * Perform actual translation
   * 1. Check dictionary
   * 2. If not found, return with [要翻訳] prefix
   */
  private async performTranslation(text: string): Promise<string> {
    // Check dictionary
    if (this.dictionaryPhrases[text]) {
      return this.dictionaryPhrases[text];
    }

    // Try partial matches (for phrases with slight variations)
    for (const [key, value] of Object.entries(this.dictionaryPhrases)) {
      if (text.toLowerCase().includes(key.toLowerCase()) && key.length > 5) {
        console.log(`   ℹ️  Partial match: "${text}" → using "${key}" → "${value}"`);
        return value;
      }
    }

    // No translation found
    console.warn(`⚠️  No translation found for: "${text}"`);
    console.warn(`   Add to dictionary or user-config.json customDictionary`);
    return `[要翻訳] ${text}`;
  }

  /**
   * Save cache to file
   */
  private saveCache() {
    try {
      writeFileSync(this.cacheFile, JSON.stringify(this.cache, null, 2));
    } catch (error) {
      console.warn('⚠️  Failed to save translation cache');
    }
  }

  /**
   * Get translation statistics
   */
  getStats() {
    return {
      languagePair: this.languagePair,
      dictionarySize: Object.keys(this.dictionaryPhrases).length,
      cacheSize: Object.keys(this.cache).length,
      customTranslations: Object.keys(this.customDictionary).length
    };
  }
}
