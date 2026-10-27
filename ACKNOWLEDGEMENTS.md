# Acknowledgements and licences

CLOAK stands on the work of many open-source projects. Our own code (everything outside
`third_party/` and `ckpts/`) is MIT-licensed. Everything below keeps its own licence, and we use it
under those terms. Licences were checked at the source in October 2026; please re-check before any
commercial use.

## Models

| Component | What CLOAK uses it for | Source | Licence |
|---|---|---|---|
| **Leffa** (Zhou et al., CVPR 2025): code and try-on checkpoints `virtual_tryon.pth`, `virtual_tryon_dc.pth` | Generates the image of the user wearing the garment | [GitHub](https://github.com/franciszzj/Leffa), [Hugging Face](https://huggingface.co/franciszzj/Leffa) | MIT |
| Stable Diffusion 1.5 inpainting (architecture Leffa builds on) | Base network design and configs | Runway / Stability AI | CreativeML OpenRAIL-M (includes use-based restrictions, which we follow) |
| OpenPose body model (as packaged in Leffa, via pytorch-openpose and ControlNet) | Finds shoulders, elbows and hips to shape the garment mask | [CMU OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) | CMU academic licence: **non-commercial research use only** |
| DensePose (Detectron2) | Maps the body surface so the garment follows the body | [facebookresearch/detectron2](https://github.com/facebookresearch/detectron2) | Apache 2.0 |
| SCHP human parsing (ONNX export packaged with Leffa) | Labels hair, face, arms and clothing regions | [Self-Correction-Human-Parsing](https://github.com/GoGoDuck912/Self-Correction-Human-Parsing) | MIT (code); see source for weights |

## Training data (used by the model authors, not by us)

Leffa's try-on checkpoints were trained by their authors on the **VITON-HD** and **DressCode**
datasets, which are released for non-commercial research. The sample people and garments shown in the
app's examples come from the Leffa checkpoint repository and originate from these datasets.

Because of the OpenPose licence and the training data, **CLOAK is a non-commercial research
prototype.** A commercial version would need to replace the pose model and use commercially
licensed weights or retrain on licensed data.

## Libraries

PyTorch (BSD-3), Hugging Face Diffusers (Apache 2.0), Hugging Face Hub (Apache 2.0), Gradio (Apache 2.0),
ONNX Runtime (MIT), OpenCV (Apache 2.0), NumPy (BSD-3), Pillow (MIT-CMU), fvcore (Apache 2.0),
scikit-image (BSD-3).

## Reused code

`cloak/engine.py` adapts the try-on steps from Leffa's `app.py` (MIT): computing the agnostic mask,
DensePose input and calling `LeffaInference`. We added memory-safe loading, full-outfit chaining,
garment routing, input clean-up (rotation, transparency) and cropping.

## AI-assisted development

Parts of this project's code and documentation were drafted with help from Claude (Anthropic), an AI
coding assistant: the engine wrapper, the Gradio interface, setup scripts, tests and README. The team
reviewed, tested and adapted all of it, and can explain every part of the implementation.

## Citation

```bibtex
@article{zhou2024learning,
  title={Learning Flow Fields in Attention for Controllable Person Image Generation},
  author={Zhou, Zijian and Liu, Shikun and Han, Xiao and Liu, Haozhe and Ng, Kam Woh and Xie, Tian and
          Cong, Yuren and Li, Hang and Xu, Mengmeng and P{\'e}rez-R{\'u}a, Juan-Manuel and Patel, Aditya and
          Xiang, Tao and Shi, Miaojing and He, Sen},
  journal={arXiv preprint arXiv:2412.08486},
  year={2024}
}
```
