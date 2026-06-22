from langchain.agents import AgentState
from pydantic import BaseModel, EmailStr, Field


class FillContactFormInput(BaseModel):
    """Tool input; email comes from agent state (pii_guard), not from the model."""

    message: str = Field(description="Project description or inquiry message")


class ContactFormFields(BaseModel):
    email: EmailStr = Field(description="Contact email address")
    message: str = Field(description="Project description or inquiry message")


class CaseStudyIntent(BaseModel):
    domain: str | None = Field(
        default=None,
        description=(
            "Industry or business domain from the case study catalog when the user implies one; "
            "when set, use exactly one label returned by get_domains_tool."
        ),
    )
    tech_stack: list[str] | None = Field(
        default=None,
        description=(
            "List of primary tech stack keywords. If multiple are given, the first two are used. Put the main tech stack items"
        ),
    )


class CustomAgentState(AgentState):
    user_email: EmailStr | None
    multiple_emails_warning: bool
    off_topic: bool
    case_study_domains: list[str] | None
    case_study_intent: CaseStudyIntent | None
