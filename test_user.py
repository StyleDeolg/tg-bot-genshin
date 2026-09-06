from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()

new_user = User(
    telegram_id="123456789",
    username="testuser",
    first_name="Test",
    last_name="User"
)

db.add(new_user)
db.commit()
db.refresh(new_user)

print(f"✅ Пользователь создан!")
print(f"🆔 ID: {new_user.id}")
print(f"📱 Telegram ID: {new_user.telegram_id}")
print(f"🔑 Public ID: {new_user.public_id}")

db.close()