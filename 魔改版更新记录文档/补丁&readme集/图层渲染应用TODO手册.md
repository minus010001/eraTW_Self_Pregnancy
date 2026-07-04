# 图层渲染应用 TODO 手册

> 基于调研决策，记录标题百叶窗效果和 VN 系统移植的实施方案与待办事项。
> 知识库参考：[setimagelayer.md](file:///d:/emuera/shared-trae/knowledge/erabasic/setimagelayer.md)、[color-pipeline.md](file:///d:/emuera/shared-trae/knowledge/erabasic/color-pipeline.md)
> 最后更新：2026-06-07（Flan UI Letterbox 基础完成 + v7.3.1 引擎修复）

## 决策摘要

| 项目 | 方案 | 核心技术 | 状态 |
|------|------|---------|------|
| 标题百叶窗 | SETIMAGELAYER 35 条图层 + opacity 动画 | depth 0~34, opacity 渐变 | 待开发 |
| VN 系统移植 | SETIMAGELAYER(背景/立绘/UI) + HTML_PRINT(文本) | 图层与文本行解耦 | 待开发 |
| Flan UI 信箱 | 9-slice 图形帧 + SETIMAGELAYERL/div 双方案 | 图层方案 + 内联方案 | **基础完成** |

---

## Phase 1: 标题百叶窗效果

### 待办

- [ ] **P1-1**: 重构 `@RM_タイトル画像用意` — 保持 35 条 Sprite 裁剪逻辑不变
- [ ] **P1-2**: 替换主循环中 35 次 `HTML_PRINT <img>` 为 `SETIMAGELAYER`
  - 坐标系：左下原点，第 i 条 y = -(35-i)*16
  - depth：0~34，与条号一致
- [ ] **P1-3**: 实现百叶窗淡入动画
  - 逐条 SETIMAGELAYER opacity 从 0→255
  - AWAIT 帧间隔控制速度
- [ ] **P1-4**: 实现百叶窗淡出动画
  - 反向逐条 SETIMAGELAYER opacity 从 255→0
- [ ] **P1-5**: 菜单文本仍走 HTML_PRINT（在图层之上，Layer 3 > Layer 1）
- [ ] **P1-6** (可选): 叠加 ColorMatrix 效果
  - 灰度→彩色渐变：淡入时从 CM_GRAY 过渡到无 CM
  - 反色闪烁：淡出时叠加 CM_INVERT

### 技术约束

- SETIMAGELAYER 坐标系为左下原点（与 CBGSETSPRITE 一致）
- opacity 范围 0~255，0=完全透明，255=完全不透明
- ColorMatrix 传入 `#DIM CM, 5, 5` 二维数组引用（如 `CM_GRAY:0:0`），元素除以 256
- 引擎版本：v7.3.1+ 已实装 SETIMAGELAYER + SETIMAGELAYERL
- **v7.0 渲染管线**：SETIMAGELAYER/CBG/escapedParts 共享统一 depth 排序，SETIMAGELAYER depth > div depth 时可渲染在 div 之上
- **DrawingParam_ShapePositionShift**：HTML img/shape/文本渲染自动加 X 偏移（≈2-4px），div 背景和 SETIMAGELAYER 不加。详见 [setimagelayer.md](file:///d:/emuera/shared-trae/knowledge/erabasic/setimagelayer.md)
- **颜色哨兵值**：v7.3.1 起从 `-1` 改为 `int.MinValue`，ARGB 格式 `0xAARRGGBB` 不再与哨兵值冲突。详见 [color-pipeline.md](file:///d:/emuera/shared-trae/knowledge/erabasic/color-pipeline.md)

### 参考代码

```erb
; 当前实现（HTML 方案）
FOR LOCAL:0, 0, 35
    HTML_PRINT "<p align='center'><img src='TW_title" + TOSTR(LOCAL:0, "000") + "'></p>"
NEXT

; 目标实现（图层方案）
FOR LOCAL, 0, 35
    SETIMAGELAYER @"TW_title{TOSTR(LOCAL, "D3")}", LOCAL, 0, -(35-LOCAL)*16
NEXT

; 百叶窗淡入
FOR LOCAL, 0, 35
    FOR opacity, 0, 256, 16
        SETIMAGELAYER @"TW_title{TOSTR(LOCAL, "D3")}", LOCAL, 0, -(35-LOCAL)*16, 0, 0, opacity
    NEXT
    AWAIT 20
NEXT
```

---

## Phase 2: VN 系统核心框架

### 待办

- [ ] **P2-1**: 设计 VN 图层 depth 分配方案
  - depth=-10: 背景图
  - depth=1~5: 立绘（多角色）
  - depth=10: UI 面板（名字框/对话框背景）
- [ ] **P2-2**: 实现 VN 背景渲染
  - `SETIMAGELAYER "bg_sprite", -10` 替代 CBGSETG
  - 背景切换时 opacity 渐变过渡
- [ ] **P2-3**: 实现 VN 立绘渲染
  - `SETIMAGELAYER "chara_sprite", N` 替代 CBGSETG
  - 立绘切换时 opacity 渐变 + CLEARIMAGELAYER
- [ ] **P2-4**: 实现 VN UI 面板渲染
  - 名字框/对话框背景用 SETIMAGELAYER
  - 或用 HTML div 封装（在文本行层面）
- [ ] **P2-5**: 实现逐字打印动画
  - 引擎层 TYPING_PRINT 指令（见 Phase 2.5）
- [ ] **P2-6**: 实现选择按钮
  - PRINTBUTTON / HTML button 替代鼠标碰撞检测
  - 或 SETIMAGELAYER + INPUTMOUSEKEY（视觉按钮）
- [ ] **P2-7**: 移植 pops-tw VN 配置系统
  - nVNGlobals: drawing/wordPrint/hearts/printFlushTime/printFlushAdd
  - VNConfig: GIWidth/GIHeight/GICharaSize 等

---

## Phase 2.5: 引擎层文本动画指令

> 详细设计见 [引擎层文本动画指令工作手册.md](file:///d:/eratw-chs/魔改版更新记录文档/补丁&readme集/引擎层文本动画指令工作手册.md)
> 核心决策：ERB 层动画每帧 CLEARLINE+重建行，引擎层保持行数据不变，只在渲染时修改参数。

### 待办

- [ ] **P2.5-1**: 定义 `IAnimatedDisplayLine` 接口
- [ ] **P2.5-2**: 修改渲染循环支持动画行
- [ ] **P2.5-3**: 实现 `TypingDisplayLine` 类（SKCanvas clip rect 裁剪）
- [ ] **P2.5-4**: 注册 `TYPING_PRINT` / `TYPING_PRINTW` / `TYPING_PRINTL` 指令
- [ ] **P2.5-5**: 实现 `FadeDisplayLine` 类（colorOverride 参数）
- [ ] **P2.5-6**: 注册 `FADE_PRINT` / `FADEOUT_PRINT` / `FADEIN_PRINT` 指令
- [ ] **P2.5-7**: ERB 层兼容重构
  - `KEYTYPING` → 调用 `TYPING_PRINTW`
  - `FADE`/`FADEIN`/`FADEOUT` → 调用 `FADE_PRINT`
  - `ROLLTEXT` 暂不引擎化（涉及位置偏移）

### 关键技术决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 字符裁剪方法 | SKCanvas clip rect | 不修改数据结构，GPU 级裁剪 |
| 同步机制 | 复用 WaitInput | ERB 线程暂停，UI 线程继续渲染 |
| 动画驱动 | Stopwatch 计时 | 与 SpriteAnime 一致，精确帧率 |
| 跳过机制 | ForceComplete() | 即时完成，零延迟 |
| DivideAt 使用 | 不使用（有副作用） | DivideAt 修改原始节点，破坏数据完整性 |

---

## Phase 2.6: 引擎层图片特效指令

> 详细设计见 [引擎层文本动画指令工作手册.md](file:///d:/eratw-chs/魔改版更新记录文档/补丁&readme集/引擎层文本动画指令工作手册.md) §8
> 核心决策：ImageLayer 已有 Opacity/ColorMatrix 属性，动画只需逐帧更新属性值，无需修改渲染管线。

### 待办

- [ ] **P2.6-1**: 定义 `IAnimatedLayer` 接口
- [ ] **P2.6-2**: 实现 `FadeAnimatedLayer` 类（opacity/CM 插值 + easing）
- [ ] **P2.6-3**: 修改 `ImageLayerManager.DrawTo` 支持动画图层
- [ ] **P2.6-4**: 注册 `LAYER_FADEIN` / `LAYER_FADEOUT` 指令
- [ ] **P2.6-5**: 实现 `LAYER_BLINDSIN` / `LAYER_BLINDSOUT` 百叶窗指令
- [ ] **P2.6-6**: 实现 `SCREEN_FLASH` 屏幕闪烁指令
- [ ] **P2.6-7**: 实现 `SCREEN_QUAKE` 屏幕震动指令
- [ ] **P2.6-8**: 实现 `BGCOLOR_FADE` 背景色渐变指令
- [ ] **P2.6-9**: ERB 层兼容重构
  - `FLASH` → 调用 `SCREEN_FLASH`
  - `QUAKE` → 调用 `SCREEN_QUAKE`
  - `ANIMATION_BGCOLOR_TRANSITION` → 调用 `BGCOLOR_FADE`

### 关键技术决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 图层动画方式 | 逐帧更新 Opacity/CM 属性 | BuildFilter 已有，无需改渲染管线 |
| 闪烁实现 | 全局状态 + canvas.DrawRect | 最轻量，不创建图层对象 |
| 震动实现 | canvas.Translate 偏移 | 像素级精度，正弦衰减平滑 |
| 百叶窗时差 | staggerMs × index | 波浪式渐变效果 |
| FADEOUT 完成后 | 自动清除图层 | 避免残留透明图层 |

---

## Phase 2.7: Flan UI VN 函数库 ✅ 基础完成

> 源码：[Flan_UI.ERB](file:///d:/eratw-chs/ERB/魔改内容/PRINT系/Flan_UI.ERB)
> 精灵资源：[IMG_K1011.csv](file:///d:/eratw-chs/resources/剧本自定义附件/flanKojo/IMG_K1011.csv)
> 核心决策：三层分离（底层原语→中层组件→上层场景）+ 两种渲染方案

### 已完成

- [x] **P2.7-1**: `FLAN_GRAPHIC_FRAME` — 9-slice 图形帧绘制器（四角+横竖边+水晶+背景填充）
- [x] **P2.7-2**: `FLAN_LETTER_LAYER` — SETIMAGELAYERL 图层方案（图形帧 + 半透明 div）
- [x] **P2.7-3**: `FLAN_LETTER_INLINE` — HTML 内联方案（img + 负 space + div）
- [x] **P2.7-4**: `FLAN_ALLOC_GID` — Graphics ID 分配器（9000~9099 范围）
- [x] **P2.7-5**: `FLAN_UI_TEST` — 基础测试（两种方案渲染验证）
- [x] **P2.7-6**: `FLAN_ALIGN_TEST` — 对齐测试（SETIMAGELAYERL vs HTML img 位置一致性）
- [x] **P2.7-7**: `FLAN_MODE_COMPARE_TEST` — 三种 letterbox 模式横向对比测试
- [x] **P2.7-8**: 引擎修复：SETIMAGELAYER 多精灵同 depth 支持（List 替代 Dictionary）
- [x] **P2.7-9**: 引擎新增：SETIMAGELAYERL 后缀指令（自动 followScroll + GetLineNo 锚定）
- [x] **P2.7-10**: 引擎修复：SETIMAGELAYER 空参数默认值支持
- [x] **P2.7-11**: 引擎修复：HTML div color ARGB 透明度支持
- [x] **P2.7-12**: 引擎修复：颜色哨兵值 `-1` → `int.MinValue`（避免与 0xFFFFFFFF 冲突）
- [x] **P2.7-13**: 引擎修复：HTML div border 无 bcolor 时默认使用 Config.ForeColor
- [x] **P2.7-14**: 引擎修复：`stringToColorInt32` ARGB 分支 ToInt32 溢出
- [x] **P2.7-15**: 引擎修复：HTML div height 自适应（省略时自动计算）
- [x] **P2.7-16**: 引擎修复：SETIMAGELAYERL 锚定从 LineCount 改为 GetLineNo（修复 Y 轴偏移）
- [x] **P2.7-17**: ERB 修复：`border='1'` → `border='1px'`（em 单位陷阱）
- [x] **P2.7-18**: 三种 letterbox 模式对比测试通过（字符画/div/图形帧渲染一致）
- [x] **P2.7-19**: 两种渲染方案对齐验证通过（SETIMAGELAYERL 图层方案 vs HTML 内联方案）

### 待办

- [ ] **P2.7-21**: 整个 box 的屏幕定位（居中/左对齐/右对齐）
  - 需要新增 POS 参数控制 box 在窗口中的水平位置
  - 涉及 SETIMAGELAYERL 的 xpos 和 HTML div/img 的 xpos
- [ ] **P2.7-22**: 图片框透明边距偏移（已采用偏移补偿方案，保留优化空间）
  - 当前方案：`L_FRAME_PAD_X = 6` / `L_FRAME_PAD_Y = 6`，xpos/ypos 负偏移补偿
  - 偏移值来源：FLAN_GRAPHIC_FRAME 中横框/竖框的 6px 内缩
  - 保留的其他解决思路：
    1. 精灵裁剪：重新制作精灵资源，去掉透明边距（最干净，但需美术配合）
    2. depth 前置：图形帧 depth > div depth，帧覆盖在 div 上层
    3. div 缩小：div 的 width/height 减去透明边距
- [ ] **P2.7-23**: 扩展中层组件：`FLAN_UI_DIALOG`（对话框组件）
  - 角色名 + 立绘 + 文本框 + 选项按钮
- [ ] **P2.7-24**: 扩展中层组件：`FLAN_UI_NOTIFY`（系统通知组件）
  - 顶部/底部浮动通知条
- [ ] **P2.7-25**: 引擎层动画指令集成
  - `FLAN_LETTER_LAYER` + `FADE_PRINT` 实现信箱淡入
  - `FLAN_LETTER_LAYER` + `LAYER_FADEIN` 实现信箱+背景淡入

### 两种渲染方案

| 方案 | 函数 | 技术 | 优势 | 劣势 |
|------|------|------|------|------|
| A: 图层 | `FLAN_LETTER_LAYER` | SETIMAGELAYERL + div | 图层解耦，支持 depth z-order、opacity 动画 | 需 ShapePositionShift 补偿 |
| B: 内联 | `FLAN_LETTER_INLINE` | img + 负 space + div | 天然与文本流对齐，无需 GETLINEY | img/div 在同一行，灵活性较低 |

### 关键技术决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 底层返回值 | 直接 HTML_PRINT 输出 | 当前阶段简单直接，后续可改为返回字符串 |
| 两种方案并存 | 函数参数切换 | 不同场景选不同方案，渐进升级 |
| 图形帧实现 | 9-slice GDRAWSPRITE | 参考 pops-tw 验证过的方案，精灵资源已就位 |
| GID 管理 | FLAN_ALLOC_GID（9000~9099） | 避免与现有代码冲突 |
| 帧透明边距 | 偏移补偿（L_FRAME_PAD_X/Y = 6） | 最小改动，效果可接受 |
| CENTERED 语义 | 只控制文本在 div 内的对齐 | 与 LETTERBOX_DRAW 一致，box 屏幕定位暂缓 |
| ARGB 颜色 | `ARGB_TO_HTML_COLOR()` 输出 8 位 | 引擎 HTML 解析器支持 >6 位为 ARGB 模式 |
| SETIMAGELAYERL 锚定 | GetLineNo（显示行索引） | v7.3.1 修复：LineCount 是逻辑行号，与 displayLineList 索引不一致 |
| 颜色哨兵值 | `int.MinValue` | v7.3.1 修复：`-1` 与 `0xFFFFFFFF`（白色 ARGB）冲突 |
| border 默认颜色 | Config.ForeColor | v7.3.1 修复：无 bcolor 时边框不绘制 |

---

## Phase 3: VN 系统高级功能

### 待办

- [ ] **P3-1**: 立绘表情切换动画（opacity 渐变 + ColorMatrix）
- [ ] **P3-2**: 转场效果库（百叶窗/淡入淡出/滑动/缩放）
- [ ] **P3-3**: 文本框样式定制（div 封装 + 圆角/边框/背景色）
- [ ] **P3-4**: 音效同步（按键音/环境音/BGM 切换）
- [ ] **P3-5**: 夜间滤镜（ColorMatrix 全局色调偏移）
- [ ] **P3-6**: 时间停止蒙版（ColorMatrix 反色 + opacity）

---

## 源码索引

| 文件 | 角色 |
|------|------|
| [Flan_UI.ERB](file:///d:/eratw-chs/ERB/魔改内容/PRINT系/Flan_UI.ERB) | Flan UI 函数库（图形帧+信箱组件） |
| [Toolkits.ERB](file:///d:/eratw-chs/ERB/魔改内容/PRINT系/Toolkits.ERB) | PRINT 系工具库（LETTER_TEXT_TO_HTML 等） |
| [UI_Components_&_Tables.ERB](file:///d:/eratw-chs/ERB/魔改内容/PRINT系/UI_Components_&_Tables.ERB) | HTML 组件库（ARGB_TO_HTML_COLOR 等） |
| `ERB\TITLE.ERB` | 标题画面（Phase 1 修改目标） |
| `ERB\魔改内容\QOL_IMAGE.ERB` | 立绘渲染系统（Phase 2 参考） |

## 外部参考

| 文件 | 角色 |
|------|------|
| [pops-tw VNStuff.ERB](file:///d:/pops-tw/ERB/TRANSLATION/OMOGATARI/DESIGN/VNStuff.ERB) | VN 系统原始实现 |
| [pops-tw VNStuff.ERH](file:///d:/pops-tw/ERB/TRANSLATION/OMOGATARI/DESIGN/VNStuff.ERH) | VN 变量定义 |
| [pops-tw Title.ERB](file:///d:/pops-tw/ERB/TRANSLATION/OMOGATARI/Title.ERB) | NAS 标题画面（CBG 全量重绘参考） |
| [ImageLayerManager.cs](file:///d:/emuera/emuera_lazyloading_selfmodified_version/Emuera/UI/Game/ImageLayerManager.cs) | 引擎图层管理核心 |
| [ColorMatrixHelper.cs](file:///d:/emuera/emuera_lazyloading_selfmodified_version/Emuera/UI/Game/image/ColorMatrixHelper.cs) | ColorMatrix 解析 |
| [setimagelayer.md](file:///d:/emuera/shared-trae/knowledge/erabasic/setimagelayer.md) | SETIMAGELAYER 知识库 |
| [color-pipeline.md](file:///d:/emuera/shared-trae/knowledge/erabasic/color-pipeline.md) | 颜色管线知识库 |
