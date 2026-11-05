#!/usr/bin/env python3
"""Interactive Python game for learning Docker."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError as exc:
    raise SystemExit("Dockerlings requires Python 3.11 or newer.") from exc


ROOT = Path(__file__).resolve().parent
PROGRESS_FILE = ROOT / ".dockerlings" / "progress.json"
EXPECTED_NGINX_TITLE = "<title>Welcome to nginx!</title>"


class AppError(Exception):
    """An expected, user-facing application error."""


class CheckError(AppError):
    """An exercise verification failed."""


@dataclass(frozen=True)
class Exercise:
    id: str
    title: str
    track: str
    depends_on: str


def load_exercises(root: Path = ROOT) -> list[Exercise]:
    config_path = root / "dockerlings.toml"
    try:
        with config_path.open("rb") as config_file:
            data = tomllib.load(config_file)
    except OSError as exc:
        raise AppError(f"Could not read {config_path}: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise AppError(f"Invalid config in {config_path}: {exc}") from exc

    raw_exercises = data.get("exercises")
    if not isinstance(raw_exercises, list) or not raw_exercises:
        raise AppError("dockerlings.toml must define at least one exercise.")

    exercises: list[Exercise] = []
    seen_ids: set[str] = set()
    for item in raw_exercises:
        if not isinstance(item, dict):
            raise AppError("Each exercise in dockerlings.toml must be a table.")
        exercise_id = item.get("id")
        title = item.get("title")
        track = item.get("track", "")
        depends_on = item.get("depends_on", "")
        if (
            not isinstance(exercise_id, str)
            or not re.fullmatch(r"[A-Za-z0-9_-]+", exercise_id)
            or not isinstance(title, str)
            or not title
            or not isinstance(track, str)
            or not isinstance(depends_on, str)
        ):
            raise AppError(f"Invalid exercise entry in dockerlings.toml: {item!r}")
        if exercise_id in seen_ids:
            raise AppError(f"Duplicate exercise ID in dockerlings.toml: {exercise_id}")
        seen_ids.add(exercise_id)
        exercises.append(Exercise(exercise_id, title, track, depends_on))

    for exercise in exercises:
        if exercise.depends_on and exercise.depends_on not in seen_ids:
            raise AppError(
                f"Exercise {exercise.id} depends on unknown exercise "
                f"{exercise.depends_on}."
            )
    return exercises


class ProgressStore:
    def __init__(self, path: Path = PROGRESS_FILE) -> None:
        self.path = path

    def load(self) -> set[str]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return set()
        except (OSError, json.JSONDecodeError) as exc:
            raise AppError(f"Could not load progress from {self.path}: {exc}") from exc

        completed = data.get("completed_ids") if isinstance(data, dict) else None
        if not isinstance(completed, list) or not all(
            isinstance(item, str) for item in completed
        ):
            raise AppError(
                f"Invalid progress file {self.path}: expected a completed_ids list."
            )
        return set(completed)

    def save(self, completed: set[str]) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=self.path.name,
                suffix=".tmp",
                delete=False,
            ) as progress_file:
                json.dump(
                    {"completed_ids": sorted(completed)},
                    progress_file,
                    indent=2,
                )
                progress_file.write("\n")
                temporary_path = Path(progress_file.name)
            os.replace(temporary_path, self.path)
        except OSError as exc:
            raise AppError(f"Could not save progress to {self.path}: {exc}") from exc
        finally:
            if "temporary_path" in locals():
                temporary_path.unlink(missing_ok=True)


def exercise_file(root: Path, exercise: Exercise, filename: str) -> str:
    path = root / "exercises" / exercise.id / filename
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AppError(f"Could not read {filename} for {exercise.id}: {exc}") from exc


def run_command(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        raise CheckError(f"Could not run {args[0]}: {exc}") from exc


def docker_command(
    root: Path, args: list[str], cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    result = run_command(["docker", *args], cwd or root)
    if result.returncode:
        detail = "\n".join(
            part for part in (result.stdout.strip(), result.stderr.strip()) if part
        )
        raise CheckError(
            f"Docker command failed ({' '.join(args)})."
            + (f"\n{detail}" if detail else "")
        )
    return result


def docker_json(root: Path, args: list[str]) -> Any:
    result = docker_command(root, args)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise CheckError(f"Docker returned invalid JSON: {exc}") from exc


def require_exercise_file(root: Path, exercise: Exercise, filename: str) -> Path:
    path = root / "exercises" / exercise.id / filename
    if not path.is_file():
        raise CheckError(f"Required file {filename!r} was not found in {exercise.id}.")
    return path


def assert_container_running(root: Path, name: str) -> dict[str, Any]:
    containers = docker_json(root, ["inspect", name])
    if not isinstance(containers, list) or len(containers) != 1:
        raise CheckError(f"Container {name!r} is not running.")
    container = containers[0]
    state = container.get("State") if isinstance(container, dict) else None
    if not isinstance(state, dict) or not state.get("Running", False):
        raise CheckError(f"Container {name!r} is not running.")
    return container


def http_body(port: int, expected: str) -> str:
    try:
        with urllib.request.urlopen(f"http://localhost:{port}", timeout=5) as response:
            body = response.read().decode("utf-8", errors="replace")
    except (OSError, urllib.error.URLError) as exc:
        raise CheckError(f"Could not reach the application on port {port}: {exc}") from exc
    if expected not in body:
        raise CheckError(
            f"Application on port {port} did not return {expected!r}. "
            f"Response was: {body[:500]!r}"
        )
    return body


def check_web_endpoint(root: Path, port: int, expected: str, container: str = "") -> None:
    time.sleep(2)
    if container:
        assert_container_running(root, container)
    http_body(port, expected)


def stop_and_remove_container(root: Path, name: str) -> None:
    run_command(["docker", "stop", name], root)
    run_command(["docker", "rm", "--force", name], root)


def remove_image(root: Path, name: str) -> None:
    run_command(["docker", "image", "rm", "--force", name], root)


def run_core_01(root: Path, exercise: Exercise) -> None:
    exercise_dir = root / "exercises" / exercise.id
    image = "dockerlings-core-01"
    docker_command(root, ["build", "--tag", image, str(exercise_dir)])
    try:
        output = docker_command(root, ["run", "--rm", image]).stdout.rstrip("\r\n")
        if output != "Hello Docker":
            raise CheckError(
                f"Expected container output 'Hello Docker', got {output!r}."
            )
    finally:
        remove_image(root, image)


def run_core_02(root: Path) -> None:
    container = assert_container_running(root, "my-nginx")
    network = container.get("NetworkSettings")
    ports = network.get("Ports") if isinstance(network, dict) else None
    bindings = ports.get("80/tcp") if isinstance(ports, dict) else None
    if not isinstance(bindings, list) or not any(
        isinstance(binding, dict) and binding.get("HostPort") == "8080"
        for binding in bindings
    ):
        raise CheckError("Container 'my-nginx' does not publish host port 8080 to port 80.")
    http_body(8080, EXPECTED_NGINX_TITLE)


def run_core_03(root: Path, exercise: Exercise) -> None:
    path = require_exercise_file(root, exercise, "logs.txt")
    raw_content = path.read_bytes()
    if raw_content.startswith((b"\xff\xfe", b"\xfe\xff")):
        encoding = "utf-16"
    elif raw_content.startswith(b"\xef\xbb\xbf"):
        encoding = "utf-8-sig"
    else:
        encoding = "utf-8"
    try:
        content = raw_content.decode(encoding)
    except UnicodeDecodeError as exc:
        raise CheckError(
            "Could not read logs.txt: expected UTF-8 or BOM-marked UTF-16 text. "
            "Save the container logs as UTF-8 or UTF-16 and retry."
        ) from exc
    expected = ("Starting process...", "Process is running.", "Process finished.")
    missing = [line for line in expected if line not in content]
    if missing:
        raise CheckError(f"Missing expected log lines in logs.txt: {', '.join(missing)}")


def run_core_04(root: Path, exercise: Exercise) -> None:
    path = require_exercise_file(root, exercise, "container-info.txt")
    name = "c4-checker-temp"
    try:
        docker_command(root, ["run", "--detach", "--name", name, "nginx"])
        time.sleep(1)
        version_output = docker_command(root, ["exec", name, "nginx", "-v"])
        expected_content = version_output.stdout + version_output.stderr
        expected = re.search(r"nginx version: nginx/[0-9]+\.[0-9]+\.[0-9]+", expected_content)
        actual = re.search(
            r"nginx version: nginx/[0-9]+\.[0-9]+\.[0-9]+",
            path.read_text(encoding="utf-8"),
        )
        if not expected or not actual or actual.group() != expected.group():
            expected_version = expected.group() if expected else "a version string"
            raise CheckError(
                "container-info.txt does not contain the Nginx version reported "
                f"by Docker. Expected {expected_version!r}."
            )
        path.unlink()
    finally:
        stop_and_remove_container(root, name)


def run_core_05(root: Path, exercise: Exercise) -> None:
    exercise_dir = root / "exercises" / exercise.id
    require_exercise_file(root, exercise, "Dockerfile")
    image, container = "dockerlings-core-05-test", "core-05-checker"
    docker_command(root, ["build", "--tag", image, str(exercise_dir)])
    try:
        docker_command(
            root,
            ["run", "--detach", "--name", container, "-p", "5005:5000", image],
        )
        check_web_endpoint(root, 5005, "Hello, Docker!", container)
    finally:
        stop_and_remove_container(root, container)
        remove_image(root, image)


def run_core_06(root: Path, exercise: Exercise) -> None:
    exercise_dir = root / "exercises" / exercise.id
    require_exercise_file(root, exercise, "Dockerfile")
    image, container = "dockerlings-core-06-test", "core-06-checker"
    docker_command(root, ["build", "--tag", image, str(exercise_dir)])
    try:
        info = docker_json(root, ["image", "inspect", image])[0]
        config = info.get("Config", {})
        labels = config.get("Labels") or {}
        if not labels.get("org.dockerlings.author"):
            raise CheckError("Image is missing LABEL org.dockerlings.author.")
        if "PORT=8000" not in config.get("Env", []):
            raise CheckError("Image ENV PORT must be set to 8000.")
        if "8000/tcp" not in (config.get("ExposedPorts") or {}):
            raise CheckError("Image must expose port 8000.")
        docker_command(
            root,
            ["run", "--detach", "--name", container, "-p", "8006:8000", image],
        )
        check_web_endpoint(root, 8006, "Hello from a configurable app!", container)
    finally:
        stop_and_remove_container(root, container)
        remove_image(root, image)


def run_core_07(root: Path, exercise: Exercise) -> None:
    exercise_dir = root / "exercises" / exercise.id
    require_exercise_file(root, exercise, "Dockerfile")
    image, container = "dockerlings-core-07-test", "core-07-checker"
    docker_command(root, ["build", "--tag", image, str(exercise_dir)])
    try:
        docker_command(
            root,
            ["run", "--detach", "--name", container, "-p", "8007:80", image],
        )
        check_web_endpoint(root, 8007, "My Custom Nginx Site", container)
    finally:
        stop_and_remove_container(root, container)
        remove_image(root, image)


def run_core_08(root: Path) -> None:
    name = "c8-checker-postgres"
    docker_json(root, ["volume", "inspect", "pgdata"])
    try:
        docker_command(
            root,
            [
                "run", "--detach", "--name", name, "-e", "POSTGRES_PASSWORD=mysecretpassword",
                "-v", "pgdata:/var/lib/postgresql/data", "postgres:16",
            ],
        )
        for _ in range(20):
            logs = run_command(["docker", "logs", name], root)
            if "database system is ready to accept connections" in logs.stdout + logs.stderr:
                break
            time.sleep(1)
        else:
            raise CheckError(f"PostgreSQL in {name!r} did not become ready.")
        query = (
            "SELECT title FROM dvd_rentals "
            "WHERE title = 'The Grand Budapest Hotel';"
        )
        result = run_command(
            [
                "docker", "exec", name, "psql", "-U", "postgres", "-d", "postgres",
                "-tA", "-c", query,
            ],
            root,
        )
        if result.returncode:
            raise CheckError(
                "Could not query dvd_rentals in the postgres database. "
                "Check the table and database names in your solution."
            )
        if result.stdout.strip() != "The Grand Budapest Hotel":
            raise CheckError("The expected DVD row was not found in the pgdata volume.")
    finally:
        stop_and_remove_container(root, name)


def run_core_09(root: Path, exercise: Exercise) -> None:
    path = require_exercise_file(root, exercise, "app/index.html")
    name, port = "c9-dev-server", 8009
    original = path.read_bytes()
    backup = path.with_name(path.name + ".bak")
    try:
        backup.write_bytes(original)
        container = assert_container_running(root, name)
        mounts = container.get("Mounts", [])
        mount = next(
            (
                item for item in mounts
                if item.get("Destination") == "/usr/share/nginx/html"
            ),
            None,
        )
        if not mount or mount.get("Type") != "bind" or mount.get("RW") is not False:
            raise CheckError("Expected a read-only bind mount at /usr/share/nginx/html.")
        path.write_text("<h1>Version 2 - Modified by Checker</h1>\n", encoding="utf-8")
        time.sleep(1)
        http_body(port, "<h1>Version 2 - Modified by Checker</h1>")
    finally:
        path.write_bytes(original)
        backup.unlink(missing_ok=True)


def find_bash() -> str | None:
    bash = shutil.which("bash")
    if bash:
        return bash
    if os.name == "nt":
        for candidate in (
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Git" / "bin" / "bash.exe",
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Git" / "usr" / "bin" / "bash.exe",
        ):
            if candidate.is_file():
                return str(candidate)
    return None


def run_core_10(root: Path, exercise: Exercise) -> None:
    network = run_command(["docker", "network", "inspect", "c10-network"], root)
    if network.returncode:
        raise CheckError(
            "Docker network 'c10-network' was not found. Create it with "
            "'docker network create c10-network' first."
        )
    script = require_exercise_file(root, exercise, "run-containers.sh")
    bash = find_bash()
    if not bash:
        raise CheckError(
            "This exercise asks you to run a Bash script. Install Git for Windows "
            "(Git Bash) and retry; no Bash installation is needed for the other checks."
        )
    try:
        result = run_command([bash, "run-containers.sh"], script.parent)
        if result.returncode:
            raise CheckError(
                f"run-containers.sh failed:\n{result.stdout}{result.stderr}".strip()
            )
        time.sleep(3)
        for name in ("c10-app", "c10-db"):
            container = assert_container_running(root, name)
            if container.get("HostConfig", {}).get("NetworkMode") != "c10-network":
                raise CheckError(f"Container {name!r} is not on the c10-network network.")
        result = run_command(
            ["docker", "exec", "c10-app", "ping", "-c", "1", "c10-db"], root
        )
        if result.returncode:
            raise CheckError(
                "c10-app could not resolve and ping c10-db by its container name."
            )
    finally:
        for name in ("c10-app", "c10-db"):
            stop_and_remove_container(root, name)


def run_core_11(root: Path, exercise: Exercise) -> None:
    exercise_dir = root / "exercises" / exercise.id
    require_exercise_file(root, exercise, "Dockerfile")
    image, name = "dockerlings-c11-test", "c11-server"
    docker_command(root, ["build", "--tag", image, str(exercise_dir)])
    try:
        info = docker_json(root, ["image", "inspect", image])[0]
        if "8080/tcp" not in (info.get("Config", {}).get("ExposedPorts") or {}):
            raise CheckError("Image must expose port 8080.")
        container = assert_container_running(root, name)
        bindings = (
            container.get("NetworkSettings", {})
            .get("Ports", {})
            .get("8080/tcp") or []
        )
        if not any(item.get("HostPort") == "8011" for item in bindings):
            raise CheckError("Container port 8080 must be published on host port 8011.")
        check_web_endpoint(root, 8011, "Hello from a container", name)
    finally:
        remove_image(root, image)


def compose_down(root: Path, exercise_dir: Path, *args: str) -> None:
    run_command(["docker", "compose", "down", *args], exercise_dir)


def run_core_12(root: Path, exercise: Exercise) -> None:
    exercise_dir = root / "exercises" / exercise.id
    require_exercise_file(root, exercise, "docker-compose.yml")
    try:
        docker_command(root, ["compose", "up", "-d"], exercise_dir)
        container = assert_container_running(root, "c12-redis")
        bindings = (
            container.get("NetworkSettings", {})
            .get("Ports", {})
            .get("6379/tcp") or []
        )
        if not any(item.get("HostPort") == "6379" for item in bindings):
            raise CheckError("Redis port 6379 is not published.")
        result = docker_command(
            root,
            [
                "run", "--rm", "--network", "core-12_default", "redis:alpine",
                "redis-cli", "-h", "redis-server", "PING",
            ],
        )
        if "PONG" not in result.stdout:
            raise CheckError("Redis did not respond with PONG.")
    finally:
        compose_down(root, exercise_dir, "-v", "--remove-orphans")


def compose_visit_counter(root: Path, port: int, expected: str) -> None:
    time.sleep(3)
    http_body(port, expected)


def run_core_13(root: Path, exercise: Exercise) -> None:
    exercise_dir = root / "exercises" / exercise.id
    require_exercise_file(root, exercise, "docker-compose.yml")
    try:
        docker_command(root, ["compose", "up", "-d", "--build"], exercise_dir)
        assert_container_running(root, "c13-web")
        assert_container_running(root, "c13-redis")
        compose_visit_counter(root, 8013, "visited 1 times")
        compose_visit_counter(root, 8013, "visited 2 times")
    finally:
        compose_down(root, exercise_dir, "-v", "--rmi", "local", "--remove-orphans")


def run_core_14(root: Path, exercise: Exercise) -> None:
    exercise_dir = root / "exercises" / exercise.id
    require_exercise_file(root, exercise, "docker-compose.yml")
    try:
        docker_command(root, ["compose", "up", "-d", "--build"], exercise_dir)
        web = assert_container_running(root, "c14-web")
        redis = assert_container_running(root, "c14-redis")
        expected_network = f"{exercise_dir.name}_c14-app-net"
        for container in (web, redis):
            networks = container.get("NetworkSettings", {}).get("Networks", {})
            if expected_network not in networks:
                raise CheckError(f"A service is not connected to {expected_network!r}.")
        mounts = redis.get("Mounts", [])
        if not any(
            mount.get("Destination") == "/data" and mount.get("Type") == "volume"
            for mount in mounts
        ):
            raise CheckError("No named volume is mounted on the Redis service at /data.")
        compose_visit_counter(root, 8014, "visited 1 times")
        compose_down(root, exercise_dir)
        docker_command(root, ["compose", "up", "-d"], exercise_dir)
        time.sleep(3)
        compose_visit_counter(root, 8014, "visited 2 times")
    finally:
        compose_down(root, exercise_dir, "-v", "--rmi", "local", "--remove-orphans")


def run_core_15(root: Path, exercise: Exercise) -> None:
    exercise_dir = root / "exercises" / exercise.id
    require_exercise_file(root, exercise, "Dockerfile")
    require_exercise_file(root, exercise, "app/app.py")
    image, naive_image, name = (
        "dockerlings-core-15-user", "dockerlings-core-15-naive", "core-15-checker"
    )
    docker_command(root, ["build", "--tag", image, str(exercise_dir)])
    try:
        with tempfile.TemporaryDirectory(prefix=".dockerlings-", dir=exercise_dir) as temp:
            dockerfile = Path(temp) / "Dockerfile"
            dockerfile.write_text(
                "FROM python:3.12\n"
                "WORKDIR /app\n"
                "COPY app/app.py .\n"
                "EXPOSE 8080\n"
                'CMD ["python", "app.py"]\n',
                encoding="utf-8",
            )
            docker_command(
                root,
                [
                    "build", "--tag", naive_image, "--file", str(dockerfile),
                    str(exercise_dir),
                ],
            )
        user_size = docker_json(root, ["image", "inspect", image])[0].get("Size", 0)
        naive_size = docker_json(root, ["image", "inspect", naive_image])[0].get("Size", 0)
        if user_size >= naive_size / 2:
            raise CheckError(
                "Your final image is not significantly smaller than a single-stage build."
            )
        docker_command(
            root,
            ["run", "--detach", "--name", name, "-p", "8015:8080", image],
        )
        check_web_endpoint(root, 8015, "Hello from a Python multi-stage build!", name)
    finally:
        stop_and_remove_container(root, name)
        remove_image(root, image)
        remove_image(root, naive_image)


def run_check(root: Path, exercise: Exercise) -> str:
    checkers = {
        "core-01": lambda: run_core_01(root, exercise),
        "core-02": lambda: run_core_02(root),
        "core-03": lambda: run_core_03(root, exercise),
        "core-04": lambda: run_core_04(root, exercise),
        "core-05": lambda: run_core_05(root, exercise),
        "core-06": lambda: run_core_06(root, exercise),
        "core-07": lambda: run_core_07(root, exercise),
        "core-08": lambda: run_core_08(root),
        "core-09": lambda: run_core_09(root, exercise),
        "core-10": lambda: run_core_10(root, exercise),
        "core-11": lambda: run_core_11(root, exercise),
        "core-12": lambda: run_core_12(root, exercise),
        "core-13": lambda: run_core_13(root, exercise),
        "core-14": lambda: run_core_14(root, exercise),
        "core-15": lambda: run_core_15(root, exercise),
    }
    checker = checkers.get(exercise.id)
    if checker is None:
        raise CheckError(f"No Python checker is defined for {exercise.id}.")
    checker()
    return ""


def dependency_is_complete(exercise: Exercise, completed: set[str]) -> bool:
    return not exercise.depends_on or exercise.depends_on in completed


def clear_screen() -> None:
    if sys.stdout.isatty() and os.environ.get("TERM") != "dumb":
        print("\033[2J\033[H", end="")


def print_game_header(exercises: list[Exercise], completed: set[str]) -> None:
    completed_count = sum(exercise.id in completed for exercise in exercises)
    total = len(exercises)
    bar_width = 24
    filled = round(bar_width * completed_count / total)
    progress_bar = "#" * filled + "-" * (bar_width - filled)
    print("=" * 64)
    print("  DOCKERGAME: THE CONTAINER QUEST")
    print("  Build your skills. Complete all 15 levels.")
    print("=" * 64)
    print(f"  CAMPAIGN  [{progress_bar}] {completed_count}/{total} levels")
    print(f"  EXPERIENCE  {completed_count * 100} XP")
    print("=" * 64)


def print_exercises(exercises: list[Exercise], completed: set[str], selected: int) -> None:
    groups = (
        ("CONTAINER BASICS", 0, 4),
        ("BUILD AN IMAGE", 4, 7),
        ("DATA & LIVE UPDATES", 7, 9),
        ("CONTAINER NETWORKING", 9, 11),
        ("COMPOSE & PRODUCTION", 11, len(exercises)),
    )
    print("\n  LEVEL MAP")
    print("  " + "-" * 60)
    for label, start, end in groups:
        if start >= len(exercises):
            continue
        print(f"\n  {label}")
        for index in range(start, min(end, len(exercises))):
            exercise = exercises[index]
            if exercise.id in completed:
                status = "DONE"
            elif dependency_is_complete(exercise, completed):
                status = "NEXT"
            else:
                status = "LOCKED"
            marker = ">" if index == selected else " "
            print(
                f"  {marker} {index + 1:02}  [{status:6}] "
                f"{exercise.title}  ({exercise.id})"
            )
    print("\n  Choose a level number, or q to quit.")


def watch(root: Path, exercises: list[Exercise], progress: ProgressStore) -> int:
    completed = progress.load()
    selected = next(
        (index for index, exercise in enumerate(exercises) if exercise.id not in completed),
        0,
    )
    while True:
        clear_screen()
        print_game_header(exercises, completed)
        print_exercises(exercises, completed, selected)
        choice = input("\n> ").strip().lower()
        if choice in {"q", "quit"}:
            print(f"\nThanks for playing DockerGame! Final score: {len(completed) * 100} XP.")
            return 0
        if not choice.isdigit() or not 1 <= int(choice) <= len(exercises):
            print("Choose a level shown on the map, or q to quit.")
            continue

        selected = int(choice) - 1
        exercise = exercises[selected]
        if not dependency_is_complete(exercise, completed):
            print(
                f"\nLevel locked. Complete {exercise.depends_on} to unlock "
                f"{exercise.id}."
            )
            continue

        clear_screen()
        print_game_header(exercises, completed)
        print(f"\n  LEVEL {selected + 1:02}  |  {exercise.id} - {exercise.title}")
        print("  " + "-" * 60 + "\n")
        print(exercise_file(root, exercise, "prompt.md").rstrip())
        while True:
            action = input("\n[c]heck level  [h]int  [m]ap  [q]uit: ").strip().lower()
            if action in {"q", "quit"}:
                return 0
            if action in {"l", "list", "m", "map"}:
                break
            if action in {"h", "hint"}:
                print(f"\n  HINT: {exercise.title}\n")
                print(exercise_file(root, exercise, "hint.md").rstrip())
                continue
            if action in {"c", "check"}:
                try:
                    output = run_check(root, exercise)
                except CheckError as exc:
                    print(f"\n  CHECK FAILED\n  {exc}")
                else:
                    if output:
                        print(output)
                    completed.add(exercise.id)
                    progress.save(completed)
                    print(
                        f"\n  LEVEL COMPLETE! +100 XP  |  "
                        f"Campaign: {len(completed)}/{len(exercises)}"
                    )
                    print("  Progress saved.")
                continue
            print("Choose c, h, m, or q.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dockergame",
        description="Play DockerGame and learn Docker by completing 15 levels.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=("play", "watch", "check"),
        default="play",
        help="play the game (default) or check one level directly",
    )
    parser.add_argument("exercise_id", nargs="?", help="level ID for the check command")
    args = parser.parse_args(argv)
    if args.command == "watch" and args.exercise_id:
        parser.error("watch does not accept an exercise ID")

    try:
        exercises = load_exercises()
        if args.command in {"play", "watch"}:
            return watch(ROOT, exercises, ProgressStore())

        exercise = next((item for item in exercises if item.id == args.exercise_id), None)
        if args.exercise_id is None:
            exercise = next((item for item in exercises if item.id == "core-01"), None)
        if exercise is None:
            valid_ids = ", ".join(item.id for item in exercises)
            raise AppError(f"Unknown exercise {args.exercise_id!r}. Available: {valid_ids}")
        print(f"Checking exercise: {exercise.id}...")
        output = run_check(ROOT, exercise)
        if output:
            print(output)
        completed = ProgressStore().load()
        completed.add(exercise.id)
        ProgressStore().save(completed)
        print(f"✅ Exercise {exercise.id} passed. Progress saved.")
        return 0
    except AppError as exc:
        if args.command == "check":
            print(f"❌ Exercise {args.exercise_id or 'core-01'} failed.", file=sys.stderr)
        print(exc, file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
