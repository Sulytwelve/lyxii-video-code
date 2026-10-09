# Lyxii 视频制作代码

收录 EP01 的程序化动画、旁白与封面制作代码，以及 EP03 的角色绘本动画、合成和检查代码。EP03 直接导入 EP02 的渲染模块，因此保留 `ep02/production/render.py` 及其导入时需要的 `timeline.json`，作为同源依赖。

```text
ep01/production/  渲染、旁白、封面、接触表、研究、剧本调整、验证；剧本和时间线
ep02/production/  EP03 使用的绘本渲染模块和时间线
ep03/production/  渲染、合成、验证、音乐研究/下载；时间线和生成提示词
ep02/assets/      仅跟踪素材来源及许可说明
ep03/assets/      仅跟踪来源说明；可选的图集裁切配置
```

本仓库提供制作脚本、剧本、时间线及来源说明，不分发图片、音轨、视频和运行环境。重现视频需要另行准备下文列出的素材；来源说明中提到的参考图和研究档案未包含在仓库中。

## 环境

原工程面向 Windows，使用 `C:/Windows/Fonts/msyh.ttc`、`msyhbd.ttc` 和 `consola.ttf`。其他系统需调整字体路径。Python 3.11 或更新版本，FFmpeg/ffprobe 需加入 PATH。

在本仓库根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
foreach ($ep in 'ep01', 'ep02', 'ep03') {
    foreach ($dir in 'assets', 'qa', 'deliverables') {
        New-Item -ItemType Directory -Force "$ep/$dir" | Out-Null
    }
}
```

## 素材准备

将有权使用的素材放在以下位置：

| 位置 | 渲染输入 |
| --- | --- |
| `ep01/assets/` | `lyxii_turnaround.png`、`lyxii_portrait.png`、`lyxii_daily.png`、`lily_apps.png`、`curl_code.png`、`demo_bad.png`、`demo_good.png` |
| `ep01/production/` | `mix.wav`；可复用原本地音轨，或显式运行 `make_audio.py` 生成 |
| `ep02/assets/` | `whale_sprite_atlas.png`，EP03 导入依赖也会读取此图 |
| `ep03/assets/` | `dragon_sprite_atlas.png`；可选 `dragon_regions.json` 为六个 `[left, top, right, bottom]` 裁切框 |
| `ep03/assets/music/` | `Let_Me_Go_Guanzhuang_Bijiasuo_BV1XbY66nEWr.m4a`；也可通过 `--music` 指定授权音轨 |

原 Lyxii 图片、网站截图、衍生图集和音乐不随源码分发。参考原图不是渲染必需输入。素材使用与代码许可见 [LICENSES.md](LICENSES.md)。替换图集须兼容原脚本的姿态布局。

## EP01

```powershell
.\.venv\Scripts\python.exe ep01/production/render.py --previews
.\.venv\Scripts\python.exe ep01/production/render.py
.\.venv\Scripts\python.exe ep01/production/cover.py
.\.venv\Scripts\python.exe ep01/production/verify.py
```

完整渲染读取现有 `timeline.json` 和 `mix.wav`。修改旁白后可显式运行 `make_audio.py`：它将剧本文字发送至 Edge TTS，生成分段声音、混音、时间线与 SRT，会覆盖本地相关产物。`tighten.py` 是历史剧本修订工具，也会覆盖 `story.json`，重现现有成片时无需执行。`research.py` 仅用于采集公开网页，常规渲染无需执行。`contact.py [图片目录]` 生成角色参考接触表，默认读取 `ep01/assets/`。

`verify.py` 检查成片编码、时长和完整解码，提取抽帧预览并生成视频工程 ZIP。报告中的字幕检查及原型测试字段为固定的历史记录，脚本不会重新执行这两项检查。

## EP03

```powershell
.\.venv\Scripts\python.exe ep03/production/render.py --previews
.\.venv\Scripts\python.exe ep03/production/render.py --picture
.\.venv\Scripts\python.exe ep03/production/render.py --mux
.\.venv\Scripts\python.exe ep03/production/verify.py
```

默认取音乐 15–69 秒；`--mux --music "授权音轨路径" --music-start 15` 可显式指定输入。验证脚本针对原片的 54 秒、1080p、24fps 参数。渲染不会修改 EP02 源码或素材。

`research_music.py` 和 `download_music.py` 为历史音乐采集代码；前者采集公开信息，后者读取 `assets/music/BV1XbY66nEWr_playurl.json` 下载音轨。接口可能变化，临时 URL 可能过期，原 JSON 未纳入 Git。常规重现优先使用已获授权的本地音轨，无需运行采集脚本。
