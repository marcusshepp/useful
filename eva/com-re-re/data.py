from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import IntEnum


@dataclass
class TrackableEntity:
    Id: int = 0
    CreatedBy: str = ""
    Created: datetime = field(default_factory=datetime.now)
    ModifiedBy: str = ""
    Modified: datetime = field(default_factory=datetime.now)


@dataclass
class CommitteeReport(TrackableEntity):
    SessionId: int = 0
    CommitteeId: int = 0
    MeetingId: int = 0
    CommitteeName: str = ""
    MeetingDate: datetime = field(default_factory=lambda: datetime(1900, 1, 1))
    MeetingTime: str = ""
    MeetingLocation: str = ""
    IsPublished: bool = False
    PublishedDate: Optional[datetime] = None
    PublishedBy: str = ""
    IsAttendancePublished: bool = False
    AttendancePublishedDate: Optional[datetime] = None
    AddendaDate: Optional[datetime] = None
    AttendancePublishedBy: str = ""
    PublishedReportDocument: Optional[bytes] = None
    PublishedAttendanceReportDocument: Optional[bytes] = None
    AgendaItems: List["CommitteeReportAgendaItem"] = field(default_factory=list)


@dataclass
class CommitteeReportAgendaItem(TrackableEntity):
    ReportId: int = 0
    CommitteeMeetingAgendaItemId: Optional[int] = None
    LegislationId: Optional[int] = None
    Prefix: str = ""
    Identifier: str = ""
    Description: str = ""
    SortOrder: int = 0
    IsPublished: bool = False
    IsRemoved: bool = False
    Report: Optional[CommitteeReport] = None
    Actions: List["CommitteeReportAction"] = field(default_factory=list)
    RollCalls: List["CommitteeReportRollCall"] = field(default_factory=list)


class COMMITTEE_ACTION_IDS(IntEnum):
    BILLPASS = 1
    SUB = 2
    IMMEDIATE_EFFECT = 3
    WHOLE = 4
    REFERRED = 5
    JR_ADOPTED = 6
    RES_ADOPTED = 7
    CR_ADOPTED = 8
    SUB_JR_ADOPTED = 9
    SUB_RES_ADOPTED = 10
    AMEND_JR_ADOPTED = 11
    AMEND_RES_ADOPTED = 12
    AMEND_CONRES_ADOPTED = 13
    RES_PLACED_RES = 14
    CONRES_PLACED_RES = 15
    RES_AND_SUB_PLACED_RES = 16
    CONRES_AND_SUB_PLACED_RES = 17
    JRES_COTW = 18
    JRES_AND_SUB_COTW = 19
    BILL_COTW = 20
    JRES_AND_AMEND_COTW = 21


class COMMITTEE_ACTION_DESCRIPTIONS:
    BILLPASS = "With recommendation that the bill pass."
    SUB = "With the recommendation that the substitute (<<freeform>>) be adopted and that the bill then pass."
    IMMEDIATE_EFFECT = "The committee further recommends that the bill be given immediate effect."
    WHOLE = "The bill was referred to the Committee of the Whole."
    REFERRED = "The bill and the substitute recommended by the committee were referred to the Committee of the Whole."
    JR_ADOPTED = "With the recommendation that the joint resolution be adopted."
    RES_ADOPTED = "With the recommendation that the resolution be adopted."
    CR_ADOPTED = "With the recommendation that the concurrent resolution be adopted."
    SUB_JR_ADOPTED = "With the recommendation that the substitute (<<freeform>>) be adopted and that the joint resolution be adopted."
    SUB_RES_ADOPTED = "With the recommendation that the substitute (<<freeform>>) be adopted and that the resolution be adopted."
    AMEND_JR_ADOPTED = "With the recommendation that the following amendment(s) be adopted and that the joint resolution be adopted."
    AMEND_RES_ADOPTED = "With the recommendation that the following amendment(s) be adopted and that the resolution be adopted"
    AMEND_CONRES_ADOPTED = "With the recommendation that the following amendment(s) be adopted and that the concurrent resolution be adopted"
    RES_PLACED_RES = "The resolution was placed on the order of Resolutions."
    CONRES_PLACED_RES = "The concurrent resolution was placed on the order of Resolutions."
    RES_AND_SUB_PLACED_RES = "The resolution and substitute recommended by the Committee were placed on the order of Resolutions."
    CONRES_AND_SUB_PLACED_RES = "The concurrent resolution and substitute recommended by the Committee were placed on the order of Resolutions."
    JRES_COTW = "The joint resolution was referred to the Committee of the Whole."
    JRES_AND_SUB_COTW = "The joint resolution and substitute recommended by the Committee were referred to the Committee of the Whole."
    BILL_COTW = "The bill and the amendment(s) recommended by the committee were referred to the Committee of the Whole."
    JRES_AND_AMEND_COTW = "The joint resolution and the amendment(s) recommended by the committee were referred to the Committee of the Whole."


