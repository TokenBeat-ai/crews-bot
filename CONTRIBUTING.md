# Contributing

Thanks for helping improve Crews Bot.

## Ways to contribute

- **Report a problem:** open an issue with your host (Codex, Cursor, Claude Code…), Python version, Crews Bot version (`VERSION`) and what you expected.
- **Improve the methods or docs:** small, focused pull requests are easiest to review.
- **Propose a workflow:** open an issue first describing the job, inputs and outputs. Workflows must not contain real customer data, credentials or content you do not have the right to share.

## Pull requests

1. Keep changes focused; explain what changed and why.
2. Run the tests: `python3 -m unittest discover -s dashboard/tests`.
3. Use fictional data in examples and screenshots.
4. Sign off every commit (see below).

## Developer Certificate of Origin

We use the [Developer Certificate of Origin](https://developercertificate.org/) instead of a contributor license agreement. By signing off, you certify that you wrote the contribution or otherwise have the right to submit it under the project's license.

Add a sign-off line to each commit:

```sh
git commit -s -m "Describe your change"
```

This adds `Signed-off-by: Your Name <you@example.com>`. Contributions are accepted under the [Apache License 2.0](LICENSE).
