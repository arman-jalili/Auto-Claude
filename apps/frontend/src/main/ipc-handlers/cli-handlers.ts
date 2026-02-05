/**
 * CLI IPC Handlers
 *
 * Handles IPC requests for CLI selection, configuration, and validation.
 * Supports both Claude Code CLI and OpenCode CLI.
 */

import { ipcMain } from 'electron';
import type { BrowserWindow } from 'electron';

// Types for CLI operations
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

// OpenCode providers (from OpenCode CLI)
const OPENCODE_PROVIDERS: CLIProvider[] = [
  {
    id: 'claude',
    name: 'claude',
    displayName: 'Claude',
    authType: 'oauth',
  },
  {
    id: 'openai',
    name: 'openai',
    displayName: 'ChatGPT (OpenAI)',
    authType: 'oauth',
  },
  {
    id: 'google',
    name: 'google',
    displayName: 'Google (Gemini)',
    authType: 'oauth',
  },
  {
    id: 'zen',
    name: 'zen',
    displayName: 'OpenCode Zen',
    authType: 'api_key',
  },
  {
    id: 'local',
    name: 'local',
    displayName: 'Local Models',
    authType: 'none',
  },
];

// Store for CLI configuration
let activeCLIType: 'claude' | 'opencode' = 'claude';
let activeOpenCodeProvider: string = 'claude';

/**
 * Get current CLI information
 */
async function getCLIInfo(): Promise<CLIInfo> {
  try {
    const { PythonEnvManager } = await import(
      '../python-env-manager'
    );

    const pythonEnvManager = PythonEnvManager.getInstance();
    const projectPath = pythonEnvManager.getProjectPath();

    if (!projectPath) {
      return {
        type: 'claude',
        path: null,
        isValid: false,
        authInfo: {
          type: 'oauth',
          envVars: ['CLAUDE_CODE_OAUTH_TOKEN'],
          supportsKeychain: true,
          requiresOAuth: true,
        },
      };
    }

    // Check CLI type from settings
    const { projectStore } = await import('../project-store');
    const settings = await projectStore.getSettings(projectPath);

    const cliType = settings.cli || 'claude';
    activeCLIType = cliType;

    // Get CLI path using Python
    const result = await pythonEnvManager.runPythonScript(`
import sys
import os
import shutil
from pathlib import Path

project_dir = Path('${projectPath}')
settings_path = project_dir / '.auto-claude' / 'settings.json'

# Get CLI type
cli_type = 'claude'
if settings_path.exists():
    import json
    try:
        with open(settings_path) as f:
            settings = json.load(f)
        cli_type = settings.get('cli', 'claude')
    except:
        pass

# Get CLI path
cli_path = None
if cli_type == 'claude':
    cli_path = shutil.which('claude')
elif cli_type == 'opencode':
    cli_path = shutil.which('opencode')

# Validate CLI
is_valid = cli_path is not None
version = None
if is_valid:
    import subprocess
    result = subprocess.run([cli_path, '--version'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        version = result.stdout.strip() or result.stderr.strip()

import json
print(json.dumps({
    'cli_type': cli_type,
    'cli_path': cli_path,
    'is_valid': is_valid,
    'version': version,
    'opencode_provider': ${activeOpenCodeProvider if cli_type == 'opencode' else 'null'}
}, separators=(',', ':'))
`);

    const data = JSON.parse(result.stdout);

    return {
      type: data.cli_type as 'claude' | 'opencode',
      path: data.cli_path,
      isValid: data.is_valid,
      version: data.version,
      authInfo: getAuthInfoForCLI(data.cli_type, data.opencode_provider),
    };
  } catch (error) {
    console.error('Error getting CLI info:', error);
    return {
      type: 'claude',
      path: null,
      isValid: false,
      authInfo: {
        type: 'oauth',
        envVars: ['CLAUDE_CODE_OAUTH_TOKEN'],
        supportsKeychain: true,
        requiresOAuth: true,
      },
    };
  }
}

/**
 * Get authentication info for a CLI type
 */
