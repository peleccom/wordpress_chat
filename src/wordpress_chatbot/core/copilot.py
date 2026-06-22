from enum import StrEnum


class CopilotFunctionName(StrEnum):
    """Host-page function names for cl.CopilotFunction / chainlit-call-fn.

    Keep public/demo/chainlit-copilot.js CopilotFn in sync when adding members.
    """

    FILL_CONTACT_FORM = "fill_contact_form"
