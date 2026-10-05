# ADR-0005: Keep real healthcare data out of the public repository

**Status:** Accepted

## Context

NaviMed is healthcare-adjacent and the portfolio repository is intended for public GitHub review. Real provider, pharmacy, patient and emergency-contact datasets are not needed to prove the architecture.

## Decision

Do not commit real personal/operational healthcare data, credentials, phone numbers, patient records or production exports to Git. Real datasets are provisioned through controlled non-repository workflows. Synthetic fixtures may be used only for tests or explicitly invoked local development.

## Consequences

The public repository remains safer and easier to review. End-to-end production validation will require a separately managed environment containing authorized data.
