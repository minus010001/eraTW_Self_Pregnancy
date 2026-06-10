# PRINT系 函数库文档

> PRINT是游戏中最重要的交互流程，为此，历史上多个era游戏及其变体都开发了各自的PRINT工具。为避免重复造轮子和引导创作者，将这些函数全部归纳在此。

## 目录

1. [打印与交互 (Print and Input)](#1-打印与交互-print-and-input)
2. [排版与字符串处理 (String Layout & Format)](#2-排版与字符串处理-string-layout--format)
3. [UI 组件与制表 (UI Components & Tables)](#3-ui-组件与制表-ui-components--tables)
4. [视觉特效与动画 (Visual Effects & Animations)](#4-视觉特效与动画-visual-effects--animations)
5. [工具箱 (Toolkit)](#5-工具箱-toolkit)
6. [使用建议](#使用建议)

---

## 1. 打印与交互 (Print and Input)

PRINT系函数的封装，PRINT系与INPUT交互的封装。

### 1.1 符号打印

#### 等级符号打印

| 函数 | 说明 |
|------|------|
| `@PRINT_RANK(VAR_VALUE, RANK_SCALE)` | 打印等级符号（Ex/SS/S/A/B/C/D...） |
| `@GET_RANK_HTML(VAR_VALUE, RANK_SCALE)` | 生成等级符号HTML字符串 |
| `@PRINT_ALPHABET(RANK, RANK_NUM, ARG)` | 打印字母式等级 |
| `@GET_ALPHABET_HTML(RANK, RANK_NUM, ARG=0)` | 生成字母等级HTML字符串 |

#### 颜色印章打印

| 函数 | 说明 |
|------|------|
| `@COLOR_STAMP(STAMP_NUM, MAX_NUM, STAMP_STR, STAMP_COLOR, ARG)` | 带颜色符号印章 |
| `@GET_STAMP_HTML(STAMP_NUM, MAX_NUM, STAMP_STR, STAMP_COLOR, ARG)` | 生成印章HTML字符串 |

#### 特殊符号打印（HTML渲染，统一使用HTMLFONT封装）

| 函数 | 说明 |
|------|------|
| `@HEARTMARK(L_COUNT, L_MODE)` | 粉色爱心 |
| `@GET_HEARTMARK_HTML(L_COUNT, USE_COLOR)` | 生成爱心HTML字符串 |
| `@SHYMARK(L_COUNT, L_MODE)` | 害羞斜杠（///） |
| `@GET_SHYMARK_HTML(L_COUNT, USE_COLOR)` | 生成斜杠HTML字符串 |
| `@MSG_CODE(ARGS)` | MS Gothic字体符号 |
| `@GET_MSG_CODE_HTML(ARGS)` | 生成符号HTML字符串 |

#### 纯文本符号

| 函数 | 说明 |
|------|------|
| `@GET_HEART()` | 返回 ♥ |
| `@CLIP_HEART(L_STR)` | 前后包裹 ♥ 符号 |

### 1.2 文本打印

#### 带颜色/字型的文本打印

| 函数 | 说明 |
|------|------|
| `@COLORMESSAGE(L_STR, L_COLOR, L_TYPE, L_STYLE)` | 带颜色打印（支持SETCOLOR/SETFONT） |
| `@COND_COLORMESSAGE(COND, MESSAGE, L_COLOR, L_TYPE)` | 条件满足时着色打印 |
| `@PRINTCOLOR(L_COLOR, L_STR, L_TYPE)` | 颜色优先的打印 |
| `@PRINTCOLORL(L_COLOR, L_STR)` | 带颜色换行打印 |
| `@PRINTCOLORW(L_COLOR, L_STR)` | 带颜色等待打印 |

#### 特殊标记解析

| 函数 | 说明 |
|------|------|
| `@HPH_PRINT(L_STR, L_MODE)` | 解析HPH/BPB标记并打印 |
| `@CLEARSTRTAGS(L_STR)` | 清除特殊标记 |

**HPH_PRINT 参数说明：**

| L_MODE | 说明 |
|--------|------|
| `""` | 普通打印 |
| `"l"` | 换行 |
| `"w"` | 等待 |
| `"dl"` | 默认色+换行 |
| `"dw"` | 默认色+等待 |

**标记：**
- `HPH` → 粉色爱心
- `BPB` → 粉色斜杠

#### 动态字符串解析打印

| 函数 | 说明 |
|------|------|
| `@PRINT_STR(L_S:0, ...)` | 解析@分隔的动态字符串 |
| `@PRINT_STRL(...)` | PRINT_STR + 换行 |
| `@PRINT_STRW(...)` | PRINT_STR + 等待 |

**@PRINT_STR 支持的标记：**

| 类型 | 标记 | 说明 |
|------|------|------|
| 角色名 | `CALLNAME:TARGET` | 目标角色名 |
| | `CALLNAME:PLAYER` | 玩家名 |
| | `CALLNAME:ASSI` | 助手名 |
| | `CALLNAME:MASTER` | 主人名 |
| 按钮 | `BUTTON` | 按钮 |
| | `BUTTONS` | 带参数的按钮 |
| | `BUTTONNUM` | 数字按钮 |
| | `NOBUTTON` | 非按钮文本 |
| 控制 | `-` | 删除线 |
| | `L` | 换行 |
| | `W` | 等待 |
| | `WAIT` | 等待 |
| | `FORCEWAIT` | 强制等待 |
| 颜色 | `RGB` | RGB颜色 |
| | `HEX` | HEX颜色 |
| 字型 | `Ｂ`/`BOLD` | 粗体 |
| | `UNDER` | 下划线 |
| | `ITALIC` | 斜体 |
| | `STRIKE` | 删除线 |
| 特殊符号 | `H`/`HEART`/`HPH` | 爱心 |
| | `／／／`/`BPB` | 斜杠 |

#### 对话框打印

| 函数 | 说明 |
|------|------|
| `@PRINT_DIALOGUE(L_STR, L_FLAGS)` | 带括号的角色对话打印 |

**L_FLAGS 参数：**
- `"p"` = 中文括号（）
- `"t"` = 书名号『』
- 默认 = 「」
- `"d"` = 逐字打字效果
- `"dc"` = 直接打印

### 架构说明

符号打印类函数采用**双层架构**：

```
GET_*_HTML  → #FUNCTIONS，生成HTML字符串，供其他函数调用
PRINT_*     → 直接调用 HTML_PRINT xxx, 1 输出（第二参数1=不换行）
```

HTML渲染统一使用底层封装器：

```
HTMLFONT(text, font_face, color)  → 字体/颜色包装（color=-1时继承当前色）
```

**示例：**

```erb
HTML_PRINT GET_HEARTMARK_HTML(3), 1
等价于
CALL HEARTMARK, 3
```

---

## 2. 排版与字符串处理 (String Layout & Format)

式中函数，不产生任何屏幕输出，仅负责加工字符串。

### 2.1 基础工具

#### 宽度计算

| 函数 | 说明 |
|------|------|
| `@MAXWIDTH()` | 当前屏幕最大半角字符数 |
| `@MAXWIDTH_PX()` | 当前屏幕最大像素宽度 |

#### 宽度转换

| 函数 | 说明 |
|------|------|
| `@TO_PXWIDTH(L_W)` | 半角字符数→像素宽度 |

### 2.2 字符串对齐与填充

#### 居中对齐

| 函数 | 说明 |
|------|------|
| `@CENTER(L_STR, L_WIDTH)` | 指定宽度内居中 |
| `@CENTERSCREEN(L_STR)` | 屏幕宽度内居中 |

#### 单元格对齐

| 函数 | 说明 |
|------|------|
| `@UNITCELL(L_STR, CELL_WIDTH)` | 单元格对齐（按倍数扩展，不截断） |
| `@FIXEDCELL(L_STR, CELL_WIDTH)` | 固定宽度单元格（超长截断） |

#### 行处理

| 函数 | 说明 |
|------|------|
| `@FULLWIDTH_LB(L_STR, L_BR_STR, L_LEN)` | 全角字符换行 |
| `@BREAKENG(L_STR, L_INDENT, L_BR_STR, L_LEN, L_MATCH)` | 英文单词换行 |
| `@HTML_BREAKLINE(HTML_STR, WIDTH_CHAR)` | HTML字符串自动换行（CJK友好，基于渲染宽度） |
| `@HTML_BREAKCJK(L_TEXT, L_WIDTH)` | CJK换行工具（"/"手动换行 + HTML_BREAKLINE自动折行） |

#### 空格与填充

| 函数 | 说明 |
|------|------|
| `@BL(L_COUNT)` | 生成半角空格 |
| `@TEXT_RJ(L_STR, L_LEN)` | 右对齐填充 |
| `@TEXT_LJ(L_STR, L_LEN)` | 左对齐填充 |

### 2.3 数字格式化

| 函数 | 说明 |
|------|------|
| `@ORDINAL(L_NUM)` | 序数词 (1st, 2nd, 3rd) |
| `@DIGIT_GROUP(L_NUM)` | 千位分隔符 (1,000) |

### 2.4 文本特效

| 函数 | 说明 |
|------|------|
| `@STUTTER(L_STR, L_FLAGS)` | 结巴修饰 (I-I-I am...) |

**L_FLAGS 参数：**
- `"nospecial"`/`"special"` - 是否启用特殊效果
- `"shy"`/`"noshy"` - 是否害羞效果
- `"ss"`/`"noss"` - 是否重复效果

### 2.5 大小写处理

| 函数 | 说明 |
|------|------|
| `@CAP_PROCESS(L_STR, L_MODE)` | 大小写转换 |
| `@CAPITALIZE(L_STR)` | 首字母大写 |
| `@UNCAPITALIZE(L_STR)` | 首字母小写 |
| `@RAND_CAP(L_STR)` | 随机大小写 |
| `@CAP_WORD(L_STR)` | 单词首字母大写 |
| `@RETURN_CAP(L_STR_REF, L_STR_TGT)` | 根据参考字符串大小写格式化目标 |
| `@IS_CAPITALIZED(L_STR)` | 判断是否首字母大写 |

**CAP_PROCESS 的 L_MODE：**
- `1` = 小写
- `2` = 大写
- `3` = 首大写
- `4` = 随机
- `5` = 单词首大写

---

## 3. UI 组件与制表 (UI Components & Tables)

由模块1、模块2组成的拼装而成的高级静态 UI 组件，及其辅助颜色模块。

### 3.1 颜色系统

#### 基础颜色转换与提取

| 函数 | 说明 |
|------|------|
| `RGB_TO_HEX` / `RGBCOLOR` | RGB→0xRRGGBB |
| `HEX_R` / `HEX_G` / `HEX_B` | HEX拆出R/G/B分量 |
| `HEX_TO_RGB` / `HEX_TO_RGB_F` | HEX→RGB数组 |
| `HEX_TO_HTML_COLOR` / `HEX_TO_STR` | 转为#RRGGBB字符串 |

#### HSV 颜色系统（核心渐变基础）

| 函数 | 说明 |
|------|------|
| `RGB_TO_HSV` / `HSV_TO_RGB` | RGB↔HSV (打包格式：H<<16 \| S<<8 \| V) |
| `BRIGHTCOLORF` / `BRIGHTCOLOR` | 调整明度 |
| `COLOR_LERP_HSV` | HSV空间线性插值（最自然渐变） |

#### 动态颜色（呼吸灯/渐变）

| 函数 | 说明 |
|------|------|
| `GET_CHANGING_COLOR(L_TYPE, L_TIME_SEED, L_OFFSET)` | 生成呼吸灯颜色 |
| `SET_CHANGING_COLOR(L_TYPE, L_OFFSET)` | 设置呼吸灯颜色 |

**L_TYPE 参数：**

| 值 | 效果 |
|----|------|
| `1` | 科技蓝白呼吸 |
| `2` | 彩虹循环 |
| `3` | 深海幽蓝呼吸 |
| `4` | 警告红黄呼吸 |
| `5` | 樱花粉白呼吸 |
| `6` | 逆彩虹循环 |

#### 颜色混合与 Alpha 处理

| 函数 | 说明 |
|------|------|
| `MIX_COLOR` | 两色按权重混合 |
| `CALC_ALPHA_COLOR` | 带透明度的前景+背景融合 |
| `SET_ALPHA_COLOR` / `RESET_ALPHA_COLOR` | 旧版兼容：设置/重置带Alpha颜色 |
| `SET_CHARA_COLOR` | 角色性别对应颜色 |
| `HTMLCCHK` | 检查HTML颜色字符串合法性 |

#### 颜色映射（已废弃，仅兼容保留）

| 函数 | 说明 |
|------|------|
| `@COLOR` / `@BARCOLORSET` | 颜色名映射（强烈不建议新增调用） |

### 3.2 进度条系统

#### 字符式进度条（HTML `<font>` 实现，轻量、易混排）

| 函数 | 说明 |
|------|------|
| `QOL_HTML_BARSTR(VAL, MAX_VAL, L_LEN, COLOR_FG, COLOR_BG, CHAR_FG, CHAR_BG, COLOR_FG2)` | 核心生成器：支持HSV逐字符渐变、自定义字符 |
| `PRINT_COLORBAR` | 直接打印版（最常用） |
| `HTML_COLORBAR` | 返回字符串版（兼容旧接口） |
| `BW_BAR` | 黑白/灰阶简洁版 |
| `COLOR_BAR` | 带彩虹尾渐变的专用条 |

#### 像素级矩形进度条（`<shape>` 实现，高精度、现代感）

| 函数 | 说明 |
|------|------|
| `HTML_RECT_BAR(VAL, MAX_VAL, WIDTH, HEIGHT, COLOR_FG, COLOR_BG, COLOR_FG2, Y_OFFSET)` | 像素级HSV渐变矩形条 |
| `PRINT_RATE_BAR` / `PRINT_RATE_BAR_EX` | 高精度分段条 |
| `LAYER_RECTBAR` | 旧接口兼容层 |

**PRINT_RATE_BAR_EX 的 L_FLAG 参数：**

| 值 | 说明 |
|----|------|
| `0x0001` | 超限(LimitOver) |
| `0x0002` | 高度=40 |
| `0x0004` | 高度=12 |
| `0x0008` | 高度=90 |
| `0x0010` | BOTTOM对齐 |
| `0x0020` | TOP对齐 |
| `0x1000` | 分段间隙 |

### 3.3 HTML 组件封装器

HTML属性打包器（按顺序组合）：

| 函数 | 说明 |
|------|------|
| `HTMLSTYLE(L_TEXT, STYLE_FLAG)` | 字型包装（粗体/斜体/删除线/下划线） |
| `HTMLFONT(L_TEXT, FONT_FACE, FONT_COLOR, BG_COLOR)` | 字体与颜色包装（数值版） |
| `HTMLFONTS(L_TEXT, FONT_FACE, FONT_COLOR, BG_COLOR)` | 字体与颜色包装（字符串版） |
| `HTMLP(L_TEXT, ALIGN_STR)` | 段落对齐包装 |
| `HTMLWRAP(...)` | 综合包装器（自动继承当前样式） |

**使用示例：**

```erb
HTMLFONT("文本", "MS Gothic", C_RED)   → 指定红字/MS Gothic字体
HTMLFONT("文本", "", -1)                → 当前颜色/继承字体
HTMLFONT("文本", "", GETCOLOR())         → 指定当前系统色
```

### 3.4 按钮组件

#### 扩展按钮

| 函数 | 说明 |
|------|------|
| `GET_PRINTBUTTON_EX_HTML(...)` | 生成扩展按钮HTML字符串 |
| `PRINTBUTTON_EX(...)` | 打印扩展按钮 |

**GET_PRINTBUTTON_EX_HTML 参数：**

| 参数 | 说明 |
|------|------|
| `BTN_TEXT` | 按钮显示文本 |
| `BTN_VAL` | 按钮值 |
| `IS_GRAY` | 是否置为灰色 |
| `IS_YELLOW` | 是否置为黄色 |
| `IS_DISABLED` | 是否禁用 |
| `WITH_BORDER` | 是否包裹"□"并用"-"填满整行 |
| `OVERRIDE_WIDTH` | 强制指定的行宽(半角字数) |

#### 内联按钮（送入制表缓存）

| 函数 | 说明 |
|------|------|
| `GET_PRINTBUTTON_EXC_HTML(...)` | 生成内联按钮HTML字符串 |
| `HTML_PRINTBUTTON_EXC(...)` | 打印内联按钮（封装HTML_PRINTBUTTONC） |

#### 通用按钮构建

| 函数 | 说明 |
|------|------|
| `BUILD_COM_BUTTON_HTML(COM_VAL, COM_TEXT, OPTION_NAME, OVERRIDE_COLOR)` | 指令菜单统一构建工具 |

### 3.5 制表系统

#### 制表打印

| 函数 | 说明 |
|------|------|
| `HTML_PRINTBUTTONC(L_TEXT, L_VAL, L_COLOR, L_ALIGN, IS_DISABLED)` | 封装内置HTML_PRINTC/HTML_PRINTLC，自动管理制表与换行 |
| `HTML_PRINTBUTTONC_FLUSH` | 强制换行（内置HTML_PRINTC自动管理换行，此函数仅用于主动换行） |

#### 行装饰

| 函数 | 说明 |
|------|------|
| `GET_PRINTLINE_HTML(L_STR, FILL_CHAR, NO_SQUARE)` | 生成分割线HTML字符串 |
| `PRINTLINE(L_STR, FILL_CHAR, NO_SQUARE)` | 打印带标题分割线 |

**示例：**
```
PRINTLINE "任务信息"  → □ 任务信息 □---------
```

#### 填充工具

| 函数 | 说明 |
|------|------|
| `HTML_FILL_LINE(HTML_STR, FILL_CHAR, TARGET_PX, ALIGN)` | 单行填充制表：将字符串用指定字符补齐到目标宽度 |

### 3.6 装饰性 UI 元素

| 函数 | 说明 |
|------|------|
| `COLOR_LINE(...)` | 彩色渐变分割线（正向淡出/反向光晕） |

### 3.7 颜色选择器（渲染与交互的高级HTML组件）

| 函数 | 说明 |
|------|------|
| `HTML_PRINT_RGB_SLIDER` | RGB三通道滑块（按钮式） |
| `HTML_PRINT_HSB_SLIDER` | HSB三通道滑块（更符合人眼感知） |

### 3.8 辅助工具

| 函数 | 说明 |
|------|------|
| `HTML_STRLENS(HTML_STR)` | 计算含`<shape>`的HTML字符串实际显示长度 |

---

## 4. 视觉特效与动画 (Visual Effects & Animations)

需要考虑屏幕刷新机能的动态效果渲染。

### 逐字打字效果

| 函数 | 说明 |
|------|------|
| `KEYTYPING(L_STR, L_FLAGS, L_DELAY, L_CHUNK_SIZE)` | 逐字打印特效，支持前后半句切换显示 |

**示例：**
```erb
CALL KEYTYPING("あくま/悪魔", "W", 2)
```
显示：あ → あく → あくま → 悪魔

**L_FLAGS 参数：**
- `"d"` = 对话框标记
- `"dc"` = 默认色
- `"l"` = 换行
- `"w"` = 等待

---

## 5. 工具箱 (Toolkit)

成系列或复杂的工具或者其位置索引。

### 图文混排与立绘系统

四层架构：应用层 → 构建层 → 排版层 → 渲染层。每个输出 HTML 的函数都有 Build（返回字符串）和 Print（直接输出）两种变体。

#### 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│ 应用层 (Application)                                            │
│   SPTALK / PRINT_FACE / PRINT_BODY / PRINT_FACE_PLAYER         │
│   职责：业务语义（CID→路由、表情拆分、口上色、MOB硬编码）      │
├─────────────────────────────────────────────────────────────────┤
│ 构建层 (Composition)                                            │
│   BUILD_FIGURE_HTML / BUILD_CHARA_IMAGE_BLOCK                  │
│   职责：业务参数→HTML字符串（不打印，返回值）                  │
├─────────────────────────────────────────────────────────────────┤
│ 排版层 (Layout)                                                 │
│   LAYOUT_IMG_TEXT / HTML_PRINTL_PX                              │
│   职责：图像+文本→图文混排HTML / 图像→换行补齐                │
│   IMG_TALK 与 QOL_SPTALK 均通过 LAYOUT_IMG_TEXT 完成排版输出   │
├─────────────────────────────────────────────────────────────────┤
│ 渲染层 (Render)                                                 │
│   ASSEMBLE_HTML_IMAGE_LAYERS / IMAGE_COMPONENT_FILTER           │
│   职责：多图层→重叠img标签 / 像素变换特效                      │
└─────────────────────────────────────────────────────────────────┘
```

#### 构建层函数（返回 HTML 字符串，不打印）

| 函数 | 文件 | 说明 |
|------|------|------|
| `BUILD_FIGURE_HTML(CID, 表情, 服装, 差分, エフェクト, 立绘种类, 立绘选择, EFFECT_OVERRIDE, BTN_VAL)` | QOL_IMAGE.ERB | 构建角色立绘 HTML 块，返回 RESULTS=HTML, RESULT=高度 |
| `BUILD_CHARA_IMAGE_BLOCK(...)` | QOL_IMAGE.ERB | 构建多图层立绘 HTML（底层，含特效叠加） |
| `BUILD_MOB_IMAGE_BLOCK(...)` | QOL_IMAGE.ERB | 构建路人立绘 HTML |

#### 应用层函数（直接打印）

| 函数 | 文件 | 说明 |
|------|------|------|
| `IMG_TALK(IMG_RES, HTML_TEXT, CID, AUTO_FMT, IMG_H_PX, CUSTOM_C)` | Toolkits.ERB | 简单图文混排，委托 LAYOUT_IMG_TEXT |
| `QOL_SPTALK(CID, 表情, デフォルト, MESSAGE, 整形, CUSTOMFONTCOLOR, エフェクト, EFFECT_OVERRIDE)` | Toolkits.ERB | 立绘表情对话，委托 BUILD_FIGURE_HTML + LAYOUT_IMG_TEXT |
| `PRINT_FIGURE(CID, 表情, 服装, 差分, エフェクト, 立绘种类, 立绘选择, EFFECT_OVERRIDE)` | QOL_IMAGE.ERB | 打印角色立绘，委托 BUILD_FIGURE_HTML |
| `PRINT_FACE(CID, ...)` | 顔絵表示.ERB | 打印角色颜绘，委托 PRINT_FIGURE |
| `PRINT_BODY(CID, ...)` | QOL_IMAGE.ERB | 打印角色膝上绘，委托 PRINT_FIGURE |
| `PRINT_FACE_PLAYER(CID, ...)` | QOL_IMAGE.ERB | 打印玩家立绘，委托 PRINT_FIGURE |

#### 排版层函数

| 函数 | 文件 | 说明 |
|------|------|------|
| `LAYOUT_IMG_TEXT(IMG_HTML, IMG_H_PX, IMG_W_PX, FONTCOLOR, TEXT, AUTO_FMT)` | Toolkits.ERB | 图文混排排版底层，图像+文本→并排HTML→打印+换行 |
| `HTML_PRINTL_PX(HTML_STR, IMG_H_PX)` | HTML_PRINT_Components.ERB | 纯图像打印+换行补齐 |

#### 颜色工具

| 函数 | 文件 | 说明 |
|------|------|------|
| `RESOLVE_KOJO_COLOR(CID, CUSTOM_C)` | UI_Components_&_Tables.ERB | 解析角色口上色，返回 RESULTS=#RRGGBB |
| `HTMLCCHK(COLOR_STR, DEFAULT_HEX)` | UI_Components_&_Tables.ERB | 验证+修复 HTML 颜色字符串 |

#### 调用关系

```
SPTALK ──→ BUILD_FIGURE_HTML ──→ BUILD_CHARA_IMAGE_BLOCK ──→ ASSEMBLE_HTML_IMAGE_LAYERS
       ──→ RESOLVE_KOJO_COLOR
       ──→ LAYOUT_IMG_TEXT

IMG_TALK ──→ RESOLVE_KOJO_COLOR
         ──→ LAYOUT_IMG_TEXT

PRINT_FIGURE ──→ BUILD_FIGURE_HTML ──→ BUILD_CHARA_IMAGE_BLOCK ──→ ASSEMBLE_HTML_IMAGE_LAYERS
             ──→ HTML_PRINTL_PX
```

### Letterbox 信箱组件

三层架构：上层兼容接口 → 中层转换 → 底层渲染。

#### 上层兼容接口

| 函数 | 说明 |
|------|------|
| `@PRINT_LETTER(LINES, MINWIDTH, MAXWIDTH, CENTERED)` | 信箱打印（兼容原版签名，内部改用 LETTERBOX_DRAW） |
| `@LETTER_CALC_WIDTH(L_TEXT)` | 计算信箱内容所需宽度（按"/"分段取最长段） |

#### 中层转换

| 函数 | 说明 |
|------|------|
| `@LETTER_TEXT_TO_HTML(L_TEXT, L_WIDTH, L_COLOR)` | 纯文本→HTML（"/"换行 + 自动折行 + 字体颜色） |

#### 底层渲染

| 函数 | 说明 |
|------|------|
| `@LETTERBOX_HTML(HTML_CONTENT, L_WIDTH, L_ALIGN, L_BORDER_C, L_BG_C, L_PADDING)` | HTML div 封装版信箱（现代渲染，支持边框/背景/内边距） |
| `@LETTERBOX_DRAW(HTML_CONTENT, L_WIDTH, L_ALIGN, L_BORDER_C)` | 字符画制表版信箱（`┌─┐│└┘`，兼容渲染，用 `<shape>` 精确填充） |

**架构关系：**

```
PRINT_LETTER（上层，兼容原版）
  └→ LETTER_TEXT_TO_HTML（中层，纯文本→HTML）
       └→ HTML_BREAKCJK（换行工具，在 String_Layout_&_Format.ERB）
            └→ HTML_BREAKLINE（底层自动折行）
       └→ LETTERBOX_DRAW / LETTERBOX_HTML（底层渲染）
```

---

## 使用建议

- **渐变颜色**：所有渐变均使用HSV空间（`COLOR_LERP_HSV`），色彩过渡更鲜艳、自然
- **字符条**：`QOL_HTML_BARSTR`系适合文字混排、轻量UI
- **矩形条**：`HTML_RECT_BAR`/`PRINT_RATE_BAR_EX`适合血条、经验条、冷却条等
- **分段条**：`PRINT_RATE_BAR_EX`支持超限延伸、多层叠加、间隙、对齐，是最灵活的高级组件
- **渲染性能**：建议在主调用函数中开启 `BITMAP_CACHE_ENABLE 1` 以提升复杂shape渲染性能
- **HTML渲染**：统一使用`HTMLFONT`封装，`color=-1`时自动继承当前控制台颜色
- **符号打印**：采用双层架构 `GET_*_HTML`（生成字符串）+ `PRINT_*`（输出打印）
