# sysmlv2-ls-service

Docker-ready SysML v2 validation microservice built on top of Sensmetry's legacy
[`sysml-2ls`](https://github.com/sensmetry/sysml-2ls) language-server core.

The service exposes a small HTTP API for parsing and validating SysML v2 / KerML
text from Node.js, Docker, Python, or other microservice clients. It is intended
as a research and integration scaffold: `sysml-2ls` provides the textual language
frontend, while project-specific state-machine extraction and model checking can
be added above this API.

## Scope

Current API:

- `GET /healthz`
- `GET /v1/capabilities`
- `GET /v1/version`
- `POST /v1/validate`

Planned API:

- `POST /v1/parse`
- `POST /v1/extract/state-machines`
- `POST /v1/check/state-machines`

This service performs syntax, linking, and semantic validation available through
`sysml-2ls`. It is not, by itself, a formal model checker.

Files in one validation request are built as a single request-local workspace, so
imports between submitted files can resolve. Requests are isolated from each
other.

## Repository Layout

```text
.
├── src/                     # TypeScript API service and sysml-2ls adapter
├── tests/                   # Vitest unit/integration tests
├── examples/python/         # Python stdlib client example
├── upstream/sysml-2ls       # Git submodule pinned to upstream sysml-2ls
├── Dockerfile
└── .github/workflows/       # CI, CodeQL, and Docker release workflows
```

`AGENTS.md` is a symlink to `CLAUDE.md`.

## Prerequisites

- Node.js 20.19 or newer
- pnpm
- Git submodules initialized

```bash
git submodule update --init --recursive
corepack enable
pnpm install
pnpm run build:upstream
```

Use Node.js 20.19+ for both local development and CI. The Docker runtime uses
the current Node.js 20 slim image.

## Local Development

Run checks:

```bash
pnpm run ci
```

Start the service:

```bash
cp .env.example .env
pnpm run dev
```

Validate a simple model:

```bash
curl -sS -X POST http://localhost:3000/v1/validate \
  -H 'content-type: application/json' \
  --data '{"files":[{"uri":"memory:///demo.sysml","text":"package Demo { part def Vehicle; }"}]}' \
  | jq
```

## Docker

Build:

```bash
docker build -t sysmlv2-ls-service:local .
```

Run:

```bash
docker run --rm -p 3000:3000 sysmlv2-ls-service:local
```

Smoke test:

```bash
curl -fsS http://localhost:3000/healthz
curl -fsS http://localhost:3000/v1/version | jq
```

The image runs as the `node` user and the build stage prunes development
dependencies before copying runtime files.

## Version Metadata

`GET /v1/version` reports the service revision, upstream `sysml-2ls` revision,
build date, and runtime Node.js version.

```json
{
  "service": {
    "name": "sysmlv2-ls-service",
    "version": "0.1.0",
    "revision": "unknown",
    "sourceRepository": "https://github.com/HansBug/sysmlv2-ls-service"
  },
  "upstream": {
    "sysml2ls": {
      "version": "0.9.1",
      "revision": "unknown",
      "packageName": "syside-languageserver",
      "repository": "https://github.com/sensmetry/sysml-2ls"
    }
  },
  "build": {
    "date": "unknown",
    "nodeVersion": "v20.x.y"
  }
}
```

Docker builds can stamp the same metadata into environment variables and OCI
image labels:

```bash
docker build -t sysmlv2-ls-service:local \
  --build-arg SERVICE_VERSION=0.1.0 \
  --build-arg SERVICE_REVISION="$(git rev-parse HEAD)" \
  --build-arg SOURCE_REPOSITORY=https://github.com/HansBug/sysmlv2-ls-service \
  --build-arg UPSTREAM_SYSML_2LS_VERSION="$(node -p 'require("./upstream/sysml-2ls/packages/syside-languageserver/package.json").version')" \
  --build-arg UPSTREAM_SYSML_2LS_REVISION="$(git -C upstream/sysml-2ls rev-parse HEAD)" \
  --build-arg UPSTREAM_SYSML_2LS_REPOSITORY=https://github.com/sensmetry/sysml-2ls \
  --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  .
```

Relevant image labels:

| Label | Meaning |
| --- | --- |
| `org.opencontainers.image.source` | Current service repository URL |
| `org.opencontainers.image.revision` | Current service commit SHA |
| `org.opencontainers.image.version` | Current service package version |
| `org.opencontainers.image.created` | UTC build timestamp |
| `io.hansbug.sysmlv2-ls-service.upstream.sysml-2ls.version` | Upstream language-server package version |
| `io.hansbug.sysmlv2-ls-service.upstream.sysml-2ls.revision` | Pinned upstream submodule commit |
| `io.hansbug.sysmlv2-ls-service.upstream.sysml-2ls.repository` | Upstream repository URL |

If build args are omitted, `/v1/version` falls back to `package.json` metadata
inside the runtime image where possible. Unknown placeholder values are treated
as unset for the API response. OCI labels are only fully populated when the
corresponding build args are supplied, as the release workflow does.

## Validation Request

```json
{
  "files": [
    {
      "uri": "memory:///demo.sysml",
      "text": "package Demo { part def Vehicle; }"
    }
  ],
  "standardLibrary": "none",
  "validationChecks": "all"
}
```

Limits:

- Maximum files per request: 64
- Maximum text per file: 512 KiB
- Maximum total text per request: 1 MiB
- Duplicate `uri`/`path` values are rejected after URI canonicalization

`validationChecks: "none"` skips semantic checks only. Lexer and parser failures
still return `ok: false`.

Response:

```json
{
  "ok": true,
  "diagnostics": [],
  "files": [
    {
      "uri": "memory:///demo.sysml",
      "language": "sysml",
      "parserErrors": 0,
      "lexerErrors": 0,
      "diagnostics": 0
    }
  ],
  "meta": {
    "standardLibrary": "none",
    "validationChecks": "all",
    "elapsedMs": 12.34
  }
}
```

`ok` is `false` when any submitted file has lexer/parser errors or when any
normalized diagnostic has severity `error`. Warnings remain visible in
`diagnostics` but do not make `ok` false by themselves.

## Python Example

The Python example uses only the standard library. It sends two intentionally
broken SysML files to the service and prints a compact diagnostics table.

Start the service first:

```bash
pnpm run build
PORT=3000 node dist/src/server.js
```

Run the example in another terminal:

```bash
python3 examples/python/validate_example.py --url http://127.0.0.1:3000
```

The example submits this problematic SysML:

```sysml
package BrokenSemantic {
    part def Vehicle;
    part def Vehicle;
    public import Missing::*;
    part loose;
    part missing : MissingType;
}
```

and this syntactically broken file:

```sysml
package BrokenSyntax { part def }
```

Expected console shape:

```text
ok: False
elapsedMs: <varies>

Files:
- memory:///broken-semantic.sysml language=sysml parserErrors=0 lexerErrors=0 diagnostics=9
- memory:///broken-syntax.sysml language=sysml parserErrors=1 lexerErrors=0 diagnostics=1

Diagnostics:
1. error linking-error memory:///broken-semantic.sysml:4:19
   Could not resolve reference to Namespace named 'Missing'.
2. error linking-error memory:///broken-semantic.sysml:4:19
   Could not resolve reference to Namespace named 'Missing'.
3. error linking-error memory:///broken-semantic.sysml:6:20
   Could not resolve reference to Type named 'MissingType'.
4. warning validateNamespaceDistinguishability memory:///broken-semantic.sysml:2:14
   Duplicate of another member named Vehicle.
5. warning validateNamespaceDistinguishability memory:///broken-semantic.sysml:3:14
   Duplicate of another member named Vehicle.
6. error validateFeatureTyping memory:///broken-semantic.sysml:5:5
   A Feature must be typed by at least one type.
7. error validatePartUsagePartDefinition memory:///broken-semantic.sysml:5:5
   At least one of the itemDefinitions of a PartUsage must be a PartDefinition.
8. error validateFeatureTyping memory:///broken-semantic.sysml:6:20
   A Feature must be typed by at least one type.
9. error validatePartUsagePartDefinition memory:///broken-semantic.sysml:6:5
   At least one of the itemDefinitions of a PartUsage must be a PartDefinition.
10. error parsing-error memory:///broken-syntax.sysml:1:33
   Expecting: one of these possible Token sequences:
```

The duplicate `linking-error` for the missing import is upstream behavior from
the pinned `sysml-2ls` validation pipeline.

Raw JSON is available with:

```bash
python3 examples/python/validate_example.py --url http://127.0.0.1:3000 --json
```

## Diagnostics

Diagnostics come from two layers:

1. Langium/Chevrotain document diagnostics for lexing, parsing, and linking.
2. `sysml-2ls` KerML/SysML semantic validators for model-level constraints.

HTTP request validation errors are returned as service errors (`400`, `413`,
`500`) rather than SysML diagnostics.

### Diagnostic Categories

| Category | Codes | Severity | Meaning | Example trigger |
| --- | --- | --- | --- | --- |
| Lexing | `lexing-error` | error | The lexer cannot tokenize input. | Illegal characters or unterminated lexical forms. |
| Parsing | `parsing-error` | error | Tokens do not match the SysML/KerML grammar. | `package BrokenSyntax { part def }` |
| Linking | `linking-error` | error | A reference cannot resolve in the request workspace. | `public import Missing::*;` or `part p : MissingType;` |
| Naming/distinguishability | `validateNamespaceDistinguishability` | warning | Duplicate names in the same namespace. | Two `part def Vehicle;` declarations. |
| Import visibility | `validateImportExplicitVisibility`, `validateImportTopLevelVisibility` | error/warning from upstream | Import visibility rule violation. | `import Some::*;` when explicit visibility is required. |
| Typing | `validateFeatureTyping`, `validatePartUsageTyping`, `validateStateUsageTyping`, and related `*UsageTyping` codes | error | A usage is missing a required type or has the wrong kind of type. | `part loose;` |
| Specialization | `validateClassSpecialization`, `validateDatatypeSpecialization`, `validateStructSpecialization`, `validateBehaviorSpecialization` | error | A specialization targets an incompatible classifier kind. | A behavior specializing a structure. |
| Multiplicity/redefinition/subsetting | `validate*Multiplicity*`, `validateRedefinition*`, `validateSubsetting*` | error | Multiplicity, uniqueness, redefinition, or subsetting conformance failed. | A nonunique feature subsets a unique feature. |
| Connectors/flows/bindings | `validateConnector*`, `validateAssociation*`, `validateBindingConnector*`, `validateFlowConnection*`, `validateItemFlow*` | error | Relationship endpoints, binary connector rules, binding conformance, or flow constraints failed. | Concrete connector with too few related features. |
| Actions/expressions | `validate*Action*`, `validate*Expression*`, `validateTriggerInvocationAction*` | error | Action parameters, receivers, invocation arguments, or expression result rules failed. | Invalid `send` receiver or trigger invocation argument. |
| Requirements/cases/views | `validateRequirement*`, `validateCase*`, `validateView*`, `validateViewpoint*` | error | SysML requirement/case/view-specific ownership, subject/objective, or typing rules failed. | Requirement usage not typed by a requirement definition. |
| State machines | `validateState*`, `validateTransition*`, `validateTriggerInvocationAction*`, `validateExhibitStateUsageReference` | error | Structural state/transition validity failed. This is not temporal model checking. | Transition guard/effect/trigger membership has the wrong owning type. |
| Metadata/packages | `validateMetadata*`, `validatePackageElementFilter*`, `validateLibraryPackageNotStandard` | error | Metadata feature/body/metaclass or package filter rules failed. | Metadata feature typed by an abstract metaclass. |
| Service request validation | HTTP `400` with `bad_request` | n/a | JSON schema, duplicate URI, unsupported option, or text limit validation failed. | Empty `files`, duplicate `uri`, unsupported `standardLibrary`. |
| Payload size | HTTP `413` with `payload_too_large` | n/a | Request body exceeded Fastify body limit. | JSON body above 5 MiB. |
| Internal failure | HTTP `500` with `internal_error` | n/a | Unexpected service-side exception. | Bug or unsupported upstream failure mode. |

### Common Diagnostic Examples

| Code | Minimal trigger | Typical remediation |
| --- | --- | --- |
| `parsing-error` | `package BrokenSyntax { part def }` | Complete the grammar construct or remove the malformed declaration. |
| `linking-error` | `part missing : MissingType;` | Submit the defining file in the same request or correct the qualified name/import. |
| `validateNamespaceDistinguishability` | `part def Vehicle; part def Vehicle;` | Rename, qualify, or merge duplicate members. |
| `validateImportExplicitVisibility` | `import Some::*;` | Use explicit visibility, for example `public import Some::*;` or `private import Some::*;`. |
| `validateFeatureTyping` | `part loose;` | Type the feature with a valid definition. |
| `validatePartUsagePartDefinition` | `part missing : MissingType;` where `MissingType` cannot resolve to a part definition | Provide or correct a `part def` type. |
| `validateStateUsageTyping` | State usage not typed by a state definition | Type the state usage by exactly one state definition. |
| `validateTransitionUsageSuccession` | Transition without a valid succession path | Define source/target succession consistently with SysML transition rules. |

### Known Upstream Diagnostic Code Inventory

This table is generated from the currently pinned upstream sources under
`upstream/sysml-2ls/packages/syside-languageserver/src/services/validation` plus
Langium's document validator. The semantic code set is open-ended because
upstream constructs some codes dynamically, for example
`validate${node.nodeType()}OwningType`.

| Family | Known codes in the pinned upstream |
| --- | --- |
| Langium document layer | `lexing-error`, `parsing-error`, `linking-error` |
| Imports, packages, namespace | `validateElementIsImpliedIncluded`, `validateImportExplicitVisibility`, `validateImportTopLevelVisibility`, `validateLibraryPackageNotStandard`, `validateNamespaceDistinguishability`, `validatePackageElementFilterIsBoolean`, `validatePackageElementFilterIsModelLevelEvaluable` |
| Type relationships and specialization | `validateBehaviorSpecialization`, `validateClassSpecialization`, `validateDatatypeSpecialization`, `validateDefinitionVariationMembership`, `validateDefinitionVariationSpecialization`, `validateSpecializationSpecificNotConjugated`, `validateStructSpecialization`, `validateTypeAtMostOneConjugator`, `validateTypeDifferencingTypesNotSelf`, `validateTypeIntersectingTypesNotSelf`, `validateTypeOwnedDifferencingNotOne`, `validateTypeOwnedIntersectingNotOne`, `validateTypeOwnedMultiplicity`, `validateTypeOwnedUnioningNotOne`, `validateTypeUnioningTypesNotSelf`, `validateUsageVariationMembership`, `validateUsageVariationSpecialization` |
| Feature typing, chaining, subsetting, redefinition | `checkFeatureCrossingSpecialization`, `validateClassifierMultiplicityDomain`, `validateCrossSubsettingCrossedFeature`, `validateCrossSubsettingCrossingFeature`, `validateFeatureChainExpressionFeatureConformance`, `validateFeatureChainingFeatureConformance`, `validateFeatureChainingFeatureNotOne`, `validateFeatureChainingFeaturesNotSelf`, `validateFeatureCrossFeatureSpecialization`, `validateFeatureCrossFeatureType`, `validateFeatureEndMultiplicity`, `validateFeatureMultiplicityDomain`, `validateFeatureOwnedCrossSubsetting`, `validateFeatureOwnedReferenceSubsetting`, `validateFeatureReferenceExpressionReferentIsFeature`, `validateFeatureTyping`, `validateFeatureValueOverriding`, `validateMultiplicityRangeBoundResultTypes`, `validateRedefinitionDirectionConformance`, `validateRedefinitionFeaturingTypes`, `validateRedefinitionMultiplicityConformance`, `validateSubsettingFeaturingTypes`, `validateSubsettingMultiplicityConformance`, `validateSubsettingUniquenessConformance` |
| Structure, parts, ports, connections, flows | `checkConnectorTypeFeaturing`, `validateAllocationUsageTyping`, `validateAssociationBinarySpecialization`, `validateAssociationRelatedTypes`, `validateBindingConnectorIsBinary`, `validateBindingConnectorTypeConformance`, `validateConjugatedPortDefinitionOriginalPortDefinition`, `validateConnectionUsageTyping`, `validateConnectorBinarySpecialization`, `validateConnectorRelatedFeatures`, `validateFlowConnectionEnd`, `validateFlowConnectionUsageTyping`, `validateInterfaceDefinitionEnd`, `validateInterfaceUsageEnd`, `validateInterfaceUsageTyping`, `validateItemFlowEndImplicitSubsetting`, `validateItemFlowEndNestedFeature`, `validateItemFlowEndOwningType`, `validateItemFlowEndSubsetting`, `validateItemFlowItemFeature`, `validateItemUsageTyping`, `validatePartUsagePartDefinition`, `validatePartUsageTyping`, `validatePortDefinitionConjugatedPortDefinition`, `validatePortDefinitionOwnedUsagesNotComposite`, `validatePortUsageNestedUsagesNotComposite`, `validatePortUsageTyping` |
| Occurrences, attributes, enumerations | `validateAttributeUsageTyping`, `validateEnumerationUsageTyping`, `validateEventOccurrenceUsageReference`, `validateOccurrenceDefinitionLifeClass`, `validateOccurrenceUsageIndividualDefinition`, `validateOccurrenceUsageIndividualUsage`, `validateOccurrenceUsageTyping` |
| Actions, behavior, expressions | `validateAcceptActionUsageParameters`, `validateActionUsageTyping`, `validateAssertConstraintUsageReference`, `validateAssignmentActionUsageReferent`, `validateCalculationUsageTyping`, `validateConstraintUsageTyping`, `validateControlNodeOwningType`, `validateExpressionReturnParameterMembership`, `validateFeatureReferenceExpressionReferentIsFeature`, `validateFunctionReturnParameterMembership`, `validateInvocationExpressionNoDuplicateParameterRedefinition`, `validateInvocationExpressionParameterRedefinition`, `validateOperatorExpressionBracketOperator`, `validateOperatorExpressionCastConformance`, `validateOperatorExpressionQuantity`, `validateParameterMembershipOwningType`, `validatePerformActionUsageReference`, `validateResultExpressionMembershipOwningType`, `validateReturnParameterMembershipOwningType`, `validateSendActionParameters`, `validateSendActionReceiver`, `validateTriggerInvocationActionAfterArgument`, `validateTriggerInvocationActionAtArgument`, `validateTriggerInvocationActionWhenArgument` |
| States and transitions | `validateExhibitStateUsageReference`, `validateStateDefinitionParallelSubactions`, `validateStateDefinitionStateSubactionKind`, `validateStateSubactionMembershipOwningType`, `validateStateUsageParallelSubactions`, `validateStateUsageStateSubactionKind`, `validateStateUsageTyping`, `validateTransitionFeatureMembershipEffectAction`, `validateTransitionFeatureMembershipGuardExpression`, `validateTransitionFeatureMembershipOwningType`, `validateTransitionFeatureMembershipTriggerAction`, `validateTransitionUsageParameters`, `validateTransitionUsageSuccession` |
| Requirements, satisfy, use cases | `validateIncludeUseCaseUsageReference`, `validateRequirementConstraintMembershipIsComposite`, `validateRequirementDefinitionOnlyOneSubject`, `validateRequirementDefinitionSubjectParameterPosition`, `validateRequirementUsageOnlyOneSubject`, `validateRequirementUsageSubjectParameterPosition`, `validateRequirementUsageTyping`, `validateRequirementVerificationMembershipOwningType`, `validateSatisfyRequirementUsageReference`, `validateUseCaseUsageTyping`, `validateVerificationCaseUsageTyping` |
| Cases, objectives, analysis | `validateAnalysisCaseUsageTyping`, `validateCaseDefinitionOnlyOneObjective`, `validateCaseDefinitionOnlyOneSubject`, `validateCaseDefinitionSubjectParameterPosition`, `validateCaseUsageOnlyOneObjective`, `validateCaseUsageOnlyOneSubject`, `validateCaseUsageSubjectParameterPosition`, `validateCaseUsageTyping`, `validateObjectiveMembershipIsComposite`, `validateObjectiveMembershipOwningType` |
| Views, rendering, expose | `validateExposeNoExplicitVisibility`, `validateExposeOwningNamespace`, `validateRenderingUsageTyping`, `validateViewDefinitionOnlyOneViewRendering`, `validateViewUsageOnlyOneViewRendering`, `validateViewUsageTyping`, `validateViewpointUsageTyping` |
| Metadata | `validateMetadataFeatureAnnotatedElement`, `validateMetadataFeatureBody`, `validateMetadataFeatureMetaclass`, `validateMetadataFeatureMetaclassNotAbstract`, `validateMetadataUsageTyping`, `validateVariantMembershipOwningNamespace` |
| Dynamically constructed owning-type codes | `validateActorMembershipOwningType`, `validateSubjectMembershipOwningType`, `validateViewRenderingMembershipOwningType`, and the template family `validate${node.nodeType()}OwningType`, including requirement/stakeholder membership variants when those node types trigger the upstream branch. |

For state-machine work, the most relevant current upstream families are
`validateState*`, `validateTransition*`, `validateTriggerInvocationAction*`, and
`validateExhibitStateUsageReference`. These are structural SysML checks. They do
not prove temporal properties such as reachability, deadlock freedom, liveness,
or CTL/LTL properties.

## Release and Registry Publishing

`.github/workflows/release.yml` prepares Docker image publishing without pushing
anything by default in manual runs.

Triggers:

| Trigger | GHCR behavior | Docker Hub behavior |
| --- | --- | --- |
| `workflow_dispatch` with defaults | Build only, no push | Skipped |
| `workflow_dispatch` with `push_image=true` | Build and push GHCR | Skipped unless `publish_dockerhub=true` |
| `push` tag matching `v*` | Build and push GHCR | Push only when `PUBLISH_DOCKERHUB_ON_TAG=true` |

On tag pushes, the workflow fails early unless the tag equals
`v${package.json.version}`. This prevents publishing an image tagged `v0.2.0`
while `/v1/version` reports `0.1.0`.

Image names:

| Registry | Image |
| --- | --- |
| GHCR | `ghcr.io/hansbug/sysmlv2-ls-service` |
| Docker Hub | `docker.io/${DOCKERHUB_NAMESPACE}/sysmlv2-ls-service` |

Required GitHub configuration before real publishing:

| Name | Kind | Needed for | Notes |
| --- | --- | --- | --- |
| `GITHUB_TOKEN` | built-in secret | GHCR | No manual secret is needed for same-repo GHCR publishing when workflow permissions include `packages: write`. Repo/org package visibility rules may still need review. |
| `DOCKERHUB_NAMESPACE` | repository variable | Docker Hub | Docker Hub user or organization namespace. |
| `DOCKERHUB_USERNAME` | repository variable | Docker Hub | Docker Hub login username. |
| `DOCKERHUB_TOKEN` | repository secret | Docker Hub | Docker Hub access token. Use an access token, not the account password. |
| `PUBLISH_DOCKERHUB_ON_TAG` | repository variable | Docker Hub tag automation | Set to `true` only when tag pushes should also publish Docker Hub. |

Manual dry-run command after the workflow is on GitHub:

```bash
gh workflow run release.yml --ref main \
  -f push_image=false \
  -f publish_dockerhub=false
```

Real GHCR release:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Real Docker Hub release can be done either with manual
`publish_dockerhub=true` or by setting `PUBLISH_DOCKERHUB_ON_TAG=true` before
pushing a `v*` tag.

Release workflow references:

- GitHub Actions Docker image publishing docs:
  <https://docs.github.com/en/actions/use-cases-and-examples/publishing-packages/publishing-docker-images>
- Docker login action docs:
  <https://github.com/docker/login-action>
- Docker build-push action docs:
  <https://github.com/docker/build-push-action>

## Security Gates

The repository includes these security controls:

| Control | Location | Purpose |
| --- | --- | --- |
| Dependency audit | `pnpm run audit`, `.github/workflows/security-audit.yml` | Fails on moderate or higher npm advisories on dependency-changing PRs, main pushes, weekly schedule, and manual dispatch. |
| Dependabot | `.github/dependabot.yml` | Weekly npm, GitHub Actions, and Docker base image update PRs. |
| CodeQL | `.github/workflows/codeql.yml`, `.github/codeql/codeql-config.yml` | JavaScript/TypeScript code scanning on PR, push, and weekly schedule, scoped to service-owned code and excluding pinned upstream. |
| Docker metadata | `Dockerfile`, `/v1/version` | Runtime and image provenance for current repo and pinned upstream. |
| Request limits | `src/contracts.ts`, `src/app.ts` | Per-file, total text, file count, duplicate URI, and body-size protections. |

The current lockfile uses patched dev tooling (`vitest`, `vite`, `esbuild`) and
an explicit `lodash` override for the `langium -> chevrotain` transitive chain.

## Notes on `sysml-2ls`

`sysml-2ls` is a legacy/deprecated open-source SysML v2 language server. It uses
Langium/Chevrotain rather than ANTLR. The submodule is intentionally pinned so
CI and Docker builds are reproducible.

Current pinned upstream:

| Item | Value |
| --- | --- |
| Submodule path | `upstream/sysml-2ls` |
| Upstream commit | `a0b3ddbf783063dd7291aac0b51d4282decc789e` |
| Language-server package | `syside-languageserver` |
| Upstream package version | `0.9.1` |
| Grammar/runtime stack | Langium + Chevrotain |
| ANTLR | Not used |

The public upstream link used by this service is the GitHub repository above.
The vendored package metadata in `syside-languageserver` also references
`https://gitlab.com/sensmetry/public/sysml-2ls`; treat that as upstream package
metadata rather than the service's configured provenance URL.

The current API runs validation without a SysML standard library
(`standardLibrary: "none"`). Standard-library-backed validation should be added
as an explicit configuration feature once the service owns a reproducible local
library path or cache.

## License

This repository is a service scaffold. The vendored upstream submodule retains
its original license terms. Review upstream licensing before redistribution.
