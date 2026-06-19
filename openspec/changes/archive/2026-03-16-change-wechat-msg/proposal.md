## Summary

- Introduce a dedicated `wechat-msg` Cursor skill that contains **self-contained** examples for sending text and files to the WeCom team, without relying on fixed file paths in the repository.
- Ensure the skill embeds the current implementation from `stock/moduledir/chatutil.py` directly in its examples, so that future file moves or refactors do not break the skill’s guidance.

## Motivation

- The project already has working WeCom integration in `stock/moduledir/chatutil.py` (`sendMsg`, `sendGroupFile`, `uploadGroupFile`).
- The existing `wechat-msg` skill references these functions but depends on the current file path and function names.
- If the file is moved or renamed, the skill will become misleading unless it is updated in lockstep.
- By **copying the actual code** into the skill’s examples, the agent always has a canonical reference implementation, even if the source file path changes.

## Goals

- Make `wechat-msg` skill robust to file path changes by embedding the concrete HTTP implementation for:
  - Sending text messages to the WeCom robot.
  - Uploading files and sending them as file messages.
- Keep the runtime behavior unchanged (no backend code changes), this change is documentation/skill-level only.

## Non-Goals

- No changes to the actual WeCom integration endpoints, keys, or phone numbers.
- No behavioral changes to `chatutil.py` or other backend modules.

