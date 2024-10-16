from aiogram.fsm.state import StatesGroup, State


class StartFlowStates(StatesGroup):
    on_geolocation = State()