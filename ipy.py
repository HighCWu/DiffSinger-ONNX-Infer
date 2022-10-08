import importlib
import re

import ipywidgets as widgets
import yaml
from gradio.inputs import Textbox

from infer import Infer
from utils.hparams import set_hparams
from utils.hparams import hparams as hp
import numpy as np
import soundfile as sf

import uuid

from IPython.display import display
from IPython.display import Audio, HTML


class IPyWidgetInfer:
    def __init__(self, exp_name, inference_cls, title, description, article, example_inputs):
        self.exp_name = exp_name
        self.title = title
        self.description = description
        self.article = article
        self.example_inputs = example_inputs

        pkg = ".".join(inference_cls.split(".")[:-1])
        cls_name = inference_cls.split(".")[-1]
        self.inference_cls = getattr(importlib.import_module(pkg), cls_name)
        
        set_hparams("model/config.yaml")
        infer_cls = self.inference_cls
        self.infer_ins: Infer = infer_cls(hp)

    def greet(self, text, notes, notes_duration):
        PUNCS = '。？；：'
        sents = re.split(rf'([{PUNCS}])', text.replace('\n', ','))
        sents_notes = re.split(rf'([{PUNCS}])', notes.replace('\n', ','))
        sents_notes_dur = re.split(rf'([{PUNCS}])', notes_duration.replace('\n', ','))

        if sents[-1] not in list(PUNCS):
            sents = sents + ['']
            sents_notes = sents_notes + ['']
            sents_notes_dur = sents_notes_dur + ['']

        audio_outs = []
        s, n, n_dur = "", "", ""
        for i in range(0, len(sents), 2):
            if len(sents[i]) > 0:
                s += sents[i] + sents[i + 1]
                n += sents_notes[i] + sents_notes[i+1]
                n_dur += sents_notes_dur[i] + sents_notes_dur[i+1]
            if len(s) >= 400 or (i >= len(sents) - 2 and len(s) > 0):
                audio_out = self.infer_ins.infer_once({
                    'text': s,
                    'notes': n,
                    'notes_duration': n_dur,
                })
                audio_out = audio_out * 32767
                audio_out = audio_out.astype(np.int16)
                audio_outs.append(audio_out)
                audio_outs.append(np.zeros(int(hp['audio_sample_rate'] * 0.3)).astype(np.int16))
                s = ""
                n = ""
        audio_outs = np.concatenate(audio_outs)
        return hp['audio_sample_rate'], audio_outs

    def run(self):
        example_inputs = self.example_inputs
        for i in range(len(example_inputs)):
            text, notes, notes_dur = example_inputs[i].split('<sep>')
            example_inputs[i] = [text, notes, notes_dur]

        uid = 'u' + str(uuid.uuid1()).replace('-', '')
        input_names = ['input_text', 'input_note', 'input_duration']

        htmlPreEnv = r"""
            <style>
            .btn_style{
                border-color: #e5e7eb;
                background-color:#a9aaab;
            }
            .box_style{
                border-color: #e5e7eb;
                background-color:#f9fafb;
            }
            </style>
            <script>
                const uuid = '$$uuid$$';
                const input_names = [$$input_names$$];
                const tableClickEvent = (i) => {
                    for (let inp of input_names)
                    {
                        el0 = document.querySelector(`.$$uuid$$_${inp}`);
                        el = el0.getElementsByTagName('textarea')[0];
                        value_el = document.querySelector(`.$$uuid$$_${inp}_example_${i}`);
                        el.value = value_el.innerText;
                        const e = new Event('change')
                        Object.defineProperty(e, 'delegateTarget', { get() { return el; }, set(){} });
                        Object.defineProperty(e, 'srcElement', { get() { return el; }, set(){} });
                        Object.defineProperty(e, 'target', { get() { return el; }, set(){} });

                        el0.dispatchEvent(e);
                    }
                }
            </script>
        """
        input_names_in_script = ','.join(["'"+inp+"'" for inp in input_names])
        htmlPreEnv = htmlPreEnv.replace('$$uuid$$', uid).replace('$$input_names$$', input_names_in_script)

        display(HTML(htmlPreEnv))

        submit_btn = widgets.Button(description='Submmit (提交)')
        submit_btn.add_class("btn_style")

        inputs_widget = []
        inputs_widget_text_only = []
        example0 = example_inputs[0]
        for i, inp in enumerate(input_names):
            label = widgets.Label(value=inp.replace('_', ' '))
            inputs_widget.append(label)
            textarea = widgets.Textarea(
                value=example0[i],
                disabled=False
            )
            textarea.add_class(f'{uid}_{inp}')
            inputs_widget_text_only.append(textarea)
            inputs_widget.append(textarea)

        input_widget = widgets.VBox([*inputs_widget, submit_btn])
        input_widget.add_class("box_style")

        out = widgets.Output(layout={'border': '1px solid black'})

        output_widget = widgets.VBox([
            widgets.Label(value='output audio'),
            out
        ])
        output_widget.add_class("box_style")

        def submit_evt(_):
            out.clear_output()
            with out:
                values = [t.value for t in inputs_widget_text_only]
                sr, wav = self.greet(*values)
                display(Audio(wav, rate=sr))

        submit_btn.on_click(submit_evt)

        func_widget = widgets.GridBox([input_widget, output_widget], layout=widgets.Layout(grid_template_columns="repeat(2, 50%)"))

        examples_html = '<h4>Examples[Click (点击选择样例)]</h4><table style="width:100%"><tr>'
        for inp in input_names:
            inp = inp.replace('_', ' ')
            examples_html += f'<th>{inp}</th>'
        examples_html += '</tr>'
        for i, example in enumerate(example_inputs):
            examples_html += '<tr>'
            for ej, inp in zip(example, input_names):
                class_name = f'{uid}_{inp}_example_{i}'
                examples_html += f'<td onclick="tableClickEvent({i})" class={class_name}>{ej}</td>'
            examples_html += '</tr>'
        examples_html += '</table>'
        examples_widget = widgets.HTML(examples_html)

        title_widget = widgets.HTML(value=f"<h1><center><b>{self.title}</b></center></h2>")

        descriptions = self.description.split('\n')
        description_html = '<p>'
        for description in descriptions:
            description_html += f'<p>{description}</p>'
        description_html += '</p>'
        description_widget = widgets.HTML(value=description_html)

        main = widgets.VBox([
            title_widget,
            description_widget,
            func_widget,
            examples_widget,
            widgets.HTML(value=f'<p>{self.article}</p>')
        ])
        display(main)

        # sr, wav = self.greet(example_inputs[0][0], example_inputs[0][1], example_inputs[0][2])
        # sf.write('example.wav', wav, sr)


if __name__ == '__main__':
    ipy_config = yaml.safe_load(open('settings.yaml'))
    ipy_infer = IPyWidgetInfer(**ipy_config)
    ipy_infer.run()
