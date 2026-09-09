from app.handlers.start import start_command
from app.handlers.help import help_command
from app.handlers.profile import profile_command
from app.handlers.bind_uid import bind_uid_start, bind_uid_input  # 👈 УБИРАЕМ bind_uid_server
from app.handlers.unbind_uid import unbind_uid
from app.handlers.app import app_command
from app.handlers.donate import donate_command
from app.handlers.error_handler import error_handler
from app.handlers.admin import (
    admin_panel,
    admin_exit,
    admin_stats,
    admin_prizes,
    admin_tasks,
    admin_give_tickets_start,
    admin_give_tickets_process,
    admin_broadcast_start,
    admin_broadcast_process,
    admin_give_moon,
    admin_give_moon_user,
    add_sponsor,
    add_sponsor_task,
    list_sponsors,
    add_referral_reward,
)

__all__ = [
    "start_command",
    "help_command",
    "profile_command",
    "bind_uid_start",
    "bind_uid_input",  # 👈 УБИРАЕМ bind_uid_server
    "unbind_uid",
    "app_command",
    "admin_panel",
    "admin_exit",
    "admin_stats",
    "admin_prizes",
    "admin_tasks",
    "admin_give_tickets_start",
    "admin_give_tickets_process",
    "admin_broadcast_start",
    "admin_broadcast_process",
    "admin_give_moon",
    "admin_give_moon_user",
    "donate_command",
    "error_handler",
    "add_sponsor",
    "add_sponsor_task",
    "list_sponsors",
    "add_referral_reward",
]