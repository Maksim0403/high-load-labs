"""Мінімальна перевірка stateless flow та відмовостійкості gateway."""

import argparse
import subprocess
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost")
    parser.add_argument("--stop-instance", default="")
    args = parser.parse_args()

    email = f"lab2-{uuid.uuid4().hex[:12]}@example.com"
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
                "phone_number": "+380990000000",
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
            recovered = request(client, "GET", f"/api/v1/orders/{order_id}").json()
            assert recovered["title"] == final["title"]

    print("Перевірка завершена: стан збережено у PostgreSQL.")


if __name__ == "__main__":
    main()
