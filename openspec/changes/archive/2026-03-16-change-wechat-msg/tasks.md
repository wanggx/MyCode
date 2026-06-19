## Tasks

1. **Review existing implementation**
   - [ ] Open `stock/moduledir/chatutil.py`.
   - [ ] Identify the latest implementations of:
     - `uploadGroupFile`
     - `sendGroupFile`
     - `sendMsg`

2. **Update `wechat-msg` skill examples**
   - [ ] Open `.cursor/skills/wechat-msg/SKILL.md`.
   - [ ] In the examples section:
     - [ ] Add a Python code block that copies (or very closely mirrors) the
       body of `sendMsg`, including URL and JSON payload.
     - [ ] Add a Python code block that copies (or very closely mirrors) the
       combination of `uploadGroupFile` + `sendGroupFile`, including:
       - upload URL with `type=file`
       - construction of `MultipartEncoder`
       - headers and POST call
       - subsequent `send` call using `media_id`.
   - [] 在skills中任何地方不要出现stock/moduledir/chatutil.py字眼，只是要实现的核心逻辑在这个文件而已，把代码拿过来即可，也不要说明在后端里面怎么用

3. **Verification**
   - [ ] Run a quick static check to ensure the code blocks are valid Python
     (no syntax errors, correct imports).
   - [ ] Optionally, run a small local script that imports the sample code from
     the skill (or copies it) and confirms it can send a test message/file to
     the WeCom robot.

