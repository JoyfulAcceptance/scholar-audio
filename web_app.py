#!/usr/bin/env python3
"""Local browser wrapper for Scholar Audio."""

from __future__ import annotations

import argparse
import cgi
import json
import mimetypes
import re
import subprocess
import threading
import uuid
import webbrowser
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import unquote, urlparse

from app import (
    ScholarAudioError,
    available_voices,
    build_packet,
    default_voice,
    infer_citation_name,
    prepare_preview_text,
    render_audio,
)


ROOT = Path(__file__).resolve().parent
UPLOADS = ROOT / "uploads"
PACKETS = ROOT / "output"
MAX_UPLOAD_BYTES = 100 * 1024 * 1024
JOBS: Dict[str, Dict[str, object]] = {}
JOBS_LOCK = threading.Lock()
PREVIEWS: Dict[str, Dict[str, object]] = {}
PREVIEWS_LOCK = threading.Lock()
PLAYBACK_PROCESS: Optional[subprocess.Popen] = None
PLAYBACK_LOCK = threading.Lock()


def stop_playback() -> None:
    """Stop any voice or prepared sample currently playing on the Mac."""
    global PLAYBACK_PROCESS

    with PLAYBACK_LOCK:
        process = PLAYBACK_PROCESS
        PLAYBACK_PROCESS = None
        if process and process.poll() is None:
            process.terminate()


def start_playback(command: list[str]) -> None:
    """Play one local preview at a time, replacing anything already speaking."""
    global PLAYBACK_PROCESS

    with PLAYBACK_LOCK:
        previous = PLAYBACK_PROCESS
        if previous and previous.poll() is None:
            previous.terminate()
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        PLAYBACK_PROCESS = process

    def reap() -> None:
        global PLAYBACK_PROCESS
        process.wait()
        with PLAYBACK_LOCK:
            if PLAYBACK_PROCESS is process:
                PLAYBACK_PROCESS = None

    threading.Thread(target=reap, daemon=True).start()


def safe_filename(name: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).name).strip("._")
    return clean[:120] or "document.txt"


def update_job(job_id: str, **changes: object) -> None:
    with JOBS_LOCK:
        JOBS[job_id].update(changes)


def run_job(job_id: str, source: Path, output: Path, voice: str, rate: int) -> None:
    def report(current: int, total: int, section: str) -> None:
        update_job(job_id, current=current, total=total, section=section)

    try:
        update_job(job_id, status="working", message="Preparing the paper for listening…")
        citation_name = infer_citation_name(source)
        output = output.parent / citation_name
        if output.exists() and any(output.iterdir()):
            suffix = 2
            while (output.parent / f"{citation_name}_{suffix}").exists():
                suffix += 1
            output = output.parent / f"{citation_name}_{suffix}"
        update_job(job_id, output=str(output))
        build_packet(source, output, voice, rate, False, progress=report)
        files = [
            {"name": path.name, "url": f"/packets/{job_id}/{path.name}"}
            for path in sorted(output.iterdir())
            if path.is_file() and path.suffix.lower() in {".m4b", ".zip"}
        ]
        update_job(job_id, status="complete", message="Your listening packet is ready.", files=files)
    except (ScholarAudioError, OSError, UnicodeError) as exc:
        update_job(job_id, status="error", message=str(exc))


def update_preview(preview_id: str, **changes: object) -> None:
    with PREVIEWS_LOCK:
        PREVIEWS[preview_id].update(changes)


def run_preview(preview_id: str, source: Path, audio: Path, voice: str, rate: int) -> None:
    try:
        update_preview(preview_id, status="working", message="Preparing your listening sample…")
        text_file = audio.with_suffix(".txt")
        text_file.write_text(prepare_preview_text(source, rate), encoding="utf-8")
        render_audio(text_file, audio, voice, rate)
        update_preview(preview_id, status="complete", message="Your listening sample is ready.")
    except (ScholarAudioError, OSError, UnicodeError) as exc:
        update_preview(preview_id, status="error", message=str(exc))


