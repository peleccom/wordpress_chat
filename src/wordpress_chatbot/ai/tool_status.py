TOOL_STATUS_LABELS: dict[str, str] = {
    "retrieve_case_studies_tool": "Finding relevant examples...",
    "fetch_page_tool": "Gathering information...",
    "fill_contact_form_tool": "Preparing your request...",
}

DEFAULT_TOOL_STATUS = "Working on it..."


def status_for_tool_calls(tool_calls: list) -> str | None:
    all_empty_names = True
    for tool_call in tool_calls:
        name = tool_call.get("name")
        if name:
            all_empty_names = False
        if name and name in TOOL_STATUS_LABELS:
            return TOOL_STATUS_LABELS[name]

    return DEFAULT_TOOL_STATUS if not all_empty_names else None
