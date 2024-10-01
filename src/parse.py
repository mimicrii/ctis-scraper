from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TrialOverview:
    ctNumber: str
    ctStatus: Optional[str] = None
    ctTitle: Optional[str] = None
    shortTitle: Optional[str] = None
    conditions: Optional[str] = None
    trialCountries: List[str] = field(default_factory=list)
    decisionDateOverall: Optional[str] = None
    decisionDate: Optional[str] = None
    therapeuticAreas: List[str] = field(default_factory=list)
    sponsor: Optional[str] = None
    sponsorType: Optional[str] = None
    trialPhase: Optional[str] = None
    endPoint: Optional[str] = None
    product: Optional[str] = None
    ageGroup: Optional[str] = None
    gender: Optional[str] = None
    trialRegion: Optional[int] = None
    totalNumberEnrolled: int = 0
    primaryEndPoint: Optional[str] = None
    resultsFirstReceived: Optional[str] = None
    lastUpdated: Optional[str] = None
    lastPublicationUpdate: Optional[str] = None
