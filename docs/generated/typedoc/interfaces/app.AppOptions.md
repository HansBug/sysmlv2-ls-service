# Interface: AppOptions

[app](../modules/app.md).AppOptions

Application construction options.

## Table of contents

### Properties

- [limits](app.AppOptions.md#limits)
- [logger](app.AppOptions.md#logger)
- [validate](app.AppOptions.md#validate)

## Properties

### limits

• `Optional` **limits**: [`ServiceLimits`](limits.ServiceLimits.md)

Effective service limits. Omit to resolve them from environment.

___

### logger

• `Optional` **logger**: `boolean`

Enable or disable Fastify logging.

___

### validate

• `Optional` **validate**: [`ValidateFunction`](../modules/app.md#validatefunction)

Optional validate function used by tests or embedding callers.
