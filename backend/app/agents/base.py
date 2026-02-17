"""Base classes for material sub-agents."""

from dataclasses import dataclass


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
