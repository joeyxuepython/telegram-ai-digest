# Privacy and data handling

Telegram AI Digest is designed for operator-controlled deployments. It does not
run a hosted service and does not receive project users' credentials.

## Data flow

1. Telethon retrieves messages from chat IDs configured by the operator.
2. The selected message text, sender display name, and message timestamp are
   sent to the OpenAI-compatible endpoint configured by that operator.
3. Generated digests are stored in the operator's local SQLite database and may
   be sent to the output channels they choose.

## Operator responsibilities

- Process only chats for which you have authorization and a lawful basis.
- Tell affected participants when required by applicable law or community rules.
- Keep `config.yaml`, environment files, sessions, and `data/` private.
- Use a least-privilege account and protect the machine hosting the tool.
- Set an appropriate retention policy and delete local digest data when it is no
  longer needed.

Do not use this project to monitor private conversations without authorization.
