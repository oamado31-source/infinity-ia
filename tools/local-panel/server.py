# SPDX-License-Identifier: Apache-2.0
"""Infinity AI Local Dev Panel: loopback-only, allowlisted desktop workflows.

Run from the repository: python3 tools/local-panel/server.py
Python standard library only. No shell execution and no arbitrary command endpoint.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shlex
import signal
import sqlite3
import subprocess
import sys
import threading
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[2]
STATIC = Path(__file__).resolve().parent / "static"
DATA = Path.home() / ".infinity-ai" / "local-panel"
LOGS = DATA / "logs"
CAMPAIGNS = Path.home() / ".infinity-ai" / "campaigns"
CONFIG_PATH = DATA / "config.json"
HOST = "127.0.0.1"
DEFAULT_PORT = 8766
BRANCH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,90}$")
CAMPAIGN = re.compile(r"^lab-[a-z0-9-]{1,48}$")
HOST_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,180}$")
USER_NAME = re.compile(r"^(?=.{1,80}$)[A-Za-z0-9_.-]+(?: [A-Za-z0-9_.-]+)*$")
MODEL = re.compile(r"^[A-Za-z0-9._:/-]{1,100}$")
SAFE_JOB = re.compile(r"^[a-f0-9]{16}$")
MAX_INPUT = 8192
CONFIG_DEFAULTS = {
    "campaign": "lab-s1f",
    "manifest": "",
    "ssh_host": "",
    "ssh_user": "",
    "ssh_key": "",
    "model": "qwen3:8b",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def valid_branch(name: object) -> bool:
    """Reject git option-like names and unsafe ref patterns even without a shell."""
    return (isinstance(name, str) and bool(BRANCH.fullmatch(name))
            and ".." not in name and "//" not in name and "@{" not in name
            and not name.endswith(("/", ".", ".lock"))
            and not any(part.startswith(".") or part.endswith(".") for part in name.split("/"))
            and name != "HEAD")


def valid_campaign(name: object) -> bool:
    return isinstance(name, str) and bool(CAMPAIGN.fullmatch(name)) and ".." not in name


def git(*args: str, timeout: int = 8) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, encoding="utf-8", errors="replace",
        capture_output=True, timeout=timeout, check=False,
    )
    if result.returncode:
        raise ValueError((result.stderr or result.stdout).strip() or "git failed")
    return result.stdout.strip()


def current_branch() -> str:
    value = git("symbolic-ref", "--quiet", "--short", "HEAD")
    if not valid_branch(value):
        raise ValueError("Branch atual inválida ou HEAD destacado.")
    return value


def remote_branches() -> list[str]:
    value = git("for-each-ref", "--format=%(refname:strip=3)", "refs/remotes/origin")
    return sorted(x for x in value.splitlines() if valid_branch(x))


def clean_worktree() -> bool:
    return not bool(git("status", "--porcelain", "--untracked-files=normal"))


def test_python() -> str:
    venv = ROOT / ".venv" / "bin" / "python"
    return str(venv) if venv.is_file() else sys.executable


def settings_validate(doc: object) -> dict[str, str]:
    if not isinstance(doc, dict):
        raise ValueError("Configuração inválida.")
    cfg = {}
    for key, default in CONFIG_DEFAULTS.items():
        value = doc.get(key, default)
        if not isinstance(value, str) or len(value) > 1024 or "\n" in value or "\r" in value:
            raise ValueError(f"Valor inválido: {key}")
        cfg[key] = value.strip()
    if not valid_campaign(cfg["campaign"]):
        raise ValueError("A campanha deve começar por lab- e conter somente letras, números e hífens.")
    if cfg["ssh_host"] and not HOST_NAME.fullmatch(cfg["ssh_host"]):
        raise ValueError("Host SSH inválido.")
    if cfg["ssh_user"] and not USER_NAME.fullmatch(cfg["ssh_user"]):
        raise ValueError("Usuário SSH inválido.")
    if cfg["ssh_user"] and not cfg["ssh_host"]:
        raise ValueError("Preencha também o host SSH.")
    if cfg["ssh_key"] and not cfg["ssh_host"]:
        raise ValueError("Preencha também o host SSH da chave.")
    if not MODEL.fullmatch(cfg["model"]):
        raise ValueError("Nome do modelo inválido.")
    if cfg["manifest"]:
        p = Path(cfg["manifest"]).expanduser()
        if p.suffix.lower() != ".json":
            raise ValueError("O manifesto deve ser um arquivo JSON.")
        cfg["manifest"] = str(p)
    if cfg["ssh_key"]:
        cfg["ssh_key"] = str(Path(cfg["ssh_key"]).expanduser())
    return cfg


def read_settings() -> dict[str, str]:
    if not CONFIG_PATH.exists():
        return dict(CONFIG_DEFAULTS)
    try:
        return settings_validate(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    except (ValueError, OSError, json.JSONDecodeError):
        return dict(CONFIG_DEFAULTS)


def write_settings(doc: object) -> dict[str, str]:
    cfg = settings_validate(doc)
    DATA.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = CONFIG_PATH.with_suffix(".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(cfg, out, ensure_ascii=False, indent=2)
            out.write("\n")
        os.replace(tmp, CONFIG_PATH)
        CONFIG_PATH.chmod(0o600)
    finally:
        if tmp.exists():
            tmp.unlink()
    return cfg


def lab_paths(cfg: dict[str, str]) -> tuple[Path, Path]:
    name = cfg["campaign"]
    if not valid_campaign(name):
        raise ValueError("Identificador de campanha inválido.")
    return CAMPAIGNS / (name + ".sqlite3"), DATA / (name + "-overlay.json")


def lab_env(cfg: dict[str, str]) -> dict[str, str]:
    env = os.environ.copy()
    host = cfg["ssh_host"]
    if host:
        argv = ["ssh", "-o", "IdentitiesOnly=yes", "-o", "BatchMode=yes",
                "-o", "ConnectTimeout=10"]
        if cfg["ssh_key"]:
            key = Path(cfg["ssh_key"]).expanduser()
            if not key.is_file():
                raise ValueError("Chave SSH não encontrada.")
            argv.extend(["-i", str(key)])
        if cfg["ssh_user"]:
            argv.extend(["-l", cfg["ssh_user"]])
        argv.append(host)
        env["INFINITY_LAB_SSH"] = shlex.join(argv)
    if not env.get("INFINITY_LAB_SSH"):
        raise ValueError("Configure o SSH da VM no painel ou inicie o painel com INFINITY_LAB_SSH.")
    env["PYTHONUNBUFFERED"] = "1"
    return env


def checked_game_time(db: Path, campaign: str) -> int:
    """Do not let the existing pin script create an unanchored pin on an empty campaign."""
    if not db.is_file():
        raise ValueError("Banco de laboratório ainda não criado. Inicie o serviço primeiro.")
    with sqlite3.connect("file:" + db.as_posix() + "?mode=ro", uri=True, timeout=3) as conn:
        row = conn.execute("SELECT campaign_id FROM campaigns").fetchone()
        if not row or row[0] != campaign:
            raise ValueError("O banco pertence a outra campanha.")
        last = conn.execute("SELECT MAX(game_time) FROM events WHERE game_time IS NOT NULL").fetchone()[0]
    if not isinstance(last, int) or last < 0:
        raise ValueError("Ainda não há observação com tempo de jogo. Carregue um save e aguarde o serviço.")
    return last


def tail(path: Path, limit: int = 180_000) -> str:
    if not path.is_file():
        return ""
    with path.open("rb") as fh:
        fh.seek(0, 2)
        size = fh.tell()
        fh.seek(max(0, size - limit))
        text = fh.read().decode("utf-8", errors="replace")
    return ("[início truncado]\n" if size > limit else "") + text


@dataclass
class Job:
    id: str
    action: str
    label: str
    started: str
    status: str = "queued"
    ended: str | None = None
    code: int | None = None

    def to_json(self) -> dict:
        return dict(id=self.id, action=self.action, label=self.label,
                    started=self.started, status=self.status,
                    ended=self.ended, code=self.code)


class Panel:
    def __init__(self) -> None:
        DATA.mkdir(parents=True, exist_ok=True, mode=0o700)
        LOGS.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = threading.RLock()
        self.token = secrets.token_urlsafe(32)
        self.jobs: dict[str, Job] = {}
        self.active: str | None = None
        self.service: subprocess.Popen | None = None
        self.service_campaign: str | None = None
        self.service_started: str | None = None
        self.service_status = "stopped"
        self.load_job_history()

    def load_job_history(self) -> None:
        """Show the most recent task logs after the panel itself is restarted."""
        candidates = sorted(LOGS.glob("job-*.log"), key=lambda p: p.stat().st_mtime)
        for path in candidates[-40:]:
            ident = path.stem.removeprefix("job-")
            if not SAFE_JOB.fullmatch(ident):
                continue
            try:
                with path.open("r", encoding="utf-8", errors="replace") as f:
                    first = f.readline().strip()
                recent = tail(path, 6000)
                match = re.match(r"^\[([^\]]+)\] (.+)$", first)
                started = match.group(1) if match else datetime.fromtimestamp(
                    path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")
                label = match.group(2) if match else "Tarefa arquivada"
                finish = re.search(r"Finalizado: código (\d+)", recent)
                code = int(finish.group(1)) if finish else None
                status = "ok" if code == 0 else ("error" if code is not None or "ERRO:" in recent
                                                 else "interrupted")
                self.jobs[ident] = Job(ident, "archived", label, started, status, None, code)
            except OSError:
                continue

    def write_log(self, path: Path, line: str) -> None:
        if path.name == "service.log" and path.exists() and path.stat().st_size > 2_000_000:
            backup = LOGS / "service.previous.log"
            os.replace(path, backup)
        with path.open("a", encoding="utf-8", errors="replace") as f:
            f.write(line)

    def service_running(self) -> bool:
        with self.lock:
            if self.service is None:
                return False
            if self.service.poll() is not None:
                self.service_status = "exited"
                return False
            return True

    def job_commands(self, action: str, options: dict) -> tuple[str, list[list[str]]]:
        py = test_python()
        if action == "fetch":
            return "Buscar atualizações", [["git", "fetch", "origin", "--prune"]]
        if action in ("pull", "sync", "switch"):
            if self.service_running():
                raise ValueError("Pare o laboratório antes de modificar a cópia local.")
            if not clean_worktree():
                raise ValueError("Existem alterações locais. Verifique git status antes de atualizar/trocar.")
            if action == "switch":
                branch = options.get("branch")
                if not valid_branch(branch) or branch not in remote_branches():
                    raise ValueError("Branch remota não encontrada. Execute Buscar atualizações.")
                exists = subprocess.run(["git", "show-ref", "--verify", "--quiet",
                                         "refs/heads/" + branch], cwd=ROOT, check=False).returncode == 0
                cmd = ["git", "switch", branch] if exists else [
                    "git", "switch", "--track", "origin/" + branch]
                return "Trocar para " + branch, [cmd]
            current = current_branch()
            pull = ["git", "pull", "--ff-only", "origin", current]
            if action == "pull":
                return "Atualizar " + current, [pull]
            return "Sincronizar " + current, [["git", "fetch", "origin", "--prune"], pull]
        if action == "setup":
            cmds = []
            venv = ROOT / ".venv" / "bin" / "python"
            if not venv.is_file():
                cmds.append([sys.executable, "-m", "venv", ".venv"])
            cmds.append([str(venv), "-m", "pip", "install", "--disable-pip-version-check",
                         "-r", "requirements-test.txt"])
            return "Preparar ambiente Python", cmds
        tasks = {
            "syntax": ("Compilar Python", [[py, "-m", "compileall", "-q", "src", "tests", "examples/chronology"]]),
            "identity": ("Testes de identidade", [[py, "-m", "unittest", "discover", "-s", "tests",
                                                      "-p", "test_identity.py", "-v"]]),
            "tests": ("Testes principais", [[py, "-m", "unittest", "discover", "-s", "tests",
                                                "-p", "test_*.py", "-v"]]),
            "chronology": ("Testes de cronologia", [[py, "-m", "unittest", "discover",
                                                     "-s", "examples/chronology", "-p", "test_*.py", "-q"]]),
            "adrs": ("Proteção de ADRs", [[py, "scripts/check_historical_adrs.py"]]),
            "public": ("Arquivos protegidos", [[py, "scripts/check_public_files.py"]]),
        }
        if action == "all":
            return "Validação completa", sum((tasks[key][1] for key in
                    ("syntax", "identity", "tests", "chronology", "adrs", "public")), [])
        if action == "pin":
            cfg = read_settings()
            if not self.service_running():
                raise ValueError("Inicie o serviço de diálogo e aguarde uma observação antes do pin.")
            if self.service_campaign != cfg["campaign"]:
                raise ValueError("Campanha configurada difere da campanha do serviço ativo.")
            db, _ = lab_paths(cfg)
            checked_game_time(db, cfg["campaign"])
            lab_env(cfg)
            return "Pin canônico " + cfg["campaign"], [[py, "tools/windows-lab/pin_canon_pack.py",
                "--campaign", cfg["campaign"], "--db", str(db), "--year", "1369"]]
        if action not in tasks:
            raise ValueError("Ação não autorizada.")
        return tasks[action]

    def start_job(self, action: str, options: dict) -> Job:
        if not isinstance(action, str) or not isinstance(options, dict):
            raise ValueError("Requisição inválida.")
        with self.lock:
            if self.active is not None:
                raise ValueError("Já existe uma tarefa em execução.")
            label, commands = self.job_commands(action, options)
            ident = secrets.token_hex(8)
            job = Job(ident, action, label, now())
            self.jobs[ident] = job
            self.active = ident
            thread = threading.Thread(target=self._run_job, args=(job, commands),
                                      name="panel-job-" + ident, daemon=True)
            thread.start()
            return job

    def _run_job(self, job: Job, commands: list[list[str]]) -> None:
        logfile = LOGS / ("job-" + job.id + ".log")
        job.status = "running"
        code = 1
        try:
            env = lab_env(read_settings()) if job.action == "pin" else os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            self.write_log(logfile, f"[{now()}] {job.label}\n")
            for command in commands:
                # All commands were built by job_commands; user text is never used as a shell.
                self.write_log(logfile, "$ " + shlex.join(command) + "\n")
                process = subprocess.Popen(command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           text=True, encoding="utf-8", errors="replace",
                                           bufsize=1)
                assert process.stdout is not None
                for line in process.stdout:
                    self.write_log(logfile, line)
                code = process.wait()
                if code:
                    break
            job.status = "ok" if code == 0 else "error"
            self.write_log(logfile, f"\n[{now()}] Finalizado: código {code}\n")
        except Exception as exc:
            job.status, code = "error", 1
            self.write_log(logfile, f"\nERRO: {type(exc).__name__}: {exc}\n")
        finally:
            with self.lock:
                job.code = code
                job.ended = now()
                self.active = None

    def start_service(self) -> None:
        with self.lock:
            if self.service_running():
                raise ValueError("Laboratório já está em execução.")
            if self.active is not None:
                raise ValueError("Conclua a tarefa em execução antes de iniciar o laboratório.")
            cfg = read_settings()
            db, overlay = lab_paths(cfg)
            manifest = Path(cfg["manifest"]).expanduser()
            if not cfg["manifest"] or not manifest.is_file():
                raise ValueError("Informe o caminho válido do manifesto JSON em Configurações.")
            if manifest.suffix.lower() != ".json":
                raise ValueError("Manifesto precisa ser JSON.")
            # Validate JSON before starting a process that connects to the VM.
            try:
                data = json.loads(manifest.read_text(encoding="utf-8-sig"))
            except (OSError, ValueError) as exc:
                raise ValueError("Manifesto inválido: " + str(exc)) from exc
            if not isinstance(data, dict):
                raise ValueError("Manifesto deve conter um objeto JSON.")
            env = lab_env(cfg)
            CAMPAIGNS.mkdir(parents=True, exist_ok=True, mode=0o700)
            command = [test_python(), "-u", "tools/windows-lab/dialogue_service.py",
                       "--pinned-manifest", str(manifest), "--config-out", str(overlay),
                       "--campaign", cfg["campaign"], "--world-seed", cfg["campaign"],
                       "--db", str(db), "--model", cfg["model"]]
            if overlay.exists():
                command.append("--reuse-token")
            path = LOGS / "service.log"
            self.write_log(path, "\n[" + now() + "] Iniciando laboratório " + cfg["campaign"] + "\n")
            proc = subprocess.Popen(command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, encoding="utf-8", errors="replace",
                                    bufsize=1, start_new_session=True)
            self.service = proc
            self.service_campaign = cfg["campaign"]
            self.service_started = now()
            self.service_status = "running"
            threading.Thread(target=self._watch_service, args=(proc,), daemon=True).start()

    def _watch_service(self, proc: subprocess.Popen) -> None:
        path = LOGS / "service.log"
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                self.write_log(path, line)
            code = proc.wait()
            self.write_log(path, f"\n[{now()}] Serviço encerrado: código {code}\n")
        except Exception as exc:
            self.write_log(path, "\nErro ao ler logs: " + str(exc) + "\n")
        finally:
            with self.lock:
                if self.service is proc:
                    self.service_status = "exited"

    def stop_service(self) -> None:
        with self.lock:
            proc = self.service
            if proc is None or proc.poll() is not None:
                self.service_status = "stopped"
                return
        try:
            os.killpg(proc.pid, signal.SIGINT)
            proc.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    if proc.poll() is None:
                        os.killpg(proc.pid, signal.SIGKILL)
        finally:
            with self.lock:
                self.service_status = "stopped"

    def status(self) -> dict:
        with self.lock:
            jobs = [j.to_json() for j in list(self.jobs.values())[-40:]]
            service = {"running": self.service_running(), "status": self.service_status,
                       "campaign": self.service_campaign, "since": self.service_started,
                       "pid": self.service.pid if self.service_running() else None}
        try:
            branch = current_branch()
            git_info = {
                "branch": branch,
                "commit": git("log", "-1", "--format=%h %s"),
                "dirty": not clean_worktree(),
                "detail": git("status", "--short", "--branch"),
                "branches": remote_branches(),
            }
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            git_info = {"error": str(exc), "branches": []}
        python_version = subprocess.run([test_python(), "--version"], cwd=ROOT, capture_output=True,
                                        text=True, timeout=5, check=False)
        return {"git": git_info, "jobs": jobs, "active": self.active,
                "service": service, "python": python_version.stdout.strip() or python_version.stderr.strip(),
                "venv": (ROOT / ".venv" / "bin" / "python").is_file(),
                "repo": str(ROOT), "config": read_settings(),
                "ssh_inherited": bool(os.environ.get("INFINITY_LAB_SSH")),
                "logs_dir": str(LOGS)}


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port: int, panel: Panel):
        super().__init__((HOST, port), Handler)
        self.panel = panel


class Handler(BaseHTTPRequestHandler):
    server: Server
    protocol_version = "HTTP/1.1"

    def log_message(self, format: str, *args: object) -> None:
        # Avoid recording tokens or query strings in terminal logs.
        return

    def secure_host(self) -> bool:
        host = self.headers.get("Host", "")
        allowed = {HOST + ":" + str(self.server.server_port),
                   "localhost:" + str(self.server.server_port)}
        return host in allowed

    def send_bytes(self, body: bytes, content_type: str, code: int = 200,
                   nonce: str | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        if nonce is not None:
            self.send_header("Content-Security-Policy",
                "default-src 'self'; script-src 'self' 'nonce-" + nonce +
                "'; style-src 'self'; connect-src 'self'; img-src 'self' data:; "
                "frame-ancestors 'none'; object-src 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, data: dict, code: int = 200) -> None:
        self.send_bytes(json.dumps(data, ensure_ascii=False).encode("utf-8"),
                        "application/json; charset=utf-8", code=code)

    def token_ok(self) -> bool:
        candidate = self.headers.get("X-Panel-Token", "")
        return secrets.compare_digest(candidate, self.server.panel.token)

    def do_GET(self) -> None:
        if not self.secure_host():
            self.send_json({"error": "Host não autorizado."}, 403)
            return
        parsed = urlsplit(self.path)
        path = parsed.path
        if path == "/":
            nonce = secrets.token_urlsafe(16)
            page = (STATIC / "index.html").read_text(encoding="utf-8")
            page = page.replace("__NONCE__", nonce).replace(
                "__TOKEN_JSON__", json.dumps(self.server.panel.token))
            self.send_bytes(page.encode("utf-8"), "text/html; charset=utf-8", nonce=nonce)
            return
        assets = {
            "/static/app.js": ("app.js", "application/javascript; charset=utf-8"),
            "/static/style.css": ("style.css", "text/css; charset=utf-8"),
        }
        if path in assets:
            filename, media_type = assets[path]
            self.send_bytes((STATIC / filename).read_bytes(), media_type)
            return
        if not self.token_ok():
            self.send_json({"error": "Sessão não autorizada."}, 403)
            return
        if path == "/api/status":
            self.send_json({"ok": True, **self.server.panel.status()})
            return
        if path == "/api/log":
            args = parse_qs(parsed.query)
            kind = args.get("kind", ["job"])[0]
            if kind == "service":
                file = LOGS / "service.log"
            elif kind == "job":
                ident = args.get("id", [""])[0]
                if not SAFE_JOB.fullmatch(ident):
                    self.send_json({"error": "Identificador inválido."}, 400)
                    return
                file = LOGS / ("job-" + ident + ".log")
            else:
                self.send_json({"error": "Tipo de log inválido."}, 400)
                return
            self.send_json({"ok": True, "text": tail(file)})
            return
        self.send_json({"error": "Rota não encontrada."}, 404)

    def do_POST(self) -> None:
        if not self.secure_host() or not self.token_ok():
            self.send_json({"error": "Sessão não autorizada."}, 403)
            return
        origin = self.headers.get("Origin")
        if origin and origin not in {
            "http://" + HOST + ":" + str(self.server.server_port),
            "http://localhost:" + str(self.server.server_port),
        }:
            self.send_json({"error": "Origem não autorizada."}, 403)
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            self.send_json({"error": "Envie application/json."}, 415)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_INPUT:
            self.send_json({"error": "Tamanho inválido."}, 413)
            return
        try:
            obj = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(obj, dict):
                raise ValueError("Corpo inválido.")
            path = urlsplit(self.path).path
            panel = self.server.panel
            if path == "/api/action":
                action = obj.get("action")
                if action == "pin" and obj.get("confirmed") is not True:
                    raise ValueError("Confirme a operação de pin.")
                job = panel.start_job(action, obj)
                self.send_json({"ok": True, "job": job.to_json()})
            elif path == "/api/config":
                cfg = write_settings(obj)
                self.send_json({"ok": True, "config": cfg})
            elif path == "/api/lab/start":
                panel.start_service()
                self.send_json({"ok": True})
            elif path == "/api/lab/stop":
                panel.stop_service()
                self.send_json({"ok": True})
            else:
                self.send_json({"error": "Rota não encontrada."}, 404)
        except (OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired,
                sqlite3.Error) as exc:
            self.send_json({"error": str(exc)}, 400)


def main() -> int:
    parser = argparse.ArgumentParser(description="Infinity AI Local Dev Panel")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("A porta deve estar entre 1024 e 65535.")
    if not (ROOT / ".git").exists():
        parser.error("Execute o painel dentro de uma cópia Git do Infinity AI.")
    panel = Panel()
    try:
        server = Server(args.port, panel)
    except OSError as exc:
        parser.error("Não foi possível abrir a porta local: " + str(exc))
    url = "http://" + HOST + ":" + str(args.port)
    print("Infinity AI — painel local")
    print("Repositório:", ROOT)
    print("Endereço:", url)
    print("Interface disponível somente neste computador.")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.3)
    except KeyboardInterrupt:
        print("\nEncerrando painel...")
    finally:
        server.server_close()
        if panel.service_running():
            panel.stop_service()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
