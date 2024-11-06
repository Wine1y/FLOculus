from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from aiogram.fsm.context import FSMContext

from db import User, FilterEntry, UserRepository, FilterEntryRepository
from utils.markups import (
                            get_main_menu_markup, get_filters_menu_markup,
                            get_filter_types_markup, get_cancel_markup
                          )
from utils.states.filters_flow import FiltersFlowStates
from utils.filter_creation_flow import flows
from utils.filter_creation_flow.stages import InvalidStageAnswer


router = Router()


async def _answer_filters_list(message: types.Message, user: User, state: FSMContext):
    filter_entries = await user.awaitable_attrs.filters
    await message.answer(
        _("You have <b>{filters_count}</b> task filters:\n\n{filters}\n\n🔠 - case-sensitive filter\n❗️- negative filter").format(
            filters_count=len(filter_entries),
            filters='\n'.join([f"[#{filter_entry.id}] {filter_entry.to_filter().translated_str()}" for filter_entry in filter_entries])
        ),
        reply_markup=get_filters_menu_markup(add_delete_button=len(filter_entries) > 0),
        parse_mode="HTML"
    )
    await state.set_state(FiltersFlowStates.on_filters_menu)

@router.message(Command("filters"))
@router.message(F.text.capitalize()==__("Manage task filters"))
async def filters(message: types.Message, state: FSMContext):
    async with UserRepository() as rep:
        user = await rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        await _answer_filters_list(message, user, state)

@router.message(StateFilter(FiltersFlowStates.on_filters_menu), F.text.capitalize()==__("Back"))
async def filters_back(message: types.Message, state: FSMContext):
    await message.answer(text=_("Ok, let's go back to main menu"), reply_markup=get_main_menu_markup())
    await state.clear()

@router.message(F.text==__("Add filter"))
async def add_filter(message: types.Message, state: FSMContext):
    await message.answer(
        _("Please, select new filter type"),
        reply_markup=get_filter_types_markup()
    )
    await state.set_state(FiltersFlowStates.on_filter_type)

@router.message(StateFilter(FiltersFlowStates.on_filter_type, FiltersFlowStates.in_creation_flow), F.text.capitalize()==__("Cancel"))
async def in_creation_flow_cancel(message: types.Message, state: FSMContext):
    await message.answer(_("Filter creation cancelled"))
    await state.clear()
    async with UserRepository() as rep:
        user = await rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        await _answer_filters_list(message, user, state)

@router.message(StateFilter(FiltersFlowStates.on_filter_type))
async def add_filter_type_selected(message: types.Message, state: FSMContext):
    TEXT_TO_CREATION_FLOW = {
        _("🔤Keyword"): flows.KeywordFilterCreationFlow,
        _("*️⃣Regex"): flows.RegexFilterCreationFlow,
        _("👁Views"): flows.ViewsFilterCreationFlow,
        _("✉️Responses"): flows.ResponsesFilterCreationFlow,
        _("💰Price"): flows.PriceFilterCreationFlow,
        _("📅Lifetime"): flows.LifetimeFilterCreationFlow
    }

    creation_flow_type: type[flows.FilterCreationFlow] = TEXT_TO_CREATION_FLOW.get(message.text)
    if creation_flow_type is None:
        await message.answer(_("Please, provide a valid filter type"))
        return
    creation_flow = creation_flow_type()
    await state.set_state(FiltersFlowStates.in_creation_flow)
    await state.update_data({"filter_creation_flow": creation_flow})

    stage = creation_flow.current_stage
    await message.answer(str(stage.stage_question), reply_markup=stage.get_keyboard())

@router.message(StateFilter(FiltersFlowStates.in_creation_flow))
async def in_creation_flow(message: types.Message, state: FSMContext):
    creation_flow: flows.FilterCreationFlow = (await state.get_data())["filter_creation_flow"]
    answer = None if message.text == _("Skip") else message.text
    if answer is None and creation_flow.current_stage.required:
        await message.answer(_("This question can't be skipped"))
        return
    
    try:
        creation_flow.process_answer(answer)
    except InvalidStageAnswer:
        await message.answer(_("Please, provide a valid answer"))
        return
    
    if not creation_flow.is_last_stage:
        next_stage = creation_flow.next_stage()
        await message.answer(str(next_stage.stage_question), reply_markup=next_stage.get_keyboard())
        return
    

    async with UserRepository() as user_rep, FilterEntryRepository() as filter_rep:
        user = await user_rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        try:
            new_filter = creation_flow.build_filter()
        except flows.InvalidFlowData:
            await state.clear()
            await message.answer(_("Invalid filter data, please try again."))
            await _answer_filters_list(message, user, state)
            return
    
        await filter_rep.create(FilterEntry.from_filter(user.id, new_filter))
        await message.answer(
            _("New filter successfully created:\n{filter}").format(filter=new_filter.translated_str()),
            parse_mode="HTML"
        )
        await state.clear()
        await _answer_filters_list(message, user, state)

@router.message(F.text==__("Remove filter"))
async def remove_filter(message: types.Message, state: FSMContext):
    await message.answer(
        _("Please, enter the filter ID (shown in brackets before the filter type)"),
        reply_markup=get_cancel_markup()
    )
    await state.set_state(FiltersFlowStates.on_remove_filter_id)

@router.message(StateFilter(FiltersFlowStates.on_remove_filter_id), F.text.capitalize()==__("Cancel"))
async def remove_filter_cancel(message: types.Message, state: FSMContext):
    await message.answer(_("Filter removal cancelled"))
    await state.clear()
    async with UserRepository() as rep:
        user = await rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        await _answer_filters_list(message, user, state)

@router.message(StateFilter(FiltersFlowStates.on_remove_filter_id))
async def remove_filter_id_selected(message: types.Message, state: FSMContext):
    try:
        filter_id = int(message.text.strip("[#]"))
    except ValueError:
        await message.answer(_("Please, provide a valid filter ID"))
        return
    
    async with UserRepository() as user_rep, FilterEntryRepository() as filter_rep:
        user = await user_rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        filter_entry = await filter_rep.get_first(
            lambda sel: sel.where(FilterEntry.owner_id==user.id, FilterEntry.id==filter_id)
        )
        if filter_entry is None:
            await message.answer(_("Filter with prodived ID was not found, try again."))
            await state.clear()
            return
        await filter_rep.delete(filter_entry)
        await state.clear()
        await message.answer(
            _("Filter was successfully deleted:\n{filter}").format(filter=filter_entry.to_filter().translated_str()),
            parse_mode="HTML"
        )
        await _answer_filters_list(message, user, state)