# OpenCode Integration Implementation Steps

This directory contains the step-by-step implementation plan for adding OpenCode CLI support to Auto Claude.

## Overview

**OpenCode** is an open-source alternative to Claude Code CLI with multi-provider support (Claude, OpenAI, Google, local models, etc.).

**Goal**: Enable Auto Claude to work with **either** Claude Code CLI **or** OpenCode CLI seamlessly.

## Implementation Steps

| Step | Status | Description |
|-------|---------|-------------|
| 1.md | ✅ Complete | Architecture analysis and design |
| 2.md | ✅ Complete | CLI abstraction layer (`cli_manager.py`) |
| 3.md | ✅ Complete | OpenCode authentication functions |
| 4.md | 🚧 In Progress | Client integration with CLI support |
| 5.md | 🚧 In Progress | CLI selection in `run.py` (`--cli` flag) |
| 6.md | ✅ Complete | Frontend IPC handlers |
| 7.md | ✅ Complete | Frontend CLI selector UI |
| 8.md | ✅ Complete | i18n translations |
| 9.md | 🚧 In Progress | Documentation updates |
| 10.md | ✅ Complete | Testing plan created |

**Legend:**
- ✅ Complete - Fully implemented
- 🚧 In Progress - Partially implemented (specs written, some code done)
- 📝 Planned - Specifications only
- ⏳ Pending - Not yet started

## Quick Start

### For Developers

1. **Review Implementation Status**: Check current step status below
2. **Start with Step 1**: Read `1.md` to understand architecture
3. **Implement Sequentially**: Each step builds on the previous
4. **Review Tests**: Each step includes test specifications
5. **Update SUMMARY**: Track progress in `SUMMARY.md`

### For Testing

After completing Steps 1-5 (backend foundation):

```bash
# Test CLI detection (not yet implemented in run.py)
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
│       └── index.ts             # MODIFIED - Register CLI handlers
├── preload/
│   └── api/
│       └── modules/
│           └── cli-api.ts         # NEW - CLI API
├── renderer/
│   └── features/
│       └── settings/
│           └── cli-selector.tsx   # NEW - CLI UI component
└── shared/
    ├── i18n/locales/
    │   ├── en/common.json            # MODIFIED - CLI translations
    │   ├── en/settings.json          # MODIFIED - CLI translations
    │   ├── en/navigation.json         # MODIFIED - CLI translations
    │   ├── en/tasks.json             # MODIFIED - CLI translations
    │   ├── en/dialogs.json           # MODIFIED - CLI translations
    │   ├── fr/common.json            # MODIFIED - CLI translations
    │   ├── fr/settings.json          # MODIFIED - CLI translations
    │   ├── fr/navigation.json         # MODIFIED - CLI translations
    │   ├── fr/tasks.json             # MODIFIED - CLI translations
    │   └── fr/dialogs.json           # MODIFIED - CLI translations
    └── types/
        └── cli-config.ts             # NEW - CLI configuration types
```

## Testing Strategy

### Phase 1: Backend Foundation (Steps 2-5)
- [x] CLI abstraction layer (`cli_manager.py`) implemented
- [x] OpenCode authentication (`auth.py`) implemented
- [ ] Client integration (`client.py`) - pending implementation
- [ ] CLI selection (`run.py`) - pending implementation
- [ ] Unit tests for CLI manager - test specs written, not yet implemented
- [ ] Unit tests for OpenCode authentication - test specs written, not yet implemented
- [ ] Manual CLI testing - documented

### Phase 2: Frontend Integration (Steps 6-7)
- [x] Frontend IPC handlers (`cli-handlers.ts`) implemented
- [x] CLI selector UI component implemented
- [ ] CLI settings persistence - pending implementation
- [ ] Unit tests for IPC handlers - test specs written, not yet implemented
- [ ] Unit tests for CLI selector - test specs written, not yet implemented
- [ ] E2E tests for settings UI - test specs written, not yet implemented

### Phase 3: End-to-End (Steps 8-10)
- [x] i18n translations implemented across 8 files
- [x] Documentation guide created (`guides/OPENCODE.md`)
- [ ] Testing plan and verification commands documented
- [ ] Main README update with OpenCode info - pending
- [ ] Test files created for CLI manager, OpenCode auth, IPC handlers, CLI selector
- [ ] Integration tests for CLI switching - test specs written, not yet implemented
- [ ] Manual testing procedures documented

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
