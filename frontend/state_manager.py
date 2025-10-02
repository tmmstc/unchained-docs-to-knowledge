def init_delete_confirmation_state(session_state):
    if "delete_confirmation_id" not in session_state:
        if hasattr(session_state, "delete_confirmation_id"):
            session_state.delete_confirmation_id = None
        else:
            session_state["delete_confirmation_id"] = None

    if "last_selected_record_id" not in session_state:
        if hasattr(session_state, "last_selected_record_id"):
            session_state.last_selected_record_id = None
        else:
            session_state["last_selected_record_id"] = None


def reset_delete_confirmation_on_selection_change(
    session_state, current_record_id: int
):
    last_id = (
        session_state.last_selected_record_id
        if hasattr(session_state, "last_selected_record_id")
        else session_state.get("last_selected_record_id")
    )

    if last_id != current_record_id:
        if hasattr(session_state, "delete_confirmation_id"):
            session_state.delete_confirmation_id = None
            session_state.last_selected_record_id = current_record_id
        else:
            session_state["delete_confirmation_id"] = None
            session_state["last_selected_record_id"] = current_record_id


def is_in_confirmation_mode(session_state, current_record_id: int) -> bool:
    conf_id = (
        session_state.delete_confirmation_id
        if hasattr(session_state, "delete_confirmation_id")
        else session_state.get("delete_confirmation_id")
    )
    return conf_id == current_record_id


def set_confirmation_mode(session_state, record_id: int):
    if hasattr(session_state, "delete_confirmation_id"):
        session_state.delete_confirmation_id = record_id
    else:
        session_state["delete_confirmation_id"] = record_id


def clear_delete_state(session_state):
    if hasattr(session_state, "delete_confirmation_id"):
        session_state.delete_confirmation_id = None
        session_state.last_selected_record_id = None
    else:
        session_state["delete_confirmation_id"] = None
        session_state["last_selected_record_id"] = None