function getAuthInfoForCLI(
  cliType: string,
  opencodeProvider: string | null,
): CLIAuthInfo {
  if (cliType === 'opencode') {
    return {
      type: 'multi_provider',
      envVars: ['OPENCODE_API_KEY', 'OPENCODE_PROVIDER'],
      supportsKeychain: true,
      requiresOAuth: false,
      providers: OPENCODE_PROVIDERS.map((p) => p.name),
    };
  }

  return {
    type: 'oauth',
    envVars: ['CLAUDE_CODE_OAUTH_TOKEN', 'ANTHROPIC_AUTH_TOKEN'],
    supportsKeychain: true,
    requiresOAuth: true,
  };
}

/**
 * Set active CLI type
 */
async function setCLIOptions(options: CLISetOptions): Promise<CLIInfo> {
  try {
    const { PythonEnvManager } = await import('../python-env-manager');
    const { projectStore } = await import('../project-store');

    const pythonEnvManager = PythonEnvManager.getInstance();
    const projectPath = pythonEnvManager.getProjectPath();

    if (!projectPath) {
      throw new Error('No active project');
    }

    // Get current settings
    const settings = await projectStore.getSettings(projectPath);

    // Update CLI type
    settings.cli = options.cliType;

    // Update OpenCode provider if OpenCode CLI
    if (options.cliType === 'opencode' && options.opencodeProvider) {
      if (!settings.opencode) {
        settings.opencode = {};
      }
      settings.opencode.provider = options.opencodeProvider;
      activeOpenCodeProvider = options.opencodeProvider;
    }

    // Save updated settings
    await projectStore.saveSettings(projectPath, settings);

    // Set environment variable for Python scripts
    process.env.CLI_PROVIDER = options.cliType;

    if (options.opencodeProvider) {
      process.env.OPENCODE_PROVIDER = options.opencodeProvider;
    }

    // Return updated CLI info
    return await getCLIInfo();
  } catch (error) {
    console.error('Error setting CLI options:', error);
    throw error;
  }
}

/**
 * Validate CLI availability
 */
async function validateCLI(): Promise<CLIValidationResult> {
  try {
    const cliInfo = await getCLIInfo();

    return {
      isValid: cliInfo.isValid,
      message: cliInfo.isValid
        ? `${cliInfo.type} CLI is working (version: ${cliInfo.version || 'unknown'})`
        : `${cliInfo.type} CLI validation failed: ${cliInfo.path ? 'not found' : 'not working'}`,
    };
  } catch (error) {
    return {
      isValid: false,
      message: `Error validating CLI: ${error}`,
    };
  }
}

/**
 * Get available OpenCode providers
 */
function getOpenCodeProviders(): CLIProvider[] {
  return OPENCODE_PROVIDERS;
}

/**
 * Register CLI IPC handlers
 */
export function registerCLIHandlers(getMainWindow: () => BrowserWindow | null): void {
  console.log('Registering CLI handlers');

  // CLI_GET_INFO - Get current CLI information
  ipcMain.handle('CLI_GET_INFO', async () => {
    try {
      const info = await getCLIInfo();
      return { success: true, data: info };
    } catch (error) {
      console.error('Error getting CLI info:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // CLI_SET_CLI - Set active CLI type and options
  ipcMain.handle('CLI_SET_CLI', async (_event, options: CLISetOptions) => {
    try {
      const info = await setCLIOptions(options);
      return { success: true, data: info };
    } catch (error) {
      console.error('Error setting CLI:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // CLI_VALIDATE_CLI - Validate CLI availability
  ipcMain.handle('CLI_VALIDATE_CLI', async () => {
    try {
      const result = await validateCLI();
      return { success: true, data: result };
    } catch (error) {
      console.error('Error validating CLI:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  // CLI_GET_PROVIDERS - Get available OpenCode providers
  ipcMain.handle('CLI_GET_PROVIDERS', () => {
    try {
      const providers = getOpenCodeProviders();
      return { success: true, data: providers };
    } catch (error) {
      console.error('Error getting providers:', error);
      return { success: false, error: (error as Error).message };
    }
  });

  console.log('CLI handlers registered');
}
