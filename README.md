# DiffSinger-ONNX-Inference

ENG | [简体中文](./README_CN.md)

Download `model.zip` from release page and unzip to the `model` folder.

Run these codes on your jupyter notebook:

```python
%pip install -r requirements.txt

import yaml
from ipy import IPyWidgetInfer

ipy_config = yaml.safe_load(open('settings.yaml'))
ipy_infer = IPyWidgetInfer(**ipy_config)

ipy_infer.run()
```

`main.ipynb` is a jupter notebook project backup to run on
[![Baidu AI Studio](https://img.shields.io/static/v1?label=Baidu&message=AI%20Studio%20V100&color=blue)](https://aistudio.baidu.com/aistudio/projectdetail/4596296).
