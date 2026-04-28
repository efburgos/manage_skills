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
```

### Options and Explanations

- **`sync`**: Checks the `conf/skills.yaml` configuration and only installs the skills that are not already present or marked as installed. Ideal for initial setup or after pulling new changes.
- **`update [name]`**: If no name is provided, it forces an update and reinstallation of all configured skills. If a `<name>` is specified, it updates only that specific skill.
- **`list`**: Displays all currently configured skills.
- **`add <url> <name>`**: Registers a new skill repository URL with the given name into the configuration file.
- **`remove <name>`**: Removes the specified skill from the configuration and uninstalls it.
- **`clean`**: Clears out any local hidden directories or cached states created by the manager.

## Antigravity (Gemini)

For the **Antigravity** framework (a Gemini-based tool) to correctly recognize all globally downloaded skills, you need to link the directories.
The script automatically creates a symlink after running the synchronization operations (`sync` or `update`).

The logical link path created by the script avoids absolute paths:
```bash
ln -s ~/.agents/skills ~/.gemini/antigravity/skills
```

This way, all tools acquired through this manager will be documented and ready to use with your Antigravity agent.
