from datetime import datetime

from flask import Flask, jsonify, request

from const import FILENAME_BD
from data import db_session
from data.couriers import Courier
from data.orders import Order
from data.orders_assign import OrderAssign
import os

app = Flask(__name__)


# TODO: Обработать параметры и добавить распознование разных форматов времени

@app.route('/couriers', methods=['POST'])
def couriers_post():
    data_couriers: list = request.json["data"]

    passed = []
    failed = []

    for i, courier in enumerate(data_couriers, start=1):
        # Проверка каждой записи на валидность
        courier: dict

        validate_keys = {'courier_id', 'courier_type', 'regions', 'working_hours'}

        all_passed = (
                not set(courier.keys()) ^ validate_keys and

                Courier.check_format_courier_id(courier['courier_id']) and
                Courier.check_format_courier_type(courier['courier_type']) and
                Courier.check_format_regions(courier['regions']) and
                Courier.check_format_working_hours(courier['working_hours'])
        )

        if all_passed:
            passed.append({'id': i})
        else:
            failed.append({'id': i})

    if failed:
        return app.make_response((jsonify(validation_error={'couriers': failed}), 400))

    with db_session.create_session() as session:
        session: db_session.Session
        for i, courier in enumerate(data_couriers, start=1):
            c = Courier()
            c.courier_id = courier['courier_id']

            c.set_courier_type(courier['courier_type'])
            c.set_regions(courier['regions'])
            c.set_working_hours(courier['working_hours'])

            session.add(c)
        session.commit()

    return jsonify(couriers=passed), 201


@app.route('/couriers/<int:courier_id>', methods=['PATCH'])
def courier_patch(courier_id: int):
    data: dict = request.json

    validate_keys = {"courier_type", "regions", "working_hours"}
    if set(data.keys()) - validate_keys:
        return "", 400

    with db_session.create_session() as session:
        session: db_session.Session
        c: Courier = session.query(Courier).filter(Courier.courier_id == courier_id).first()
        if not c:
            return "", 404
        c.set_courier_type(data.get('courier_type', c.get_courier_type()))
        c.set_regions(data.get('regions', c.get_regions()))
        c.set_working_hours(data.get('workings_hours', c.get_working_hours()))

        # noinspection PyComparisonWithNone
        for order in session.query(OrderAssign).filter(OrderAssign.courier_id == c.courier_id,
                                                       OrderAssign.complete_time != None).all():
            if not c.can_assign(order):
                session.delete(order)

        session.commit()

        return jsonify(courier_id=c.get_courier_id(),
                       courier_type=c.get_courier_type(),
                       regions=c.get_regions(),
                       working_hours=c.get_working_hours()), 200


@app.route('/orders', methods=['POST'])
def orders_post():
    data_orders: list = request.json["data"]

    passed = []
    failed = []

    for i, order in enumerate(data_orders, start=1):
        # Проверка каждой записи на валидность
        order: dict

        validate_keys = {'order_id', 'weight', 'region', 'delivery_hours'}

        all_passed = (
                not set(order.keys()) ^ validate_keys and

                Order.check_format_order_id(order['order_id']) and
                Order.check_format_weight(order['weight']) and
                Order.check_format_region(order['region']) and
                Order.check_format_delivery_hours(order['delivery_hours'])
        )

        if all_passed:
            passed.append({'id': i})
        else:
            failed.append({'id': i})

    if failed:
        return app.make_response((jsonify(validation_error={'orders': failed}), 400))

    with db_session.create_session() as session:
        session: db_session.Session
        for i, courier in enumerate(data_orders, start=1):
            order: Order = Order()
            order.order_id = courier['order_id']

            order.set_weight(courier['weight'])
            order.set_region(courier['region'])
            order.set_delivery_hours(courier['delivery_hours'])

            session.add(order)
        session.commit()

    return jsonify(orders=passed), 201


# noinspection PyComparisonWithNone
@app.route('/orders/assign', methods=['POST'])
def orders_assign_post():
    courier_id: int = request.json['courier_id']
    with db_session.create_session() as session:
        session: db_session.Session
        courier = session.query(Courier).filter(Courier.courier_id == courier_id).first()
        if not courier:
            return "", 400

        # Выполняем поиск заказов удовлетворяющих курьеру
        orders = session.query(Order).all()
        orders = list(filter(
            lambda x: not bool(session.query(OrderAssign).filter(OrderAssign.order_id == x.order_id,
                                                                 OrderAssign.complete_time != None).first()),
            filter(
                courier.can_assign,
                orders
            )
        ))
        if orders:
            now = datetime.now()
            for order in orders:
                if session.query(OrderAssign).filter(OrderAssign.order_id == order.order_id).first():
                    continue

                oa = OrderAssign()

                oa.order_id = order.order_id
                oa.courier_id = courier.courier_id
                oa.assign_time = now

                session.add(oa)

            session.commit()
            return jsonify(orders=[{"id": order.order_id} for order in orders], assign_time=now.isoformat())

        return jsonify(orders=[]), 200


@app.route('/orders/complete', methods=['POST'])
def orders_complete_post():
    courier_id = request.json['courier_id']
    order_id = request.json['order_id']
    complete_time = request.json['complete_time']
    with db_session.create_session() as session:
        session: db_session.Session

        ao: OrderAssign = session.query(OrderAssign).filter(OrderAssign.order_id == order_id,
                                                            OrderAssign.courier_id == courier_id).first()
        if not ao:
            return "", 400
        ao.complete(datetime.strptime(complete_time, '%Y-%m-%dT%H:%M:%S.%fZ'))
        session.commit()

    return jsonify({"order_id": order_id})


# TODO: Проверить все тут
@app.route('/couriers/<int:courier_id>', methods=['GET'])
def couriers_get(courier_id: int):
    with db_session.create_session() as session:
        session: db_session.Session

        courier = session.query(Courier).filter(Courier.courier_id == courier_id).first()
        if not courier:
            return "", 404

        payload = {
            "courier_id": courier.get_courier_id(),
            "courier_type": courier.get_courier_type(),
            "regions": courier.get_regions(),
            "working_hours": courier.get_working_hours()
        }

        def td(number):
            # noinspection PyComparisonWithNone
            orders: list = session.query(OrderAssign).filter(OrderAssign.complete_time != None).all()
            orders = list(filter(lambda x: x.order.region == number, orders))

            if not orders:
                return 0
            orders.sort(key=lambda x: (x.complete_time, x.assign_time))
            total = 0
            for i in range(len(orders)):
                order_a: OrderAssign = orders[i]
                if i == 0:
                    total += (order_a.complete_time - order_a.assign_time).total_seconds()
                else:
                    order_b = orders[i - 1]
                    total += (order_a.complete_time - order_b.complete_time).total_seconds()
            return total / len(orders)

        t = min(td(i) for i in courier.get_regions())
        if t != 0:
            payload["rating"] = (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5

        # noinspection PyComparisonWithNone
        orders_complete: list = session.query(OrderAssign).filter(OrderAssign.complete_time != None).all()
        payload['earnings'] = sum(map(lambda x: x.price, orders_complete))
        return jsonify(payload)


def main(host="0.0.0.0", port=8080, **kwargs):
    directory = os.path.split(FILENAME_BD)[0]
    if directory and not os.path.isdir(directory):
        os.mkdir(directory)
    db_session.global_init(FILENAME_BD)

    app.run(host, port, **kwargs)


if __name__ == '__main__':
    main()
