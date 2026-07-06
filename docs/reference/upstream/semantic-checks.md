# Upstream semantic checks

Generated inventory of validator methods discovered from the pinned upstream `sysml-2ls` submodule. These are structural SysML/KerML checks, not temporal model-checking results.

Inventory context: upstream package `0.9.1` at revision `a0b3ddbf783063dd7291aac0b51d4282decc789e`. Evidence target: TypeScript source. Compiled JS/d.ts artifacts are checked for presence after `pnpm run build:upstream`, but are not primary evidence in this first inventory version.

!!! warning "Static evidence"
    Rows are discovered from upstream TypeScript source. They show validator methods and decorators in the pinned submodule; they do not prove temporal model-checking capability or dynamic reachability from every service request.

## Summary

| Metric | Value |
| --- | --- |
| Rows | 110 |
| Unique check names | 76 |
| Languages | `sysml`: 110 |
| Source files | `sysml-validator.ts`: 110 |

## Complete discovered table

The table focuses on check names and decorators for readability. The summary lists compact source filenames, and the committed JSON data under `docs/_data/upstream/semantic-checks.json` retains full source paths and generator metadata.

<div class="compact-table wide-table" markdown>

| Check | Lang | Decorators |
| --- | --- | --- |
| `validateAcceptActionUsageParameters` | sysml | `AcceptActionUsage` |
| `validateActionUsageTyping` | sysml | `ActionUsage, excluding StateUsage, CalculationUsage, FlowConnectionUsage` |
| `validateActorMembershipOwningType` | sysml | `ActorMembership` |
| `validateAllocationUsageTyping` | sysml | `AllocationUsage` |
| `validateAllTypings` | sysml | `AttributeUsage` |
| `validateAllTypings` | sysml | `OccurrenceUsage, excluding ItemUsage, PortUsage, Step` |
| `validateAllTypings` | sysml | `ItemUsage, excluding PartUsage, PortUsage, MetadataUsage` |
| `validateAllTypings` | sysml | `PartUsage, excluding ConnectionUsage` |
| `validateAllTypings` | sysml | `PortUsage` |
| `validateAllTypings` | sysml | `ConnectionUsage, excluding FlowConnectionUsage, InterfaceUsage, AllocationUsage` |
| `validateAllTypings` | sysml | `FlowConnectionUsage` |
| `validateAllTypings` | sysml | `InterfaceUsage` |
| `validateAllTypings` | sysml | `AllocationUsage` |
| `validateAllTypings` | sysml | `ActionUsage, excluding StateUsage, CalculationUsage, FlowConnectionUsage` |
| `validateAllTypings` | sysml | `StateUsage` |
| `validateAnalysisCaseUsageTyping` | sysml | `AnalysisCaseUsage` |
| `validateAssertConstraintUsageReference` | sysml | `AssertConstraintUsage` |
| `validateAssignmentActionUsageReferent` | sysml | `AssignmentActionUsage` |
| `validateAssocStructSpecialization` | sysml | `AssociationStructure`, `Interaction` |
| `validateAtLeastTyping` | sysml | `PartUsage, excluding ConnectionUsage` |
| `validateAttributeUsageTyping` | sysml | `AttributeUsage` |
| `validateCalculationUsageTyping` | sysml | `CalculationUsage, excluding CaseUsage` |
| `validateCaseDefinitionOnlyOneSubject` | sysml | `CaseDefinition`, `CaseUsage` |
| `validateCaseOnlyOneObjective` | sysml | `CaseDefinition`, `CaseUsage` |
| `validateCaseSubjectParameterPosition` | sysml | `CaseDefinition`, `CaseUsage` |
| `validateCaseUsageTyping` | sysml | `CaseUsage, excluding AnalysisCaseUsage, VerificationCaseUsage, UseCaseUsage` |
| `validateClassSpecialization` | sysml | `Class, excluding AssociationStructure, Interaction` |
| `validateConjugatedPortDefinitionOriginalPortDefinition` | sysml | `ConjugatedPortDefinition` |
| `validateConnectionUsageTyping` | sysml | `ConnectionUsage, excluding FlowConnectionUsage, InterfaceUsage, AllocationUsage` |
| `validateConstraintUsageTyping` | sysml | `ConstraintUsage, excluding RequirementUsage` |
| `validateControlNodeOwningType` | sysml | `ControlNode` |
| `validateDatatypeSpecialization` | sysml | `DataType` |
| `validateEnumerationUsageTyping` | sysml | `EnumerationUsage` |
| `validateEventOccurrenceUsageReference` | sysml | `EventOccurrenceUsage` |
| `validateExactlyOneTyping` | sysml | `EnumerationUsage` |
| `validateExactlyOneTyping` | sysml | `CalculationUsage, excluding CaseUsage` |
| `validateExactlyOneTyping` | sysml | `ConstraintUsage, excluding RequirementUsage` |
| `validateExactlyOneTyping` | sysml | `RequirementUsage, excluding ViewpointUsage` |
| `validateExactlyOneTyping` | sysml | `CaseUsage, excluding AnalysisCaseUsage, VerificationCaseUsage, UseCaseUsage` |
| `validateExactlyOneTyping` | sysml | `AnalysisCaseUsage` |
| `validateExactlyOneTyping` | sysml | `VerificationCaseUsage` |
| `validateExactlyOneTyping` | sysml | `UseCaseUsage` |
| `validateExactlyOneTyping` | sysml | `RenderingUsage` |
| `validateExactlyOneTyping` | sysml | `ViewpointUsage` |
| `validateExactlyOneTyping` | sysml | `ViewUsage` |
| `validateExactlyOneTyping` | sysml | `MetadataUsage` |
| `validateExhibitStateUsageReference` | sysml | `ExhibitStateUsage` |
| `validateExposeNoExplicitVisibility` | sysml | `Expose` |
| `validateExposeOwningNamespace` | sysml | `Expose` |
| `validateFlowConnectionEnd` | sysml | `FlowConnectionDefinition` |
| `validateFlowConnectionUsageTyping` | sysml | `FlowConnectionUsage` |
| `validateIncludeUseCaseUsageReference` | sysml | `IncludeUseCaseUsage` |
| `validateInterfaceEnds` | sysml | `InterfaceDefinition`, `InterfaceUsage` |
| `validateInterfaceUsageTyping` | sysml | `InterfaceUsage` |
| `validateItemUsageTyping` | sysml | `ItemUsage, excluding PartUsage, PortUsage, MetadataUsage` |
| `validateMetadataUsageTyping` | sysml | `MetadataUsage` |
| `validateObjectiveMembershipIsComposite` | sysml | `ObjectiveMembership` |
| `validateObjectiveMembershipOwningType` | sysml | `ObjectiveMembership` |
| `validateOccurrenceDefinitionLifeClass` | sysml | `OccurrenceDefinition` |
| `validateOccurrenceUsageIndividual` | sysml | `OccurrenceUsage` |
| `validateOccurrenceUsageTyping` | sysml | `OccurrenceUsage, excluding ItemUsage, PortUsage, Step` |
| `validateOperatorExpressionQuantity` | sysml | `OperatorExpression, excluding CollectExpression, SelectExpression, FeatureChainExpression` |
| `validatePartUsageTyping` | sysml | `PartUsage, excluding ConnectionUsage` |
| `validatePerformActionUsageReference` | sysml | `PerformActionUsage, excluding ExhibitStateUsage, IncludeUseCaseUsage` |
| `validatePortDefinitionConjugatedPortDefinition` | sysml | `PortDefinition, excluding ConjugatedPortDefinition` |
| `validatePortOwnedUsagesNotComposite` | sysml | `PortDefinition`, `PortUsage` |
| `validatePortUsageTyping` | sysml | `PortUsage` |
| `validateRenderingUsageTyping` | sysml | `RenderingUsage` |
| `validateRequirementConstraintMembershipIsComposite` | sysml | `RequirementConstraintMembership` |
| `validateRequirementMembershipOwningType` | sysml | `RequirementConstraintMembership`, `StakeholderMembership` |
| `validateRequirementOnlyOneSubject` | sysml | `RequirementDefinition`, `RequirementUsage` |
| `validateRequirementSubjectParameterPosition` | sysml | `RequirementDefinition`, `RequirementUsage` |
| `validateRequirementUsageTyping` | sysml | `RequirementUsage, excluding ViewpointUsage` |
| `validateRequirementVerificationMembershipOwningType` | sysml | `RequirementVerificationMembership` |
| `validateSatisfyRequirementUsageReference` | sysml | `SatisfyRequirementUsage` |
| `validateSendActionParameters` | sysml | `SendActionUsage` |
| `validateSendActionReceiver` | sysml | `SendActionUsage` |
| `validateStateParallelSubactions` | sysml | `SuccessionAsUsage`, `TransitionUsage` |
| `validateStateSubactionKind` | sysml | `StateDefinition`, `StateUsage` |
| `validateStateSubactionMembershipOwningType` | sysml | `StateSubactionMembership` |
| `validateStateUsageTyping` | sysml | `StateUsage` |
| `validateSubjectMembershipOwningType` | sysml | `SubjectMembership` |
| `validateSysML` | sysml | `Definition` |
| `validateSysML` | sysml | `Definition` |
| `validateSysML` | sysml | `PortDefinition` |
| `validateSysML` | sysml | `InterfaceDefinition` |
| `validateSysML` | sysml | `SuccessionAsUsage` |
| `validateSysML` | sysml | `StateDefinition` |
| `validateSysML` | sysml | `RequirementConstraintMembership` |
| `validateSysML` | sysml | `RequirementDefinition` |
| `validateSysML` | sysml | `RequirementDefinition` |
| `validateSysML` | sysml | `CaseDefinition` |
| `validateSysML` | sysml | `CaseDefinition` |
| `validateSysML` | sysml | `CaseDefinition` |
| `validateSysML` | sysml | `ViewDefinition` |
| `validateSysML` | sysml | `AssociationStructure` |
| `validateTransitionFeatureMembership` | sysml | `TransitionFeatureMembership` |
| `validateTransitionFeatureMembershipOwningType` | sysml | `TransitionFeatureMembership` |
| `validateTransitionUsageParameters` | sysml | `TransitionUsage` |
| `validateTransitionUsageSuccession` | sysml | `TransitionUsage` |
| `validateTriggerInvocationExpression` | sysml | `TriggerInvocationExpression` |
| `validateUseCaseUsageTyping` | sysml | `UseCaseUsage` |
| `validateVariantMembershipOwningNamespace` | sysml | `VariantMembership` |
| `validateVariationMembership` | sysml | `Definition`, `Usage` |
| `validateVariationSpecialization` | sysml | `Definition`, `Usage` |
| `validateVerificationCaseUsageTyping` | sysml | `VerificationCaseUsage` |
| `validateViewDefinitionOnlyOneViewRendering` | sysml | `ViewDefinition`, `ViewUsage` |
| `validateViewpointUsageTyping` | sysml | `ViewpointUsage` |
| `validateViewRenderingMembershipOwningType` | sysml | `ViewRenderingMembership` |
| `validateViewUsageTyping` | sysml | `ViewUsage` |

</div>
