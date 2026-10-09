# EP03 音乐研究：Let Me Go

核实日期：2026-10-09。此次不是根据其他二创署名推断许可，已直接找到音乐投稿作者的公开许可留言，并下载该原投稿的音轨。

## 结论

可使用 **罐装毕加索的《Let Me Go（共创版）》版本**作为此次龙娘与蓝色大肥鱼小剧场 BGM，依作者本人公开留言标注出处。原评论说「大家二创转载也只需要标注出处就好啦～开源万岁～」。这是明确的二创/转载许可说明，但未指定 MIT、Creative Commons 或其他标准许可证；不能将角色的 CC BY-NC-SA 4.0 自动套到音乐上，也不宣称音乐无版权。

成片采用非商业同人用途，不参加付费推广。本研究只核对本人原投稿和公开评论，不代表将其他版本或作者所有歌曲一并授权。

## 可核验的一手来源

1. 音源原投稿：[罐装毕加索《[AI] 大肥鱼摸鱼歌〈Let Me Go〉》](https://www.bilibili.com/video/BV1XbY66nEWr/)，作者 UID `290500073`。原简介署名：原作 `@星落落_oi`（`BV1R5YL69EC5`）、词 `deepseek`、曲 `Suno/豆包`、背景 `@ZipZipPipe`。
2. 原作者本人置顶许可留言：[原视频评论入口](https://www.bilibili.com/video/BV1XbY66nEWr/#reply314678966401)，评论 ID `314678966401`，发言人 UID `290500073` 与投稿作者一致。作者说明该共创版已在网易云和 QQ 音乐上线，并明确允许二创转载、要求标注出处。公开接口：`https://api.bilibili.com/x/v2/reply?type=1&oid=117265542420369&sort=2&pn=1`。本地原始回复保存在 `assets/music/BV1XbY66nEWr_replies.json`；单条署名与许可证据保存在 `assets/music/authorization.json`。
3. 投稿简介指向的原作：[星落落_oi《大肥鱼干活唱歌1分钟试听版》](https://www.bilibili.com/video/BV1R5YL69EC5/)，UID `30584746`，约 60 秒；原简介说明音色未稳定，因此先放试听。
4. 上述原作置顶链接的完整版：[星落落_oi《Let me go大肥鱼和用户深情对唱》](https://www.bilibili.com/video/BV13SYr6dEiQ/)，约 219 秒，简介另署名「词曲：大肥鱼 deepseek；编曲：谱乐 ai；音鲸：豆包」。它与此次罐装毕加索版不是同一段音频，最终使用音乐仍应指向 `BV1XbY66nEWr`。

原作者留言的音乐服务链接是 `https://163cn.tv/bgqW5O62` 和 `https://c6.y.qq.com/base/fcgi-bin/u?__=rK3KcVGo9mmC`。本次没有从这些服务下载，没有登录、付费、使用私有凭据或绕过付费/访问限制。

## 实际获取与技术验证

- 文件：`videos/ep03/assets/music/Let_Me_Go_Guanzhuang_Bijiasuo_BV1XbY66nEWr.m4a`。
- 获取方式：匿名请求原投稿页面和公开 Bilibili `x/player/playurl`；从成功返回的 DASH 音轨列表选择最高 advertised bandwidth 的音轨 `30280`，按该视频 Referer 直接请求公开媒体 URL。
- 未下载或使用原视频画面；动画画面由本期另行制作。
- 实际音频：AAC-LC，48 kHz，立体声，`125.376` 秒。
- 文件大小：`2,729,718` 字节。AAC 音轨约 `132.5 kbps`，整个 DASH M4A 含容器约 `174.2 kbps`。不要将容器/接口 advertised bandwidth 写成固定 174 kbps AAC。
- SHA256：`ec10f5985de259d36eba6d9c187c61d32f0b0334c9addf90e6d9a115acd02bc8`。
- FFprobe 结果保存在 `assets/music/audio_probe.json`；FFmpeg 全段解码完成，无解码错误，音量记录在 `assets/music/audio_decode.log`。
- 音轨下载保持原样，成片需要截取、混音、降音量或淡出时在本期制作记录注明。尚未由本研究代理主观试听；成片代理应结合实际播放检查曲段与画面节奏。
- 可复跑脚本：`production/research_music.py` 和 `production/download_music.py`。Bilibili 媒体 URL 带短期有效签名，重下需要先刷新 playurl，不应把暂时媒体 URL 当成长期出处。

## 对外建议署名

> BGM：罐装毕加索《Let Me Go（共创版）》；音源：https://www.bilibili.com/video/BV1XbY66nEWr/ 。原作：星落落_oi（BV1R5YL69EC5）；词：DeepSeek；曲：Suno／豆包（沿原投稿署名）。按音源作者公开二创许可标注出处。

片尾可用简写：`BGM：Let Me Go · 罐装毕加索 · BV1XbY66nEWr`，详细署名留简介。不要把 BGM 写作本期原创，也不要将角色许可或本期代码许可声明为这段音源的新许可证。其他未采用的歌曲版本与候选研究不必写进简介。
