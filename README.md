# SRE Skills Manager

This repository contains the tools and configurations to manage and synchronize AI skills in your local environment.
It uses a robust Python-based system with `uv` for dependency management and `yaml` for configuration.

## Dependencies

You must have `uv`, `node`, and `npx` installed on your system.
Skills are downloaded globally to the `~/.agents/skills` directory.

## Usage

The project uses `uv` to run the python script `bin/manage_skills.py`, which interacts with the `conf/skills.yaml` file (where repositories are configured) and a local state file to track installed skills.

```bash
uv run bin/manage_skills.py sync               # Installs only new or missing skills
uv run bin/manage_skills.py update             # Forces update/reinstallation of ALL skills
uv run bin/manage_skills.py update <name>      # Forces update of a specific skill by name
uv run bin/manage_skills.py list               # Lists the configured skills in the project
uv run bin/manage_skills.py add <url> <name>   # Adds a new skill to the list
uv run bin/manage_skills.py remove <name>      # Removes a skill from the list
uv run bin/manage_skills.py clean              # Cleans local hidden folders
uv run bin/manage_skills.py inject             # Injects global skills into local project IDE configs
```

### Options and Explanations

- **`sync`**: Checks the `conf/skills.yaml` configuration and only installs the skills that are not already present or marked as installed. Ideal for initial setup or after pulling new changes.
- **`update [name]`**: If no name is provided, it forces an update and reinstallation of all configured skills. If a `<name>` is specified, it updates only that specific skill.
- **`list`**: Displays all currently configured skills.
- **`add <url> <name>`**: Registers a new skill repository URL with the given name into the configuration file.
- **`remove <name>`**: Removes the specified skill from the configuration and uninstalls it.
- **`clean`**: Clears out any local hidden directories or cached states created by the manager.
- **`inject`**: Detects if you are using Cursor or Roo Code (Cline) in your current project directory, and automatically creates the necessary symlinks (`.cursor/rules` or `.roomodes`) pointing to your global downloaded skills so that your IDE can natively use them.

## Antigravity (Gemini)

For the **Antigravity** framework (a Gemini-based tool) to correctly recognize all globally downloaded skills, you need to link the directories.
The script automatically creates a symlink after running the synchronization operations (`sync` or `update`).

The logical link path created by the script avoids absolute paths:
```bash
ln -s ~/.agents/skills ~/.gemini/antigravity/skills
```

This way, all tools acquired through this manager will be documented and ready to use with your Antigravity agent.

## IDE Integration (Cursor, VSCode, Copilot) - Planned Feature

Currently, IDEs like **Cursor** or **VSCode** do not read global rule directories natively. They expect rule files (`.cursor/rules/`, `.github/copilot-instructions.md`, `.clinerules`) to be located directly inside the root of each project.

**Planned UX Improvement:** We are planning to introduce an `inject` (or `link-project`) command. 
Running `uv run bin/manage_skills.py inject` inside any of your project repositories will automatically:
- Detect the target IDE rules.
- Safely generate the necessary `symlinks` from your global `~/.agents/skills` directly into your local project.
- Provide a true "plug-and-play" experience without manually copying files or creating symlinks per project. 

*For more details on this decision, refer to [ADR-0001: IDE Local Skills Integration](docs/architecture/decisions/ADR-0001-ide-local-skills-integration.md).*