class ScholarAudioHandler(BaseHTTPRequestHandler):
    server_version = "ScholarAudio/0.1"

    def log_message(self, format: str, *args: object) -> None:
        print(f"[web] {self.address_string()} {format % args}")

    def send_json(self, data: object, status: int = HTTPStatus.OK) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def send_file(self, path: Path, download: bool = False) -> None:
        if not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(path.stat().st_size))
        self.send_header("Cache-Control", "no-store")
        if download:
            self.send_header("Content-Disposition", f'attachment; filename="{path.name}"')
        self.end_headers()
        with path.open("rb") as source:
            while chunk := source.read(64 * 1024):
                self.wfile.write(chunk)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self.send_file(ROOT / "templates" / "index.html")
        elif path == "/static/style.css":
            self.send_file(ROOT / "static" / "style.css")
        elif path == "/static/app.js":
            self.send_file(ROOT / "static" / "app.js")
        elif path == "/api/voices":
            try:
                self.send_json({"voices": available_voices()})
            except (OSError, ScholarAudioError) as exc:
                self.send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
        elif path.startswith("/api/jobs/"):
            job_id = path.rsplit("/", 1)[-1]
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                response = dict(job) if job else None
            if response:
                self.send_json(response)
            else:
                self.send_json({"error": "Job not found."}, HTTPStatus.NOT_FOUND)
        elif path.startswith("/api/previews/"):
            preview_id = path.rsplit("/", 1)[-1]
            with PREVIEWS_LOCK:
                preview = PREVIEWS.get(preview_id)
                response = dict(preview) if preview else None
            if response:
                response.pop("audio", None)
                self.send_json(response)
            else:
                self.send_json({"error": "Preview not found."}, HTTPStatus.NOT_FOUND)
        elif path.startswith("/packets/"):
            parts = path.split("/", 3)
            if len(parts) != 4:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            job_id, filename = parts[2], safe_filename(unquote(parts[3]))
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                output_value = job.get("output") if job else None
            if not output_value:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            output = Path(str(output_value)).resolve()
            candidate = (output / filename).resolve()
            if output not in candidate.parents:
                self.send_error(HTTPStatus.FORBIDDEN)
                return
            self.send_file(candidate, download=True)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        request_path = urlparse(self.path).path
        if request_path.startswith("/api/previews/") and request_path.endswith("/play"):
            preview_id = request_path.split("/")[3]
            with PREVIEWS_LOCK:
                preview = PREVIEWS.get(preview_id)
                audio_value = preview.get("audio") if preview and preview.get("status") == "complete" else None
            if not audio_value:
                self.send_json({"error": "The listening sample is not ready."}, HTTPStatus.NOT_FOUND)
                return
            try:
                start_playback(["afplay", str(audio_value)])
                self.send_json({"ok": True})
            except OSError as exc:
                self.send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        if request_path == "/api/previews":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > MAX_UPLOAD_BYTES:
                    raise ScholarAudioError("Choose a PDF, Markdown, or text file smaller than 100 MB.")
                content_type = self.headers.get("Content-Type", "")
                if "multipart/form-data" not in content_type:
                    raise ScholarAudioError("The preview form was not understood.")
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type, "CONTENT_LENGTH": str(length)},
                )
                upload = form["document"] if "document" in form else None
                if upload is None or not getattr(upload, "filename", ""):
                    raise ScholarAudioError("Choose a document first.")
                filename = safe_filename(upload.filename)
                if Path(filename).suffix.lower() not in {".pdf", ".md", ".txt"}:
                    raise ScholarAudioError("Scholar Audio accepts PDF, Markdown, and text files.")
                voice = form.getfirst("voice", default_voice()).strip()
                rate = int(form.getfirst("rate", "130"))
                if voice not in available_voices() or not 80 <= rate <= 400:
                    raise ScholarAudioError("Choose an installed voice and a valid speaking pace.")
                UPLOADS.mkdir(exist_ok=True)
                preview_id = uuid.uuid4().hex[:12]
                preview_folder = UPLOADS / f"preview_{preview_id}"
                preview_folder.mkdir()
                source = preview_folder / filename
                source.write_bytes(upload.file.read())
                audio = preview_folder / "listening_sample.m4a"
                with PREVIEWS_LOCK:
                    PREVIEWS[preview_id] = {
                        "id": preview_id,
                        "status": "queued",
                        "message": "Starting…",
                        "audio": str(audio),
                    }
                threading.Thread(target=run_preview, args=(preview_id, source, audio, voice, rate), daemon=True).start()
                self.send_json({"preview_id": preview_id}, HTTPStatus.ACCEPTED)
            except (ScholarAudioError, ValueError, OSError) as exc:
                self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        if request_path == "/api/preview":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                data = json.loads(self.rfile.read(length).decode("utf-8"))
                voice = str(data.get("voice", default_voice()))
                rate = int(data.get("rate", 130))
                if voice not in available_voices():
                    raise ScholarAudioError("That Mac voice is not installed.")
                if not 80 <= rate <= 400:
                    raise ScholarAudioError("Speaking rate must be between 80 and 400.")
                start_playback(
                    ["say", "-v", voice, "-r", str(rate), "Scholar Audio turns dense papers into listening time."]
                )
                self.send_json({"ok": True})
            except (ScholarAudioError, ValueError, OSError, json.JSONDecodeError) as exc:
                self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        if request_path != "/api/jobs":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        stop_playback()
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_UPLOAD_BYTES:
                raise ScholarAudioError("Choose a PDF or text file smaller than 100 MB.")
            content_type = self.headers.get("Content-Type", "")
            if "multipart/form-data" not in content_type:
                raise ScholarAudioError("The upload form was not understood.")
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type, "CONTENT_LENGTH": str(length)},
            )
            upload = form["document"] if "document" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                raise ScholarAudioError("Choose a PDF or text file first.")
            filename = safe_filename(upload.filename)
            if Path(filename).suffix.lower() not in {".pdf", ".md", ".txt"}:
                raise ScholarAudioError("Scholar Audio accepts PDF, Markdown, and text files.")
            voice = form.getfirst("voice", default_voice()).strip()
            rate = int(form.getfirst("rate", "130"))
            if voice not in available_voices():
                raise ScholarAudioError("That Mac voice is not installed.")
            if not 80 <= rate <= 400:
                raise ScholarAudioError("Speaking rate must be between 80 and 400.")

            UPLOADS.mkdir(exist_ok=True)
            PACKETS.mkdir(exist_ok=True)
            job_id = uuid.uuid4().hex[:12]
            upload_folder = UPLOADS / job_id
            upload_folder.mkdir()
            source = upload_folder / filename
            source.write_bytes(upload.file.read())
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = PACKETS / f"{Path(filename).stem}_{stamp}_{job_id[:4]}"
            with JOBS_LOCK:
                JOBS[job_id] = {
                    "id": job_id,
                    "status": "queued",
                    "message": "Starting…",
                    "current": 0,
                    "total": 0,
                    "section": "",
                    "files": [],
                    "output": str(output),
                }
            threading.Thread(target=run_job, args=(job_id, source, output, voice, rate), daemon=True).start()
            self.send_json({"job_id": job_id}, HTTPStatus.ACCEPTED)
        except (ScholarAudioError, ValueError, OSError) as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Scholar Audio's local browser interface.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true", help="Do not open the browser automatically")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    address = ("127.0.0.1", args.port)
    server = ThreadingHTTPServer(address, ScholarAudioHandler)
    url = f"http://{address[0]}:{address[1]}"
    print(f"Scholar Audio is ready at {url}")
    print("Press Control-C to stop it.")
    if not args.no_open:
        threading.Timer(0.6, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nScholar Audio stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
