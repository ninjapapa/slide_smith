# slide_smith

slide_smith is a demo agent-first application for Python-based PowerPoint creation.

It uses the `python-pptx` (`pptx`) library as the core PowerPoint generation engine, but the goal here is not just deck generation — it is to wrap that capability in an agent-first app that agents can operate reliably.

An agent-first application is designed to be usable not just by humans, but directly by calling agents: it exposes clear operable interfaces, good documentation, informative errors, and feedback loops that let agents reliably create, inspect, and refine outputs over multiple steps.

## Early project status

The repo now includes early design docs under `docs/design/`, issue drafts under `docs/issues/`, and an initial Python CLI scaffold in `src/slide_smith/`.
