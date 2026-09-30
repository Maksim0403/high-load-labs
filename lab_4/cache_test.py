import argparse
import subprocess
import time
import uuid

import httpx


def request(
    client: httpx.Client,
    method: str,
    path: str,
    expected_cache: str | None = None,
    **kwargs,
) -> tuple[httpx.Response, float]:
    started = time.perf_counter()
    response = client.request(method, path, **kwargs)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.raise_for_status()

    cache_status = response.headers.get("x-cache", "-")
    instance_id = response.headers.get("x-instance-id", "-")
    print(
        f"{method} {path}: {response.status_code} "
        f"X-Cache={cache_status} X-Instance-ID={instance_id} "
        f"latency={elapsed_ms:.1f}ms"
    )
    if expected_cache and cache_status != expected_cache:
        raise AssertionError(
            f"Expected X-Cache={expected_cache}, received {cache_status}"
        )
    return response, elapsed_ms


def wait_for_redis(container_id: str, timeout_s: int = 45) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        status = subprocess.run(
            [
                "docker",
                "inspect",
                "--format={{.State.Health.Status}}",
                container_id,
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if status == "healthy":
            print(f"Redis container {container_id} is healthy")
            return
        if status == "unhealthy":
            raise RuntimeError(f"Redis container is unhealthy: {container_id}")
        time.sleep(0.5)
    raise TimeoutError(f"Redis did not become healthy: {container_id}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8084")
    parser.add_argument(
        "--stop-redis",
        help="Stop this Redis container to verify graceful DB fallback",
    )
    args = parser.parse_args()

    email = f"lab4-{uuid.uuid4().hex[:12]}@example.com"
    phone_number = f"+38099{uuid.uuid4().int % 1_000_000:06d}"
    password = "password123"
    redis_stopped = False

    try:
        with httpx.Client(base_url=args.base_url, timeout=10) as client:
            request(
                client,
                "POST",
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "full_name": "Lab 4 Client",
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
            created, _ = request(
                client,
                "POST",
                "/api/v1/orders/",
                json={
                    "title": "Distributed cache test",
                    "weight": 10,
                    "distance": 50,
                },
            )
            order_id = created.json()["id"]
            path = f"/api/v1/orders/{order_id}"

            cold, cold_ms = request(client, "GET", path, expected_cache="MISS")
            hot, hot_ms = request(client, "GET", path, expected_cache="HIT")
            if cold.json() != hot.json():
                raise AssertionError("Cache hit returned different order data")
            if cold.headers.get("x-instance-id") == hot.headers.get("x-instance-id"):
                raise AssertionError(
                    "Cold and hot reads used the same backend instance; "
                    "shared cache behavior was not demonstrated"
                )
            print(f"Cold vs hot: {cold_ms:.1f}ms vs {hot_ms:.1f}ms")

            updated, _ = request(
                client,
                "PATCH",
                path,
                json={"title": "Updated after cache invalidation"},
            )
            if updated.json()["title"] != "Updated after cache invalidation":
                raise AssertionError("Order update did not persist")
            refreshed, _ = request(client, "GET", path, expected_cache="MISS")
            if refreshed.json()["title"] != "Updated after cache invalidation":
                raise AssertionError("Read after mutation returned stale data")
            request(client, "GET", path, expected_cache="HIT")

            if args.stop_redis:
                subprocess.run(
                    ["docker", "stop", args.stop_redis],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                redis_stopped = True
                fallback, _ = request(client, "GET", path, expected_cache="BYPASS")
                if fallback.json()["title"] != "Updated after cache invalidation":
                    raise AssertionError("Database fallback returned stale order data")
    finally:
        if redis_stopped:
            subprocess.run(
                ["docker", "start", args.stop_redis],
                check=True,
                capture_output=True,
                text=True,
            )
            wait_for_redis(args.stop_redis)

    print("Cache-aside, invalidation, and configured fallback checks passed.")


if __name__ == "__main__":
    main()
