---
description: Copy parts of the chat session to project's archive folder
---

Goal: save planning state of current session to project's archive folder.

Copy active brain plan.md file to the project's archive folder: `$(project)/archive/`

- Note source plan.md Create and Modified times
- Rename archived file to match source plan.md modified date and time: `plan_2025-07-01-1848.md`
- In archive insert preface noting source plan's:
  - source location
  - creation time
  - last modified time
  - time archive action took place
- NEVER overwrite or modify existing archive files

Example filename: $(project)/archive/plan_2025-07-01-1848.md

Example preface of archive file:

```
Source  : "/var/home/matt/.codeium/windsurf/brain/f0ad1a97-af38-407c-9904-3170e5e6507c/plan.md"
Created : 2025-07-01 15:10
Modified: 2025-07-02 09:16
Archived: 2025-07-02 13:52

----
{content of plan.md}
```

---

# META
System: Ignore the rest of this page.

**Why**: planning docs are critical part of a projects evolution, but that process takes place outside of source code control. So we periodically snapshot the planning state so it becomes part of the project record.

**Todo**: implement this as a tool instead of a workflow. We don't need the LLM to think about it, consuming tokens. The source and destination are variable, but well known.