/**
 * CLI Configuration Types
 *
 * TypeScript interfaces for CLI selection and configuration.
 */

export interface CLISettings {
  cli: 'claude' | 'opencode';
  opencode?: OpenCodeConfig;
}

export interface OpenCodeConfig {
  provider?: 'claude' | 'openai' | 'google' | 'zen' | 'local';
  apiKey?: string; // Only for api_key auth type
}

export interface CLIProvider {
  id: string;
  name: string;
  displayName: string;
  authType: 'oauth' | 'api_key' | 'none';
}
