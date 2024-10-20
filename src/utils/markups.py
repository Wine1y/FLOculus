from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.i18n import gettext as _


def get_geo_request_markup() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=_("Provide geolocation"), request_location=True)],
        [KeyboardButton(text=_("Skip"))]
    ], resize_keyboard=True)