from dataclasses import dataclass, field, is_dataclass
from typing import List, Optional, Any, Union


# ---- Trial Overview ----
@dataclass
class TrialOverview:
    ctNumber: str
    ctStatus: Optional[str]  # TODO: Decode CT Status
    ctTitle: Optional[str]
    shortTitle: Optional[str]
    conditions: Optional[str]
    decisionDateOverall: Optional[str]
    decisionDate: Optional[str]
    sponsor: Optional[str]
    sponsorType: Optional[str]
    trialPhase: Optional[str]
    endPoint: Optional[str]
    product: Optional[str]
    ageGroup: Optional[str]
    ageRangeSecondary: Optional[str]
    gender: Optional[str]
    trialRegion: Optional[int]
    totalNumberEnrolled: int
    primaryEndPoint: Optional[str]
    resultsFirstReceived: Optional[str]
    endDate: Optional[str]
    endDateEU: Optional[str]
    lastUpdated: Optional[str]
    lastPublicationUpdate: Optional[str]
    startDateEU: Optional[str]
    trialCountries: List[str] = field(default_factory=list)
    therapeuticAreas: List[str] = field(default_factory=list)


# ---- Full Trial ----
@dataclass
class Organisation:
    id: int
    type: str
    typeCode: str
    name: str
    commercial: Optional[bool]
    isBusinessKeyValidated: Optional[bool]
    businessKey: str
    organisationLocationStatus: Optional[str]


@dataclass
class ScientificContact:
    id: int
    type: str
    functionalName: str
    functionalEmailAddress: str
    telephone: str
    organisation: Organisation


@dataclass
class PublicContact:
    id: int
    type: str
    functionalName: str
    functionalEmailAddress: str
    telephone: str
    organisation: Organisation


@dataclass
class Address:
    addressId: int
    oneLine: Optional[str]
    addressLine1: Optional[str]
    addressLine2: Optional[str]
    addressLine3: Optional[str]
    addressLine4: Optional[str]
    city: Optional[str]
    postcode: Optional[str]
    country: Optional[int]
    countryName: Optional[str]


@dataclass
class OrganisationAddress:
    id: int
    organisation: Organisation
    address: Address
    isBusinessKeyValidated: bool
    businessKey: Optional[str]
    email: Optional[str]
    phone: Optional[str]


@dataclass
class SponsorDuty:
    id: int
    code: str
    value: Optional[str]  # Only provided for third parties with duty "other"


@dataclass
class ThirdParty:
    id: int
    organisationAddress: OrganisationAddress
    phoneNumber: str
    email: str
    sponsorDuties: List[SponsorDuty] = field(default_factory=list)


@dataclass
class Sponsor:
    id: int
    primary: bool
    organisation: Organisation
    isCommercial: Optional[bool]
    commercial: str
    article77ComplianceResp: Optional[str]
    contactPointResp: Optional[bool]
    legislationComplianceResp: Optional[str]
    publicContacts: List[PublicContact] = field(default_factory=list)
    scientificContacts: List[ScientificContact] = field(default_factory=list)
    thirdParties: List[ThirdParty] = field(default_factory=list)
    addresses: List[OrganisationAddress] = field(default_factory=list)


@dataclass
class TherapeuticArea:
    code: int
    name: str


@dataclass
class ProductSubstance:
    productPk: Optional[str]
    substancePk: Optional[str]
    nameOrg: Optional[str]
    substanceOrigin: Optional[str]
    actSubstOrigin: Optional[str]
    actSubstName: Optional[str]
    substanceEvCode: Optional[str]
    synonyms: Optional[List[str]]


