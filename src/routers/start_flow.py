from datetime import datetime

from aiogram import Router, F, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _, lazy_gettext as __
from tzfpy import get_tz
from pytz import timezone

from db import User, UserRepository
from utils.markups import get_geo_request_markup
from utils.states.start_flow import StartFlowStates


router = Router()

@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    async with UserRepository() as rep:
        user = await rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
    
    if user is None:
        await rep.create(User(telegram_id=message.from_user.id))
        await message.answer(_("Hello, i'm FLOculus-Bot!\nI can help you find freelance tasks on various freelance platforms."))
        await message.answer(_("Please, provide your geolocation so i can display the time in your timezone."), reply_markup=get_geo_request_markup())
        await state.set_state(StartFlowStates.on_geolocation)
    else:
        await message.answer(_("Hello again!"))

@router.message(StateFilter(StartFlowStates.on_geolocation), F.location)
async def geolocation_skipped(message: types.Message, state: FSMContext):
    await state.clear()
    tz = timezone(get_tz(message.location.longitude, message.location.latitude))
    utc_offset_minutes = datetime.now(tz).utcoffset().total_seconds()//60

    async with UserRepository() as rep:
        user = await rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        user.utc_offset_minutes = utc_offset_minutes
        await rep.commit()
    
    await message.answer(_("Thanks, time will be displayed in your timezone ({timezone})").format(
        timezone=f"{tz}, UTC{'+' if utc_offset_minutes > 0 else ''}{int(utc_offset_minutes//60)}"
    ))

@router.message(StateFilter(StartFlowStates.on_geolocation), F.text==__("Skip"))
async def geolocation_skipped(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(_("Ok, time will be displayed in UTC timezone."))