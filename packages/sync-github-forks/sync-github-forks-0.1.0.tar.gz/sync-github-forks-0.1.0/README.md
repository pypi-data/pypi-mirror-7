# Abstract

This command line utility merges all of your forks with the parent project. This is to ensure your forks do not get out of date.

In general, you should be using separate branches for pull requests, so you should not be bothered if the default branch gets updated.

# Installation

Use `pip`:

```bash
pip install sync-github-forks
```

# Configuration

To use this you need a simple configuration file in your home directory at `~/.github-api.yml`. It should have 2 keys: `user` and `password`. Both are strings.

```yaml
username: my_user_name
password: 'password'
```

Remember to quote your any of the values if necessary (if your password begins with `{` for example).

# Running

Running the utility is simple. Just run `sync-github-forks`.