@dataclass
class ProductDictionaryInfo:
    productPharmForm: Optional[str]
    euMpNumber: str
    pharmForm: Optional[str]
    activeSubstanceName: Optional[str]
    nameOrg: Optional[str]
    activeSubstanceOtherDescriptiveName: str
    sponsorProductCode: Optional[str]
    prodAuthStatus: Optional[int]
    productPk: Optional[str]
    marketingAuthNumber: Optional[str]
    mrpNumber: Optional[str]
    prodName: Optional[str]
    productOtherName: Optional[str]
    authorisationCountryCode: Optional[str]
    sponsorSubstanceCode: Optional[str]
    atcCode: Optional[str]
    atcName: Optional[str]
    atcTermLevel: Optional[str]
    activeSubstanceOtherDescriptiveName: Optional[str]
    productSubstances: Optional[List[ProductSubstance]] = field(default_factory=list)


@dataclass
class Therapy:
    id: Optional[int]
    catReferenceNumber: Optional[str]
    advancedTherapyType: Optional[str]
    cellTypeCode: Optional[str]
    cellTypeMoreInformation: Optional[str]
    cellOriginCode: Optional[str]
    cellOriginSpeciesOfOrigin: Optional[str]
    cellTypeOtherSomatic: Optional[str]
    geneOfInterest: Optional[str]
    description: Optional[str]
    isGmo: Optional[bool]
    geneTransferProductType: Optional[str]
    gmoCellType: Optional[str]


@dataclass
class Device:
    id: Optional[int]
    deviceTypeCode: Optional[str]
    deviceNotifiedBody: Optional[str]
    productUseDeviceCode: Optional[str]
    productUseDeviceUsage: Optional[List[Any]]
    tradeName: Optional[str]
    description: Optional[str]
    hasCeMark: Optional[bool]


@dataclass
class ClinicalTrialStatusHistory:
    id: int
    mscId: int
    trialStatus: str
    trialStatusDate: str


@dataclass
class TrialPeriod:
    id: Optional[int]
    trialStartDate: Optional[str]
    trialEndDate: Optional[str]
    fromDate: Optional[str]
    isBenefitRiskBalanceTemporaryHalt: Optional[bool]
    isBenefitRiskBalanceEndTrail: Optional[bool]
    isTemporaryHalt: Optional[bool]
    isEndTrial: Optional[bool]


@dataclass
class TrialRecruitmentPeriod:
    id: int
    recruitmentStartDate: Optional[str]
    recruitmentEndDate: Optional[str]
    fromDate: str


@dataclass
class MemberStateConcernedInfo:
    id: int
    clinicalTrialId: int
    countryOrganisationId: int
    reportingStatusCode: str
    fromDate: str
    toDate: str
    isProposedRms: bool
    expressDecision: Optional[str]
    countryName: str
    organisationInfo: Optional[dict]
    trialStatus: str
    trialPeriod: Optional[List[TrialPeriod]]
    trialRestartDate: Optional[str]
    trialRecruitmentPeriod: Optional[List[TrialRecruitmentPeriod]]
    hasRecruitmentStarted: bool
    activeTrialPeriod: Optional[dict]
    activeTrialRecruitmentPeriod: Optional[dict]
    isWillingAtDayThreeView: bool
    applicationTypeMsc: str
    mscName: str
    clinicalTrialStatusHistory: List[ClinicalTrialStatusHistory] = field(
        default_factory=list
    )


@dataclass
class Part1MedicinalProductRoleMscInfo:
    memberStateConcernedInfo: MemberStateConcernedInfo
    countryOrganisationId: int


