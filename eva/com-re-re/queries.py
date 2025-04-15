from typing import Set

# Committee Reports Query
def get_committee_reports_query() -> str:
    return """
SELECT 
    cr.Id,
    cr.SessionId,
    cr.CommitteeId,
    cr.MeetingId,
    cr.IsPublished,
    cr.PublishedDate,
    cr.AddendaDate,
    cr.PublishedBy,
    cr.AttendancePublishedBy,
    cr.IsAttendancePublished,
    cr.PublishedReportDocument,
    cr.PublishedAttendanceReportDocument,
    cr.AttendancePublishedDate,
    cr.CreatedBy,
    cr.Created,
    cr.Modified,
    cr.ModifiedBy
FROM CommitteeReports cr
    """

# Removed Agenda Items Query
def get_removed_agenda_items_query() -> str:
    return """
SELECT [MeetingId]
      ,[AgendaItemId]
FROM [dbo].[CommitteeReportRemovedAgendaItems]
    """

# Agenda Items Query
def get_agenda_items_query(meeting_ids_string: str, removed_agenda_item_ids_string: str) -> str:
    query = f"""
SELECT [CommitteeMeetingAgendaItemID]
      ,[SessionID]
      ,[CommitteeMeetingID]
      ,[LegislationID]
      ,[Description]
      ,[SortOrder]
      ,[IsActive]
      ,[DateAdded]
      ,[LastModified]
      ,[LastModifiedBy]
      ,[IsPublic]
FROM [dbo].[CommitteeMeetingAgendaItem]
WHERE 
    [IsActive] = 1 
    AND [CommitteeMeetingID] IN ({meeting_ids_string}) 
    """
    if removed_agenda_item_ids_string and len(removed_agenda_item_ids_string) > 0:
        query += f"AND [CommitteeMeetingAgendaItemID] NOT IN ({removed_agenda_item_ids_string})"
    return query

# Meeting Committee Info Query
def get_meeting_committee_info_query(meeting_ids_string: str) -> str:
    return f"""
SELECT m.CommitteeMeetingID, m.MeetingLocation, c.CommitteeID, c.CommitteeName 
FROM Committee c
INNER JOIN CommitteeMeetingCommittee cmc ON cmc.CommitteeID = c.CommitteeID
INNER JOIN CommitteeMeeting m ON m.CommitteeMeetingID = cmc.CommitteeMeetingID
WHERE m.CommitteeMeetingID IN ({meeting_ids_string})
    """

# Action to Agenda Items Query
def get_action_to_agenda_items_query() -> str:
    return """
SELECT [Id]
    ,[CommitteeReportCommitteeActionId]
    ,[AgendaItemId]
    ,[CustomRecommendedAction]
    ,[CustomReportOutAction]
    ,[MeetingId]
    ,[SortOrder]
    ,[Sub]
FROM [dbo].[CommitteeReportCommitteeActionToAgendaItems]
    """

# Published Items Query
def get_published_items_query() -> str:
    return """
SELECT [Id]
    ,[MeetingId]
    ,[AgendaItemId]
    ,[CreatedBy]
    ,[Created]
    ,[Modified]
    ,[ModifiedBy]
FROM [dbo].[CommitteeReportPublishedItems]
    """

# Published Actions Query
def get_published_actions_query() -> str:
    return """
SELECT [Id]
      ,[CommitteeReportCommitteeActionId]
      ,[AgendaItemId]
      ,[CustomRecommendedAction]
      ,[CustomReportOutAction]
      ,[MeetingId]
      ,[SortOrder]
      ,[Sub]
FROM [dbo].[CommitteeReportPublishedActions]
    """

def get_roll_call_query() -> str:
    return """
SELECT [Id]
      ,[AddendaDate]
      ,[AgendaItemId]
      ,[CommitteeId]
      ,[Created]
      ,[CreatedBy]
      ,[MeetingId]
      ,[MemberId]
      ,[Modified]
      ,[ModifiedBy]
      ,[PublishedBy]
      ,[PublishedDate]
      ,[RoleCallVote]
      ,[SessionId]
  FROM [dbo].[CommitteeMemberRollCalls]
"""

def get_legislation_items_query(legislation_ids: Set[int]) -> str:
    legislation_ids_string = ', '.join(map(str, legislation_ids))
    query: str = f"""
SELECT [LegislationID]
      ,[SessionID]
      ,[ChamberID]
      ,[Prefix]
      ,[Identifier]
      ,[IsPublic]
      ,[DateAdded]
      ,[LastModified]
      ,[LastModifiedBy]
      ,[IsActive]
FROM [dbo].[Legislation]
WHERE [LegislationID] IN ({legislation_ids_string})
"""
    return query

