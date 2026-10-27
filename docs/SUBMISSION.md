# Submission form answers (draft)

**Project name:** CLOAK

**Team:** Favour Akinyeye (Obafemi Awolowo University), Samuel Oluwatuyi (Obafemi Awolowo University)

**Problem statement:**
Young Nigerians increasingly buy clothes from vendors on Instagram, WhatsApp and TikTok. Buyers pay
upfront based on a photo of the item on a mannequin or someone else, with no fitting room and little
chance of a return. They cannot tell how a style, colour or print will look on their own body, or which
combination works, until after they have paid. For students and young workers on tight budgets, a
wrong purchase is wasted money.

**Solution description:**
CLOAK is an open-source virtual fitting room. The user uploads a photo of themselves and photos of a
top and/or bottom, or a dress, for example cropped screenshots from a vendor's page. An open-weight
try-on model generates an image of the user wearing the full outfit. Every look is saved to a
moodboard that shows each new look next to the original photo, so the user can compare combinations before buying. It runs on a free Google
Colab GPU.

**GitHub repository:** https://github.com/___/cloak

**Working demonstration:** ___ (demo video link) and the Colab notebook in the repo for running it live.

**Model information:**
Leffa (CVPR 2025, MIT licence, huggingface.co/franciszzj/Leffa), a diffusion-based virtual try-on
model built on Stable Diffusion 1.5 inpainting. It generates the person wearing the garment. We chose
it because it is designed to preserve fine garment detail (important for Ankara and other printed
fabrics), supports tops, bottoms and dresses through two checkpoints, has a permissive licence, and,
with our memory-safe loading, runs on a free T4 GPU. Supporting open models: SCHP human parsing,
OpenPose keypoints and DensePose. Limitations: shows style, not size or fit; trained on Western
catalogue datasets so native styles and some skin tones are less accurate; best with front-facing
photos and clean product images; some components are non-commercial research licences.

**Documentation:** README.md covers setup, model choice, technical decisions, limitations and tests.

**Acknowledgements:** See ACKNOWLEDGEMENTS.md: Leffa (MIT), Stable Diffusion inpainting
(CreativeML OpenRAIL-M), OpenPose (CMU non-commercial), DensePose/Detectron2 (Apache 2.0), SCHP,
VITON-HD and DressCode datasets, Gradio, Diffusers, PyTorch. Code and docs were partly drafted with
the AI assistant Claude and reviewed and tested by the team.