@dataclass
class Product:
    id: int
    productDictionaryInfo: ProductDictionaryInfo
    isPaediatricFormulation: bool
    mpRoleInTrial: str
    productName: Optional[str]
    orphanDrugEdit: Optional[bool]
    orphanDrugDesigNumber: Optional[str]
    doseUom: Optional[str]
    maxDailyDoseAmount: Optional[str]
    doseUomTotal: Optional[str]
    maxTotalDoseAmount: Optional[str]
    maxTreatmentPeriod: Optional[int]
    timeUnitCode: Optional[str]
    evCode: Optional[str]
    miaNumber: Optional[str]
    sponsorProductCodeEdit: Optional[str]
    allSubstancesChemicals: Optional[bool]
    jsonActiveSubstanceNames: Optional[str]
    pharmaceuticalFormDisplay: Optional[str]
    part1MpRoleTypeCode: Optional[str]
    otherMedicinalProduct: Optional[str]
    productChangedRelationMA: Optional[bool]
    productChangeDescription: Optional[str]
    scientificProductEvCode: Optional[str]
    scientificProductPharmEvCode: Optional[str]
    therapies: List[Therapy] = field(default_factory=list)
    devices: List[Device] = field(default_factory=list)
    characteristics: List[str] = field(default_factory=list)
    routes: List[str] = field(default_factory=list)
    part1MedicinalProductRoleMscInfos: Optional[
        List[Part1MedicinalProductRoleMscInfo]
    ] = field(default_factory=list)


@dataclass
class FullTitleTranslation:
    id: Optional[int]
    uuid: Optional[str]
    attributeTranslation: Optional[str]
    language: Optional[int]
    languageDescription: Optional[str]


@dataclass
class PublicTitleTranslation:
    id: Optional[int]
    uuid: Optional[str]
    attributeTranslation: Optional[str]
    language: Optional[int]
    languageDescription: Optional[str]


@dataclass
class AdditionalRegistry:
    id: Optional[int]
    number: Optional[str]
    otherRegistryName: Optional[str]
    ctRegistryCode: Optional[str]


@dataclass
class WhoUniversalTrialNumber:
    id: Optional[int]
    number: Optional[str]


@dataclass
class NctNumber:
    id: Optional[int]
    number: Optional[str] = None


@dataclass
class IsrctnNumber:
    id: Optional[int]
    number: Optional[str]


@dataclass
class SecondaryIdentifyingNumber:
    whoUniversalTrialNumber: Optional[WhoUniversalTrialNumber] = WhoUniversalTrialNumber
    nctNumber: Optional[NctNumber] = NctNumber
    isrctnNumber: Optional[IsrctnNumber] = IsrctnNumber
    additionalRegistries: List[AdditionalRegistry] = field(default_factory=list)


@dataclass
class ClinicalTrialIdentifier:
    fullTitle: Optional[str]
    publicTitle: str
    shortTitle: Optional[str]
    secondaryIdentifyingNumbers: SecondaryIdentifyingNumber
    publicTitleTranslations: List[PublicTitleTranslation] = field(default_factory=list)
    fullTitleTranslations: List[FullTitleTranslation] = field(default_factory=list)


@dataclass
class TrialCategory:
    isLowIntervention: Optional[bool]
    justificationOfLowIntervention: Optional[str]
    trialPhase: str
    trialCategory: str
    justificationForTrialCategory: Optional[str]
    trialCategoryId: int


@dataclass
class MedicalConditionTranslation:
    id: Optional[int]
    uuid: Optional[str]
    attributeTranslation: Optional[str]
    language: Optional[int]
    languageDescription: Optional[str]


@dataclass
class PartIMedicalCondition:
    id: int
    medicalCondition: str
    isConditionRareDisease: bool
    medicalConditionTranslations: List[MedicalConditionTranslation] = field(
        default_factory=list
    )


@dataclass
class MeddraConditionTerm:
    termId: int
    version: str
    level: str
    termName: str
    classificationCode: str
    organClass: int
    active: bool


@dataclass
class MedicalCondition:
    partIMedicalConditions: List[PartIMedicalCondition] = field(default_factory=list)
    meddraConditionTerms: List[MeddraConditionTerm] = field(default_factory=list)


@dataclass
class TrialScope:
    code: str
    trialScopeId: int
    otherDescription: Optional[str]


@dataclass
class MainObjectiveTranslation:
    id: Optional[int]
    uuid: Optional[str]
    attributeTranslation: Optional[str]
    language: Optional[int]
    languageDescription: Optional[str]


@dataclass
class SecondaryObjectiveTranslation:
    id: Optional[int]
    uuid: Optional[str]
    attributeTranslation: Optional[str]
    language: Optional[int]
    languageDescription: Optional[str]


