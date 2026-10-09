# EP03 素材链与改编说明

## 鲸鱼娘

- 原型「溟月」：上善无形，[原帖与许可](https://www.bilibili.com/opus/1231977657712771073)。
- 女仆版参考：ZipZipPipe，[三视图](https://www.bilibili.com/opus/1238267551429951496)、[许可重申](https://www.bilibili.com/opus/1247156596114456581)。
- 本期直接复用 `../../ep02/assets/whale_sprite_atlas.png` 六姿态绘本衍生素材，不覆盖旧文件；其生成提示词和原参考见 EP02 素材清单。
- 鲸鱼娘形象与本片鲸鱼衍生材料按 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans) 使用与分享，保留署名、非商业与相同方式共享。新动画含位移、转向、呼吸、吃饭、入睡、摸翼与庆祝的代码编排。

## GPT 白龙娘

- 形象作者：ZipZipPipe；原参考及作者非商业取用说明：[Pixiv《AI娘化》](https://www.pixiv.net/artworks/148186519) 第四张 / p3；[B 站三视图](https://www.bilibili.com/opus/1238613841710940181) 第一张。
- 实际参考 `gpt_reference.png`；完整来源与证据见 `GPT_REFERENCE_SOURCE.md`。
- 本期内置 imagegen 生成 `dragon_sprite_atlas.png` 六姿态绘本 Q 版改编，保留白紫长发、龙角、龙翼、鳞尾、白裙和结环装饰；原提示词在 `../production/imagegen_prompt.txt`。用 EP02 鲸鱼图集辅助匹配画风，未把鲸鱼画进新龙娘图集。
- 作者说明开放非商业取用、要求署名；未指定 GPT 的标准 CC。此处保留其要求与作者权利，不将鲸鱼协议重新授予 GPT 原图或混称全部 AI 角色统一开源。

## 音乐

- 实际音源：罐装毕加索《Let Me Go（共创版）》，[BV1XbY66nEWr](https://www.bilibili.com/video/BV1XbY66nEWr/)。
- 原作：星落落_oi，[BV1R5YL69EC5](https://www.bilibili.com/video/BV1R5YL69EC5/)；词 DeepSeek、曲 Suno／豆包，沿该音源投稿署名。
- 原作者本人置顶公开允许二创转载、标注出处。证据 `music/authorization.json`，原评论/投稿数据保存在同目录；完整研究 `../production/music_research.md`。
- 原音源不覆盖为本期原创，不给它重新套用角色或代码许可证。成片剪取 15–69 秒，速度/音调保持，淡入 0.35 秒、尾部淡出 5 秒，响度处理目标 -18 LUFS、真峰值 -2 dB；实际结果见 QA。

## 原创代码与场景

- Python 时间线、角色编排、规则纸、葱粒、圆弧袖手触碰、消化进度、双碗饭桌、气泡与庆祝：梨希 Lyxii / Codex 辅助创作。
- 房间、美术辅助函数与鲸鱼图集直接引用 EP02 唯一原目录，既有材料保留该期 CC BY-NC-SA 4.0。新渲染代码按相同协议分享；它是代码许可，不授予第三方音乐或 GPT 参考新的权利。
- 微软雅黑来自本机 Windows，Pillow/NumPy/FFmpeg 等沿各自许可证。运行环境、凭据、Git 元数据不作为公开素材。
- 制作助手 Codex 基于 GPT-6，具体子版本未暴露；内置图像工具的精确模型 ID 未暴露，生产记录不猜测。视频片尾署已确认身份，简介如实说明。

本片非商业社区同人，角色与台词为原创情景演绎，不表示品牌合作、官方角色设定或真实模型能力。
