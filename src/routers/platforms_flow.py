from typing import List
from html import escape

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from aiogram.fsm.context import FSMContext

from db import async_session, User, UserRepository, Platform, PlatformRepository
from utils.markups import (
                            get_main_menu_markup, get_platforms_menu_markup,
                            get_platforms_list_markup
                          )
from utils.states.platforms_flow import PlatformsFlowStates


router = Router()


async def _answer_platforms_list(
        message: types.Message, platforms: List[Platform], disabled_platforms: List[Platform]
):
    disabled_platform_ids = {platform.id for platform in disabled_platforms}
    enabled_platforms_count = len(platforms)-len(disabled_platforms)
    await message.answer(
        _(
            "You are subscribed to <b>{enabled_platform_count}</b> platform out of <b>{platform_count}</b> available:\n\n{platforms}",
            "You are subscribed to <b>{enabled_platform_count}</b> platforms out of <b>{platform_count}</b> available:\n\n{platforms}",
            enabled_platforms_count
        ).format(
            enabled_platform_count=enabled_platforms_count, platform_count=len(platforms),
            platforms='\n'.join([
                f"{'🔕' if platform.id in disabled_platform_ids else '🔔'} {escape(platform.name)}"
                for platform in platforms
            ])
        ),
        reply_markup=get_platforms_menu_markup(
            add_subscribe_button=len(disabled_platform_ids) > 0,
            add_unsubscribe_button=len(disabled_platform_ids) < len(platforms)
        ),
        parse_mode="HTML"
    )

@router.message(Command("platforms"))
@router.message(F.text.capitalize()==__("Manage platforms"))
async def platforms(message: types.Message, state: FSMContext):
    async with UserRepository() as user_rep, PlatformRepository() as platform_rep:
        user = await user_rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        await _answer_platforms_list(
            message,
            await platform_rep.get_all(limit=None),
            await user.awaitable_attrs.disabled_platforms
        )
    await state.set_state(PlatformsFlowStates.on_platforms_menu)

@router.message(StateFilter(PlatformsFlowStates.on_platforms_menu), F.text.capitalize()==__("Back"))
async def platforms_back(message: types.Message, state: FSMContext):
    await message.answer(text=_("Ok, let's go back to main menu"), reply_markup=get_main_menu_markup())
    await state.clear()

@router.message(
    StateFilter(PlatformsFlowStates.on_unsubscribe_platform_name, PlatformsFlowStates.on_subscribe_platform_name),
    F.text.capitalize()==__("Cancel")
)
async def platforms_update_cancelled(message: types.Message, state: FSMContext):
    async with UserRepository() as user_rep, PlatformRepository() as platform_rep:
        user = await user_rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        await _answer_platforms_list(
            message,
            await platform_rep.get_all(limit=None),
            await user.awaitable_attrs.disabled_platforms
        )
    await state.set_state(PlatformsFlowStates.on_platforms_menu)

@router.message(StateFilter(PlatformsFlowStates.on_platforms_menu), F.text.capitalize()==__("Unsubscribe from the platform"))
async def platforms_unsubscribe(message: types.Message, state: FSMContext):
    async with UserRepository() as user_rep, PlatformRepository() as platform_rep:
        user = await user_rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        platforms = await platform_rep.get_all(limit=None)
        disabled_platform_ids = {platform.id for platform in await user.awaitable_attrs.disabled_platforms}

    await state.set_state(PlatformsFlowStates.on_unsubscribe_platform_name)
    await message.answer(
        _("Please, select a platform name"),
        reply_markup=get_platforms_list_markup([
            platform.name
            for platform in platforms
            if platform.id not in disabled_platform_ids
        ])
    )

@router.message(StateFilter(PlatformsFlowStates.on_unsubscribe_platform_name))
async def platforms_unsubscribe_name_selected(message: types.Message, state: FSMContext):
    platform_name = message.text.lower()
    session = async_session()
    async with UserRepository(session) as user_rep, PlatformRepository(session) as platform_rep:
        selected_platform = await platform_rep.get_first(lambda sel: sel.where(Platform.name==platform_name))
        if selected_platform is None:
            await message.answer(_("Platform was not found, try again."))
            return
        
        user = await user_rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        disabled_platforms = await user.awaitable_attrs.disabled_platforms
        if selected_platform in disabled_platforms:
            await message.answer(_("You're not subscribed to this platform"))
            return

        disabled_platforms.append(selected_platform)
        await user_rep.commit()

        await message.answer(
            _("You have unsubscribed from the platform \"{platform}\"").format(
                platform=selected_platform.name
            )
        )
        await _answer_platforms_list(message, await platform_rep.get_all(limit=None), disabled_platforms)
        await state.set_state(PlatformsFlowStates.on_platforms_menu)

@router.message(StateFilter(PlatformsFlowStates.on_platforms_menu), F.text.capitalize()==__("Subscribe to the platform"))
async def platforms_subscribe(message: types.Message, state: FSMContext):
    async with UserRepository() as user_rep:
        user = await user_rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        disabled_platforms = await user.awaitable_attrs.disabled_platforms

    await state.set_state(PlatformsFlowStates.on_subscribe_platform_name)
    await message.answer(
        _("Please, select a platform name"),
        reply_markup=get_platforms_list_markup([
            platform.name
            for platform in disabled_platforms
        ])
    )

@router.message(StateFilter(PlatformsFlowStates.on_subscribe_platform_name))
async def platform_subscribe_name_selected(message: types.Message, state: FSMContext):
    platform_name = message.text.lower()
    session = async_session()
    async with UserRepository(session) as user_rep, PlatformRepository(session) as platform_rep:
        selected_platform = await platform_rep.get_first(lambda sel: sel.where(Platform.name==platform_name))
        if selected_platform is None:
            await message.answer(_("Platform was not found, try again."))
            return
        
        user = await user_rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        try:
            disabled_platforms = await user.awaitable_attrs.disabled_platforms
            disabled_platforms.remove(selected_platform)
        except ValueError:
            await message.answer(_("You're already subscribed to this platform"))
            return
        await user_rep.commit()

        await message.answer(
            _("You have subscribed to the platform \"{platform}\"").format(
                platform=selected_platform.name
            )
        )
        await _answer_platforms_list(message, await platform_rep.get_all(limit=None), disabled_platforms)
        await state.set_state(PlatformsFlowStates.on_platforms_menu)