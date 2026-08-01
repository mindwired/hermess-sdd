# Hermes SDD installed

The Agent tool, slash commands, skills, CLI command, and Dashboard adapter are bundled in this plugin.

This repository is private during the initial rollout. Install it with the authenticated GitHub CLI or Git
credential helper configured for the `mindwired` account.

1. Restart the gateway so Python routes and commands are reloaded:

   ```bash
   hermes gateway restart
   ```

2. Install the optional native Desktop adapter:

   ```bash
   hermes sdd ui install
   ```

3. Open a project and initialize it:

   ```bash
   hermes sdd init auto "Describe the project goal"
   ```

Run `hermes sdd doctor` to verify the installation.
