import random
from locust import HttpUser, task, between


EVENT_IDS = [
    "697b95c6538c43fc66f46ac5",
    "69808274010c74dd9b3a4203",
    "69971f2eb59d31712c9b0b7c",
    "69971f3bb59d31712c9b0b7d",
    "69971f4db59d31712c9b0b80",
]


USER_IDS = [
    "507f1f77bcf86cd799439013",
    "507f1f77bcf86cd799439012",
    "507f1f77bcf86cd799439011",
    "507f1f77bcf86cd799439010",
]

class EventUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        self.token = random.choice(USER_IDS)

    @task(1)
    def get_list_events(self):
        user_id = random.choice(USER_IDS)
        headers = {
            "x-user-id": user_id,
            "x-user-role": "user",
            "accept": "application/json",
        }

        with self.client.get(
            "/events/my?limit=10",
            headers=headers,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Unexpected status: {response.status_code}")
                return

            data = response.json()
            if "items" not in data:
                response.failure("No items in response")
                return

            for item in data["items"]:
                if item["owner_id"] != user_id:
                    response.failure("Returned events of another user")
                    return

            response.success()

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