def update_committee_report_query() -> str:
    return """
UPDATE [dbo].[CommitteeReports]
SET
    [MeetingDate] = ?,
    [MeetingTime] = ?,
    [MeetingLocation] = ?
WHERE [Id] = ?;

SELECT SCOPE_IDENTITY() AS Id;
"""

def get_legislation_details_query(legislation_ids_str: str) -> str:
    return f"""
SELECT
    l.[LegislationID],
    l.[Prefix],
    l.[Identifier]
FROM [dbo].[Legislation] l
WHERE l.[LegislationID] IN ({legislation_ids_str})
"""

def get_committee_actions_query() -> str:
    return """
SELECT [Id]
      ,[Description]
      ,[IsRecommendation]
FROM [dbo].[CommitteeReportCommitteeActions]
"""

def get_meeting_details_query() -> str:
    return """
SELECT
    cm.[CommitteeMeetingID],
    cm.[MeetingDate],
    CONVERT(varchar, cm.[MeetingTime], 108) AS MeetingTime,
    cm.[MeetingLocation]
FROM [dbo].[CommitteeMeeting] cm
WHERE cm.[CommitteeMeetingID] = ?
"""

def insert_agenda_item_query() -> str:
    return """
DECLARE @InsertedId INT;

INSERT INTO [dbo].[CommitteeReportAgendaItems]
(
    [ReportId],
    [CommitteeMeetingAgendaItemId],
    [LegislationId],
    [Prefix],
    [Identifier],
    [Description],
    [SortOrder],
    [IsPublished],
    [CreatedBy],
    [Created],
    [Modified],
    [ModifiedBy]
)
VALUES
(
    ?, -- ReportId
    ?, -- CommitteeMeetingAgendaItemId
    ?, -- LegislationId
    ?, -- Prefix
    ?, -- Identifier
    ?, -- Description
    ?, -- SortOrder
    ?, -- IsPublished
    ?, -- CreatedBy
    ?, -- Created
    ?, -- Modified
    ?  -- ModifiedBy
);

SET @InsertedId = SCOPE_IDENTITY();
SELECT @InsertedId AS Id;
"""

def insert_action_query() -> str:
    return """
DECLARE @InsertedId INT;

INSERT INTO [dbo].[CommitteeReportActions]
(
    [AgendaItemId],
    [CommitteeReportAgendaItemActionId],
    [ActionText],
    [ActionSubText],
    [SortOrder],
    [IsRecommendation],
    [CustomRecommendationText],
    [CustomReportOutText],
    [IsPublished],
    [CreatedBy],
    [Created],
    [Modified],
    [ModifiedBy]
)
VALUES
(
    ?, -- AgendaItemId
    ?, -- CommitteeReportAgendaItemActionId
    ?, -- ActionText
    ?, -- ActionSubText
    ?, -- SortOrder
    ?, -- IsRecommendation
    ?, -- CustomRecommendationText
    ?, -- CustomReportOutText
    ?, -- IsPublished
    ?, -- CreatedBy
    ?, -- Created
    ?, -- Modified
    ?  -- ModifiedBy
);

SET @InsertedId = SCOPE_IDENTITY();
SELECT @InsertedId AS Id;
"""

def insert_roll_call_query() -> str:
    return """
DECLARE @InsertedId INT;

INSERT INTO [dbo].[CommitteeReportRollCalls]
(
    [SessionId],
    [CommitteeId],
    [MeetingId],
    [MemberId],
    [AgendaItemId],
    [RollCallVote],
    [PublishedDate],
    [AddendaDate],
    [PublishedBy],
    [CreatedBy],
    [Created],
    [Modified],
    [ModifiedBy]
)
VALUES
(
    ?, -- SessionId
    ?, -- CommitteeId
    ?, -- MeetingId
    ?, -- MemberId
    ?, -- AgendaItemId
    ?, -- RollCallVote
    ?, -- PublishedDate
    ?, -- AddendaDate
    ?, -- PublishedBy
    ?, -- CreatedBy
    ?, -- Created
    ?, -- Modified
    ?  -- ModifiedBy
);

SET @InsertedId = SCOPE_IDENTITY();
SELECT @InsertedId AS Id;
"""

def count_migrated_records_query(table_name: str) -> str:
    return f"""
SELECT COUNT(*) AS Count
FROM [dbo].[{table_name}]
"""
