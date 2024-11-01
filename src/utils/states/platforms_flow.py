from aiogram.fsm.state import StatesGroup, State


class PlatformsFlowStates(StatesGroup):
    on_platforms_menu = State()
    on_unsubscribe_platform_name = State()
    on_subscribe_platform_name = State()