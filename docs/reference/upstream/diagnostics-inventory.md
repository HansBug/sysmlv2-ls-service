# Upstream diagnostics inventory

Generated inventory of diagnostic message patterns statically associated with upstream validation checks. Low-confidence rows mean the script found a check but no direct message literal.

Inventory context: upstream package `0.9.1` at revision `a0b3ddbf783063dd7291aac0b51d4282decc789e`. Evidence target: TypeScript source. Compiled JS/d.ts artifacts are checked for presence after `pnpm run build:upstream`, but are not primary evidence in this first inventory version.

!!! warning "Message wording"
    Message patterns are static source evidence. Runtime diagnostics may include template interpolation or additional Langium/linking diagnostics that are not direct semantic-check literals.

## Summary

| Metric | Value |
| --- | --- |
| Rows | 118 |
| Confidence | `low`: 87, `medium`: 31 |
| Unique check IDs | 76 |

## Complete discovered table

<div class="compact-table wide-table" markdown>

| Check | Message pattern | Confidence |
| --- | --- | --- |
| `sysml:validateAcceptActionUsageParameters` | No static message literal found by the inventory script. | low |
| `sysml:validateActionUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateActorMembershipOwningType` | The owningType of ActorMembership must be a RequirementDefinition, RequirementUsage, CaseDefinition, or CaseUsage. | medium |
| `sysml:validateAllocationUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateAllTypings` | No static message literal found by the inventory script. | low |
| `sysml:validateAllTypings` | No static message literal found by the inventory script. | low |
| `sysml:validateAllTypings` | No static message literal found by the inventory script. | low |
| `sysml:validateAllTypings` | No static message literal found by the inventory script. | low |
| `sysml:validateAllTypings` | No static message literal found by the inventory script. | low |
| `sysml:validateAllTypings` | No static message literal found by the inventory script. | low |
| `sysml:validateAllTypings` | No static message literal found by the inventory script. | low |
| `sysml:validateAllTypings` | No static message literal found by the inventory script. | low |
| `sysml:validateAllTypings` | No static message literal found by the inventory script. | low |
| `sysml:validateAllTypings` | No static message literal found by the inventory script. | low |
| `sysml:validateAllTypings` | No static message literal found by the inventory script. | low |
| `sysml:validateAnalysisCaseUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateAssertConstraintUsageReference` | No static message literal found by the inventory script. | low |
| `sysml:validateAssignmentActionUsageReferent` | An assignment must have a Feature referent. | medium |
| `sysml:validateAssocStructSpecialization` | No static message literal found by the inventory script. | low |
| `sysml:validateAtLeastTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateAttributeUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateCalculationUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateCaseDefinitionOnlyOneSubject` | No static message literal found by the inventory script. | low |
| `sysml:validateCaseOnlyOneObjective` | No static message literal found by the inventory script. | low |
| `sysml:validateCaseSubjectParameterPosition` | No static message literal found by the inventory script. | low |
| `sysml:validateCaseUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateClassSpecialization` | No static message literal found by the inventory script. | low |
| `sysml:validateConjugatedPortDefinitionOriginalPortDefinition` | The originalPortDefinition of the ownedPortConjugator of a ConjugatedPortDefinition must be the originalPortDefinition of the ConjugatedPortDefinition. | medium |
| `sysml:validateConnectionUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateConstraintUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateControlNodeOwningType` | The owningType of a ControlNode must be an ActionDefinition or ActionUsage. | medium |
| `sysml:validateDatatypeSpecialization` | No static message literal found by the inventory script. | low |
| `sysml:validateEnumerationUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateEventOccurrenceUsageReference` | No static message literal found by the inventory script. | low |
| `sysml:validateExactlyOneTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateExactlyOneTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateExactlyOneTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateExactlyOneTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateExactlyOneTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateExactlyOneTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateExactlyOneTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateExactlyOneTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateExactlyOneTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateExactlyOneTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateExactlyOneTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateExactlyOneTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateExhibitStateUsageReference` | No static message literal found by the inventory script. | low |
| `sysml:validateExposeNoExplicitVisibility` | An Expose cannot have an explicit visibility. | medium |
| `sysml:validateExposeOwningNamespace` | The importOwningNamespace of an Expose must be a ViewUsage. | medium |
| `sysml:validateFlowConnectionEnd` | No static message literal found by the inventory script. | low |
| `sysml:validateFlowConnectionUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateIncludeUseCaseUsageReference` | No static message literal found by the inventory script. | low |
| `sysml:validateInterfaceEnds` | No static message literal found by the inventory script. | low |
| `sysml:validateInterfaceUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateItemUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateMetadataUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateObjectiveMembershipIsComposite` | The ownedConstraint of a ObjectiveMembership must be composite. | medium |
| `sysml:validateObjectiveMembershipOwningType` | The owningType of an ObjectiveMembership must be a CaseDefinition or CaseUsage. | medium |
| `sysml:validateOccurrenceDefinitionLifeClass` | No static message literal found by the inventory script. | low |
| `sysml:validateOccurrenceUsageIndividual` | An OccurrenceUsage must have at most one occurrenceDefinition with isIndividual = true. | medium |
| `sysml:validateOccurrenceUsageIndividual` | An individual OccurrenceUsage must an individualDefinition. | medium |
| `sysml:validateOccurrenceUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateOperatorExpressionQuantity` | ${options.type} must have ${key} parameter. | medium |
| `sysml:validateOperatorExpressionQuantity` | Invalid quantity expression, expected a measurement reference unit | medium |
| `sysml:validateOperatorExpressionQuantity` | ReferenceSubsettings owned by ${options.type} must reference ${options.reference} | medium |
| `sysml:validatePartUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validatePerformActionUsageReference` | No static message literal found by the inventory script. | low |
| `sysml:validatePortDefinitionConjugatedPortDefinition` | No static message literal found by the inventory script. | low |
| `sysml:validatePortOwnedUsagesNotComposite` | No static message literal found by the inventory script. | low |
| `sysml:validatePortUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateRenderingUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateRequirementConstraintMembershipIsComposite` | The ownedConstraint of a RequirementConstraintMembership must be composite. | medium |
| `sysml:validateRequirementMembershipOwningType` | The owningType of an ${node.nodeType()} must be a RequirementDefinition or RequirementUsage. | medium |
| `sysml:validateRequirementOnlyOneSubject` | No static message literal found by the inventory script. | low |
| `sysml:validateRequirementSubjectParameterPosition` | No static message literal found by the inventory script. | low |
| `sysml:validateRequirementUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateRequirementVerificationMembershipOwningType` | The owningType of a RequirementVerificationMembership must be a RequirementUsage that is owned by an ObjectiveMembership. | medium |
| `sysml:validateSatisfyRequirementUsageReference` | No static message literal found by the inventory script. | low |
| `sysml:validateSendActionParameters` | No static message literal found by the inventory script. | low |
| `sysml:validateSendActionReceiver` | Sending to a port should be done through | medium |
| `sysml:validateStateParallelSubactions` | Parallel ${type} ${member} must not have any incomingTransitions or outgoingTransitions. | medium |
| `sysml:validateStateSubactionKind` | No static message literal found by the inventory script. | low |
| `sysml:validateStateSubactionMembershipOwningType` | The owningType of a StateSubactionMembership must be a StateDefinition or a StateUsage. | medium |
| `sysml:validateStateUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateSubjectMembershipOwningType` | The owningType of SubjectMembership must be a RequirementDefinition, RequirementUsage, CaseDefinition, or CaseUsage. | medium |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateSysML` | No static message literal found by the inventory script. | low |
| `sysml:validateTransitionFeatureMembership` | TransitionFeature of kind effect must be an ActionUsage. | medium |
| `sysml:validateTransitionFeatureMembership` | TransitionFeature of kind guard must be a boolean expression. | medium |
| `sysml:validateTransitionFeatureMembership` | TransitionFeature of kind trigger must be an AcceptActionUsage. | medium |
| `sysml:validateTransitionFeatureMembershipOwningType` | The owningType of a TransitionFeatureMembership must be a TransitionUsage. | medium |
| `sysml:validateTransitionUsageParameters` | A TransitionUsage must have a transitionLinkSource. | medium |
| `sysml:validateTransitionUsageParameters` | A TransitionUsage with a triggerAction must have a payload. | medium |
| `sysml:validateTransitionUsageSuccession` | A TransitionUsage must have an ownedMember that is a Succession with an ActionUsage as its targetFeature. | medium |
| `sysml:validateTriggerInvocationExpression` | A when expression must be Boolean. | medium |
| `sysml:validateTriggerInvocationExpression` | An after expression must be a DurationValue. | medium |
| `sysml:validateTriggerInvocationExpression` | An at expression must be a TimeInstantValue. | medium |
| `sysml:validateUseCaseUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateVariantMembershipOwningNamespace` | No static message literal found by the inventory script. | low |
| `sysml:validateVariationMembership` | No static message literal found by the inventory script. | low |
| `sysml:validateVariationSpecialization` | No static message literal found by the inventory script. | low |
| `sysml:validateVerificationCaseUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateViewDefinitionOnlyOneViewRendering` | No static message literal found by the inventory script. | low |
| `sysml:validateViewpointUsageTyping` | No static message literal found by the inventory script. | low |
| `sysml:validateViewRenderingMembershipOwningType` | The owningType of an ViewRenderingMembership must be a CaseDefinition or CaseUsage. | medium |
| `sysml:validateViewUsageTyping` | No static message literal found by the inventory script. | low |

</div>
