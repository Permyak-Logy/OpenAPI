import unittest
from requests import post, patch, get
from flask import jsonify

host = 'http://127.0.0.1:5000'


class MyTestCase(unittest.TestCase):
    def test_all(self):
        # POST .../couriers
        self.assertEqual(post(f'{host}/couriers', json={"data": [
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
                "courier_id": 2,
                "courier_type": "foot",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            },
            {
                "courier_id": 3,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": []
            }
        ]}).json(), {"couriers": [{"id": 1}, {"id": 2}, {"id": 3}]})
        self.assertEqual(post(f'{host}/couriers', json={"data": [
            {
                "courier_id": 4,
                "courier_type": "car",
                "regions": [],
                "working_hours": ["09:00-19:00", "00-11"]
            }, {
                "courier_id": 5,
                "courier_type": "car",
                "working_hours": []
            }, {
                "courier_id": 9,
                "courier_type": "foot",
                "working_hours": [],
                "regions": []
            }, {
                "courier_id": -1,
                "courier_type": "car",
                "working_hours": [],
                "regions": []
            }, {
                "courier_id": 6,
                "courier_type": "train",
                "working_hours": [],
                "regions": [10, 11]
            }
        ]}).json(), {"validation_error": {
            "couriers": [{"id": 1}, {"id": 2}, {"id": 4}, {"id": 5}]
        }})

        # PARCH .../couriers/<courier_id>
        self.assertEqual(patch(f'{host}/couriers/2', json={
            "regions": [11, 33, 2]
        }).json(), {"courier_id": 2,
                    "courier_type": "foot",
                    "regions": [11, 33, 2],
                    "working_hours": ["09:00-18:00"]})
        self.assertEqual(patch(f'{host}/couriers/2', json={'name': "Max"}).status_code, 400)
        self.assertEqual(patch(f'{host}/couriers/93102930129031', json={'regions': [1, 2, 3, 4]}).status_code, 404)

        # POST .../orders
        self.assertEqual(post(f'{host}/orders', json={
            "data": [
                {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 2,
                    "weight": 15,
                    "region": 1,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        }).json(), {"orders": [{"id": 1}, {"id": 2}, {"id": 3}]})
        self.assertEqual(post(f'{host}/orders', json={
            "data": [
                {
                    'order_id': 10,
                    "weight": 100,
                    "region": 21,
                    "delivery_hours": ["09:00-12:00"]
                }
            ]
        }).json(), {"validation_error": {
            "orders": [{"id": 1}]
        }})

        # POST .../orders/assign
        self.assertEqual(post(f'{host}/orders/assign', json={"courier_id": 1}).json().get('orders'),
                         [{"id": 1}, {"id": 3}])
        self.assertEqual(post(f'{host}/orders/assign', json={"courier_id": 2}).json().get('orders'), [])

        # POST .../orders/complete
        self.assertEqual(post(f'{host}/orders/complete', json={
            "courier_id": 1,
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42Z"
        }).json(), {"order_id": 1})

        # GET .../couriers/courier_id
        self.assertEqual(get(f'{host}/couriers/999999').status_code, 404)
        self.assertEqual(get(f'{host}/couriers/2').status_code, 202)


if __name__ == '__main__':
    unittest.main()