@dataclass
class SecondaryObjective:
    id: int
    number: int
    secondaryObjective: str
    secondaryObjectiveTranslations: List[SecondaryObjectiveTranslation] = field(
        default_factory=list
    )


@dataclass
class TrialObjective:
    mainObjective: str
    trialScopes: List[TrialScope] = field(default_factory=list)
    mainObjectiveTranslations: List[MainObjectiveTranslation] = field(
        default_factory=list
    )
    secondaryObjectives: List[SecondaryObjective] = field(default_factory=list)


@dataclass
class PrincipalInclusionCriteriaTranslations:
    id: Optional[int]
    uuid: Optional[str]
    attributeTranslation: Optional[str]
    language: Optional[int]
    languageDescription: Optional[str]


@dataclass
class PrincipalInclusionCriteria:
    id: int
    number: int
    principalInclusionCriteria: str
    principalInclusionCriteriaTranslations: List[
        PrincipalInclusionCriteriaTranslations
    ] = field(default_factory=list)


@dataclass
class PrincipalExclusionCriteriaTranslation:
    id: Optional[int]
    uuid: Optional[str]
    attributeTranslation: Optional[str]
    language: Optional[int]
    languageDescription: Optional[str]


@dataclass
class PrincipalExclusionCriteria:
    id: int
    number: int
    principalExclusionCriteria: str
    principalExclusionCriteriaTranslations: List[
        PrincipalExclusionCriteriaTranslation
    ] = field(default_factory=list)


@dataclass
class EligibilityCriteria:
    principalInclusionCriteria: List[PrincipalInclusionCriteria] = field(
        default_factory=list
    )
    principalExclusionCriteria: List[PrincipalExclusionCriteria] = field(
        default_factory=list
    )


@dataclass
class EndPointTranslation:
    id: Optional[int]
    uuid: Optional[str]
    attributeTranslation: Optional[str]
    language: Optional[int]
    languageDescription: Optional[str]


@dataclass
class PrimaryEndPoint:
    id: int
    number: int
    endPoint: str
    isPrimary: bool
    endPointTranslations: List[EndPointTranslation] = field(default_factory=list)


@dataclass
class SecondaryEndPoint:
    id: int
    number: int
    endPoint: str
    isPrimary: bool
    endPointTranslations: List[EndPointTranslation] = field(default_factory=list)


@dataclass
class EndPoint:
    primaryEndPoints: List[PrimaryEndPoint] = field(default_factory=list)
    secondaryEndPoints: List[SecondaryEndPoint] = field(default_factory=list)


@dataclass
class TrialDuration:
    estimatedEndDate: str
    estimatedGlobalEndDate: Optional[str]
    estimatedRecruitmentStartDate: str


@dataclass
class AgeRange:
    id: int
    ageRangeCategoryCode: str
    ageRangeCategory: str


@dataclass
class AgeRangeSecondaryId:
    id: int
    ageRangeCategoryCode: str
    ctAgeRangeCode: str
    ageRangeCategory: str
    ctAgeRange: str


@dataclass
class ClinicalTrialGroup:
    code: str
    name: str


@dataclass
class PopulationOfTrialSubjects:
    isFemaleSubjects: bool
    isMaleSubjects: bool
    isVulnerablePopulationSelected: bool
    ageRanges: List[AgeRange] = field(default_factory=list)
    ageRangeSecondaryIds: List[AgeRangeSecondaryId] = field(default_factory=list)
    clinicalTrialGroups: List[ClinicalTrialGroup] = field(default_factory=list)


@dataclass
class MonetarySupport:
    id: Optional[int]
    organisationName: Optional[int]


@dataclass
class TrialInformation:
    trialCategory: TrialCategory
    medicalCondition: MedicalCondition
    trialObjective: Optional[TrialObjective]
    eligibilityCriteria: Optional[EligibilityCriteria]
    endPoint: Optional[EndPoint]
    trialDuration: TrialDuration
    populationOfTrialSubjects: PopulationOfTrialSubjects
    individualParticipantData: Optional[dict]
    sourceOfMonetarySupport: List[MonetarySupport] = field(default_factory=list)


