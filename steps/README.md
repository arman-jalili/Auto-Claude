# OpenCode Integration Implementation Steps

This directory contains the step-by-step implementation plan for adding OpenCode CLI support to Auto Claude.

## Overview

**OpenCode** is an open-source alternative to Claude Code CLI with multi-provider support (Claude, OpenAI, Google, local models, etc.).

**Goal**: Enable Auto Claude to work with **either** Claude Code CLI **or** OpenCode CLI seamlessly.

## Implementation Steps

| Step | Status | Description |
|-------|----------|-------------|
| 1.md | ✅ Complete | Architecture analysis and design |
| 2.md | ✅ Complete | CLI abstraction layer (`cli_manager.py`) |
| 3.md | ✅ Complete | OpenCode authentication functions |
| 4.md | 📝 Planned | Client integration with CLI support |
| 5.md | 📝 Planned | CLI selection in `run.py` (`--cli` flag) |
| 6.md | ⏳ Pending | Frontend IPC handlers |
| 7.md | ⏳ Pending | Frontend CLI selector UI |
| 8.md | ⏳ Pending | i18n translations |
| 9.md | ⏳ Pending | Documentation updates |
| 10.md | ⏳ Pending | Testing and validation |

**Legend:**
- ✅ Complete
- 📝 Planned (specifications written, implementation pending)
- ⏳ Pending (not yet started)

## Quick Start

### For Developers

1. **Start with Step 1**: Read `1.md` to understand the architecture
2. **Implement Sequentially**: Each step builds on the previous
3. **Review Tests**: Each step includes test specifications
4. **Update SUMMARY**: Track progress in `SUMMARY.md`

### For Testing

After completing Steps 1-5 (backend foundation):

```bash
# Test CLI detection
cd apps/backend
python3 -c "from core import get_cli_manager; from pathlib import Path; print(get_cli_manager(Path('.')).get_cli_type().value)"

# Test with Claude CLI (default)
python run.py --info

# Test with OpenCode CLI
python run.py --info --cli opencode

# Test environment variable
CLI_PROVIDER=opencode python run.py --info
```

## Key Design Principles

### 1. Non-Breaking
- Default CLI remains "claude" (existing behavior)
- All existing commands work unchanged
- New functionality is opt-in via flags/settings

### 2. Modular
- CLI Manager abstracts differences between CLIs
- Authentication functions separated by CLI type
- Client creation accepts CLI type parameter

### 3. Extensible
- Easy to add future CLIs (other alternatives)
- Provider enum for OpenCode's multi-provider support
- Settings-based configuration for long-term flexibility

### 4. Secure
- No tokens stored in git
- Respect OS keychain for credential storage
- Clear error messages guide users to secure setup

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│         User / Configuration                │
└───────────────────┬─────────────────────┘
                    │
        ┌───────────┴─────────────┐
        │                         │
        ▼                         ▼
┌─────────────┐       ┌───────────────┐
│ Claude Code │       │  OpenCode     │
│    CLI     │       │     CLI       │
└──────┬──────┘       └──────┬────────┘
       │                     │
       │   CLI Manager     │   CLI Manager
       │                     │
       └─────────┬──────────┘
                 │
                 │
        ┌────────┴─────────┐
        │                │
        ▼                ▼
┌─────────────┐  ┌───────────────┐
│    Auth     │  │   Auth       │
│  Functions  │  │  Functions   │
└──────┬───────┘  └──────┬────────┘
       │                     │
       └─────────┬───────────┘
                 │
                 │
        ┌────────┴─────────┐
        │                │
        ▼                ▼
┌─────────────────────────────┐
│      Auto Claude         │
│       Application        │
└─────────────────────────────┘
```

## File Structure Reference

### Backend
```
apps/backend/
├── core/
│   ├── cli_manager.py         # NEW - CLI abstraction
│   ├── auth.py                # MODIFIED - OpenCode auth
│   └── client.py              # TO MODIFY - CLI integration
└── cli/
    └── run.py                 # TO MODIFY - --cli flag
```

### Frontend
```
apps/frontend/src/
├── main/
│   └── ipc-handlers/
│       ├── cli-handlers.ts      # NEW - CLI IPC handlers
│       └── index.ts             # TO MODIFY - Register handlers
├── renderer/
│   └── features/
│       └── settings/
│           └── cli-selector.tsx   # NEW - CLI UI component
└── shared/
    ├── i18n/locales/
    │   ├── en/settings.json      # TO MODIFY - CLI translations
    │   └── fr/settings.json
    └── types/
        └── cli-config.ts         # NEW - CLI configuration types
```

## Testing Strategy

### Phase 1: Backend Foundation (Steps 2-5)
- [ ] Unit tests for CLI manager
- [ ] Unit tests for OpenCode authentication
- [ ] Integration tests for client creation
- [ ] Manual CLI testing

### Phase 2: Frontend Integration (Steps 6-7)
- [ ] Unit tests for IPC handlers
- [ ] Component tests for CLI selector
- [ ] E2E tests for settings UI

### Phase 3: End-to-End (Steps 8-10)
- [ ] Full workflow tests with Claude CLI
- [ ] Full workflow tests with OpenCode CLI
- [ ] CLI switching tests
- [ ] Error handling tests

## Rollback Plan

If issues arise during implementation:

1. **Backend Only**: Keep frontend changes separate
2. **Feature Flag**: Add `OPENCODE_ENABLED=false` to disable
3. **Graceful Degradation**: Fall back to Claude Code on errors
4. **Documentation**: Mark features as "Beta" if experimental

## Additional Resources

- **OpenCode Docs**: https://opencode.ai/docs
- **OpenCode GitHub**: https://github.com/anomalyco/opencode
- **Auto Claude CLAUDE.md**: Project-specific guidance

## Support

For questions or issues:
- Review individual step documents for detailed specifications
- Check `SUMMARY.md` for overall progress
- Refer to Auto Claude's main documentation

---

**Note**: This is a significant feature addition. Take time to understand each step before proceeding.
