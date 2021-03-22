from sqlalchemy import Column, Integer, String, orm

from const import TYPES_WEIGHTS
from data.orders import Order
from extra import check_time_string
from extra import split_time_string, collide_time
from .db_session import SqlAlchemyBase


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    courier_id = Column(Integer, primary_key=True)
    courier_type = Column(String, nullable=False)
    regions = Column(String)
    working_hours = Column(String)

    orders = orm.relation('OrderAssign', back_populates='courier')

    def can_assign(self, order: Order) -> bool:
        if not TYPES_WEIGHTS[self.get_courier_type()] >= order.get_weight():
            return False

        if order.get_region() not in self.get_regions():
            return False

        for working_time_string in self.get_working_hours():
            for deliver_time_string in order.get_delivery_hours():
                working_time = split_time_string(working_time_string)
                deliver_time = split_time_string(deliver_time_string)
                if any([collide_time(working_time[0], deliver_time),
                        collide_time(working_time[1], deliver_time),
                        collide_time(deliver_time[0], working_time),
                        collide_time(deliver_time[1], working_time)]):
                    return True
        return False

    def set_courier_type(self, type_: str):
        self.courier_type = type_

    def set_regions(self, regions: list):
        self.regions = ";".join(map(str, regions)) or None

    def set_working_hours(self, whs: list):
        self.working_hours = ";".join(whs) or None

    def get_courier_id(self) -> int:
        return self.courier_id

    def get_courier_type(self) -> str:
        return self.courier_type

    def get_regions(self) -> list:
        regions = self.regions
        return list(map(int, filter(bool, (regions or "").split(';'))))

    def get_working_hours(self) -> list:
        whs = self.working_hours
        return list(filter(bool, (whs or "").split(';')))

    @staticmethod
    def check_format_courier_id(id_: int) -> bool:
        return isinstance(id_, int) and id_ > 0

    @staticmethod
    def check_format_courier_type(type_: str) -> bool:
        return type_ in {'foot', 'bike', 'car'}

    @staticmethod
    def check_format_regions(regions: list) -> bool:
        if not isinstance(regions, list):
            return False
        return all(map(lambda x: isinstance(x, int) and x > 0, regions))

    @staticmethod
    def check_format_working_hours(whs: list) -> bool:
        if not isinstance(whs, list):
            return False

        return all(map(lambda x: isinstance(x, str) and check_time_string(x), whs))
