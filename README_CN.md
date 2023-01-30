# DiffSinger-ONNX-Inference

[ENG](./README.md) | 简体中文

从发布页面（或启智平台中仓库的模型页面）下载`model.zip`并解压到`model`文件夹。

在你的jupyter notebook中运行以下代码：
```python
%pip install -r requirements.txt

import yaml
from ipy import IPyWidgetInfer

ipy_config = yaml.safe_load(open('settings.yaml'))
ipy_infer = IPyWidgetInfer(**ipy_config)

ipy_infer.run()
```

`main.ipynb`是一个可以在
[![Baidu AI Studio](https://img.shields.io/static/v1?label=Baidu&message=AI%20Studio%20V100&color=blue)](https://aistudio.baidu.com/aistudio/projectdetail/4596296)上运行的jupyter notebook的备份。
