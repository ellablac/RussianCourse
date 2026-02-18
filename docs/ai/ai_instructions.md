## Engineering priorities

- Finding simple, elegant solutions to complex problems is the top priority.
  - Always consider multiple approaches and select the simplest solution that does not compromise the outcome.
  - If a significantly simpler solution requires a trade-off, discuss it with me before proceeding.
- Design code and suggest improvements based on established software engineering best practices.
- Prioritize clear, maintainable solutions.
- Keep code well organized, modular, and documented.
- Avoid long files when possible. When long files make sense, clearly divide them into labeled sections.
- As complexity increases, continuously refactor procedural code into an object-oriented structure.

## Documentation and comments

- Every file must include a file-level overview describing:
  - the purpose of the file
  - important assumptions or constraints
- Code must be documented using the standard conventions for the language:
  - Python: docstrings
  - JavaScript: JSDoc
- Document the purpose of all classes and functions. 
- For every function and method, include:
    - A description of all parameters with their types.
    - A description of the return value and its type.
    - Any errors or exceptions that may be thrown, and under what conditions they occur.
    - When needed explain side effects, pre- and post-conditions. 
- Use type hints wherever the language supports them.
- Add inline comments whenever logic is not immediately obvious, especially to explain *why* something is done.

## Naming conventions

- Use widely accepted naming conventions appropriate for each language and ecosystem.
- Use meaningful, descriptive names.
- Be consistent within each repository.

## HTML instructions

- Start every HTML file with a file overview comment.
- Use semantic HTML elements where appropriate.
- Clearly mark page sections using comments.
- Keep DOM nesting reasonable and avoid unnecessary complexity.
- Use CSS and JavaScript to avoid HTML duplication whenever possible.


## CSS instructions

- Start every CSS file with a file overview comment describing its purpose and structure.
- Organize CSS into clearly marked sections (variables, base styles, layout, components, utilities).
- Prefer readable selectors and avoid unnecessary specificity.
- Comment intent and non-obvious behavior.
- Reuse CSS styles across multiple pages and keep styling consistent within the same site.

## JavaScript instructions

- Keep JavaScript modular and focused.
- Avoid large, monolithic functions.
- Avoid unnamed functions and implicit parameters.
- Prefer JavaScript constructs that are easily understandable by programmers familiar with other languages.
- Comment edge cases and non-obvious logic.

## JSON instructions

- JSON files must be valid JSON (no comments, no trailing commas).
- Use a consistent key naming style within a repository.
- Structure JSON for clarity and long-term stability.
- When JSON is non-trivial, include documentation describing the schema or fields.
- Validate JSON inputs in code when appropriate.

## Python instructions

- Follow standard Python conventions (PEP 8 style).
- Every module must have a module-level docstring.
- Favor readability over clever one-liners.
- Handle file operations and errors explicitly.

## Dependencies

- Before using or suggesting external libraries:
  - confirm they appear maintained and reputable
  - favor well-adopted libraries
  - avoid unnecessary dependencies when a simple solution is available
  - briefly explain why any dependency is justified

## How I expect you to respond

- Restate my request in clear, polished English at the start of your response.
- Ask clarifying questions when necessary.
  - Do not make assumptions unless they are trivial or reasonably implied.
- Avoid long responses:
  - provide the first part of the response
  - ask whether to continue or adjust
  - apply feedback, then continue when prompted
  - do not rewrite entire files unless explicitly requested; show only the relevant changes and explain them briefly.
  - keep responses conversational and interactive, favoring back-and-forth over long, uninterrupted explanations.
  
- Lightweight override
    - if I include the token "Relax:" as the first word of the message, then temporarily relax strict structure, documentation, and formatting rules
    - this override applies only to the single response unless I explicitly extend it