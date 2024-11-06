from typing import List

from aiogram.types import (
                            ReplyKeyboardMarkup, KeyboardButton,
                            InlineKeyboardMarkup, InlineKeyboardButton
                          )
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_geo_request_markup() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=_("Provide geolocation"), request_location=True)],
        [KeyboardButton(text=_("Skip"))]
    ], resize_keyboard=True)

def get_main_menu_markup() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=_("Manage task filters"))],
        [KeyboardButton(text=_("Manage platforms"))]
    ], resize_keyboard=True)

def get_filters_menu_markup(add_delete_button: bool=True) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.max_width = 1
    builder.add(KeyboardButton(text=_("Add filter")))
    if add_delete_button:
        builder.add(KeyboardButton(text=_("Remove filter")))
    builder.add(KeyboardButton(text=_("Back")))
    keyboard = builder.as_markup()
    keyboard.resize_keyboard = True
    return keyboard

def get_filter_types_markup() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=_("🔤Keyword")), KeyboardButton(text=_("*️⃣Regex"))],
        [KeyboardButton(text=_("👁Views")), KeyboardButton(text=_("✉️Responses"))],
        [KeyboardButton(text=_("💰Price")), KeyboardButton(text=_("📅Lifetime"))],
        [KeyboardButton(text=_("Cancel"))]
    ], resize_keyboard=True)

def get_cancel_markup() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=_("Cancel"))]
    ], resize_keyboard=True)

def get_platforms_menu_markup(
        add_subscribe_button: bool=True,
        add_unsubscribe_button: bool =True
) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.max_width = 1
    if add_subscribe_button:
        builder.add(KeyboardButton(text=_("Subscribe to the platform")))
    if add_unsubscribe_button:
        builder.add(KeyboardButton(text=_("Unsubscribe from the platform")))
    builder.add(KeyboardButton(text=_("Back")))
    keyboard = builder.as_markup()
    keyboard.resize_keyboard = True
    return keyboard

def get_platforms_list_markup(platform_names: List[str]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.max_width = 3
    builder.add(*[
        KeyboardButton(text=platform_name)
        for platform_name in platform_names
    ])
    builder.row(KeyboardButton(text=_("Cancel")))
    keyboard = builder.as_markup()
    keyboard.resize_keyboard = True
    return keyboard

def get_open_task_markup(task_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_("Open Task"), url=task_url)]
    ])