@dataclass
class CompetentAuthority:
    id: int
    organisation: Organisation
    address: Address
    phone: Optional[str]
    email: Optional[str]
    isBusinessKeyValidated: bool
    businessKey: str


@dataclass
class ScientificAdvice:
    id: int
    competentAuthority: CompetentAuthority


@dataclass
class ScientificAdviceAndPip:
    scientificAdvices: List[ScientificAdvice] = field(default_factory=list)
    paediatricInvestigationPlan: List = field(default_factory=list)


@dataclass
class AssociatedClinicalTrial:
    id: int
    ctNumber: str
    sponsorName: Optional[str]
    fullTitle: Optional[str]
    sponsorAgreementOption: str
    sponsorAgreementOptionName: str
    parentClinicalTrialId: Optional[str]
    hasDocument: bool
    associatedCtDocs: List = field(default_factory=list)


@dataclass
class TrialDetails:
    clinicalTrialIdentifiers: ClinicalTrialIdentifier
    trialInformation: TrialInformation
    protocolInformation: Optional[dict]
    scientificAdviceAndPip: Optional[ScientificAdviceAndPip]
    associatedClinicalTrials: List[AssociatedClinicalTrial] = field(
        default_factory=list
    )
    references: List = field(default_factory=list)
    pubmedCode: List = field(default_factory=list)
    pubmedUrl: List = field(default_factory=list)


@dataclass
class PartOneTherapeuticArea:
    id: int
    therapeuticArea: TherapeuticArea


@dataclass
class ProductRoleGroupInfo:
    id: int
    comments: Optional[str]
    miaNumber: Optional[str]
    reasonNoAmp: Optional[str]
    productRoleCode: str
    productRoleName: str
    products: List[Product] = field(default_factory=list)


@dataclass
class CountriesInfo:
    eutctId: Optional[str]
    name: Optional[str]
    isoNumber: Optional[int]
    isoAlpha2Code: Optional[str]
    isoAlpha3Code: Optional[str]
    current: Optional[str]


@dataclass
class AuthorizedPartI:
    id: int
    rowSubjectCount: Optional[int]
    trialDetails: TrialDetails
    assessmentOutcome: Optional[str]
    assessmentOutcomeDate: Optional[str]
    conclusionDate: Optional[str]
    trialCategoryCode: str
    trialCategoryJustificationComment: Optional[str]
    isLowIntervention: Optional[bool]
    parentPartIId: Optional[int]
    rowCountriesInfo: Optional[List[CountriesInfo]] = field(default_factory=list)
    products: List[Product] = field(default_factory=list)
    therapeuticAreas: List[TherapeuticArea] = field(default_factory=list)
    medicalConditions: List[PartIMedicalCondition] = field(default_factory=list)
    sponsors: List[Sponsor] = field(default_factory=list)
    partOneTherapeuticAreas: List[PartOneTherapeuticArea] = field(default_factory=list)
    productRoleGroupInfos: List[ProductRoleGroupInfo] = field(default_factory=list)


@dataclass
class ActiveTrialRecruitmentPeriod:
    recruitmentStartDate: Optional[str]
    recruitmentEndDate: Optional[str]


