import sys
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if getattr(sys, "frozen", False):
    bundle_dir = Path(sys._MEIPASS)
    static_dir = bundle_dir / "static"
    base_dir = Path(sys.executable).parent

else:
    project_root = Path(__file__).parent.parent.resolve()
    static_dir = project_root / "static"
    base_dir = project_root

logger.info(f"Static directory resolved to: {static_dir}")

if not static_dir.exists():
    logger.error(f"Static directory not found: {static_dir}")

app = FastAPI()
app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

CONFIG_DIR = base_dir / "config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = CONFIG_DIR / "config.json"

def load_config():
    import json

    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

            if isinstance(data, dict):
                return data

        except Exception as e:
            logger.warning(f"Failed to load config.json: {e}")

    return {}

def save_config(ac_path: str):
    import json
    data = {"ac_path": ac_path}

    try:
        CONFIG_PATH.write_text(json.dumps(data, indent=4), encoding="utf-8")
        logger.info(f"Config saved to {CONFIG_PATH}")

    except Exception as e:
        logger.exception("Error writing config.json")
        raise

class SettingsInput(BaseModel):
    ac_path: str

@app.get("/api/settings")
async def get_settings():
    cfg = load_config()
    return {"ac_path": cfg.get("ac_path", "")}

@app.post("/api/settings")
async def post_settings(settings: SettingsInput):
    from pathlib import Path as PPath
    p = PPath(settings.ac_path)

    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=400, detail="Invalid AC root path")

    if not (p / "content" / "cars").exists() or not (p / "content" / "tracks").exists():
        raise HTTPException(status_code=400, detail="AC content folders not found")

    save_config(settings.ac_path)

    return {"status": "success"}