from sqlalchemy import Column, Integer, Float, String

from extra import check_time_string
from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    weight = Column(Float, nullable=False)
    region = Column(Integer, nullable=False)
    delivery_hours = Column(String, nullable=False)

    def get_order_id(self) -> int:
        return self.order_id

    def get_weight(self) -> float:
        return self.weight

    def get_region(self) -> int:
        return self.region

    def get_delivery_hours(self):
        dhs = self.delivery_hours
        return list(filter(bool, (dhs or "").split(';')))

    def set_weight(self, weight: float):
        self.weight = float(round(weight, 2))

    def set_region(self, region: int):
        self.region = region

    def set_delivery_hours(self, dhs: list):
        self.delivery_hours = ";".join(dhs)

    @staticmethod
    def check_format_order_id(id_: int):
        return isinstance(id_, int) and id_ > 0

    @staticmethod
    def check_format_weight(weight: float):
        return isinstance(weight, (float, int)) and 50 >= weight >= 0.01

    @staticmethod
    def check_format_region(region: int):
        return isinstance(region, int) and region > 0

    @staticmethod
    def check_format_delivery_hours(dhs: list) -> bool:
        if not isinstance(dhs, list):
            return False

        return all(map(lambda x: isinstance(x, str) and check_time_string(x), dhs))
