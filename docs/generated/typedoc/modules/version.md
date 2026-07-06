# Module: version

## Table of contents

### Interfaces

- [PackageInfo](../interfaces/version.PackageInfo.md)
- [VersionInfoSources](../interfaces/version.VersionInfoSources.md)

### Functions

- [composeVersionInfo](version.md#composeversioninfo)
- [envOverride](version.md#envoverride)
- [getVersionInfo](version.md#getversioninfo)
- [readPackageInfo](version.md#readpackageinfo)
- [readVersionFile](version.md#readversionfile)
- [repositoryUrl](version.md#repositoryurl)

## Functions

### composeVersionInfo

▸ **composeVersionInfo**(`sources`): [`VersionResponse`](../interfaces/contracts.VersionResponse.md)

Compose version metadata from explicit source objects.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `sources` | [`VersionInfoSources`](../interfaces/version.VersionInfoSources.md) | Package and VERSION metadata inputs. |

#### Returns

[`VersionResponse`](../interfaces/contracts.VersionResponse.md)

Public version response DTO.

**`Example`**

```ts
composeVersionInfo({
  servicePackage: { name: "svc", version: "1" },
  upstreamPackage: { name: "up", version: "2" }
});
```

___

### envOverride

▸ **envOverride**(`name`): `string` \| `undefined`

Read a meaningful build metadata environment override.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `name` | `string` | Environment variable name. |

#### Returns

`string` \| `undefined`

Trimmed override value, or `undefined` for missing/placeholder
values.

**`Example`**

```ts
envOverride("SERVICE_VERSION");
```

___

### getVersionInfo

▸ **getVersionInfo**(): [`VersionResponse`](../interfaces/contracts.VersionResponse.md)

Return version metadata for the current runtime.

#### Returns

[`VersionResponse`](../interfaces/contracts.VersionResponse.md)

Public version response DTO.

**`Example`**

```ts
getVersionInfo().service.name;
```

___

### readPackageInfo

▸ **readPackageInfo**(`paths`): [`PackageInfo`](../interfaces/version.PackageInfo.md)

Read package metadata from the first available package path.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `paths` | `string`[] | Candidate paths relative to this module. |

#### Returns

[`PackageInfo`](../interfaces/version.PackageInfo.md)

Parsed package metadata or an empty object.

**`Example`**

```ts
readPackageInfo(["../package.json"]).version;
```

___

### readVersionFile

▸ **readVersionFile**(`paths`): `string` \| `undefined`

Read the canonical service version file from the first available path.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `paths` | `string`[] | Candidate VERSION paths relative to this module. |

#### Returns

`string` \| `undefined`

Trimmed version string, or `undefined` when no candidate exists.

**`Example`**

```ts
readVersionFile(["../VERSION"]);
```

___

### repositoryUrl

▸ **repositoryUrl**(`repository`, `fallback`): `string`

Resolve a package repository value into a URL string.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repository` | `undefined` \| `string` \| \{ `url?`: `string`  } | Package repository field. |
| `fallback` | `string` | URL returned when repository metadata is missing. |

#### Returns

`string`

Repository URL.

**`Example`**

```ts
repositoryUrl({ url: "https://example.test/repo" }, "fallback");
```
