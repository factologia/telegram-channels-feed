from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from typing import Generator, Optional

from src.config import db
from src.domain.entities import Subscription, Channel


class Notifications:
    def get_channel_info(self, channel_telegram_id) -> Optional[Channel]:
        return db.session.query(Channel).filter(Channel.telegram_id == channel_telegram_id).first()

    def list_not_notified(self, channel_telegram_id: int, message_id: int) -> Generator[Subscription, None, None]:
        query = db.session \
            .query(Subscription) \
            .options(joinedload(Subscription.user)) \
            .join(Subscription.channel) \
            .filter(Channel.telegram_id == channel_telegram_id) \
            .filter(or_(Channel.last_message_id < message_id, Channel.last_message_id == None)) \
            .filter(or_(Subscription.last_message_id < message_id, Subscription.last_message_id == None))

        return db.get_lazy(query)

    def mark_subscription(self, user_id: int, channel_id: int, message_id: int):
        db.session \
            .query(Subscription) \
            .filter(Subscription.user_id == user_id) \
            .filter(Subscription.channel_id == channel_id) \
            .filter(or_(Subscription.last_message_id < message_id, Subscription.last_message_id == None)) \
            .update({Subscription.last_message_id: message_id})
        db.session.commit()

    def mark_channel(self, channel_telegram_id: int, message_id: int):
        db.session \
            .query(Channel) \
            .filter(Channel.telegram_id == channel_telegram_id) \
            .filter(or_(Channel.last_message_id < message_id, Channel.last_message_id == None)) \
            .update({Channel.last_message_id: message_id})
        db.session.commit()