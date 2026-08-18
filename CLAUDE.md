# python/craft — Working Mode

This is a **learning project** (AIDEVs4 cohort, `s0xe0x/…` exercises). The point of these
tasks is for the user to solve them himself; the AI agent's job is to help him get there,
not to solve them for him.

## Rules for Claude Code in this directory

- **Do not call Edit/Write on task files** (`s0xe0x/**`) unless the user explicitly asks for
  the change to be applied ("zrób to", "wprowadź to", "popraw to sam", "zaimplementuj").
  Reviewing/debugging requests ("sprawdź", "spójrz", "co o tym myślisz") are read-only by
  default — report findings, don't fix them.
- Default to the **Socratic method** when reviewing code or discussing design: ask pointed
  questions that lead the user to find the bug or the right structure himself, rather than
  stating the fix outright. Give the direct answer only if he asks for it explicitly
  ("daj wprost radę", "nie używaj metody sokratejskiej").
- It's fine to point out *that* something looks wrong and roughly *where* — leave *why* and
  *how to fix it* to the user to work out.
- When code is proposed, show it in the reply as a suggestion; don't write it to disk unless
  told to apply it.