@dataclass
class MscInfo:
    id: int
    clinicalTrialId: int
    countryOrganisationId: int
    reportingStatusCode: str
    fromDate: str
    toDate: str
    isProposedRms: bool
    expressDecision: Optional[str]
    countryName: str
    organisationInfo: dict
    firstDecisionDate: str
    revertedDecision: Optional[str]
    revertedDecisionDate: Optional[str]
    trialStatus: str
    hasRecruitmentStarted: bool
    activeTrialPeriod: TrialPeriod
    activeTrialRecruitmentPeriod: ActiveTrialRecruitmentPeriod
    isWillingAtDayThreeView: bool
    applicationTypeMsc: str
    mscName: str
    trialRestartDate: Optional[str]
    decision: Optional[str]
    decisionDate: Optional[str]
    recruitmentRestartDate: Optional[str]
    assessmentOutcome: Optional[str]
    assessmentOutcomeDate: Optional[str]
    trialPeriod: List[TrialPeriod] = field(default_factory=list)
    trialRecruitmentPeriod: List[TrialRecruitmentPeriod] = field(default_factory=list)
    clinicalTrialStatusHistory: List[ClinicalTrialStatusHistory] = field(
        default_factory=list
    )


@dataclass
class OrganisationAddressInfo:
    id: int
    organisation: Organisation
    address: Address
    phone: Optional[str]
    email: Optional[str]
    isBusinessKeyValidated: Optional[bool]
    businessKey: Optional[str]


@dataclass
class PersonInfo:
    id: int
    firstName: str
    lastName: str
    telephone: str
    email: str
    title: Optional[str]


@dataclass
class TrialSite:
    id: int
    organisationAddressInfo: OrganisationAddressInfo
    personInfo: PersonInfo
    departmentName: str


@dataclass
class AuthorizedPartII:
    id: int
    mscId: int
    mscInfo: MscInfo
    decisionDate: str
    recruitmentSubjectCount: Optional[int]
    applicationStatusCode: str
    trialSites: List[TrialSite] = field(default_factory=list)


@dataclass
class PartIInfo:
    assessmentOutcome: Optional[str]
    assessmentOutcomeDate: Optional[str]


@dataclass
class MscShortInfo:
    id: int
    mscName: str
    countryOrganisationId: int
    assessmentOutcome: Optional[str]
    assessmentOutcomeDate: Optional[str]
    decision: Optional[str]
    decisionDate: Optional[str]
    reportingStatusCode: str
    countryName: str
    trialStatus: str
    firstDecisionDate: Optional[str]


@dataclass
class PartIIInfo:
    id: int
    mscId: int
    mscInfo: MscShortInfo
    applicationStatusCode: str


@dataclass
class MscByApplication:
    id: int
    mscName: str
    reportingStatusCode: str


@dataclass
class Decision:
    id: int
    applicationId: int
    mscId: Optional[int]
    mscName: Optional[str]
    decisionDate: str
    decision: str
    justification: Optional[str]
    assessmentOutcome: Optional[str]
    eventType: str
    part2Id: Optional[int]
    part1Id: Optional[int]
    applicationType: str
    isRMS: bool


@dataclass
class ProductRoleGroupDocument:
    documentUuid: Optional[str]
    productRoleGroupId: Optional[int]


@dataclass
class ApplicationInfo:
    id: int
    type: str
    status: str
    ctNumber: str
    trialStatus: str
    submissionDate: str
    partI: PartIInfo
    decisionDate: Optional[str]
    businessKey: str
    modScope: Optional[str]
    allPartTwosOutOfScope: Optional[bool]
    applicationTrialDecisionByMsc: dict
    ctMSCsByApplication: List[MscByApplication] = field(default_factory=list)
    partIIInfo: List[PartIIInfo] = field(default_factory=list)
    decisions: List[Decision] = field(default_factory=list)
    productRoleGroupDocument: Optional[List[ProductRoleGroupDocument]] = field(
        default_factory=list
    )


@dataclass
class MemberStateConcerned:
    mscName: str
    mscId: int
    firstDecisionDate: str
    lastDecisionDate: str
    mscPublicStatusCode: Optional[int]


@dataclass
class EudraCt:
    isTransitioned: Optional[bool]
    eudraCtCode: Optional[str]


@dataclass
class AuthorizedApplication:
    authorizedPartI: AuthorizedPartI
    eudraCt: EudraCt
    authorizedPartsII: List[AuthorizedPartII] = field(default_factory=list)
    applicationInfo: List[ApplicationInfo] = field(default_factory=list)
    trialGlobalEnd: List = field(default_factory=list)
    memberStatesConcerned: List[MemberStateConcerned] = field(default_factory=list)


