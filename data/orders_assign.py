from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, orm, ForeignKey

from const import TYPES_PRICES_M
from .db_session import SqlAlchemyBase


class OrderAssign(SqlAlchemyBase):
    __tablename__ = "orders_assign"

    order_id = Column(Integer, ForeignKey('orders.order_id'), primary_key=True)
    courier_id = Column(Integer, ForeignKey('couriers.courier_id'))

    assign_time = Column(DateTime, nullable=False, default=datetime.now)
    complete_time = Column(DateTime, nullable=True, default=None)

    price = Column(Integer)

    order = orm.relation('Order')
    courier = orm.relation('Courier')

    def complete(self, time=None):
        self.complete_time = time or datetime.now()

        self.price = 500 * TYPES_PRICES_M[self.courier.get_courier_type()]
