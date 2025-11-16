#!/usr/bin/env node
/**
 * Setup Verification Script
 * Verifies that the user's environment and configuration are correct
 */

import { existsSync, readFileSync } from 'fs';
import dotenv from 'dotenv';
import { BacklogClient } from '../../../src/backlog-client.js';

// Load environment variables
dotenv.config();

interface VerificationResult {
  step: string;
  status: 'success' | 'error' | 'warning';
  message: string;
  details?: string;
}

const results: VerificationResult[] = [];

function addResult(step: string, status: 'success' | 'error' | 'warning', message: string, details?: string) {
  results.push({ step, status, message, details });
}

function printResult(result: VerificationResult) {
  const icon = result.status === 'success' ? '✅' : result.status === 'error' ? '❌' : '⚠️';
  console.log(`${icon} ${result.message}`);
  if (result.details) {
    console.log(`   ${result.details}`);
  }
}

async function verifySetup() {
  console.log('🔍 Verifying Backlog Workflow SKILL setup...\n');

  // Step 1: Check environment variables
  console.log('Step 1: Checking environment variables...');

  const requiredEnvVars = ['BACKLOG_DOMAIN', 'BACKLOG_API_KEY'];
  let envOk = true;

  for (const envVar of requiredEnvVars) {
    if (!process.env[envVar]) {
      addResult('environment', 'error', `Missing ${envVar} in .env file`,
        `Add to .env: ${envVar}=your_value_here`);
      envOk = false;
    }
  }

  if (envOk) {
    addResult('environment', 'success', 'Environment variables loaded');
  }

  printResult(results[results.length - 1]);

  // Step 2: Check user-config.json
  console.log('\nStep 2: Checking user configuration...');

  const configPath = 'workflow/user-config.json';
  if (!existsSync(configPath)) {
    addResult('user-config', 'error', 'user-config.json not found',
      'Run interactive setup with Claude, or copy from references/config-template.json');
    printResult(results[results.length - 1]);
    console.log('\n❌ Setup verification failed. Please fix the errors above.');
    process.exit(1);
  }

  let userConfig;
  try {
    userConfig = JSON.parse(readFileSync(configPath, 'utf-8'));
    addResult('user-config', 'success', 'User configuration found');
  } catch (error) {
    addResult('user-config', 'error', 'Invalid JSON in user-config.json',
      'Check file syntax and ensure it\'s valid JSON');
    printResult(results[results.length - 1]);
    console.log('\n❌ Setup verification failed. Please fix the errors above.');
    process.exit(1);
  }

  printResult(results[results.length - 1]);

  // Step 3: Verify required config fields
  console.log('\nStep 3: Validating configuration fields...');

  const requiredFields = [
    'backlog.projectId',
    'backlog.projectKey',
    'translation.languagePair'
  ];

  let configOk = true;
  for (const field of requiredFields) {
    const parts = field.split('.');
    let value = userConfig;
    for (const part of parts) {
      value = value?.[part];
    }

    if (!value || (typeof value === 'string' && value.startsWith('<'))) {
      addResult('config-fields', 'error', `Missing or invalid: ${field}`,
        'Update workflow/user-config.json with your actual values');
      configOk = false;
    }
  }

  if (configOk) {
    addResult('config-fields', 'success', 'All required fields present');
  }

  printResult(results[results.length - 1]);

  if (!configOk) {
    console.log('\n❌ Setup verification failed. Please fix the errors above.');
    process.exit(1);
  }

  // Step 4: Test Backlog connection
  console.log('\nStep 4: Testing Backlog connection...');

  if (!envOk) {
    addResult('backlog-connection', 'error', 'Skipped - environment variables missing');
    printResult(results[results.length - 1]);
    console.log('\n❌ Setup verification failed. Please fix the errors above.');
    process.exit(1);
  }

  try {
    const client = new BacklogClient({
      domain: process.env.BACKLOG_DOMAIN!,
      apiKey: process.env.BACKLOG_API_KEY!
    });

    // Try to fetch projects
    const response = await client.listProjects();

    if (response.projects && response.projects.length > 0) {
      addResult('backlog-connection', 'success', 'Connected to Backlog');

      // Verify project exists
      const project = response.projects.find(
        (p: any) => p.id === userConfig.backlog.projectId
      );

      if (project) {
        addResult('project-verification', 'success',
          `Found project: ${project.projectKey} (ID: ${project.id})`,
          `Project name: ${project.name}`);
      } else {
        addResult('project-verification', 'warning',
          `Project ID ${userConfig.backlog.projectId} not found in your projects`,
          'Verify the project ID is correct');
      }
    } else {
      addResult('backlog-connection', 'warning', 'Connected but no projects found');
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    addResult('backlog-connection', 'error', 'Cannot connect to Backlog',
      errorMessage);
  }

  printResult(results[results.length - 2]); // connection result
  printResult(results[results.length - 1]); // project verification result

  // Step 5: Verify translation dictionary
  console.log('\nStep 5: Checking translation dictionary...');

  const languagePair = userConfig.translation.languagePair;
  const dictionaryPath = `backlog/backlog-workflow-skill/references/translation-dictionaries/${languagePair}.json`;

  if (existsSync(dictionaryPath)) {
    try {
      const dictionary = JSON.parse(readFileSync(dictionaryPath, 'utf-8'));
      const phrasesCount = Object.keys(dictionary.commonPhrases || {}).length;
      addResult('translation-dictionary', 'success',
        `Translation dictionary loaded: ${languagePair}`,
        `Contains ${phrasesCount} pre-translated phrases`);
    } catch (error) {
      addResult('translation-dictionary', 'warning',
        `Dictionary file exists but has invalid JSON: ${languagePair}`,
        'Check file syntax');
    }
  } else if (languagePair === 'custom') {
    addResult('translation-dictionary', 'warning',
      'Using custom language pair - ensure customDictionary is defined in user-config.json');
  } else {
    addResult('translation-dictionary', 'error',
      `Dictionary not found: ${languagePair}`,
      `Available: vi-ja, en-ja, or create custom`);
  }

  printResult(results[results.length - 1]);

  // Step 6: Check Google Sheets config (optional)
  if (userConfig.googleSheets?.spreadsheetId && !userConfig.googleSheets.spreadsheetId.startsWith('<')) {
    console.log('\nStep 6: Checking Google Sheets configuration...');
    addResult('google-sheets', 'success', 'Google Sheets configuration found',
      `Sheet: ${userConfig.googleSheets.sheetName}, Range: ${userConfig.googleSheets.range}`);
    printResult(results[results.length - 1]);
  }

  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 Verification Summary\n');

  const successCount = results.filter(r => r.status === 'success').length;
  const errorCount = results.filter(r => r.status === 'error').length;
  const warningCount = results.filter(r => r.status === 'warning').length;

  console.log(`✅ Success: ${successCount}`);
  console.log(`❌ Errors: ${errorCount}`);
  console.log(`⚠️  Warnings: ${warningCount}`);

  if (errorCount > 0) {
    console.log('\n❌ Setup verification failed. Please fix the errors above.');
    process.exit(1);
  } else if (warningCount > 0) {
    console.log('\n⚠️  Setup verification completed with warnings. Review warnings above.');
    process.exit(0);
  } else {
    console.log('\n✅ Setup verification complete! Ready to use the SKILL.');
    process.exit(0);
  }
}

// Run verification
verifySetup().catch((error) => {
  console.error('\n❌ Verification failed with error:', error);
  process.exit(1);
});