@dataclass
class SubEvent:
    notificationType: str
    date: str


@dataclass
class EarlyTerminationReason:
    code: Optional[str]
    name: Optional[str]
    isLateCandidate: Optional[bool]


@dataclass
class TrialEvent:
    mscId: int
    mscName: str
    earlyTerminationReason: Optional[EarlyTerminationReason]
    events: List[SubEvent] = field(default_factory=list)


@dataclass
class UnexpectedEvent:
    pass


@dataclass
class SeriousBreachSite:
    organisationAddressInfo: OrganisationAddressInfo
    otherTypeOfOrganization: Optional[str]
    organisationType: Optional[List[str]] = field(default_factory=list)


@dataclass
class SeriousBreachCategory:
    id: Optional[int]
    name: Optional[str]


@dataclass
class SeriousBreach:
    sponsorBusinessKey: Optional[str]
    businessKey: Optional[str]
    awareDate: Optional[str]
    breachDate: Optional[str]
    submissionDate: Optional[str]
    updatedOn: Optional[str]
    description: Optional[str]
    actionsTaken: Optional[str]
    isBenefitRiskBalanceChanged: Optional[bool]
    mscs: Optional[List[str]]
    countryList: Optional[List[CountriesInfo]] = field(default_factory=list)
    impactedAreaList: Optional[List[str]] = field(default_factory=list)
    seriousBreachSites: Optional[List[SeriousBreachSite]] = field(default_factory=list)
    categories: Optional[List[SeriousBreachCategory]] = field(default_factory=list)


@dataclass
class UrgentSafetyMeasure:
    pass


@dataclass
class HaltReason:
    code: Optional[str]
    name: Optional[str]
    isSmRequiredForRestart: Optional[bool]
    isCommentRequired: Optional[bool]


@dataclass
class TemporaryHalt:
    mscId: Optional[int]
    businessKey: Optional[str]
    haltDate: Optional[str]
    plannedRestartDate: Optional[str]
    reasonList: Optional[List[HaltReason]]
    isTreatmentStopped: Optional[bool]
    sponsorJustificationComment: Optional[str]
    bnftRskBalanceChngJstfctn: Optional[str]
    isBenefitRiskBalanceChange: Optional[bool]
    submitDate: Optional[str]
    subjectFuMeasuresComment: Optional[str]
    isPublished: Optional[bool]
    updatedOn: Optional[str]
    subjectsStillReceivingTreatment: Optional[int]
    mscList: Optional[List[dict]]


@dataclass
class Events:
    trialGlobalEndDate: Optional[str]
    temporaryHaltList: List[TemporaryHalt] = field(default_factory=list)
    trialEvents: List[TrialEvent] = field(default_factory=list)
    unexpectedEvents: List[UnexpectedEvent] = field(default_factory=list)
    seriousBreaches: List[SeriousBreach] = field(default_factory=list)
    urgentSafetyMeasures: List[UrgentSafetyMeasure] = field(default_factory=list)


@dataclass
class Document:
    title: Optional[str]
    uuid: Optional[str]
    documentType: Optional[str]
    documentTypeLabel: Optional[str]
    fileType: Optional[str]
    associatedEntityId: Optional[str]
    manualVersion: Optional[str]
    systemVersion: Optional[str]


@dataclass
class FullTrial:
    ctNumber: str
    ctStatus: str
    startDateEU: Optional[str]
    endDateEU: Optional[str]
    decisionDate: str
    publishDate: str
    ctPublicStatusCode: int
    authorizedApplication: AuthorizedApplication
    events: Events
    trialRegion: Optional[str]
    trialRegionCode: Optional[int]
    results: dict = field(default_factory=dict)
    documents: List[Document] = field(default_factory=list)
    correctiveMeasures: List = field(default_factory=list)
