import uuid

from sqlalchemy import select

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.prompts.contrarian import CONTRARIAN_SYSTEM_PROMPT, WHAT_IF_WRONG_SYSTEM_PROMPT
from app.db.session import async_session
from app.models.article import Article
from app.models.dossier import DossierEvent
from app.services.claude import claude_service


class ContrarianAgent(BaseAgent):
    """Mines counter-narratives, scores credibility, builds 'What If I'm Wrong' arguments."""

    name = "contrarian"

    async def execute(self, context: AgentContext) -> AgentResult:
        dossier_id = context.dossier_id
        self.logger.info("contrarian.start", dossier_id=dossier_id)

        if not dossier_id:
            return AgentResult(
                agent_name=self.name, success=False, error="No dossier_id provided"
            )

        async with async_session() as db:
            # Load events and articles
            events_result = await db.execute(
                select(DossierEvent)
                .where(DossierEvent.dossier_id == uuid.UUID(dossier_id))
                .order_by(DossierEvent.occurred_at.desc())
                .limit(20)
            )
            events = events_result.scalars().all()

            articles_result = await db.execute(
                select(Article)
                .where(Article.dossier_id == uuid.UUID(dossier_id))
                .order_by(Article.published_at.desc())
                .limit(15)
            )
            articles = articles_result.scalars().all()

        # Also check parent results for fresh data
        synthesis_data = context.parent_results.get("synthesis")
        if synthesis_data and synthesis_data.success:
            events_from_synthesis = synthesis_data.data.get("timeline_events", [])
        else:
            events_from_synthesis = [
                {"title": e.title, "summary": e.summary, "event_type": e.event_type}
                for e in events
            ]

        article_snippets = [
            f"[{a.published_at.strftime('%Y-%m-%d') if a.published_at else '?'}] {a.title}: {a.content[:400]}"
            for a in articles
        ]

        # Phase 1: Build consensus vs contrarian analysis
        contrarian_analysis = await self._analyze_contrarian(
            events_from_synthesis, article_snippets, context.query or ""
        )

        # Phase 2: Build "What If I'm Wrong" argument
        user_perspective = context.data.get("perspective", {})
        what_if_wrong = await self._build_what_if_wrong(
            events_from_synthesis, article_snippets, context.query or "", user_perspective
        )

        self.logger.info("contrarian.complete")

        return AgentResult(
            agent_name=self.name,
            success=True,
            data={
                "consensus": contrarian_analysis.get("consensus"),
                "contrarian_view": contrarian_analysis.get("contrarian_view"),
                "evidence_comparison": contrarian_analysis.get("evidence_comparison"),
                "unresolved_questions": contrarian_analysis.get("unresolved_questions", []),
                "confidence_scores": contrarian_analysis.get("confidence_scores"),
                "what_if_wrong": what_if_wrong,
            },
        )

    async def _analyze_contrarian(
        self, events: list[dict], article_snippets: list[str], query: str
    ) -> dict:
        """Build consensus vs contrarian analysis."""
        events_text = "\n".join(
            f"- {e.get('title', '')}: {e.get('summary', '')}" for e in events[:15]
        )
        articles_text = "\n\n".join(article_snippets[:10])

        prompt = f"""Story: "{query}"

Key events:
{events_text}

Recent article excerpts:
{articles_text}

Analyze the narrative landscape and produce:

1. consensus: {{
    summary: "the dominant narrative in 2-3 sentences",
    key_evidence: ["list of evidence points supporting consensus"],
    proponents: ["analysts, institutions, or media voices supporting this view"],
    confidence: float (0-1, how well-supported is this view?)
}}

2. contrarian_view: {{
    summary: "the strongest credible counter-narrative in 2-3 sentences",
    key_evidence: ["list of evidence points supporting contrarian view"],
    proponents: ["credible sources backing this view"],
    confidence: float (0-1, how credible is this counter-view?),
    source_quality: "high/medium/low — based on track record and evidence depth"
}}

3. evidence_comparison: [
    {{point: "specific data point", supports: "consensus or contrarian", strength: "strong/moderate/weak"}}
]

4. unresolved_questions: ["questions neither side has adequately answered"]

5. confidence_scores: {{
    consensus_confidence: float,
    contrarian_confidence: float,
    verdict: "consensus strong/contrarian credible/too close to call"
}}

If no credible contrarian view exists, say so honestly.
Return as JSON."""

        try:
            return await claude_service.complete_json(
                system_prompt=CONTRARIAN_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
            )
        except Exception as e:
            self.logger.error("contrarian.analysis.error", error=str(e))
            return {
                "consensus": {"summary": "Analysis unavailable", "confidence": 0},
                "contrarian_view": None,
                "unresolved_questions": [],
            }

    async def _build_what_if_wrong(
        self, events: list[dict], article_snippets: list[str], query: str, perspective: dict
    ) -> dict:
        """Build 'What If I'm Wrong' self-interrogation argument."""
        events_text = "\n".join(
            f"- {e.get('title', '')}: {e.get('summary', '')}" for e in events[:10]
        )

        # Infer user stance from perspective
        stance_description = "neutral"
        if perspective:
            sentiment = perspective.get("sentiment", 0.5)
            if sentiment > 0.6:
                stance_description = "bullish / optimistic about the outcome"
            elif sentiment < 0.4:
                stance_description = "bearish / pessimistic about the outcome"

            stakeholder = perspective.get("stakeholder", "investor")
            stance_description += f" (viewing as {stakeholder})"

        prompt = f"""Story: "{query}"

User's apparent stance: {stance_description}

Key events:
{events_text}

Recent coverage:
{chr(10).join(article_snippets[:8])}

The user is following this story. Build the strongest possible case AGAINST their apparent position.

Return JSON with:
1. inferred_position: "Your apparent view: [what we think they believe]"
2. counter_argument: "The strongest case against it: [2-3 paragraph argument]"
3. overlooked_evidence: ["Evidence you may be overlooking: [specific data points]"]
4. historical_caution: "Historical caution: [similar situations where this view was wrong, with specific examples]"
5. key_question: "The question to ask yourself: [the single most important unresolved question]"
6. confidence_in_counter: float (0-1, how strong is the counter-case?)"""

        try:
            return await claude_service.complete_json(
                system_prompt=WHAT_IF_WRONG_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
            )
        except Exception as e:
            self.logger.error("contrarian.what_if_wrong.error", error=str(e))
            return {
                "inferred_position": "Unable to determine your position",
                "counter_argument": "Self-interrogation unavailable",
                "overlooked_evidence": [],
                "historical_caution": "",
                "key_question": "",
            }
