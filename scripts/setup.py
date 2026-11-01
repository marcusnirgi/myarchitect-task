from subprocess import run
from pathlib import Path
import shutil
from sys import exit, executable

BASE_DIR = Path(__file__).resolve().parent.parent
COMFY_PATH = BASE_DIR.joinpath("comfy")
SHELL_DEPENDENCIES = ["git", "curl"]
for dep in SHELL_DEPENDENCIES:
    if not shutil.which(dep):
        exit(f"error: dependency '{dep}' not found in PATH - please install it on your system!")

print("installing comfyui")
if not COMFY_PATH.exists():
    run(["git", "clone", "https://github.com/Comfy-Org/ComfyUI.git", str(COMFY_PATH)], check=True)
run([executable, "-m", "pip", "install", "-r", str(COMFY_PATH.joinpath("requirements.txt")), "--extra-index-url", "https://download.pytorch.org/whl/cu128"], check=True)

print("installing custom node: comfyui-ic-light")
ic_path = COMFY_PATH.joinpath("custom_nodes", "ComfyUI-IC-Light")
if not ic_path.exists():
    run(["git", "clone", "https://github.com/kijai/ComfyUI-IC-Light.git", str(ic_path)], check=True)
ic_reqs = ic_path.joinpath("requirements.txt")
if ic_reqs.exists():
    run([executable, "-m", "pip", "install", "-r", str(ic_reqs)], check=True)

print("creating model directories")
models_path = COMFY_PATH.joinpath("models")
for subdir in ["unet", "checkpoints"]:
    models_path.joinpath(subdir).mkdir(parents=True, exist_ok=True)

print("downloading IC-Light fc model (to models/unet/)")
ic_unet_url = "https://huggingface.co/lllyasviel/ic-light/resolve/main/iclight_sd15_fc.safetensors"
ic_unet_dest = models_path.joinpath("unet", "iclight_sd15_fc.safetensors")
if not ic_unet_dest.exists():
    run(["curl", "-L", "-o", str(ic_unet_dest), ic_unet_url])

print("downloading SD 1.5 checkpoint (Realistic Vision V5.1)")
ckpt_url = "https://huggingface.co/SG161222/Realistic_Vision_V5.1_noVAE/resolve/main/Realistic_Vision_V5.1_fp16-no-ema.safetensors"
ckpt_dest = models_path.joinpath("checkpoints", "Realistic_Vision_V5.1_fp16-no-ema.safetensors")
if not ckpt_dest.exists():
    run(["curl", "-L", "-o", str(ckpt_dest), ckpt_url])

print("copying assets to input folder")
assets_path = BASE_DIR.joinpath("assets")
input_path = COMFY_PATH.joinpath("input")
if assets_path.exists():
    shutil.copytree(assets_path, input_path, dirs_exist_ok=True)
else:
    print(f"warning: assets folder not found at {assets_path}")

print("copying workflows to comfy user workflows")
repo_workflows = BASE_DIR.joinpath("workflows")
comfy_workflows = COMFY_PATH.joinpath("user", "default", "workflows")
comfy_workflows.mkdir(parents=True, exist_ok=True)
if repo_workflows.exists():
    for wf in repo_workflows.glob("*.json"):
        shutil.copy2(str(wf), str(comfy_workflows))
        print(f"  copied {wf.name}")
else:
    print(f"warning: workflows folder not found at {repo_workflows}")

print("done! you may now run comfyui using 'mise start'")