# GMF 幻想乡大地图重构 Changelog

> 记录 2026-05 期间 eratw-chs 仓库中 GMF（幻想乡大地图）系统的全部重构变更。
> 本文档作为开发者备忘，参照 `gmf-knowledge-base.md` 知识库编写。

---

## 六、R10 第十轮修复详细记录

### 6.1 触发原因

审查 commit b3234f36（外部回报的 GMF 修复）时发现 GETOUT 函数在 GMF 下存在 Bug：`MINROOM()`/`MAXROOM()` 无参调用默认遍历家地图范围，当角色在非家据点被赶出时 FOR 循环找不到可达房间。

### 6.2 commit b3234f36 方案审查

| # | 缺陷 | 严重度 | 说明 |
|---|------|--------|------|
| 1 | `GMF_LARGE_MAP_ID()` 是玩家视角 | 高 | 被赶出的可能是任意角色，其位置与玩家位置可能不同地图 |
| 2 | `GMF_CAN_MOVE` 替换 `CAN_MOVE` 是倒退 | 高 | `CAN_MOVE` 已实现扁平路由，`GMF_CAN_MOVE` 是已弃用栈路由 |
| 3 | `#DIM DYNAMIC MAP_ID` 不必要 | 低 | 函数级 `#DIM` 即可 |

### 6.3 正确修复

