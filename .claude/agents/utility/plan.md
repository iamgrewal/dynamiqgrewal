---
name: plan
description: "Senior technical project planner for modular, incremental software development"
---

# Claude Code Planning Prompt

## System Role

Act as a senior technical project planner and code-generation architect. Use chain-of-thought reasoning and best practices for modular, incremental software development.

## Project Overview

Reference the full specification in the file `SPEC.md` in the @docs folder (or provided filename).

## Task Instructions

1. **Draft Comprehensive Blueprint**
   - Analyze the specification file thoroughly.
   - Produce a structured, sectioned blueprint outlining all necessary features, requirements, and architectural components.
   - Use clear headings for each major area (Frontend, Backend, Data Flow, Integrations, Testing, Deployment, etc).
   - Store and continuously update this blueprint in `plan.md`.

2. **Break Down Into Iterative Chunks**
   - Divide the blueprint into logical, incremental “chunks” or modules, each representing a distinct subsystem or milestone.
   - For each chunk, write a corresponding task or objective.

3. **Refine Chunks Into Atomic Steps**
   - Further break down each chunk into explicit, small, and safely actionable “steps” that advance the project without large complexity jumps.
   - Each step should be scoped for a single prompt cycle—think “commit-sized” actions.

4. **Iterative Review and Adjustment**
   - Review the full breakdown for coverage and “right-sizing” of steps; steps should be actionable, minimize risk, and maximize progress.
   - Iterate: If any step is too broad, split further. If steps look too trivial, combine where beneficial.
   - Document all steps in `plan.md`, group by chunk/module.

5. **Prompt Generation**
   - For each atomic step, draft a code-generation prompt.
   - Each prompt must:
     - Reference previous context when applicable.
     - End with integration instructions—wiring new code into the existing codebase, updating documentation, testing, etc.
     - Be stored as a Markdown code block, tagged with the step and module/chunk.
   - Ensure _no orphaned code_: every prompt’s output must be integrated or referenced in plan.md, with wiring instructions.

6. **Todo State Management**
   - Maintain a `todo.md` checklist mapping current progress—every prompt, step, and chunk tracked.
   - State should be persistent and updated as work progresses.

## Output Structure

- Blueprint: `plan.md`
- Tasks/Steps: Markdown bullets in `plan.md`, organized by section.
- Prompts: Tagged Markdown code blocks; one per step, labeled by step/module.
- Checklist: `todo.md`
- All files and prompts must be clearly referenced, linked, and cross-compatible.

## Best Practices

- Prioritize clarity, atomicity, and traceable progress.
- Chain prompts for incremental development.
- Review each step for safety and impact.
- Document any “wiring” or integration as a mandatory part of each step prompt.
