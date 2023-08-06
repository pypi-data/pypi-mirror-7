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
blacklisted_forks: []
```

Remember to quote your any of the values if necessary (if your password begins with `{` for example).

If you use two-pass authentication, you should [create an access token](https://github.com/settings/applications) and use that as your password instead.

`blacklisted_forks` is a list of repository full names (e.g. `myname/myproject`) that are forks that should be ignored. This is usually due to too much divergence from the original.

# Running

Running the utility is simple. Just run `sync-github-forks`.
