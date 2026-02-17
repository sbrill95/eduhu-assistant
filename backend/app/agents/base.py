"""Base classes for material sub-agents."""

import logging
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext

logger = logging.getLogger(__name__)


@dataclass
class BaseMaterialDeps:
    """Common dependencies for all material sub-agents.
    
    Every sub-agent inherits from this to ensure consistent access to:
    - teacher_id: For DB lookups (knowledge, preferences, curriculum)
    - conversation_id: For get_conversation_context tool
    - fach: For filtering knowledge and curriculum
    - wissenskarte: Compact summary injected into system prompt
    - teacher_context: Profile + memories block
    """
    teacher_id: str
    conversation_id: str = ""
    fach: str = ""
    wissenskarte: str = ""
    teacher_context: str = ""


class ClarificationNeededError(Exception):
    """Raised by sub-agents when they need clarification from the teacher.
    
    The material_router catches this, saves agent state, and returns
    the question to the main agent for relay to the user.
    """
    def __init__(self, question: str, options: list[str] | None = None, message_history: list | None = None):
        self.question = question
        self.options = options
        self.message_history = message_history or []
        super().__init__(question)


def register_ask_teacher_tool(agent: Agent) -> None:
    """Register the ask_teacher tool on any material sub-agent.
    
    This tool allows the agent to ask clarifying questions when:
    - There's a CONTRADICTION in the request
    - A CRITICAL decision can't be derived from available context
    
    It raises ClarificationNeededError which the router catches.
    """

    @agent.tool
    async def ask_teacher(
        ctx: RunContext[BaseMaterialDeps],
        question: str,
        options: list[str] | None = None,
    ) -> str:
        """Stelle eine Rückfrage an die Lehrkraft.
        
        NUR nutzen wenn:
        - Ein WIDERSPRUCH vorliegt (z.B. "45 Min aber 10 komplexe Aufgaben")
        - Eine KRITISCHE Entscheidung ansteht die du NICHT aus Tools/Kontext ableiten kannst
        
        NICHT nutzen für:
        - Stil-Fragen, Format-Fragen → entscheide selbst
        - Infos die du per Tool finden könntest → nutze erst search_curriculum / get_teacher_preferences
        
        question: Die konkrete Frage an die Lehrkraft (1-2 Sätze, deutsch)
        options: Optionale Multiple-Choice-Antworten. Nutze bei Oder-Fragen!
                 Beispiel: ["30/40/30 (Standard)", "25/50/25 (Transfer-Schwerpunkt)", "Andere Verteilung"]
                 Die letzte Option sollte immer eine Freitext-Alternative sein ("Andere...", "Eigene Angabe").
        """
        logger.info(f"Sub-agent asks teacher: {question} (options: {options})")
        msg_history = []
        try:
            if hasattr(ctx, '_result') and hasattr(ctx._result, 'all_messages'):
                msg_history = ctx._result.all_messages()
        except Exception:
            pass
        raise ClarificationNeededError(
            question=question,
            options=options,
            message_history=msg_history,
        )
