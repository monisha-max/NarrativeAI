from enum import StrEnum


class EventType(StrEnum):
    CORPORATE = "corporate"
    REGULATORY = "regulatory"
    FINANCIAL = "financial"
    MANAGEMENT = "management"
    MARKET = "market"
    LEGAL = "legal"


class DossierStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class NarrativeVelocity(StrEnum):
    SLOW = "slow"           # < 1 event/month
    MODERATE = "moderate"    # 1-2 events/month
    RAPID = "rapid"          # 1-2 events/week
    CRISIS = "crisis"        # multiple events/day


class UserType(StrEnum):
    STUDENT = "student"
    RETAIL_INVESTOR = "retail_investor"
    FOUNDER = "founder"
    CFO = "cfo"
    POLICY = "policy"
    JOURNALIST = "journalist"


class ArchetypeSlug(StrEnum):
    CORPORATE_GOVERNANCE_COLLAPSE = "corporate-governance-collapse"
    SHORT_ATTACK_PLAYBOOK = "short-attack-playbook"
    REGULATORY_ESCALATION = "regulatory-escalation"
    FOUNDER_VS_BOARD = "founder-vs-board"
    MNA_SAGA = "mna-saga"


EVENT_TYPE_COLORS = {
    EventType.CORPORATE: "#3B82F6",    # blue
    EventType.REGULATORY: "#EF4444",    # red
    EventType.FINANCIAL: "#10B981",     # green
    EventType.MANAGEMENT: "#F97316",    # orange
    EventType.MARKET: "#8B5CF6",        # purple
    EventType.LEGAL: "#6B7280",         # gray
}
