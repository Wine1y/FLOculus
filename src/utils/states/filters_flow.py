from aiogram.fsm.state import StatesGroup, State


class FiltersFlowStates(StatesGroup):
    on_filters_menu = State()
    on_filter_type = State()
    in_creation_flow = State()
    on_remove_filter_id = State()