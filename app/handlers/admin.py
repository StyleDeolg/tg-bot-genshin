from telegram import Update
from telegram.ext import ContextTypes
from app.database import SessionLocal
from app.models.sponsor import Sponsor
from app.models.task import Task
from app.models.referral import ReferralReward
from app.config import ADMIN_IDS
import uuid

async def add_sponsor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав.")
        return
    # ... остальной код

async def add_sponsor_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав.")
        return
    # ... остальной код

async def list_sponsors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... этот метод может быть открытым
    pass

async def add_referral_reward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав.")
        return
    # ... остальной код