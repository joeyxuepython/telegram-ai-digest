# Security policy

Please do not disclose suspected vulnerabilities in a public issue before a fix
is available. Instead, use GitHub's private security advisory flow for this
repository, or contact the repository owner through their GitHub profile with a
minimal reproduction and impact description.

Do not include API keys, session files, private Telegram messages, or database
contents in a report. A maintainer will acknowledge reports and coordinate a
fix when the issue is confirmed.

## Security boundaries

- Telegram messages are untrusted input and may contain prompt-injection text.
- The local web viewer is unauthenticated and is not intended for direct public
  exposure.
- Telegram session files and API credentials are operator secrets and must
  never be attached to issues or committed.
- Webhook endpoints are operator-controlled data recipients and should use
  HTTPS and appropriate access controls.