**GETOUT**（[COMMON.ERB:2380](file:///d:/eratw-chs/ERB/COMMON.ERB#L2380)）：

```erab
; 修复前
FOR LOCAL, MINROOM(), MAXROOM()

; 修复后
MAP_ID = GET_CURRENT_MAP(ARG)
FOR LOCAL, MINROOM(MAP_ID), MAXROOM(MAP_ID)
```

**KICKOUT**（[PLACE_拠点共通.ERB:648](file:///d:/eratw-chs/ERB/MOVEMENTS/物件関連/PLACE_拠点共通.ERB#L648)）：

```erab
; 修复前：IF GMF_GETBIT/ELSE/ENDIF 分支 + 裸 ARG/100 + GMF_MAXROOM
IF GMF_GETBIT("幻想乡大地图")
    MAP_ID = ARG / 100
    FOR LOCAL, MAP_ID * 100 + 1, GMF_MAXROOM:MAP_ID
        ...
    NEXT
ELSE
    FOR LOCAL, MINROOM(), MAXROOM
        ...
    NEXT
ENDIF

; 修复后：函数化接口，无需分支
MAP_ID = GET_MAPID(ARG)
FOR LOCAL, MINROOM(MAP_ID), MAXROOM(MAP_ID)
    ...
NEXT
```

### 6.4 无参调用全量审计

R10 对全代码库 `MINROOM()`/`MAXROOM()`/`SUKIMA()`/`OMANEKIBEYA()` 无参调用进行全量扫描，按风险等级分类：

**风险判定标准**：

| 等级 | 标准 | 处理 |
|------|------|------|
| 🔴 高 | 操作任意角色的位置/状态，角色可能不在家地图 | 必须参数化 |
| 🟡 中 | 操作 MASTER 的位置/状态，MASTER 可能外出 | 验证调用上下文 |
| 🟢 低 | 操作家地图全局资源（污垢、ROOMDATA），语义就是"家地图" | 无参调用正确 |

**审计结果**：

| 等级 | 函数 | 文件 | 状态 |
|------|------|------|------|
| 🔴 | `GETOUT(ARG)` | COMMON.ERB | ✅ R10 已修复 |
| 🟡 | `KICKOUT(ARG)` | PLACE_拠点共通.ERB | ✅ R10 已简化 |
| 🟡 | COMF400 移動 | COMF400.ERB | ✅ 安全（玩家在家地图时调用） |
| 🟡 | 开锁系统 | 开锁系统.ERB | ✅ 安全（仅在 COMF400 中调用） |
| 🟡 | ADD_MOVEMENT_COSTS | Add_Misc.ERB | ⚠️ 有限影响（外出时结果全 0） |
| 🟢 | SUM_ALL_YOGORE | COMMON.ERB | ✅ 安全（家地图污垢合计） |
| 🟢 | 大扫除/清扫/污垢 | COMF410/DAIRY_EV0/AFTERTRA/AUTO_SWEEP | ✅ 安全（家地图资源） |
| 🟢 | MOB_PLACE_N | MOB.ERB | ✅ 安全（原版限制，非 GMF 引入） |
| 🟢 | ROOMSETTING_N | ROOMSETTING_0~11 | ✅ 安全（GMF_ALL_MAP_ROOMSETTING 中调用） |
| 🟢 | DRAW_MAP | DRAW_MAP.ERB | ✅ 安全（非外出模式时渲染家地图） |
| 🟢 | MAP_NODE_TO_XML | MAP_NODE_TO_XML.ERB | ✅ 安全（调试工具） |
| 🟢 | MAP_MANAGE | MAP_MANAGE.ERB | ✅ 安全（家地图设施检查） |

### 6.5 审查方案缺陷反思与整改

**R8 的审查盲区**：R8 重构了据点范围函数的参数化，但只处理了 NAME_FROM_PLACE 内部的调用，没有做全代码库无参调用扫描。GETOUT 和 KICKOUT 被遗漏。

**整改措施**：

1. **无参调用审计规范**：每次参数化重构后，必须对全代码库做 `MINROOM()`/`MAXROOM()`/`SUKIMA()`/`OMANEKIBEYA()` 无参调用扫描
2. **风险分类标准**：按"操作对象"（任意角色 vs MASTER vs 家地图资源）分类，优先修复高风险
3. **函数化接口优先**：新适配应使用 `GET_CURRENT_MAP(ARG)`/`GET_MAPID(ARG)` + `MINROOM(MAP_ID)`/`MAXROOM(MAP_ID)` 函数化接口，而非 `IF GMF_GETBIT/ELSE/ENDIF` 分支
4. **KICKOUT/GETOUT 一致性**：同类函数（逐出逻辑）必须同步适配

---

## 一、重构总览

### 核心目标

GMF（Gensokyo Map Fix）补丁让所有角色在 12 个据点上自由行动，但原版不存在跨地图移动机制。GMF 原选择"全局变量替换+栈路由"策略复用原版函数，导致 10~20x 性能退化。本次重构将栈路由全面替换为**扁平路由**和**函数化参数**，恢复起床管线性能至原版 ~1.1x。

### 重构阶段

| 阶段 | 名称 | 核心变更 | 性能影响 |
|------|------|---------|---------|
| P0 | SKIPSTART 清理 | 删除 23 个 SKIPSTART 残留块 | — |
| P1 | MAP_CAN_MOVE 扁平化 | `GET_MAPID(ARG)` 分发 + `GMF_ROOMDATA`/`GMF_PRIVATEROOM` | 消除栈路由 |
| P2 | 角色移動処理 扁平化 | `MAP_ID = GET_MAPID(...)` + 全部二维数组替换 | 消除栈路由 |
| P3 | 起床就寝処理 扁平化 | `MAP_ID = GET_MAPID(...)` + `GMF_MAXROOM`/`GMF_ENTRANCE` | 消除栈路由 |
| P4 | BASE自然変動 扁平化 | `MAP_ID = GET_MAPID(...)` + `GMF_ROOMDATA` | 消除栈路由 |
| P5 | 流程控制类 | 死代码删除/轻量级上下文切换/直接替换 | 消除轻量上下文切换 |
| P6 | 渲染类 | 轻量级上下文切换/移除中间层 | 消除轻量上下文切换 |
| P7 | 清理 | 活跃调用全部清除，路由器定义保留备用 | — |
| R2 | 第二轮修复 | LOCAL 魔法数字清理、变量语义化 | 代码质量 |
| R3 | 第三轮修复 | SETTING_MAP 兜底、GMF_AT_LARGE_MAP 精确匹配 | Bug 修复 |
| R4 | 第四轮修复 | MAIN_MAP 路由分发全量审计 | Bug 修复 |
| R5 | 第五轮修复 | GET_ENTRANCE 函数化重构 | 架构统一 |
| R6 | 第六轮修复 | GET_HOME_MAP/GET_CURRENT_MAP 函数化 | 架构统一 |
| R7 | 第七轮修复 | 来访位置系统 MAIN_MAP 硬编码 + GET_CURRENT_MAP 参数化 | Bug 修复 |
| R8 | 第八轮修复 | NAME_FROM_PLACE 轻量上下文切换 + MAP_PLACENAME_N 语义替换 | Bug 修复 |
| R9 | 第九轮修复 | GMF 函数作用域泄漏（GMF_IS_ODEKAKE 等五函数添加 GMF_GETBIT 守卫） | Bug 修复 |
| R10 | 第十轮修复 | GETOUT/KICKOUT GMF 适配 + 无参调用全量审计 | Bug 修复 |

---

## 二、按文件记录变更

### 2.1 GMF 核心文件

#### `ERB/DLC/GENSOKYO_MAP_FIX/GMF_MOVEMENTS.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `GMF_LARGE_MAP_ID()` | P0+ | 返回"当前上下文中的大地图"MAPID，三路逻辑（非GMF→MAIN_MAP, 据点模式→GMF_HOME_MAP, 外出模式→玩家位置） |
| `GMF_IS_ODEKAKE` | P0+ | 判断给定 MAPID 是否为"外出"状态。栈路由消除后不再受 GMF_METHOD_STACK 影响 |
| `GMF_KITAKU` | P0+ | 归宅处理：非外出模式→初期位置，外出模式→自宅/隙间 |
| `GMF_JOINT_MOVE` | P0+ | 同行角色 GMF_現在拠点位置 同步 |
| `GMF_FORCE_MOVE` | P0+ | 衰弱角色强制移动 |
| `GMF_LOCATION_FIX` | R3 | 新增大地图位置修正防止位置错误 |
| `GMF_SLEEP_AND_AWAKE` | R2 | 角色睡觉时排除不应该判定回到初期的情况 |

#### `ERB/DLC/GENSOKYO_MAP_FIX/幻想乡地图重修.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| 五种路由器定义 | P7 | `GMF_MAP_METHOD/F/FS/M/FM` 定义保留为死代码，无活跃调用 |
| `GMF_METHOD_UPDATE/RESTORE` | P7 | 全局变量替换/恢复逻辑保留，仅 `GMF_ALL_MAP_ROOMSETTING` 调用 |
| `GMF_ALL_MAP_ROOMSETTING` | — | 唯一活跃的全局变量替换点（初始化专用，不可消除） |
| `GMF_GETBIT/SETBIT/CLEARBIT/INVERTBIT` | — | 位操作函数，活跃使用中 |
| `GMF_CAN_MOVE` | P1 | 函数定义保留为死代码，调用端已扁平化 |
| `GMF_ODEKAKEMAP_SETTING` | P1 | 函数定义保留为死代码，调用端已扁平化 |
| `GMF_SETTING_MENU` | — | GMF 设置菜单，活跃使用中 |

#### `ERB/DLC/GENSOKYO_MAP_FIX/GENSOKYO_MAP_FIX.ERH`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 全局变量定义 | — | GMF_HOME_MAP, GMF_MAP_MODE, GMF_MAXROOM, GMF_ENTRANCE 等 |

### 2.2 移动系统文件

#### `ERB/MOVEMENTS/物件関連/COMMON2.ERB`

| 变更 | 阶段 | 行号 | 说明 |
|------|------|------|------|
| `GET_HOME_MAP()` | R6 | 新增 | 非GMF→MAIN_MAP，GMF→GMF_HOME_MAP。语义：玩家的家地图ID |
| `GET_CURRENT_MAP(CHARA_ID=-1)` | R7 | L110-128 | 参数化：省略时基于MASTER位置，指定时返回该角色所在地图MAPID |
| `GET_ENTRANCE(MAPID=-1)` | R5 | L112-123 | 函数化参数：GMF开启时始终返回GMF_ENTRANCE:MAPID |
| `MAXROOM(MAP_ID=-1)` | R5 | L130+ | 函数化参数：GMF→GMF_MAXROOM:MAP_ID |
| `IN_HOME(ARG)` | R6 | — | 内部 GMF_LARGE_MAP_ID() 改为 GET_CURRENT_MAP() |
| `CHK_DATENOW(ARG)` | — | L8-20 | 扁平路由后 MAIN_MAP 不再被替换，行为正确 |

#### `ERB/MOVEMENTS/MOVEMENT_SUB.ERB`

| 变更 | 阶段 | 行号 | 说明 |
|------|------|------|------|
| `主人公物件へ向かう` 来访位置 | R7 | L375-391 | `450 + MAIN_MAP/地图判断` → `450 + GET_CURRENT_MAP(ARG)`（3处） |
| `主人公物件へ向かう` 守卫条件 | R7 | — | `地图判断` 变量保留用于 GMF_MAP_MODE 判断和提前 RETURN |
| `主人公物件へ向かう` GMF分支 | P0+ | — | GMF 拜访/归宅处理 |

#### `ERB/MOVEMENTS/JOB_仕事開始終了処理.ERB`

| 变更 | 阶段 | 行号 | 说明 |
|------|------|------|------|
| `CHARA_JOBEND_GO_HOME` 来访位置 | R7 | L296-297 | `450 + MAIN_MAP` → `450 + GET_CURRENT_MAP(ARG)`，删除 `#DIM 地图判断` |

#### `ERB/MOVEMENTS/MOVEMENT_キャラ移動処理.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `角色移動処理` 扁平化 | P2 | `MAP_ID = GET_MAPID(...)` + GMF_ROOMDATA/GMF_PRIVATEROOM/GMF_MAXROOM |
| `角色移動処理２` MAP_ID 初始化 | R2 | `MAP_ID = GET_MAPID(N_ID)`（修复未初始化 Bug） |
| `角色移動率` MAP_ID 初始化 | R2 | `MAP_ID = GET_MAPID(CFLAG:ARG:現在位置)`（修复未初始化 Bug） |
| `G_POINT = GET_ENTRANCE(MAP_ID)` | R5 | 替代三元运算符 |

#### `ERB/MOVEMENTS/MOVEMENT2.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| KITAKU 归宅处理 | P0+ | 原版 KITAKU 先执行位置设置，GMF_KITAKU 再覆盖 |

#### `ERB/MOVEMENTS/BASE自然変動.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `BASE自然変動` 扁平化 | P4 | `MAP_ID = GET_MAPID(...)` + GMF_ROOMDATA |

#### `ERB/MOVEMENTS/SLEEP.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `CHARA_SLEEP` 入口 | R5 | `CURRENT_ENTRANCE = GET_ENTRANCE()` 替代直接引用 ENTRANCE |
| `SLEEP_VISITOR` | R5 | 简化：删除 GMF 条件分支，改为 `GET_ENTRANCE()` 函数化调用 |
| `CFLAG:ARG:デート中 = MAIN_MAP` | R6 | → `= GET_HOME_MAP()`（清除约会状态） |

#### `ERB/MOVEMENTS/物件関連/PLACE_拠点共通.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `MINROOM(MAP_ID=-1)` | R5 | 函数化参数：`MAP_ID*100+1`，默认 MAIN_MAP |
| `SUKIMA(MAP_ID=-1)` | R5 | 函数化参数：`99+MAP_ID*100`，默认 MAIN_MAP |
| `OMANEKIBEYA()` | R6 | 非GMF 分支 MAIN_MAP 改为 `GET_HOME_MAP()` |
| `KICKOUT(ARG)` 函数化简化 | R10 | `IF GMF_GETBIT/ELSE/ENDIF` + 裸 `ARG/100` + `GMF_MAXROOM` → `GET_MAPID(ARG)` + `MINROOM(MAP_ID)`/`MAXROOM(MAP_ID)` |
| `ROAD_TO(MAPID)` | — | 无变化 |

#### `ERB/MOVEMENTS/物件関連/PLACE_拠点別分岐.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `MAP_CAN_MOVE` 扁平化 | P1 | `SELECTCASE GET_MAPID(ARG)` 分发 + GMF_ROOMDATA/GMF_PRIVATEROOM |
| `CAN_MOVE` 扁平化 | P1 | GMF_CAN_MOVE 调用端已替换为内联逻辑 |
| `ODEKAKEMAP_SETTING` 扁平化 | P1 | GMF_ODEKAKEMAP_SETTING 调用端已替换为内联逻辑 |
| `OUTROOF` Bug 修复 | R2 | GMF 分支 `場所_赏月` → `場所_屋内`，与原版一致 |
| `NAME_FROM_PLACE` | R3 | SETTING_MAP 检测，跳过 GMF 逻辑直接查表 |
| `NAME_FROM_PLACE2` | R3 | chs 独有极简查表函数 `STR_TR(ARG + 8000)` |

#### `ERB/MOVEMENTS/物件関連/MAP_MANAGE.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `SETTING_MAP` 变量 | R3 | 非 SAVEDATA 的 #DIM，搬家时设为 1 让 NAME_FROM_PLACE 跳过 GMF 逻辑 |
| `SETTING_MAP` 兜底重置 | R3 | QOL_SET_MAINHOME 返回后立即 `SETTING_MAP = 0` |
| 搬家流程伪装 | R3 | 三层伪装：GMF_MAP_MODE=0 + SETTING_MAP=1 + MAIN_MAP 临时替换 |

#### `ERB/MOVEMENTS/物件関連/MAP_NODE_TO_XML.ERH`

| 变更 | 阶段 | 说明 |
|------|------|------|
| 地图节点定义 | — | 配合 GMF 多据点支持 |

### 2.3 指令文件

#### `ERB/コマンド関連/COMF/日常系/COMF400 移動.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `COM400` 局部变量替换 | P5 | `LOCAL_MAP` 替代全局 MAIN_MAP |
| `TRYCALLFORM MAP_{MAIN_MAP}` | P1 | → `TRYCALLFORM MAP_{LOCAL_MAP}` |
| `SKIP_MOVE` | P5 | `GET_MAPID(出発地点)` 替代 MAIN_MAP |

#### `ERB/コマンド関連/COMF/外出系/COMF604 散策する.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `COM604` 局部变量替换 | P5 | `LOCAL_MAP` 替代全局 MAIN_MAP |

#### `ERB/コマンド関連/COMF/日常系/COMF405 出掛ける.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `COM405` 局部变量替换 | P5 | 9 个命名 DYNAMIC 变量替代 LOCAL 魔法数字 |

#### `ERB/コマンド関連/COMF/日常系/COMF420 る～ことと話す.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `COM420_DISPLAY` | R4 | `SELECTCASE MAIN_MAP` → MAP_ID 局部变量替换（真Bug：GMF下指令名显示错误） |
| `COM_ABLE420` | R4 | `SELECTCASE MAIN_MAP` → MAP_ID 局部变量替换（真Bug：GMF下指令可用性判断错误） |

#### `ERB/コマンド関連/COMF/日常系/COMF447 露店を開く.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `STALL_SPOT` | R4 | `SELECTCASE MAIN_MAP` → MAP_ID 局部变量替换（真Bug：GMF下摆摊位置判定错误） |
| `STALL_PERMISSION` | R4 | `SELECTCASE MAIN_MAP` → MAP_ID 局部变量替换（防御性修复） |
| `STALL_PERMISSION_TIPS` | R4 | `SELECTCASE MAIN_MAP` → MAP_ID 局部变量替换（防御性修复） |

#### `ERB/コマンド関連/COMF/日常系/COMF449 虫捕り.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `MUSHITORI_SPOT` | R4 | `SELECTCASE MAIN_MAP` → MAP_ID 局部变量替换（防御性修复） |

#### `ERB/コマンド関連/COMF/日常系/COMF446 調合する.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `PHARMACY_SPOT` | R4 | `SELECTCASE MAIN_MAP` → MAP_ID 局部变量替换（真Bug：无守卫，调合位置错误） |

#### `ERB/コマンド関連/COMF/外出系/COMF697 部屋を訪ねる.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()`/`GET_CURRENT_MAP()` 替换 |

#### `ERB/コマンド関連/COMF/外出系/COMF699外に出る.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()`/`GET_CURRENT_MAP()` 替换 |

#### `ERB/コマンド関連/COMF/外出系/COMF603 手を繋ぐ.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换约会状态清除 |

#### `ERB/コマンド関連/COMF/700 自慰系/COMF461我に返る.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换约会状态清除 |

#### `ERB/コマンド関連/COMF/外出系/NASIKUZUSI.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/コマンド関連/集合.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `SYUGOS_COST` 局部变量替换 | P5 | `LOCAL_MAP = GMF_LARGE_MAP_ID()` 替代全局替换 |
| `CALC_SYUGOS_COST` 参数化 | P5 | 增加 `MAP_ID` 参数，`QOL_GET_DISTANCE(,,MAP_ID)` |

#### `ERB/コマンド関連/USERCOM.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_ENTRANCE(MAIN_MAP)` → `GET_ENTRANCE(GET_HOME_MAP())` |

#### `ERB/コマンド関連/外出先から帰宅.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R5+R6 | `GET_ENTRANCE(GET_HOME_MAP())` 替换归宅入口 |

### 2.4 事件文件

#### `ERB/イベント関連/BEFORETRAIN.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| 起床入口 | P3 | `GET_ENTRANCE()` 替代 ENTRANCE 全局变量 |
| `CHANGE_TIMEZONE` | P5 | `GMF_LARGE_MAP_ID()` 替换 MAIN_MAP |

#### `ERB/イベント関連/DATE_CMN.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `DATENAME_PLACE` | R3 | `GMF_AT_LARGE_MAP` truthy→`==2` 精确匹配 + CHK_DATENOW 检查 |
| `DATENAME_SPOT` | R3 | 同类修复，值 2 时返回"途中" |

#### `ERB/イベント関連/EVENTCOMEND.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R5 | `GET_ENTRANCE(GET_HOME_MAP())` 替换気絶归宅入口 |

#### `ERB/イベント関連/デート終了タイムアップ処理.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换约会状态清除 |

#### `ERB/イベント関連/来訪フラグ.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/イベント関連/情事発覚.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换约会状态 |

#### `ERB/イベント関連/お出かけイベント/GO_OUT_EV04_予定外の来訪.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R5 | `GET_ENTRANCE(GET_HOME_MAP())` 替换来访入口 |

#### `ERB/イベント関連/AFTERTRA.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换约会状态清除 |

#### `ERB/イベント関連/APPEND_SYS.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

### 2.5 渲染文件

#### `ERB/MOVEMENTS/DRAW_MAP.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `DRAW_MAP` 局部变量替换 | P6 | `LOCAL_MAP` 替代全局 MAIN_MAP |
| `GETMAP` | P6 | 局部变量替换 + GMF_ROOMDATA 内联 |
| `SET_MAINHOME_DRAW_UI` | P6 | 移除 GMF_MAP_METHODM 中间层 |
| `HIKKOSHI_ROOM_DRAW_UI` | P6 | 移除 GMF_MAP_METHODM 中间层 |

#### `ERB/COLOREDMAPS/DRAW_COLOREDMAP.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `DRAW_COLOREDMAP` 局部变量替换 | P6 | `LOCAL_MAP` 替代全局 MAIN_MAP |

### 2.6 状态显示文件

#### `ERB/ステータス表示関連/INFO.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| `INFO_GPS` | R3 | `GMF_AT_LARGE_MAP(MASTER)` → `== 1` 精确匹配 |
| 睡意提示 | — | `约会中 != MAIN_MAP` → 安全（扁平路由后 MAIN_MAP 正确） |

### 2.7 QOL / 魔改文件

#### `ERB/魔改内容/qol/qol_MAP.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_CURRENT_MAP()`/`GET_HOME_MAP()` 替换 |

#### `ERB/DLC/实用设置补丁/实用设置.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| 背景展示 | R3 | `GMF_AT_LARGE_MAP == 2` 时用 GET_MAPID 直接决定默认地点名 |

#### `ERB/SET_CMN.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| 约会开始/结束 | R6 | `CFLAG:MASTER:约会中 = P_ID` / `= GET_HOME_MAP()` 替换 `= MAIN_MAP` |
| `GET_MAPNAME(MAIN_MAP)` | R6 | → `GET_MAPNAME(GET_HOME_MAP())` |

#### `ERB/SHOP関連/SHOP.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

### 2.8 外部添加文件

#### `ERB/fromEN/Addition/Banquets/Add_Banquet.ERB`

| 变更 | 阶段 | 行号 | 说明 |
|------|------|------|------|
| 宴会结束来访位置 | R7 | L680-681 | `450 + MAIN_MAP` → `450 + GET_CURRENT_MAP(ARG)` |
| 宴会配置归宅 | R5 | — | `GET_ENTRANCE(GET_HOME_MAP())` 替换 |

#### `ERB/fromEN/Addition/Group Dates/MOREDATES_HELPERS.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| 多人约会状态 | R6 | `GET_HOME_MAP()` 替换约会状态清除 |

#### `ERB/fromEN/Addition/Group Dates/MOREDATES_CONFIG.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/fromEN/QOL/Com_Stuff.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R5+R6 | `GET_ENTRANCE(GET_HOME_MAP())` + `GET_HOME_MAP()` 替换 |

#### `ERB/fromEN/QOL/Map Travel/QoL_DANGEROUS_TRAVEL.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/fromEN/QOL/QoL_Misc.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/fromEN/DAYEVENT.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

### 2.9 其他修改文件

#### `ERB/COMMON.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| 地名获取 | R6 | `SUKIMA(GET_CURRENT_MAP())` 替代轻量上下文切换 |
| `GETOUT(ARG)` GMF 适配 | R10 | `MAP_ID = GET_CURRENT_MAP(ARG)` + `MINROOM(MAP_ID)`/`MAXROOM(MAP_ID)` 替代无参调用 |

#### `ERB/ANOTHER_TALK.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/日時天候管理.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/DLC/开锁系统.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | — | MINROOM()/MAXROOM() 无参调用（隐式依赖 MAIN_MAP，仅在 COMF400 中调用，此时语义正确） |

#### `ERB/DLC/魔法DLC/使用魔法.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/口上・メッセージ関連/EVENT_MESSAGE_COM_押し倒し.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/口上・メッセージ関連/個人口上/069 Mamizou [マミゾウ]/マミゾウ/M_KOJO_K69_イベント.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R5 | `GET_ENTRANCE(GET_HOME_MAP())` 替换归宅入口 |

#### `ERB/コマンド関連/COMF/日常系/COMF443 固有コマンド.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/コマンド関連/COMF/日常系/COMF444 女の子を物色.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/コマンド関連/COMF/日常系/COMF490 アイテム.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/コマンド関連/COMF/日常系/MOBGIRL_NEWPLAN.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/コマンド関連/COMF/外出系/COMF630 ホフゴブリンに依頼.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/イベント関連/デイリーイベント/DAIRY_EV0 散らかし.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

#### `ERB/魔改内容/DokuToolLib/DOKU_GET_AND_CHECK.ERB`

| 变更 | 阶段 | 说明 |
|------|------|------|
| GMF 适配 | R6 | `GET_HOME_MAP()` 替换 |

---

## 三、架构变更总结

### 3.1 三种拦截模式（重构后）

| 模式 | 适用场景 | 典型函数 | 状态 |
|------|---------|---------|------|
| **扁平路由** | 内部大量引用 ROOMDATA/PRIVATEROOM/MAXROOM 的核心函数 | MAP_CAN_MOVE, 角色移動処理, 起床就寝処理, BASE自然変動 | ✅ 已实施 |
| **局部变量替换** | UI/渲染/流程/集合函数 | COM400/604/405, DRAW_MAP, SYUGOS_COST | ✅ 已实施 |
| **栈路由** | 已弃用，代码保留备用 | GMF_MAP_METHOD* | ❌ 无活跃调用 |

### 3.2 函数化参数体系

| 函数 | 语义 | 默认值 | GMF 行为 |
|------|------|--------|---------|
| `GET_HOME_MAP()` | 家在哪 | — | GMF_HOME_MAP |
| `GET_CURRENT_MAP(CHARA_ID=-1)` | 当前在哪个大地图 | MASTER 位置 | GMF_LARGE_MAP_ID() / GET_MAPID(CFLAG:CHARA_ID:現在位置) |
| `GET_ENTRANCE(MAPID=-1)` | 指定地图的入口 | GET_CURRENT_MAP() | GMF_ENTRANCE:MAPID |
| `MAXROOM(MAP_ID=-1)` | 指定地图的最大部屋 | MAIN_MAP | GMF_MAXROOM:MAP_ID |
| `MINROOM(MAP_ID=-1)` | 指定地图的最小部屋 | MAIN_MAP | MAP_ID*100+1 |
| `SUKIMA(MAP_ID=-1)` | 指定地图的隙间 | MAIN_MAP | 99+MAP_ID*100 |

### 3.3 两种调用约定的心智模型

| 调用 | 语义 | 典型场景 |
|------|------|---------|
| `GET_HOME_MAP()` | "家在哪" | 归宅、清除约会、显示家地图名 |
| `GET_CURRENT_MAP()` | "当前在哪个大地图" | 寻路、渲染、集合、移动 |
| `GET_CURRENT_MAP(ARG)` | "角色ARG在哪个大地图" | 来访位置系统、角色归宅 |
| `GET_ENTRANCE()` | "当前大地图入口" | COMF400 移動、SLEEP、BEFORETRAIN |
| `GET_ENTRANCE(MAIN_MAP)` | "家地图入口" | 归宅、约会終了、来訪、気絶 |

---

## 四、Bug 修复记录

### 4.1 已修复的 Bug

| Bug | 根因 | 修复阶段 | 影响文件 |
|-----|------|---------|---------|
| OUTROOF 場所_赏月 vs 場所_屋内 | GMF 分支独自改变下游逻辑 | R2 | PLACE_拠点共通.ERB |
| 角色移動処理 ワンルーム空条件 | MAP_ID 未初始化 | R2 | MOVEMENT_キャラ移動処理.ERB |
| LOCAL 魔法数字 | LOCAL:N 可读性差 | R2 | 多文件 |
| QOL_COM400 RETURN 前缺少恢复 | 轻量上下文切换脆弱 | R2 | COMF400.ERB |
| SETTING_MAP 兜底重置缺失 | 搬家中止时 SETTING_MAP 残留 | R3 | MAP_MANAGE.ERB |
| GMF_AT_LARGE_MAP truthy 检查 | 值 2 被误判为"在大地图" | R3 | DATE_CMN.ERB, 实用设置.ERB, INFO.ERB |
| STALL_SPOT/COMF420/COMF446 SELECTCASE MAIN_MAP | GMF 下路由分发错误 | R4 | COMF447/420/449/446.ERB |
| GET_ENTRANCE 归宅到外出地图 | 无参调用返回外出地图入口 | R5 | 10 个文件 |
| ENTRANCE 全局变量直接引用 | GMF 下入口不正确 | R5 | 14 个文件 |
| MAIN_MAP 硬编码 | GMF 下应使用动态地图ID | R6 | 100+ 处 |
| 来访位置 450+MAIN_MAP 硬编码 | GMF 模式下来访位置查询错误 | R7 | MOVEMENT_SUB.ERB, JOB_仕事開始終了処理.ERB, Add_Banquet.ERB |
| GET_CURRENT_MAP 隐式假设 | 省略参数假设 MASTER 位置 | R7 | COMMON2.ERB |
| GETOUT MINROOM()/MAXROOM() 无参调用 | GMF 下角色在非家据点被赶出时遍历错误范围 | R10 | COMMON.ERB |
| KICKOUT IF/ELSE 分支冗余 | 可用函数化接口简化 | R10 | PLACE_拠点共通.ERB |

### 4.2 已知未修复

| 问题 | 原因 | 优先级 |
|------|------|--------|
| 口上系统 SELECTCASE MAIN_MAP（3处） | 口上修复由口上作者负责 | P2 |
| LOCKPICK_INFO MINROOM()/MAXROOM() 无参调用 | 仅在 COMF400 中调用，此时 MAIN_MAP 语义正确 | 低 |
| GMF_ALL_MAP_ROOMSETTING EVENTLOAD 去重 | 架构性限制 | 低 |
| CSVCFLAG 缓存 | GETNUM 每次重新计算 | 低 |

---

## 五、性能对比

| 维度 | 栈路由（重构前） | 扁平路由（重构后） |
|------|--------------|------------|
| 起床管线性能 | 原版 10~20x 慢 | 原版 ~1.1x |
| GMF_MAP_METHOD 活跃调用 | 56 处 | 0 处 |
| GMF_METHOD_STACK 使用 | 深度 0-2 | 不使用 |
| 变量语义污染 | 严重（MAIN_MAP 不可靠） | 无 |
| 栈溢出风险 | 有（深度 8） | 无 |
| SKIPSTART 残留 | 23 块 | 已清理 |
| 每角色每 CHARA_MOVEMENT 循环操作 | ~24,850 次 | ~21 次 |

---
