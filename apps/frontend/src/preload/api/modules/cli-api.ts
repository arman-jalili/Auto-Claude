/**
 * CLI API
 *
 * Provides interface for CLI selection and configuration operations
 * in the Electron renderer process via IPC.
 */

import type { IPCResult } from '@shared/types/ipc';

export interface CLIInfo {
  type: 'claude' | 'opencode';
  path: string | null;
  isValid: boolean;
  version?: string;
  authInfo: CLIAuthInfo;
}

export interface CLIAuthInfo {
  type: 'oauth' | 'multi_provider';
  envVars: string[];
  supportsKeychain: boolean;
  requiresOAuth: boolean;
  providers?: string[];
}

export interface CLIValidationResult {
  isValid: boolean;
  message: string;
}

export interface CLISetOptions {
  cliType: 'claude' | 'opencode';
  opencodeProvider?: 'claude' | 'openai' | 'google' | 'zen' | 'local';
}

export interface CLIProvider {
  id: string;
  name: string;
  displayName: string;
  authType: 'oauth' | 'api_key';
}

/**
 * Create CLI API
 */
export function createCLIAPI(): {
  return {
    getInfo: async (): Promise<IPCResult<CLIInfo>> => {
      return await window.electronAPI.invoke('CLI_GET_INFO');
    },

    setCLI: async (options: CLISetOptions): Promise<IPCResult<CLIInfo>> => {
      return await window.electronAPI.invoke('CLI_SET_CLI', options);
    },

    validateCLI: async (): Promise<IPCResult<CLIValidationResult>> => {
      return await window.electronAPI.invoke('CLI_VALIDATE_CLI');
    },

    getProviders: async (): Promise<IPCResult<CLIProvider[]>> => {
      return await window.electronAPI.invoke('CLI_GET_PROVIDERS');
    },
  };
}
