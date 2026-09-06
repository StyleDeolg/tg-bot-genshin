from aiogram.fsm.state import State, StatesGroup

class BindUIDStates(StatesGroup):
    waiting_for_uid = State()
    waiting_for_confirm = State()

class SupportStates(StatesGroup):
    waiting_for_message = State()