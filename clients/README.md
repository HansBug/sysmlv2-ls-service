# Clients

This directory contains installable clients for `sysmlv2-ls-service`.

## Available Clients

| Client | Module | Service API | Runtime |
| --- | --- | --- | --- |
| Python | `sysmlv2slclient` | Current public v1 endpoints | Python >=3.7 |

## Client Rules

Each client should:

- be independently installable;
- document the supported service API version;
- include its own tests;
- enforce 100% package branch coverage by default;
- keep SDK examples separate from service smoke examples;
- preserve service-owned DTO semantics without exposing Langium internals.
