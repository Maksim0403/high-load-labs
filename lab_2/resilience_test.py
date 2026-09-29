"""Мінімальна перевірка stateless flow та відмовостійкості gateway."""

import argparse
import subprocess
import time
import uuid

import httpx


def request(client: httpx.Client, method: str, path: str, **kwargs):
    response = client.request(method, path, **kwargs)
    response.raise_for_status()
    instance = response.headers.get("x-instance-id")
    if not instance:
        raise RuntimeError("Відповідь не містить X-Instance-ID")
    print(f"{method} {path}: {response.status_code} ({instance})")
    return response


def request_after_failover(
    client: httpx.Client, method: str, path: str, **kwargs
):
    last_error = None
    for attempt in range(8):
        try:
            return request(client, method, path, timeout=2, **kwargs)
        except httpx.TimeoutException as exc:
            last_error = exc
        except httpx.NetworkError as exc:
            last_error = exc
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in {502, 503, 504}:
                raise
            last_error = exc

        if attempt < 7:
            time.sleep(1)

    raise RuntimeError(
        f"Gateway did not recover after stopping a backend instance: {path}"
    ) from last_error


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost")
    parser.add_argument("--stop-instance", default="")
    args = parser.parse_args()

    email = f"lab2-{uuid.uuid4().hex[:12]}@example.com"
    phone_number = f"+38099{uuid.uuid4().int % 1_000_000:06d}"
    password = "password123"
    with httpx.Client(base_url=args.base_url, timeout=10) as client:
        request(client, "GET", "/api/v1/health")
        request(
            client,
            "POST",
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": password,
                "full_name": "Lab 2 Client",
                "role": "client",
                "phone_number": phone_number,
            },
        )
        request(
            client,
            "POST",
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        created = request(
            client,
            "POST",
            "/api/v1/orders/",
            json={"title": "Stateless flow", "weight": 10, "distance": 50},
        ).json()
        order_id = created["id"]
        request(client, "GET", f"/api/v1/orders/{order_id}")
        updated = request(
            client,
            "PATCH",
            f"/api/v1/orders/{order_id}",
            json={"title": "Updated on shared storage"},
        ).json()
        assert updated["title"] == "Updated on shared storage"
        final = request(client, "GET", f"/api/v1/orders/{order_id}").json()
        assert final["title"] == updated["title"]

        if args.stop_instance:
            subprocess.run(["docker", "stop", args.stop_instance], check=True)
            recovered = request_after_failover(
                client, "GET", f"/api/v1/orders/{order_id}"
            ).json()
            assert recovered["title"] == final["title"]

    print("Перевірка завершена: стан збережено у PostgreSQL.")


if __name__ == "__main__":
    main()
