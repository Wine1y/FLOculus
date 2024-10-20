from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _, lazy_gettext as __, ngettext as ___

from db import User, UserRepository


router = Router()

@router.message(Command("filters"))
async def filters(message: types.Message):
    async with UserRepository() as rep:
        user = await rep.get_first(lambda sel: sel.where(User.telegram_id==message.from_user.id))
        filter_entries = await user.awaitable_attrs.filters

    
    await message.answer(
        _("You have {filters_count} task filters:\n\n{filters}\n\n🔠 - case-sensitive filter\n❗️- negative filter").format(
            filters_count=len(filter_entries),
            filters='\n'.join([filter_entry.to_filter().translated_str() for filter_entry in filter_entries])
        )
    )