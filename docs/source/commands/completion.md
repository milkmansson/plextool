# plextool completion

Prints a script that completes plextool's commands, subcommands, options and fixed choices when Tab is pressed.
The script is built from the commands as they are now, so it does not fall behind when a command is added. It needs no
extra package, which also makes it work for a plextool installed with [pipx](https://pipx.pypa.io/stable/).

Handy when:
- The names of commands and options are hard to remember, and `--help` takes longer than a Tab.
- A command with many options, such as `users invite` or `stale`, is being typed.
- A choice that Plex or plextool fixes (such as `--type jwt` or `--downloads yes`) needs completing.

```console
$ eval "$(plextool completion bash)"
$ eval "$(plextool completion zsh)"
```

## Setting it up

`plextool completion bash` only prints the script. Nothing is saved until the output is put somewhere the shell reads
when it starts. To try it in the current shell first, without saving anything:

```console
$ eval "$(plextool completion bash)"
```

Typing `plextool to` and pressing Tab then gives `token`. Closing the shell forgets it.

### Keeping it for bash

There are three ways, from cheapest to simplest.

1. A completions folder. This costs nothing at start-up, but it only works if the `bash-completion` package is
   installed, since that package is what reads the folder. If Tab does nothing after this, install the package or use
   one of the other two.

   ```console
   $ mkdir -p ~/.local/share/bash-completion/completions
   $ plextool completion bash > ~/.local/share/bash-completion/completions/plextool
   ```

2. A saved file that `~/.bashrc` loads:

   ```console
   $ mkdir -p ~/.config/plextool
   $ plextool completion bash > ~/.config/plextool/completion.bash
   $ echo 'source ~/.config/plextool/completion.bash' >> ~/.bashrc
   ```

3. An `eval` line in `~/.bashrc`:

   ```console
   $ echo 'eval "$(plextool completion bash)"' >> ~/.bashrc
   ```

   This runs plextool at the start of every shell, which took about 0.2 seconds when measured on a development
   machine.

Open a new shell afterwards. Bash reads `~/.bashrc` for interactive shells that are not login shells. A login shell
(an SSH session, or `su -`) reads `~/.bash_profile` or `~/.profile` first, and many systems make that file load
`~/.bashrc`. If completion works in a new terminal window but not after logging in, add
`[ -f ~/.bashrc ] && . ~/.bashrc` to `~/.bash_profile`. A service account may have neither file, in which case
creating `~/.bashrc` as above is enough for non-login shells.

### Keeping it for zsh

Add `eval "$(plextool completion zsh)"` to `~/.zshrc`, or save the output to a file and `source` it from there. The
zsh script loads zsh's `bashcompinit` support first and uses the same logic as the bash one.

### After an upgrade

A saved script lists the commands as they were when it was saved, so it has to be saved again after plextool is
upgraded and gains a command (options 1 and 2 above). The `eval` form always reads the current commands.

## What it completes

| After typing | Tab offers |
| --- | --- |
| `plextool ` | The commands. |
| `plextool token ` | The subcommands (`new`, `list`, `claim`, `revoke`). |
| `plextool token new --` | The options of that subcommand. |
| `plextool auth login --type ` | The fixed choices for the option (`jwt`, `token`). |
| `plextool token new --file ` | File names, from the shell. |

An option's value is skipped when working out the command, so `plextool stale --library Movies --` offers the
options of `stale`. Values that depend on the server, such as library names and device IDs, are not completed.
