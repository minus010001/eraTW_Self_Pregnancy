# DRAW_COLOREDMAP 重构深度分析手册

## 目录

1. [原函数功能梳理](#1-原函数功能梳理)
2. [调用链与上下文](#2-调用链与上下文)
3. [渲染模式分析：阻塞 vs 非阻塞](#3-渲染模式分析阻塞-vs-非阻塞)
4. [瓶颈根因：滚动刷新的底层机制](#4-瓶颈根因滚动刷新的底层机制)
5. [动图渲染 + 静态 DIV 交互框架](#5-动图渲染--静态-div-交互框架)
6. [实施方案](#6-实施方案)
7. [风险与注意事项](#7-风险与注意事项)

---

## 1. 原函数功能梳理

### 1.1 `@DRAW_COLOREDMAP` 的核心职责

原始 `@DRAW_COLOREDMAP(ANIMATION_SEED, ARGS)` 位于 `ERB\COLOREDMAPS\DRAW_COLOREDMAP.ERB`，其核心职责为：

| 职责 | 说明 |
|------|------|
| **地图数据获取** | 根据 `ARGS`（空/`"ODEKAKE"`/`"GLOBAL"`）调用对应的 `COLOREDMAP_*`、`COLOREDODEKAKEMAP_*` 或 `COLOREDFIELD` 获取 `MAP[]` 和 `COLOR[]` 数组 |
| **逐行逐字渲染** | 遍历 42 行地图数据，对每个字符判断类型（数字→地点按钮 / 季节动画字符→动态着色 / 普通字符→直接输出） |
| **动画字符处理** | 通过 `@GETANIMATIONCHARACTER` 根据类型（`water`/`ground`/`flower`/`flame`/`steam` 等）和 `ANIMATION_SEED` 计算当前帧的字符与颜色 |
| **季节颜色系统** | 通过 `@GETSEASONALCOLORS` 处理竹/花/樱的季节渐变色，支持雪效果覆盖 |
| **地点按钮生成** | 数字位置调用 `@GETMAP` 获取状态颜色和 Tooltip，生成 `<button>` 标签 |
| **时停颜色反转** | `@APPLYCOLOR` / `@APPLYCOLOR_F` 在 `FLAG:70`（时停）时对颜色取反 |

### 1.2 渲染输出格式

原函数逐行调用 `HTML_PRINT`，每行输出结构为：

```
<font face='ＭＳ ゴシック'>
  <font color='#RRGGBB'><button value='LOC' title='Tooltip'>字</button></font>
  <font color='#RRGGBB'>动画字符</font>
  ...
</font>
```

**关键特征**：每行一次 `HTML_PRINT`，共最多 42 次调用，产生 42 行输出。

### 1.3 `@DRAW_COLOREDMAP_GD` 的重构改进

重构版本 `DRAW_COLOREDMAP_GD.ERB` 将渲染拆分为两层：

| 层 | 实现 | 说明 |
|----|------|------|
| **底图动画层** | `BUILD_MAP_BG_ANIMATION` → `SPRITEANIMECREATE` + `SPRITEANIMEADDFRAME` | 预渲染 20 帧到 Graphics，组装为动画精灵，由 `SETANIMETIMER` 驱动自动播放 |
| **交互按钮层** | `DRAW_COLOREDMAP_GD` → `<div rect='...'><button><img src='...' srcb='...'></button></div>` | 动态解析地点状态，生成高亮图/悬停图精灵，用 `<div>` 精确定位覆盖在底图上 |

最终 HTML 结构：

```html
<img src='MAP_ANIME_cacheKey' height='CANVAS_HEIGHTpx'>   <!-- 动画底图 -->
<shape type='space' param='-MAX_WIDTH_PXpx'>               <!-- 回退光标 -->
<div rect='X,Y,W,H'>                                       <!-- 按钮覆盖层 -->
  <button value='LOC' title='Tooltip'>
    <img src='MAP_COLOR_...' srcb='MAP_HOVER_...' width='Wpx' height='Hpx'>
  </button>
</div>
...
```

---

## 2. 调用链与上下文

### 2.1 主要调用路径

```
@COM400 (移动指令)
  ├─ @QOL_COM400 (魔改版入口，优先调用)
  │    ├─ @COM400_DRAW_UI(ANIMATION_SEED, UI_MESSAGE)
  │    │    └─ @DRAW_COLOREDMAP(ANIMATION_SEED)  ← 原版渲染
  │    ├─ @AWAIT_UI_INPUT(CONFIG, UPDATE_TIME)   ← 非阻塞输入
  │    └─ @COM400_PROCESS_INPUT(EVENT_TYPE, EVENT_DATA, UI_MESSAGE)
  │
  └─ (原版路径) @COM400
       ├─ @DRAW_COLOREDMAP(ANIMATION_SEED)       ← 原版渲染
       ├─ TINPUTS ANIMATERECOLOREDMAPS, "UPDATE"  ← 定时输入
       └─ INPUTS                                  ← 阻塞输入

@COM604 (散步指令)
  └─ @QOL_COM604
       ├─ @COM604_DRAW_UI → @DRAW_COLOREDMAP(ANIMATION_SEED, "ODEKAKE")
       └─ @AWAIT_UI_INPUT

@OTHERREGIONS / 魔法DLC
  └─ @DRAW_COLOREDMAP(ANIMATION_SEED, "GLOBAL")
```

### 2.2 GD 版调用路径（目标架构）

```
@QOL_COM400_GD (GD版入口)
  ├─ SETANIMETIMER 40
  ├─ @DRAW_COLOREDMAP_GD(MAP_MODE)  ← 一次性渲染
  │    ├─ @BUILD_MAP_BG_ANIMATION    ← 底图缓存（每日/切换时）
  │    └─ HTML_PRINT FINAL_HTML      ← 动画精灵 + 按钮覆盖
  ├─ INPUTS                           ← 阻塞输入（动画由 SETANIMETIMER 驱动）
  └─ @COM400_PROCESS_INPUT
```

---

## 3. 渲染模式分析：阻塞 vs 非阻塞

### 3.1 阻塞模式（原版 `INPUTS` / `TINPUTS`）

**流程**：

```
渲染地图 → INPUTS等待 → 用户输入 → 处理 → 重新渲染
                ↑
         TINPUTS超时 → CLEARLINE → 重新渲染 → 回到等待
```

**动画实现**（原版 COM400）：

```erb
; 动画开启时
IF ANIMATERECOLOREDMAPS && !FLAG:70
    TINPUTS ANIMATERECOLOREDMAPS, "UPDATE", 0, ""
ELSE
    INPUTS
ENDIF

; 超时处理
CASE "UPDATE"
    REDRAW 0
    CLEARLINE LINECOUNT - LINESTART
    BREAK    ; → 回到 $MAPANIMATION 重绘
```

**痛点**：

| 问题 | 原因 |
|------|------|
| **滚动被强制回底** | `CLEARLINE` + 重新 `HTML_PRINT` 产生新行 → `verticalScrollBarUpdate()` 自动将 `ScrollBar.Value += move` → 强制滚动到底部 |
| **输入框闪烁** | 每次重绘都重新创建输入框，用户正在输入的内容丢失 |
| **CPU 占用高** | 每帧都要重新解析地图数据、生成 HTML、调用 `HTML_PRINT` |
| **Tooltip 丢失** | `CLEARLINE` 清除所有行，包括按钮的 Tooltip 状态 |

### 3.2 非阻塞模式（`AWAIT` + `AWAIT_UI_INPUT`）

**流程**：

```
渲染地图 → AWAIT循环 {
    AWAIT 16ms
    检查 MOUSEB() → 悬停状态
    检查 GETKEYTRIGGERED → 按键/鼠标
    检查超时 → 动画Tick
} → 事件触发 → 处理 → 条件重绘
```

**动画实现**（QOL_COM400）：

```erb
IF AWAIT_HANG
    CALL AWAIT_UI_INPUT(LISTEN_CONF, UPDATE_INTERVAL)
ELSE
    TINPUTS 1500, "UPDATE", 0, ""
ENDIF
```

**`AWAIT_UI_INPUT` 内部**：

```erb
DO
    AWAIT AWAIT_TIME        ; 释放 CPU 16ms
    IF MOUSEB() != AWAIT_HOVER_VALUE
        ; 悬停状态变化 → 立即返回 UPDATE
        RETURN 0
    ENDIF
    IF GETKEYTRIGGERED(1)   ; 左键
        RESULTS '= MOUSEB() ; 获取按钮值
        RETURN 1
    ENDIF
    IF GETKEYTRIGGERED(13)  ; 回车
        RESULTS '= GETTEXTBOX()
        RETURN 1
    ENDIF
    ; ... 其他按键检测
    IF UPDATE_TIME > 0 && 超时
        RESULTS '= "UPDATE"
        RETURN 0
    ENDIF
LOOP 1
```

**痛点**：

| 问题 | 原因 |
|------|------|
| **本质是 Hack** | 绕过了 Emuera 原生的 `INPUT` 系统，自行用 `AWAIT` + `GETKEYTRIGGERED` + `MOUSEB()` + `GETTEXTBOX()` 模拟输入 |
| **宏/跳过功能失效** | `AWAIT` 循环中 ESC 跳过、右键跳过、宏展开等 Emuera 内置功能全部不可用 |
| **悬停检测不精确** | `MOUSEB()` 在 `AWAIT` 中返回的是上一次 `INPUT` 状态的缓存值，非实时 |
| **仍需 CLEARLINE 重绘** | 动画 Tick 触发后仍需 `CLEARLINE LINECOUNT - LINESTART` + 重绘，同样导致滚动回底 |
| **文本框同步问题** | `SETTEXTBOX MOUSEB()` 尝试将悬停值写入输入框，但时序不可靠 |

### 3.3 两种模式的核心矛盾

```
┌─────────────────────────────────────────────────────────────┐
│                    核心矛盾图示                               │
│                                                             │
│  阻塞模式 (INPUTS/TINPUTS)                                  │
│  ├── 优点：原生输入系统，宏/跳过/Tooltip 全部可用            │
│  └── 缺点：动画需 CLEARLINE+重绘 → 滚动回底                 │
│                                                             │
│  非阻塞模式 (AWAIT+GETKEY)                                  │
│  ├── 优点：可细粒度控制事件，悬停检测                         │
│  └── 缺点：绕过原生系统，功能残缺，仍需 CLEARLINE            │
│                                                             │
│  共同痛点：动画更新 = CLEARLINE + 重绘 = 滚动回底            │
│  根本原因：HTML_PRINT 产生新行 → verticalScrollBarUpdate     │
│            自动将 ScrollBar.Value += move                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 瓶颈根因：滚动刷新的底层机制

### 4.1 Emuera 渲染管线分析

通过阅读 Emuera 源码 (`EmueraConsole.cs`)，渲染管线如下：

```
ERB: HTML_PRINT / PRINT
  → ConsoleDisplayLine 加入 displayLineList
  → RefreshStrings(force_Paint)
    → verticalScrollBarUpdate()
      → ScrollBar.Maximum = displayLineList.Count
      → ScrollBar.Value += move        ← 自动滚到底部！
    → window.Refresh()
      → OnPaint(graph)
        → 遍历 displayLineList 绘制可见行
```

### 4.2 `verticalScrollBarUpdate` 的自动滚动逻辑

```csharp
private void verticalScrollBarUpdate()
{
    int max = displayLineList.Count;
    int move = max - window.ScrollBar.Maximum;
    if (move == 0)
        return;                         // 行数没变 → 不动
    if (move > 0)
    {
        window.ScrollBar.Maximum = max;
        window.ScrollBar.Value += move; // 新增行 → 自动滚到底！
    }
    // ...
}
```

**关键发现**：只要 `displayLineList` 的行数增加（即有新的 `PRINT`/`HTML_PRINT` 输出），滚动条就会自动移到底部。`CLEARLINE` 减少行数后再 `HTML_PRINT` 增加行数，净效果仍然是 `move > 0`，导致滚动回底。

### 4.3 `SETANIMETIMER` 的渲染路径

```csharp
private void tickRedrawTimer(object sender, EventArgs e)
{
    if (state != ConsoleState.WaitInput || genericTimer.Enabled)
        return;
    window.Refresh();  // 仅触发 OnPaint，不调用 verticalScrollBarUpdate！
}
```

**关键发现**：`SETANIMETIMER` 的定时器回调只调用 `window.Refresh()`，触发 `OnPaint` 重绘当前可见行。**不会调用 `verticalScrollBarUpdate()`，不会改变滚动位置！**

这意味着：如果地图动画通过 `SPRITEANIME` 实现，由 `SETANIMETIMER` 驱动刷新，那么动画播放期间**不会**导致滚动回底。

### 4.4 `RefreshStrings` 的滚动保护

```csharp
public void RefreshStrings(bool force_Paint)
{
    bool isBackLog = window.ScrollBar.Value != window.ScrollBar.Maximum;
    // 用户已向上滚动时，即使 REDRAW=0 也允许重绘（为了显示历史内容）
    if ((redraw == ConsoleRedraw.None) && (!force_Paint) && (!isBackLog))
        return;
    // ...
    verticalScrollBarUpdate();  // 只在有新行时才改变滚动位置
    window.Refresh();
}
```

当 `SETANIMETIMER` 触发 `window.Refresh()` 时，走的是 `tickRedrawTimer → window.Refresh() → OnPaint` 路径，**不经过 `RefreshStrings`**，因此完全不会干扰滚动位置。

### 4.5 根因总结

| 场景 | 是否触发 `verticalScrollBarUpdate` | 是否滚动回底 |
|------|------|------|
| `HTML_PRINT` 新行 | ✅ 是（行数增加） | ✅ 是 |
| `CLEARLINE` + `HTML_PRINT` | ✅ 是（净行数增加或不变但 Value 被重置） | ✅ 是 |
| `SETANIMETIMER` 定时刷新 | ❌ 否（仅 `window.Refresh()`） | ❌ 否 |
| `REDRAW 2` 强制刷新 | ✅ 是（经过 `RefreshStrings`） | 视情况 |

**结论**：只要避免在动画播放期间调用 `HTML_PRINT` / `CLEARLINE`，就不会触发滚动回底。`SPRITEANIME` + `SETANIMETIMER` 天然满足此条件。

---

## 5. 动图渲染 + 静态 DIV 交互框架

### 5.1 核心思路

将地图渲染拆分为两个完全解耦的层：

```
┌──────────────────────────────────────────┐
│  层1：动画底图层 (SPRITEANIME)            │
│  ├── 由 SETANIMETIMER 驱动自动播放        │
│  ├── 仅 window.Refresh() 刷新帧          │
│  └── 不产生新行，不干扰滚动               │
│                                          │
│  层2：交互按钮层 (<div display='absolute'>)│
│  ├── 固定在窗口顶部，不受滚动影响          │
│  ├── <button> + <img src/srcb> 悬停切换   │
│  └── 仅在状态变化时重新渲染               │
│                                          │
│  层3：UI 文本层 (普通 PRINT)              │
│  ├── 当前位置、移动选项、察知说明等        │
│  ├── 正常滚动，不受动画影响               │
│  └── INPUTS 输入框在此层                  │
└──────────────────────────────────────────┘
```

### 5.2 `<div display='absolute'>` 的关键特性

根据 EM+EE 文档：

| 属性 | 说明 |
|------|------|
| `display='absolute'` | 窗口固定位置渲染，**滚动时不移动** |
| `rect='x,y,w,h'` | 简写定位，`(0,0)` 为窗口左下角，y 正方向向上 |
| `depth` | 负值=手前（覆盖其他内容），正值=奥（被覆盖） |
| 行外显示 | **行的高度超出的内容，所在行画面外也能显示** |

**关键**：`display='absolute'` 的 div 即使所在行已滚出可视区域，其内容仍然可见且可交互。这正好满足地图始终可见的需求。

### 5.3 坐标系映射

Emuera 的 `display='absolute'` 坐标系：

```
(0, WindowHeight) ─────────────── (WindowWidth, WindowHeight)
     │                                    │
     │         窗口可视区域                 │
     │                                    │
(0, 0) ─────────────────────────── (WindowWidth, 0)
↑ 左下角，y 正方向向上
```

地图应定位在窗口顶部，因此：

```
MAP_Y = WindowHeight - MAP_HEIGHT   (从窗口底部算起的偏移)
```

可通过 `GETCONFIG` 获取窗口尺寸：

```erb
WINDOW_HEIGHT = GETCONFIG("ウィンドウ高さ")   ; 窗口高度(px)
LINE_HEIGHT = GETCONFIG("一行の高さ")          ; 行高(px)
VISIBLE_LINES = WINDOW_HEIGHT / LINE_HEIGHT    ; 可见行数
```

### 5.4 按钮覆盖层的精确定位

按钮层使用 `<div rect='x,y,w,h'>` 相对于动画底图定位。由于底图在 absolute div 内部，按钮的坐标应与底图像素坐标对齐：

```erb
; 每个地点按钮
HTML_BUTTONS += @"<div rect='{当前位置X}px,{当前位置Y}px,{TILE_W}px,{CELL_HEIGHT}px'>"
HTML_BUTTONS += @"<button value='{REAL_LOC}' title='%HTML_ESCAPE(TOOLTIP_STR)%'>"
HTML_BUTTONS += @"<img src='MAP_COLOR_{CURRENT_COLOR}_%TEMP_TILE%' srcb='MAP_HOVER_{REAL_LOC}' width='{TILE_W}px' height='{CELL_HEIGHT}px'>"
HTML_BUTTONS += @"</button></div>"
```

**注意**：`<div>` 内部的 `rect` 坐标是相对于父 div 的，因此按钮的 `(当前位置X, 当前位置Y)` 直接对应底图上的像素位置，无需额外转换。

### 5.5 动画帧与 SETANIMETIMER 的配合

```erb
; 创建动画精灵（已在 BUILD_MAP_BG_ANIMATION 中完成）
SPRITEANIMECREATE @"MAP_ANIME_%MAP_CACHE_KEY%", MAX_WIDTH_PX, CANVAS_HEIGHT
FOR FRAME, 0, ANIMATION_FRAMES
    SPRITEANIMEADDFRAME @"MAP_ANIME_%MAP_CACHE_KEY%", GID_ANIME, 0, 0, MAX_WIDTH_PX, CANVAS_HEIGHT, 0, 0, ANIMATERECOLOREDMAPS
NEXT

; 设置动画刷新间隔（在进入输入循环前）
SETANIMETIMER 40   ; 40ms 刷新，约 25fps

; 进入输入等待
INPUTS              ; SETANIMETIMER 在 INPUTS 期间自动刷新动画帧
```

**SETANIMETIMER 的关键约束**：

| 约束 | 说明 |
|------|------|
| 仅在 `INPUT`/`INPUTS` 等待期间生效 | `TINPUT`/`TINPUTS` 期间**不刷新** |
| 不受 `REDRAW 0` 影响 | 即使禁止自动重绘，动画仍会刷新 |
| 刷新仅调用 `window.Refresh()` | 不经过 `RefreshStrings`，不改变滚动位置 |
| 实际间隔略大于设定值 | 受系统负载影响，建议设定值小于帧 delay |

### 5.6 状态更新时的渲染策略

当察知模式、季节、地点状态等发生变化时，需要更新按钮层。策略：

| 变化类型 | 底图层 | 按钮层 | 处理方式 |
|----------|--------|--------|----------|
| 动画帧推进 | 自动（SPRITEANIME） | 无需更新 | SETANIMETIMER 自动处理 |
| 察知模式切换 | 无需更新 | 需要更新 | 仅重绘按钮层 |
| 地点状态变化 | 无需更新 | 需要更新 | 仅重绘按钮层 |
| 地图切换/翻页 | 需要更新 | 需要更新 | 重新渲染整个地图 |
| 天数变化 | 需要更新 | 需要更新 | 清空缓存，重新生成底图 |

**按钮层重绘方式**：使用 `CLEARLINE` 清除地图行，然后重新 `HTML_PRINT` 按钮层。由于此时是用户主动触发（非动画 Tick），短暂的滚动回底是可接受的。

---

## 6. 实施方案

### 6.1 阶段一：SPRITEANIME 底图 + SETANIMETIMER 驱动（已完成大部分）

当前 `BUILD_MAP_BG_ANIMATION` 和 `DRAW_COLOREDMAP_GD` 已实现：
- ✅ 20 帧底图预渲染
- ✅ SPRITEANIMECREATE + SPRITEANIMEADDFRAME 组装动画精灵
- ✅ 按钮覆盖层用 `<div rect>` 精确定位
- ✅ 高亮图/悬停图精灵缓存

**待完善**：
- ❌ 将 `<img src='MAP_ANIME_...'>` 和按钮层包裹在 `<div display='absolute'>` 中
- ❌ 计算正确的 absolute 定位坐标
- ❌ 在 absolute div 下方预留空间（避免 UI 文本被地图遮挡）

### 6.2 阶段二：Absolute DIV 固定地图框架

**目标**：地图始终固定在窗口顶部，UI 文本在下方正常滚动。

**修改 `DRAW_COLOREDMAP_GD`**：

```erb
@DRAW_COLOREDMAP_GD(MAP_MODE)
    ; ... 现有的底图生成和按钮层生成逻辑 ...

    ; 计算窗口尺寸
    WINDOW_H = GETCONFIG("ウィンドウ高さ")
    MAP_Y_POS = WINDOW_H - CANVAS_HEIGHT   ; absolute 坐标：y 正方向向上

    ; 组装 absolute div
    FINAL_HTML += @"<div display='absolute' rect='0px,{MAP_Y_POS}px,{MAX_WIDTH_PX}px,{CANVAS_HEIGHT}px' depth='-1'>"
    FINAL_HTML += @"<img src='MAP_ANIME_%MAP_CACHE_KEY%' width='{MAX_WIDTH_PX}px' height='{CANVAS_HEIGHT}px'>"
    FINAL_HTML += HTML_BUTTONS
    FINAL_HTML += @"</div>"

    ; 预留空间：打印与地图等高的空行，防止 UI 文本被遮挡
    MAP_LINES = CANVAS_HEIGHT / CELL_HEIGHT
    FOR LOCAL, 0, MAP_LINES
        PRINTL
    NEXT

    HTML_PRINT FINAL_HTML, 1   ; 第二参数=1 不自动换行
```

**关键点**：
1. `depth='-1'` 使地图 div 在手前（覆盖其他内容）
2. 预留空行确保 UI 文本不被地图遮挡
3. `HTML_PRINT FINAL_HTML, 1` 不自动换行，避免产生多余的空行

### 6.3 阶段三：简化输入循环

**目标**：移除 `AWAIT_UI_INPUT` hack，回归原生 `INPUTS`。

**修改 `QOL_COM400_GD`**：

```erb
@QOL_COM400_GD
    ; ... 初始化 ...

    ; 启用动画定时器
    SIF ANIMATERECOLOREDMAPS > 0 && !FLAG:70
        SETANIMETIMER 40

    TOOLTIP_SETDELAY 100
    LINESTART = LINECOUNT

    $MAP_LOOP
    CLEARLINE LINECOUNT - LINESTART
    CALL COM400_DRAW_UI(0, UI_MESSAGE)
    UI_MESSAGE =

    $INPUT_LOOP
    CLEARLINE LINECOUNT - LINECOUNT  ; 不清除任何行

    INPUTS    ; 原生输入，SETANIMETIMER 自动驱动动画

    LOCALS:0 = %RESULTS%

    ; 退出指令拦截
    IF LOCALS:0 == "" || LOCALS:0 == "MOUSE_R" || LOCALS:0 == "ESC"
        TOOLTIP_SETDELAY 500
        SETANIMETIMER 0    ; 关闭动画定时器
        RETURN -1
    ENDIF

    ; 热键处理 → 状态变化时 GOTO MAP_LOOP 重绘
    ; 地点跳转 → 处理移动
    ; ...
```

**关键变化**：
1. **移除 `AWAIT_UI_INPUT`**：不再需要非阻塞输入 hack
2. **移除 `TINPUTS` 超时循环**：动画由 `SPRITEANIME` + `SETANIMETIMER` 自动驱动
3. **仅在状态变化时重绘**：察知模式切换、翻页等才 `GOTO MAP_LOOP`
4. **退出时关闭定时器**：`SETANIMETIMER 0`

### 6.4 阶段四：悬停交互优化

**问题**：`SPRITEANIME` 的动画帧切换是全局的，无法针对单个地点实现"悬停暂停"。

**方案**：利用 `<img src='...' srcb='...'>` 的内置悬停切换机制。

当前实现已使用 `srcb` 属性：

```erb
; 默认色地点：底图透明，悬停显示金字
<img src='MAP_BLANK' srcb='MAP_HOVER_{REAL_LOC}' width='{TILE_W}px' height='{CELL_HEIGHT}px'>

; 高亮色地点：底图高亮字，悬停显示金字
<img src='MAP_COLOR_{CURRENT_COLOR}_%TEMP_TILE%' srcb='MAP_HOVER_{REAL_LOC}' width='{TILE_W}px' height='{CELL_HEIGHT}px'>
```

**Emuera 原生行为**：当鼠标悬停在 `<button>` 上时，自动将 `<img>` 的 `src` 切换为 `srcb`。这是 Emuera 内置功能，无需额外代码。

**Tooltip**：`<button title='...'>` 的 Tooltip 也是 Emuera 原生功能，在 `INPUTS` 等待期间正常工作。

### 6.5 阶段五：动态状态更新（高级）

**目标**：察知模式切换时，仅更新按钮层，不重绘底图。

**方案**：将底图和按钮层分离为两次独立的 `HTML_PRINT`。

```erb
; 第一次 HTML_PRINT：底图（仅在地图切换/天数变化时重绘）
HTML_PRINT @"<div display='absolute' ...><img src='MAP_ANIME_...'></div>", 1

; 第二次 HTML_PRINT：按钮层（察知模式等状态变化时重绘）
HTML_PRINT @"<div display='absolute' ...>%HTML_BUTTONS%</div>", 1
```

**挑战**：两次 `HTML_PRINT` 产生两行，需要确保它们的 absolute 定位不冲突。可以通过相同的 `rect` 坐标实现重叠。

---

## 7. 风险与注意事项

### 7.1 `display='absolute'` 的已知限制

| 限制 | 影响 | 对策 |
|------|------|------|
| `<div>` 不支持嵌套 | 按钮层和底图不能分别放在嵌套的 div 中 | 将底图和按钮放在同一个 div 内 |
| absolute 定位基于窗口左下角 | 窗口大小变化时地图位置可能偏移 | 每次渲染时重新计算坐标 |
| 行外内容可能影响按钮点击 | 滚动后按钮的点击区域可能不精确 | 测试验证，必要时调整 depth |
| `SETANIMETIMER` 在 `TINPUT` 期间不工作 | 不能使用 `TINPUT` 做超时处理 | 使用 `INPUTS` + `SETANIMETIMER` |

### 7.2 SPRITEANIME 内存管理

| 资源 | 生命周期 | 清理时机 |
|------|----------|----------|
| 动画帧 Graphics (GID 9000+) | 每日/切换地图 | `BUILD_MAP_BG_ANIMATION` 开头 `SPRITEDISPOSE` |
| 高亮图精灵 (MAP_COLOR_*) | 游戏全程 | 不需要清理（颜色组合有限） |
| 悬停图精灵 (MAP_HOVER_*) | 游戏全程 | 不需要清理（地点数有限） |
| 动画精灵 (MAP_ANIME_*) | 每日/切换地图 | `SPRITEDISPOSE` 在重建前调用 |

**注意**：`GCREATE` 的 GID 范围有限，需避免与其他系统冲突。当前分配：
- 底图帧：`9000 + MAP_HASH_ID * 20 + FRAME`
- 高亮图：`85000 + CURRENT_COLOR % 5000`（可能冲突，需改进）
- 悬停图：`GID_HOVER_BASE (80000) + REAL_LOC`

### 7.3 SETANIMETIMER 与 INPUT 系列的兼容性

| 输入命令 | SETANIMETIMER 是否生效 | 适用性 |
|----------|----------------------|--------|
| `INPUT` | ✅ 生效 | 可用，但不支持字符串输入 |
| `INPUTS` | ✅ 生效 | **推荐**：支持字符串和按钮 |
| `ONEINPUT` | ✅ 生效 | 可用，单次输入 |
| `ONEINPUTS` | ✅ 生效 | 可用，单次字符串输入 |
| `TINPUT` | ❌ 不生效 | 不可用 |
| `TINPUTS` | ❌ 不生效 | 不可用 |
| `INPUTMOUSEKEY` | ❌ 不生效 | 不可用 |

**结论**：必须使用 `INPUTS`（或 `ONEINPUTS`）作为输入命令，`SETANIMETIMER` 才能驱动动画。

### 7.4 滚动行为验证清单

在实施后需验证以下场景：

- [ ] 动画播放期间向上滚动 → 地图保持在窗口顶部
- [ ] 动画播放期间向下滚动 → UI 文本正常滚动
- [ ] 点击 absolute div 中的按钮 → 正确触发移动
- [ ] 悬停按钮 → Tooltip 正常显示，img 切换到 srcb
- [ ] 察知模式切换 → 按钮层正确更新
- [ ] 地图翻页 → 底图和按钮层正确更新
- [ ] 窗口大小变化 → 地图位置正确调整
- [ ] 退出地图 → SETANIMETIMER 正确关闭
- [ ] 时停状态 → 动画暂停，颜色反转正确

---

## 附录 A：Emuera 渲染管线源码关键路径

### A.1 正常 PRINT 路径（导致滚动回底）

```
HTML_PRINT / PRINT
  → PrintLine() / PrintSLine()
    → displayLineList.Add(newLine)
    → RefreshStrings(false)
      → verticalScrollBarUpdate()
        → ScrollBar.Value += move     ← 自动滚到底部
      → window.Refresh()
        → OnPaint(graph)
```

### A.2 SETANIMETIMER 路径（不导致滚动回底）

```
redrawTimer.Tick
  → tickRedrawTimer()
    → window.Refresh()               ← 仅重绘，不更新滚动
      → OnPaint(graph)
        → 绘制当前可见行（含 SPRITEANIME 当前帧）
```

### A.3 REDRAW 2 强制刷新路径

```
REDRAW 2
  → setRedraw(2)
    → RefreshStrings(true)           ← force_Paint=true
      → verticalScrollBarUpdate()    ← 可能改变滚动位置
      → window.Refresh()
```

## 附录 B：AWAIT_UI_INPUT 与原生 INPUT 的功能对比

| 功能 | 原生 INPUTS | AWAIT_UI_INPUT |
|------|-------------|----------------|
| 按钮点击 | ✅ | ✅ (MOUSEB) |
| 文本输入 | ✅ | ⚠️ (GETTEXTBOX) |
| Tooltip | ✅ | ✅ |
| 宏展开 | ✅ | ❌ |
| ESC 跳过 | ✅ | ⚠️ (需自行处理) |
| 右键跳过 | ✅ | ⚠️ (需自行处理) |
| SETANIMETIMER | ✅ | ❌ (AWAIT 期间不触发) |
| 滚动不回底 | ❌ | ❌ |
| CPU 占用 | 低 | 中 (16ms 轮询) |

## 附录 C：推荐最终架构伪代码

```erb
@QOL_COM400_GD
    ; 初始化
    SIF ANIMATERECOLOREDMAPS > 0 && !FLAG:70
        SETANIMETIMER 40
    TOOLTIP_SETDELAY 100

    LINESTART = LINECOUNT

    $MAP_LOOP
    ; 仅在状态变化时重绘整个地图
    CLEARLINE LINECOUNT - LINESTART
    CALL COM400_DRAW_UI_GD(0, UI_MESSAGE)
    UI_MESSAGE =

    $INPUT_LOOP
    ; 原生输入，动画由 SETANIMETIMER 自动驱动
    INPUTS

    ; 处理输入...
    SELECTCASE RESULTS
        CASE "" ; 空输入/右键
            SETANIMETIMER 0
            RETURN -1
        CASE "Y", "y" ; 察知切换
            ; ... 切换察知模式 ...
            GOTO MAP_LOOP    ; 需要重绘按钮层
        CASE "C", "c" ; 显示切换
            ; ... 切换显示模式 ...
            GOTO MAP_LOOP
        CASEELSE
            ; ... 地点跳转处理 ...
    ENDSELECT

@COM400_DRAW_UI_GD(ANIMATION_SEED, UI_MESSAGE)
    ; 渲染地图（absolute div，一次性输出）
    CALL DRAW_COLOREDMAP_GD("")

    ; 渲染 UI 文本（正常 PRINT，可滚动）
    PRINTFORML 当前位置→...
    ; ... 移动选项、察知说明等 ...

@DRAW_COLOREDMAP_GD(MAP_MODE)
    ; 确保底图已生成
    CALL BUILD_MAP_BG_ANIMATION(MAP_MODE)

    ; 生成按钮覆盖层 HTML
    ; ... (现有逻辑) ...

    ; 计算窗口定位
    WINDOW_H = GETCONFIG("ウィンドウ高さ")
    MAP_Y = WINDOW_H - CANVAS_HEIGHT

    ; 组装 absolute div
    FINAL_HTML += @"<div display='absolute' rect='0px,{MAP_Y}px,{MAX_WIDTH_PX}px,{CANVAS_HEIGHT}px' depth='-1'>"
    FINAL_HTML += @"<img src='MAP_ANIME_%MAP_CACHE_KEY%' width='{MAX_WIDTH_PX}px' height='{CANVAS_HEIGHT}px'>"
    FINAL_HTML += HTML_BUTTONS
    FINAL_HTML += @"</div>"

    ; 预留空间
    MAP_LINES = CANVAS_HEIGHT / CELL_HEIGHT
    FOR LOCAL, 0, MAP_LINES
        PRINTL
    NEXT

    HTML_PRINT FINAL_HTML, 1
```
