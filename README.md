# DiffSinger-ONNX-Inference

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
