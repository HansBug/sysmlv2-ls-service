# Upstream semantic checks

Generated inventory of validator methods discovered from the pinned upstream `sysml-2ls` submodule. These are structural SysML/KerML checks, not temporal model-checking results.

Inventory context: upstream package `0.9.1` at revision `a0b3ddbf783063dd7291aac0b51d4282decc789e`. Evidence target: TypeScript source. Compiled JS/d.ts artifacts are checked for presence after `pnpm run build:upstream`, but are not primary evidence in this first inventory version.

| Check | Language | Decorators | Source |
| --- | --- | --- | --- |
| `validateAcceptActionUsageParameters` | sysml | `ast.AcceptActionUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateActionUsageTyping` | sysml | `ast.ActionUsage, [ast.StateUsage, ast.CalculationUsage, ast.FlowConnectionUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateActorMembershipOwningType` | sysml | `ast.ActorMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAllocationUsageTyping` | sysml | `ast.AllocationUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAllTypings` | sysml | `ast.AttributeUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAllTypings` | sysml | `ast.OccurrenceUsage, [ast.ItemUsage, ast.PortUsage, ast.Step]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAllTypings` | sysml | `ast.ItemUsage, [ast.PartUsage, ast.PortUsage, ast.MetadataUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAllTypings` | sysml | `ast.PartUsage, [ast.ConnectionUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAllTypings` | sysml | `ast.PortUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAllTypings` | sysml | `ast.ConnectionUsage, [         ast.FlowConnectionUsage,         ast.InterfaceUsage,         ast.AllocationUsage,     ]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAllTypings` | sysml | `ast.FlowConnectionUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAllTypings` | sysml | `ast.InterfaceUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAllTypings` | sysml | `ast.AllocationUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAllTypings` | sysml | `ast.ActionUsage, [ast.StateUsage, ast.CalculationUsage, ast.FlowConnectionUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAllTypings` | sysml | `ast.StateUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAnalysisCaseUsageTyping` | sysml | `ast.AnalysisCaseUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAssertConstraintUsageReference` | sysml | `ast.AssertConstraintUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAssignmentActionUsageReferent` | sysml | `ast.AssignmentActionUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAssocStructSpecialization` | sysml | `ast.AssociationStructure`, `ast.Interaction` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAtLeastTyping` | sysml | `ast.PartUsage, [ast.ConnectionUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateAttributeUsageTyping` | sysml | `ast.AttributeUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateCalculationUsageTyping` | sysml | `ast.CalculationUsage, [ast.CaseUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateCaseDefinitionOnlyOneSubject` | sysml | `ast.CaseDefinition`, `ast.CaseUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateCaseOnlyOneObjective` | sysml | `ast.CaseDefinition`, `ast.CaseUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateCaseSubjectParameterPosition` | sysml | `ast.CaseDefinition`, `ast.CaseUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateCaseUsageTyping` | sysml | `ast.CaseUsage, [         ast.AnalysisCaseUsage,         ast.VerificationCaseUsage,         ast.UseCaseUsage,     ]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateClassSpecialization` | sysml | `ast.Class, [ast.AssociationStructure, ast.Interaction]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateConjugatedPortDefinitionOriginalPortDefinition` | sysml | `ast.ConjugatedPortDefinition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateConnectionUsageTyping` | sysml | `ast.ConnectionUsage, [         ast.FlowConnectionUsage,         ast.InterfaceUsage,         ast.AllocationUsage,     ]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateConstraintUsageTyping` | sysml | `ast.ConstraintUsage, [ast.RequirementUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateControlNodeOwningType` | sysml | `ast.ControlNode` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateDatatypeSpecialization` | sysml | `ast.DataType` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateEnumerationUsageTyping` | sysml | `ast.EnumerationUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateEventOccurrenceUsageReference` | sysml | `ast.EventOccurrenceUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExactlyOneTyping` | sysml | `ast.EnumerationUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExactlyOneTyping` | sysml | `ast.CalculationUsage, [ast.CaseUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExactlyOneTyping` | sysml | `ast.ConstraintUsage, [ast.RequirementUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExactlyOneTyping` | sysml | `ast.RequirementUsage, [ast.ViewpointUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExactlyOneTyping` | sysml | `ast.CaseUsage, [         ast.AnalysisCaseUsage,         ast.VerificationCaseUsage,         ast.UseCaseUsage,     ]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExactlyOneTyping` | sysml | `ast.AnalysisCaseUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExactlyOneTyping` | sysml | `ast.VerificationCaseUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExactlyOneTyping` | sysml | `ast.UseCaseUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExactlyOneTyping` | sysml | `ast.RenderingUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExactlyOneTyping` | sysml | `ast.ViewpointUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExactlyOneTyping` | sysml | `ast.ViewUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExactlyOneTyping` | sysml | `ast.MetadataUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExhibitStateUsageReference` | sysml | `ast.ExhibitStateUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExposeNoExplicitVisibility` | sysml | `ast.Expose` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateExposeOwningNamespace` | sysml | `ast.Expose` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateFlowConnectionEnd` | sysml | `ast.FlowConnectionDefinition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateFlowConnectionUsageTyping` | sysml | `ast.FlowConnectionUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateIncludeUseCaseUsageReference` | sysml | `ast.IncludeUseCaseUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateInterfaceEnds` | sysml | `ast.InterfaceDefinition`, `ast.InterfaceUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateInterfaceUsageTyping` | sysml | `ast.InterfaceUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateItemUsageTyping` | sysml | `ast.ItemUsage, [ast.PartUsage, ast.PortUsage, ast.MetadataUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateMetadataUsageTyping` | sysml | `ast.MetadataUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateObjectiveMembershipIsComposite` | sysml | `ast.ObjectiveMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateObjectiveMembershipOwningType` | sysml | `ast.ObjectiveMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateOccurrenceDefinitionLifeClass` | sysml | `ast.OccurrenceDefinition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateOccurrenceUsageIndividual` | sysml | `ast.OccurrenceUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateOccurrenceUsageTyping` | sysml | `ast.OccurrenceUsage, [ast.ItemUsage, ast.PortUsage, ast.Step]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateOperatorExpressionQuantity` | sysml | `ast.OperatorExpression, [         ast.CollectExpression,         ast.SelectExpression,         ast.FeatureChainExpression,     ]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validatePartUsageTyping` | sysml | `ast.PartUsage, [ast.ConnectionUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validatePerformActionUsageReference` | sysml | `ast.PerformActionUsage, [ast.ExhibitStateUsage, ast.IncludeUseCaseUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validatePortDefinitionConjugatedPortDefinition` | sysml | `ast.PortDefinition, [ast.ConjugatedPortDefinition]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validatePortOwnedUsagesNotComposite` | sysml | `ast.PortDefinition`, `ast.PortUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validatePortUsageTyping` | sysml | `ast.PortUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateRenderingUsageTyping` | sysml | `ast.RenderingUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateRequirementConstraintMembershipIsComposite` | sysml | `ast.RequirementConstraintMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateRequirementMembershipOwningType` | sysml | `ast.RequirementConstraintMembership`, `ast.StakeholderMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateRequirementOnlyOneSubject` | sysml | `ast.RequirementDefinition`, `ast.RequirementUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateRequirementSubjectParameterPosition` | sysml | `ast.RequirementDefinition`, `ast.RequirementUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateRequirementUsageTyping` | sysml | `ast.RequirementUsage, [ast.ViewpointUsage]` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateRequirementVerificationMembershipOwningType` | sysml | `ast.RequirementVerificationMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSatisfyRequirementUsageReference` | sysml | `ast.SatisfyRequirementUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSendActionParameters` | sysml | `ast.SendActionUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSendActionReceiver` | sysml | `ast.SendActionUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateStateParallelSubactions` | sysml | `ast.SuccessionAsUsage`, `ast.TransitionUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateStateSubactionKind` | sysml | `ast.StateDefinition`, `ast.StateUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateStateSubactionMembershipOwningType` | sysml | `ast.StateSubactionMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateStateUsageTyping` | sysml | `ast.StateUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSubjectMembershipOwningType` | sysml | `ast.SubjectMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.Definition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.Definition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.PortDefinition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.InterfaceDefinition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.SuccessionAsUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.StateDefinition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.RequirementConstraintMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.RequirementDefinition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.RequirementDefinition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.CaseDefinition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.CaseDefinition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.CaseDefinition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.ViewDefinition` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateSysML` | sysml | `ast.AssociationStructure` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateTransitionFeatureMembership` | sysml | `ast.TransitionFeatureMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateTransitionFeatureMembershipOwningType` | sysml | `ast.TransitionFeatureMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateTransitionUsageParameters` | sysml | `ast.TransitionUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateTransitionUsageSuccession` | sysml | `ast.TransitionUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateTriggerInvocationExpression` | sysml | `ast.TriggerInvocationExpression` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateUseCaseUsageTyping` | sysml | `ast.UseCaseUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateVariantMembershipOwningNamespace` | sysml | `ast.VariantMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateVariationMembership` | sysml | `ast.Definition`, `ast.Usage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateVariationSpecialization` | sysml | `ast.Definition`, `ast.Usage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateVerificationCaseUsageTyping` | sysml | `ast.VerificationCaseUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateViewDefinitionOnlyOneViewRendering` | sysml | `ast.ViewDefinition`, `ast.ViewUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateViewpointUsageTyping` | sysml | `ast.ViewpointUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateViewRenderingMembershipOwningType` | sysml | `ast.ViewRenderingMembership` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
| `validateViewUsageTyping` | sysml | `ast.ViewUsage` | `packages/syside-languageserver/src/services/validation/sysml-validator.ts` |
