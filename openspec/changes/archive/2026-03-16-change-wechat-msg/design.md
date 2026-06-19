## Overview

This change standardizes and hardens the `wechat-msg` Cursor skill by embedding
the actual HTTP implementation for sending WeCom text and file messages
directly into the skill examples.

The runtime implementation in `stock/moduledir/chatutil.py` remains the single
source of truth for production behavior; the skill mirrors that code so that
agents and developers can see the exact request structure without depending on
the file path.

## Components

1. **Skill file**: `.cursor/skills/wechat-msg/SKILL.md`
   - Already exists and describes when/why to send messages to WeCom.
   - Needs its examples section updated to include full code copies.

2. **Backend helper**: `stock/moduledir/chatutil.py`
   - Contains `uploadGroupFile`, `sendGroupFile`, and `sendMsg`.
   - Acts as the canonical implementation that examples should mirror.

## Design Details

- The skill will include two explicit example blocks:
  - **Send text**: identical to `sendMsg` implementation, including URL,
    payload shape, and mentioned mobile list.
  - **Send file**: identical to `uploadGroupFile` + `sendGroupFile`
    workflow, including multipart upload and subsequent `media_id` send.
- Examples will be clearly marked as “copied from `chatutil.py`” so future
  maintainers know to keep them in sync when changing the backend code.
- The skill will still recommend reusing `chatutil.sendMsg` /
  `chatutil.sendGroupFile` in code, but the embedded examples mean the skill
  remains valid even if the file moves.

## Alternatives Considered

- **Only reference the module path**: rejected because path changes are common
  and would silently break the skill.
- **Generate pseudo-code instead of real code**: rejected because we want the
  exact HTTP request structure, headers, and URL formats.

