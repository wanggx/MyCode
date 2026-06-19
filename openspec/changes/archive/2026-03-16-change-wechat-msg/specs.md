## Functional Specs

1. **Skill robustness**
   - The `wechat-msg` skill must contain complete, working examples that mirror
     the current implementation in `stock/moduledir/chatutil.py`.
   - The examples must be sufficient to re‑implement the behavior (send text
     and file messages) even if `chatutil.py` is moved, renamed, or refactored.

2. **Examples content**
   - The skill must include:
     - A code block showing how to send a text message to the WeCom robot,
       with the same URL, payload structure, and mentioned mobile list as
       `sendMsg`.
     - A code block showing how to upload and send a file to the WeCom robot,
       with the same upload URL, headers, use of `MultipartEncoder`, and
       subsequent `send` call as `uploadGroupFile` + `sendGroupFile`.
   - These blocks should be clearly annotated as being based on/copying the
     implementation in `chatutil.py`.

3. **No runtime behavior changes**
   - The change must not alter:
     - Any URLs or keys used to talk to the WeCom robot.
     - The phone number list / mention list.
     - The behavior of `chatutil.py` or any backend endpoints.

## Non-Functional Specs

1. **Skill clarity**
   - The examples must be short, copy‑paste‑able, and valid Python.
   - They must use the same imports and structure as the real implementation
     (e.g. `requests`, `MultipartEncoder`).

2. **Maintenance hints**
   - The skill should include a short note telling maintainers: “If you change
     `chatutil.py`, also update these examples to match”.

