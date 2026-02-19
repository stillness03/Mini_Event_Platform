import random
from locust import HttpUser, task, between


EVENT_IDS = [
    "697b95c6538c43fc66f46ac5",
    "69808274010c74dd9b3a4203",
    "69971f2eb59d31712c9b0b7c",
    "69971f3bb59d31712c9b0b7d",
    "69971f4db59d31712c9b0b80",
]


class EventUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(8)
    def get_hot_event(self):
        hot_id = EVENT_IDS[0]

        with self.client.get(f"/events/{hot_id}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(2)
    def get_random_event(self):
        event_id = random.choice(EVENT_IDS)

        with self.client.get(f"/events/{event_id}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")