@dataclass
class CommitteeReportCommitteeAction:
    Id: int = 0
    Description: str = ""
    IsRecommendation: bool = False


@dataclass
class CommitteeReportAction(TrackableEntity):
    AgendaItemId: int = 0
    CommitteeReportAgendaItemActionId: Optional[int] = None
    ActionText: str = ""
    ActionSubText: str = ""
    SortOrder: int = 0
    IsRecommendation: bool = False
    CustomRecommendationText: str = ""
    CustomReportOutText: str = ""
    IsPublished: bool = False
    AgendaItem: Optional[CommitteeReportAgendaItem] = None
    CommitteeReportAgendaItemAction: Optional[CommitteeReportCommitteeAction] = None


class RollCallVoteTypes:
    YAY = "Yea"
    NAY = "Nay"
    PASS = "Pass"
    NA = "N/A"


@dataclass
class CommitteeReportRollCall(TrackableEntity):
    SessionId: int = 0
    CommitteeId: int = 0
    MeetingId: int = 0
    MemberId: int = 0
    AgendaItemId: int = 0
    RollCallVote: str = ""
    PublishedDate: Optional[datetime] = None
    AddendaDate: Optional[datetime] = None
    PublishedBy: str = ""
    AgendaItem: Optional[CommitteeReportAgendaItem] = None


@dataclass
class CommitteeReportAttendance(TrackableEntity):
    ReportId: int = 0
    MemberId: int = 0
    MemberName: str = ""
    AttendanceTypeId: int = 0


@dataclass
class CommitteeReportJointCommittee(TrackableEntity):
    ReportId: int = 0
    JointCommitteeId: int = 0
    JointCommitteeName: str = ""


def to_dict(obj) -> Dict:
    """Convert a dataclass instance to a dictionary, excluding None values and relationship objects."""
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for key, _ in obj.__dataclass_fields__.items():
            value = getattr(obj, key)
            # Skip None values
            if value is None:
                continue
            # Skip relationship objects
            if key in ["Report", "AgendaItem", "CommitteeReportAgendaItemAction", "AgendaItems", "Actions", "RollCalls"]:
                continue
            # Handle datetime objects
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            # Handle list of objects
            elif isinstance(value, list):
                result[key] = [to_dict(item) if hasattr(item, "__dataclass_fields__") else item for item in value]
            # Handle regular values
            else:
                result[key] = value
        return result
    return obj


def from_dict(cls, data: Dict) -> Any:
    """Create an instance of a dataclass from a dictionary."""
    if not data:
        return None
        
    # Filter out keys that are not fields in the dataclass
    field_names = set(cls.__dataclass_fields__.keys())
    filtered_data = {k: v for k, v in data.items() if k in field_names}
    
    # Handle datetime fields
    for key, value in filtered_data.items():
        field_type = cls.__dataclass_fields__[key].type
        if isinstance(value, str) and "datetime" in str(field_type):
            try:
                filtered_data[key] = datetime.fromisoformat(value)
            except ValueError:
                filtered_data[key] = None
    
    return cls(**filtered_data)
