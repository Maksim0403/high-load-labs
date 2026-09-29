"""Concurrent load generator for the lab 3 Nginx upstream."""

import argparse
import asyncio
import csv
import math
import subprocess
import time
from collections import Counter
from pathlib import Path

import httpx


def percentile(values: list[float], percent: int) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(percent / 100 * len(ordered)) - 1)]


def restart_and_wait(container_id: str, timeout_s: int = 45) -> None:
    subprocess.run(
        ["docker", "start", container_id],
        check=True,
        capture_output=True,
        text=True,
    )
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
            print(f"restored backend container {container_id} (healthy)")
            return
        if status == "unhealthy":
            raise RuntimeError(
                f"Backend container did not become healthy: {container_id}"
            )
        time.sleep(0.5)
    raise TimeoutError(
        f"Timed out waiting for backend container health: {container_id}"
    )


async def run_load(args):
    semaphore = asyncio.Semaphore(args.concurrency)
    samples = []

    async with httpx.AsyncClient(
        base_url=args.base_url,
        timeout=args.timeout,
        trust_env=False,
    ) as client:
        for _ in range(min(5, args.concurrency)):
            response = await client.get(args.path)
            response.raise_for_status()
            if not response.headers.get("x-instance-id"):
                raise RuntimeError("Response missing X-Instance-ID")

        async def send_request(index: int) -> None:
            async with semaphore:
                started = time.perf_counter()
                try:
                    response = await client.get(args.path)
                    elapsed_ms = (time.perf_counter() - started) * 1000
                    instance_id = response.headers.get("x-instance-id", "")
                    samples.append(
                        {
                            "request": index,
                            "status": (
                                response.status_code
                                if instance_id
                                else "missing-instance-id"
                            ),
                            "instance_id": instance_id,
                            "latency_ms": elapsed_ms,
                        }
                    )
                except httpx.HTTPError as exc:
                    elapsed_ms = (time.perf_counter() - started) * 1000
                    samples.append(
                        {
                            "request": index,
                            "status": "error",
                            "instance_id": "",
                            "latency_ms": elapsed_ms,
                            "error": str(exc),
                        }
                    )

        started = time.perf_counter()
        await asyncio.gather(
            *(send_request(index) for index in range(args.requests))
        )
        elapsed_s = time.perf_counter() - started

    return samples, elapsed_s


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8083")
    parser.add_argument("--path", default="/health")
    parser.add_argument("--requests", type=int, default=500)
    parser.add_argument("--concurrency", type=int, default=50)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--label", default="")
    parser.add_argument("--csv", type=Path)
    parser.add_argument(
        "--stop-instance",
        help="Stop a running backend container for the duration of the test",
    )
    args = parser.parse_args()

    if args.requests <= 0 or args.concurrency <= 0 or args.timeout <= 0:
        parser.error("requests, concurrency, and timeout must be positive")

    instance_stopped = False
    try:
        if args.stop_instance:
            subprocess.run(
                ["docker", "stop", args.stop_instance],
                check=True,
                capture_output=True,
                text=True,
            )
            instance_stopped = True
            time.sleep(2.5)
        samples, elapsed_s = asyncio.run(run_load(args))
    finally:
        if instance_stopped:
            restart_and_wait(args.stop_instance)
    latencies = [sample["latency_ms"] for sample in samples]
    statuses = Counter(sample["status"] for sample in samples)
    instances = Counter(
        sample["instance_id"] for sample in samples if sample["instance_id"]
    )
    failures = sum(
        count
        for status, count in statuses.items()
        if status == "error"
        or status == "missing-instance-id"
        or not isinstance(status, int)
        or not 200 <= status < 300
    )
    successes = len(samples) - failures

    print(
        f"label={args.label or 'unspecified'} requests={args.requests} "
        f"concurrency={args.concurrency} duration={elapsed_s:.2f}s "
        f"throughput={len(samples) / elapsed_s:.1f} req/s"
    )
    print(
        f"success={successes} failed={len(samples) - successes} "
        f"p50={percentile(latencies, 50):.1f}ms "
        f"p95={percentile(latencies, 95):.1f}ms "
        f"p99={percentile(latencies, 99):.1f}ms"
    )
    print("instance distribution:")
    for instance, count in sorted(instances.items()):
        print(f"  {instance}: {count} ({count / len(samples) * 100:.1f}%)")
    if statuses:
        print(f"HTTP status distribution: {dict(statuses)}")

    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        with args.csv.open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(
                output,
                fieldnames=[
                    "request",
                    "status",
                    "instance_id",
                    "latency_ms",
                    "error",
                ],
            )
            writer.writeheader()
            writer.writerows(samples)
        print(f"raw samples saved to {args.csv}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
