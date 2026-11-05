# DockerGame

**A terminal adventure for learning Docker, one level at a time.**

DockerGame turns 15 practical Docker exercises into a progressive campaign. Read a mission, try the Docker commands yourself, unlock hints when you need them, and verify your work to earn XP.

## The campaign

| Levels | Mission |
|---|---|
| 01–04 | Run containers, inspect logs, and work with running containers |
| 05–07 | Build images and use Dockerfile instructions |
| 08–09 | Persist data and use bind mounts |
| 10–11 | Connect containers and publish ports |
| 12–14 | Build multi-service applications with Compose |
| 15 | Use a multi-stage build for a smaller Python runtime image |

## Play

Install Python 3.11+ and Docker. On Windows, install [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/).

```powershell
git clone https://github.com/af-codex/DockerGame.git
cd DockerGame
python dockergame.py
```

Select a level from the campaign map. In a mission, enter:

- `c` to check your solution and earn 100 XP
- `h` to show the level hint
- `m` to return to the campaign map
- `q` to quit

Your completed levels are saved locally in `.dockerlings/progress.json`, which is ignored by Git. Each clone starts with a fresh campaign at level 1 and keeps its own progress without uploading it.

You can also verify a level directly:

```powershell
python dockergame.py check core-01
```

The game and exercise verifiers run in Python on Windows, macOS, and Linux. Level 10 asks you to create and run a Bash script; checking this level on Windows requires Git Bash. The other levels do not require Bash.

## Run the tests

```powershell
python -m unittest discover -s tests -v
```

## License

Distributed under the MIT License. See [LICENSE](./LICENSE).

## Contributors

- [af-codex](https://github.com/af-codex)
