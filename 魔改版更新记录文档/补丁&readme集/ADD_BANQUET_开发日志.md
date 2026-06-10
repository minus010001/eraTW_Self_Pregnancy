=====================================================
  ADD_BANQUET 框架 — 开发日志
=====================================================

## v0.3d (2026-06-10) — Bug #20：补完"烂醉复活"三段式状态机

> 详见 ADR 决策记录：[`shared-trae/knowledge/adr/banquet-drunk-recovery.md`](file:///d:/emuera/shared-trae/knowledge/adr/banquet-drunk-recovery.md)
> 知识库章节：[`banquet-system.md §13`](file:///d:/emuera/shared-trae/knowledge/eratw/banquet-system.md#13-宴会角色烂醉复活三段式状态机)

### 问题描述

用户报告：宴会中喝醉到烂醉状态的角色会脱离宴会，但旧系统支持"通过照料复活+返回宴会"机制。
经源码调研发现：原作者在 [Add_Banquet_Drinking_Common.ERB:104](file:///d:/eratw-chs/ERB/fromEN/Addition/Banquets/Add_Banquet_Drinking_Common.ERB#L104) 和 [Add_Banquet.ERB:762](file:///d:/eratw-chs/ERB/fromEN/Addition/Banquets/Add_Banquet.ERB#L762) **明确预期**"TCVAR:泥酔==1 但保留宴会身份"的中间态，但 `ADD_BANQUET_DRINKING` 在 `仕事量==0` 时**直接** `END_PARTICIPATION`——`TCVAR:泥酔==1` 的状态**永远无法进入**。

### Changed

**修改 1：ADD_BANQUET_DRINKING 补完"烂醉中间态"**
- 文件：[Add_Banquet_Drinking_Common.ERB:17-27](file:///d:/eratw-chs/ERB/fromEN/Addition/Banquets/Add_Banquet_Drinking_Common.ERB#L17-L27)
- 行为：`仕事量==0` 时区分"烂醉"vs"自然退出"
  - 酒气 > 80% → 进入状态 2（烂醉中间态）：`CFLAG:職種=51` + `CFLAG:行動=5` + `TCVAR:泥酔=1` + `TCVAR:烂醉=1`，**保留** `CFLAG:BANQUET` 宴会身份
  - 酒气 < 80% → 原有行为：`ADD_BANQUET_END_PARTICIPATION` 自然退出
- 主办者（`BANQUET_ROLE >= 2`）仍由 `BANQUET_ROLE < ADD_BANQUET_ROLE_HOST` 守卫保护——保留原行为

**修改 2：CHARA_ACTION_DRUNK 复活路径分支**
- 文件：[泥酔処理.ERB:34-46](file:///d:/eratw-chs/ERB/ステータス計算関連/泥酔処理.ERB#L34-L46)
- 行为：酒气 < 40% + 复活检测时分流
  - `CFLAG:職種==51 && CFLAG:BANQUET!=0` → 新系统"复活+保留"：`CFLAG:職種=49` + `TCVAR:泥酔=0` + `TCVAR:烂醉=0` + 重新调用 `ADD_BANQUET_WORKLOAD_PARTICIPATION{ID}` 重设仕事量
  - 其他情况 → 旧 ENKAI 路径：`CALL 烂醉復活共通(ARG)` 复活+退出（**完全保留**）

### Compatibility（兼容性矩阵）

| 场景 | 行为 |
|------|------|
| 非宴会角色喝酒 | 不变（仍走 `烂醉復活共通` 复活+退出） |
| 宴会中角色喝醉 | **新增** 状态 2 烂醉保留 |
| 照料（COMF335）烂醉角色 | **新增** 支持：酒气降低 → `CHARA_ACTION_DRUNK` 自动检测并复活+保留 |
| 婚礼宴会烂醉 | 通用代码，所有宴会受益 |
| 不会喝酒的角色（酒耐性=-2） | 不变（酒气不上升） |
| 主办者烂醉 | 不变（守卫保护） |

### Verification（验证方法）

1. 启动 Emuera.exe
2. 触发宴会（如灵梦即兴酒会 ID 1）
3. 持续劝酒使角色酒气 > 80%
4. **预期**：角色 `CFLAG:職種=51`（JOB_酔いつぶれる），仍在宴会中
5. 照料（COMF335）使酒气 < 40%
6. **预期**：角色 `CFLAG:職種=49`（JOB_宴会参加）—— 复活并保留宴会身份
7. 继续劝酒验证可循环

### Follow-up（后续清理任务）

| # | 任务 | 优先级 | 状态 | 调研结论 |
|---|------|--------|------|---------|
| 1 | 统一 `TCVAR:烂醉` 和 `TCVAR:泥酔` 为单一常量 | 低 | **跳过** | 同一 TCVAR_145 双名，功能无影响，统一需修改 ERH 生成逻辑，成本远超收益 |
| 2 | 评估 `ADD_BANQUET_DRINKING_DESCRIPTIONS` 对状态 3（复活+49）的描述支持 | 中 | **低优先级改进** | 复活后 `職種=49` + 酒气<40% 走 `ELSEIF CFLAG:職種==49` → "还很能喝呢…"，语义不完美但非 Bug；可增加"刚从醉意中恢复"变体描述 |
| 3 | 评估旧 `@烂醉復活共通` 中 `CFLAG:宴会参加=3` 的清理 | 低 | **无需修改** | `CFLAG:宴会参加=3` 仅被写入从未被读取为特定值 3；新系统复活路径不走 `烂醉復活共通`；旧路径设置后值会被 `ADD_BANQUET_END`/`ADD_BANQUET_CHECK` 清零 |

---

## v0.3c (2026-06-08) — Phase 3b+3c 游戏指令与游戏型宴会

### Added
- COM0"玩游戏"指令（Add_CUSTOM_COM0 Play Game.ERB/.ERH）
- 变态服从 COM0 移至 COM19，释放 COM0 槽位
- 游戏列表（Add_CUSTOM_COM0 Game List.ERB）：纸牌(1)/将棋(2)/桌游(4) + 默认计算 + 赌注系统
- 网球单打（Game 9）和双打（Game 10），需 TENNIS 活动标志
- 宴会21"幻想乡网球俱乐部"（TENNIS 活动标志，日夜交替，[[网球服套装]]换装）
- 宴会22"湖畔嬉水"（SWIMMING+WATERMELON 活动标志，夏季周日，ADD_START_SWIMMING 换装）
- ADD_GAME_INFO OBJ 类注册到 qol_OBJ.ERB
- 全部文本翻译为中文

### Changed
- ADD_GAME_INFO 从旧模式改为新模式：
  - `@ADD_GAME_INFO{N}(ARG, O_DATA, V_NAME)` + `CALLF MAKE_STR/MAKE_INT` → `@FADD_GAME_INFO{N}(ARG, O_DATA)` + `#FUNCTIONS` + `RETURNF`
  - `@EXIST_ADD_GAME_INFO{N}` 存在标记 → 删除（新模式由 EXISTFUNCTION 检测 F 前缀）
  - `GET_INT`/`GET_STR` → `GETMETH_INT`/`GETMETH_STR`（Play Game.ERB 中 14 处）
  - 修复 qol_OBJ.ERB 中 `MAKE_OOP_MAP("ADD_GAME_INFO", ...)` 因缺少 F 函数而 MAP 为空的问题
- 宴会21/22 从旧模式改为新模式：
  - `@ADD_BANQUET{N}(ARG, O_DATA, V_NAME)` → `@FADD_BANQUET{N}(ARG, O_DATA)` + `#FUNCTIONS` + `RETURNF`
  - `OBJNAME_TO_ID(ARG, "GET", "衣装セット", "テニスウェアセット")` → `[[网球服套装]]` _Rename 宏
- CHARISMA 翻译：~~"魅力"~~ → "筹码"（赌注显示名 + 结算文本，共 4 处）

### Fixed
- 变态服.ERB 函数名未更新：`@ADD_CUSTOM_COM0` → `@ADD_CUSTOM_COM19`（与文件重命名同步）
- Play Game.ERB 服装函数不存在：`SHOW_上半身下着`/`SHOW_下半身下着` → `SHOW_上半身内衣`/`SHOW_下半身内衣`（chs 函数名差异）
- 宴会21 LOCALSIZE 不足：`#LOCALSIZE 1` → `#LOCALSIZE 2`（PLANNING 函数使用 LOCAL:1）
- 宴会21/22 地点描述函数不存在：`NAME_FROM_PLACE_THE` → `NAME_FROM_PLACE`（中文不需要 the 冠词）
- 宴会21/22 素质名不存在：`TALENT:ARG:吸血鬼` → `TALENT:ARG:妖怪 == 3`（chs 中吸血鬼是妖怪素质的值3，非独立素质）
- Game 9/10 红线系统不存在：`CALL Add_RedThread` → `TRYCALL Add_RedThread`（chs 未移植红线系统，TRYCALL 静默跳过）

---

## v0.3a-post (2026-06-03) — 知识库修正

### Changed
- 宴会服整合：~~"宴会服决定是死代码，需迁移到各 SET_OUTFIT"~~ → 实际已被 `ADD_BANQUET_DRESS_UP`（Add_Banquet.ERB:1053）和 `SET_OUTFIT11`（Add_Banquet_11:312）调用，映射集中管理，无需迁移
- テニスウェアセット：~~"需检查 CSV，可能需要新建"~~ → 衣装セット58=网球服套装，CLOTHES（衣装セット.ERB:1460）+ CLOTHES_METH（METH_衣装セット.ERB:1243）双文件已存在
- Phase 3a 任务10 宴会服整合：~~未开始~~ → ✅ 已整合
- Phase 3c 任务3c-3 网球服：~~确认/新建~~ → ✅ 已确认存在

---

## v0.3a (2026-06-03) — Phase 3a 移植质量检修

### Fixed
- P406玄武の沢 不存在（AI幻觉）→ `P703玄武の沢`（宴会41）
- WEATHER_DEPENDENT 固定=0 丢失恋慕分岐 → 改为动态：恋慕→0（室内決行），非恋慕→1（屋外中止）（宴会41）
- PLANNING 中手动天气检查与框架冲突 → 删除，由框架 WEATHER_DEPENDENT 机制处理（宴会41）
- LOCATION 错误：42→P202中央広場, 8→P708大蝦蟇の池, 9→P11庭, 10→P218小料理屋
- 参加率错误：42→恢复旧版同地图100%/异地图规模分档, 8→住所不定100%/部外者3%
- 通知文本缺失：8→补充「平时不太见到的面孔」
- CONDITIONS 不匹配：9→`DAY:2==1||DAY:2==2`（春夏限定）, 10→添加3組出禁守卫
- HOST 固定丢失持ち回り：10→`ADD_BANQUET_10_HOST()` 动态轮换（蕾米莉亚/觉/豊姫）

---

## v0.3 (2026-06-03) — Phase 3a 宴会风味文本回填

### Added
- 恢复精确日期条件：7(DAY:3==4&&DAY:2!=4), 8(DAY:3==10&&DAY:2!=4), 9(DAY:3==20&&DAY:2!=4), 10(DAY:3==3&&夏冬), 41(DAY:3==8&&DAY:2!=4)
- 恢复持ち回り机制：7(組長轮换), 10(長女轮换)，使用 `宴会開催回数:N % 3`
- 恢复动态通知文本：7→调用 `ADD_BANQUET_7_FAMILIAR()` 生成动态邀请文本
- 添加開始/終了居合わせ文本：7(組長抢座/部下围坐+空酒瓶), 10(长女万岁+醉鬼胡言+品性被怀疑)
- 恢复住所不定动态机制：8→最低8人门槛, HOST动态选择(`ADD_BANQUET_8_HOST`)
- 恢复恋慕分岐：41→恋慕P431兎の洞穴/非恋慕P703玄武の沢, 非恋慕+悪天候→RETURN
- 恢复親密门槛：41→CONDITIONS 添加 `ABL:[[正邪]]:親密>=8`
- 恢复CRAZY_THURSDAY条件：42→CONDITIONS 添加检查
- 恢复天气依赖：8→`WEATHER_DEPENDENT=1` + `ALTERNATIVE_INDOOR_LOCATION=P933酒場`

### Fixed
- CFLAG:宴会参加 残留导致旧系统路径误触发 → ADD_BANQUET_END/END_PARTICIPATION 添加清除, MOVEMENT_SUB 添加 CFLAG:BANQUET 守卫
- 宴会開催回数 未递增 → ADD_BANQUET_END 中添加 `宴会開催回数:BANQUET_ID++`

---

## v0.2d (2026-06-03) — Phase 2d 神道式婚礼

### Added
- `@WEDDING_JAPANESE` 仪式函数：参入→修祓→致辞→誓词（自宣读式）→三献仪（三三九度）→交杯+亲吻→玉串奉奠→退场
- 主持人选择：灵梦非新娘→灵梦→先代→早苗（全禁则 THROW）；灵梦是新娘→先代→早苗→可跳过
- 换装：新郎=衣装セット5(神官服)，新娘=衣装セット69(白无垢)
- 婚礼策划神道式分支：启用 JAPANESE ASK_M 选项 + 灵梦场地确认对话
- 三种婚礼场地确认对话均新增"地主是新娘"分支（蕾米莉亚→咲夜，灵梦→先代/早苗，幽香→拉尔瓦）
- 口上模板 JAPANESE/FAIRY 分支（M_KOJO_KX_X2_MARRIAGE.ERB）
- KOJO_MESSAGE EVENT 分支 RESULT=0 修复：TRYCALLFORM 前重置 RESULT/RESULTS

### Fixed
- 宴会双重描写Bug：MOVEMENT_SUB 排除職種 48(宴会準備)/49(宴会参加)/51(酔いつぶれる)

---

## v0.2c — Phase 2c 婚姻散布修改

### Added
- Deep Love QoL 日期记录：EVENTTURNEND 取消注释 + 恋慕rank1日期
- Add_Wife the Dust.ERB：妻保存/恢复（Bite the Dust 系统），BITE_THE_DUST_BACKUP 妻标记保存（bit7）
- GET_CHARAHOME 妻同居：LIVE_IN_WIFE → RETURNF 初期位置
- SET_MAINHOME 妻搬入：WIFE_MOVE_IN 取消注释
- CHARA_HOLIDAY 婚礼休假：WEDDING_DATE 当天配偶休假
- 衣装セット106 婚礼套装（皮鞋/衬衫/西裤/西装夹克/领带）
- COM350 妻性许可：妻/妾+心情不差→直接推倒（2处）
- EVALUATE_GIRLPOWER 妻乘数：妻x3.0/未婚夫x2.5/恋人x2.0
- MAP_DEFAULTRESIDENT 妻位置保留：LIVE_IN_WIFE 角色跳过重置
- COM312/SCOM63 反感抑制：妻/妾+心情不差→不产生反感
- ORGASM_ADD 反感抑制：绝顶反感对妻/妾豁免（4处）
- UPDATE_TR 妻位置恢复：LIVE_IN_WIFE→MARRIAGE_MOVE_WIFE_IN
- CLOTHES 下着 second rank Love：恋慕值直接用于概率公式（CLOTHES 7处+METH 9处）

---

## v0.2 — Phase 2 婚姻系统核心 + 婚礼宴会

### Added
- COM13 求婚（pedy COM11→13，避免与换衣服冲突）
- COM14 婚礼策划（pedy COM13→14）
- Add_Wedding.ERB：3种婚礼类型（西式/神道/妖精）+ 翻译
- Add_Banquet_31 婚礼宴会：QOL 改写 + 翻译
- 散布修改：COM名注册、TALENT_INFO 妻/妾、Look婚戒显示、日程表婚礼日期、EVENTCOMEND触发、新游戏重置

### Fixed
- BEFORETRAIN 婚礼触发：取消注释 WEDDING_CEREMONY 调用
- 婚礼 qol_FORCESET：Add_Wedding.ERB 添加3个区域天气同步调用
- BEFORETRAIN 提前唤醒：移除 SKIPSTART/SKIPEND 包裹

---

## v0.1 — Phase 0+1 框架部署 + 宴会迁移

### Added
- Add_Banquet.ERH 变量定义与状态常量
- CFLAG:BANQUET(9106)/BANQUET_ROLE(9107)/BANQUET_CLEANUP(9108) 定义
- OBJ CLASS "ADD_BANQUET" 注册（CLASS_NUM 25→26）
- Add_Banquet.ERB 解除 SKIP（2处）+ GETMETH 适配（GETMETH_INT 12处 + GETMETH_STR 18处）
- Add_Banquet_Drinking_Common.ERB（GETMETH 适配 2处）
- 宴会 1~6：从 pedy-tw 复制 + QOL 改写 + 翻译
- 宴会 11~16：从 pedy-tw 复制 + QOL 改写 + 翻译
- 节日 23：从 pedy-tw 复制 + QOL 改写 + 翻译
- chs 独有宴会 7~10：新建（畜生界/住所不定/自机/姐姐）
- chs 独有宴会 41~42：新建（正邪一人/疯狂木曜日，重编号避免与 pedy 11/12 冲突）
- MOVEMENT_SUB.ERB：ADD_BANQUET_PREVENT_MOVEMENT（3处）
- MOVEMENT.ERB + COMF400：ADD_BANQUET_ARRIVAL（2处）

### Changed
- 架构策略：原"双轨并行"改为"渐进替换"（与 pedy-tw 一致）
  - `ENKAI_SETTING` → `ADD_BANQUET_CHECK`，`ENKAI_ENTRY` → `ADD_BANQUET_SET_PARTICIPANTS`
  - `ENKAI_WORK` 保留（MOVEMENT_SUB 仍调用），`ENKAI_START` 清空为 `RETURN 1`
  - `CFLAG:宴会参加` 是共享桥接变量，`CFLAG:BANQUET` 是 ADD_BANQUET 扩展追踪

### Fixed
- Add_Marriage.ERB MARRIAGE_NEW_GAME CVARSET 修复（取消注释三行）
- ENKAI 入口替换：EVENTTURNEND/INFO(2处), BEFORETRAIN/INFO(2处), EVENTCOMEND(1处)
- ENKAI_START 函数体清空为 `RETURN 1`
- OBJNAME_TO_ID→_Rename 宏替换（3处）
- ENKAI_END 注释（3处）：BEFORETRAIN:704, EVENTTURNEND:8, INFO:1265
- RESET_OUTFIT 缺失：宴会23/41/42添加DRESS_UP/DOWN+RESET_OUTFIT
- 宴会31换装路径确认：婚纱走OKIGAE体系，不走DRESS_UP/RESET_OUTFIT

---

## 系统说明

### 宴会系统（ADD_BANQUET 框架）

ADD_BANQUET 框架替代了旧版 ENKAI 系统，使用 OBJ 系统的 GETMETH 动态分发机制管理宴会生命周期。

**核心文件**：
- `ERB\fromEN\Addition\Banquets\Add_Banquet.ERB` — 框架核心（40个函数）
- `ERB\fromEN\Addition\Banquets\Add_Banquet.ERH` — 变量/常量定义
- `ERB\fromEN\Addition\Banquets\Add_Banquet_Drinking_Common.ERB` — 饮酒通用
- `ERB\fromEN\Addition\Banquets\Add_Banquet_Performance.ERB` — 演奏系统

**宴会调用链**：
```
EVENTTURNEND → ADD_BANQUET_CHECK（每日检查+创建）
BEFORETRAIN  → ADD_BANQUET_SET_PARTICIPANTS（参与者设定）
EVENTCOMEND  → ADD_BANQUET_ARRIVAL（到达检查）
EVENTTRAIN   → ADD_BANQUET_PROGRESS（每回合推进）
MOVEMENT     → ADD_BANQUET_ARRIVAL + ADD_BANQUET_PREVENT_MOVEMENT
```

**创建新宴会**：需实现3个必须函数 + 若干可选函数：
- `FADD_BANQUET{ID}(ARG, O_DATA)` — 属性定义
- `ADD_BANQUET_PLANNING{ID}` — 创建逻辑
- `ADD_BANQUET_SET_PARTICIPANTS{ID}` — 参与者设定

饮酒型宴会可委托 `ADD_BANQUET_DRINKING_*` 通用函数。

### 婚礼系统

婚礼系统覆盖 求婚→策划→仪式→婚宴 的完整流程。婚宴通过宴会ID 31 与 ADD_BANQUET 框架联动。

**核心文件**：
- `ERB\fromEN\Addition\Marriage\Add_Marriage.ERB` — 主文件（新游戏重置等）
- `ERB\fromEN\Addition\Marriage\Add_Marriage.ERH` — 变量定义
- `ERB\fromEN\Addition\Marriage\Add_Wedding.ERB` — 婚礼仪式
- `ERB\fromEN\Addition\Marriage\Add_CUSTOM_COM14*.ERB` — 婚礼策划命令
- `ERB\fromEN\Addition\Marriage\Add_CUSTOM_COM13*.ERB` — 求婚命令
- `ERB\fromEN\Addition\Marriage\Add_Marriage_Concubinage.ERB` — 侧室系统
- `ERB\fromEN\Addition\Banquets\Add_Banquet_31*.ERB` — 婚宴定义

**婚礼触发链路**：
- `BEFORETRAIN:200-210` — 婚礼当天提前唤醒
- `BEFORETRAIN:567` — 触发 WEDDING_CEREMONY
- `EVENTCOMEND:33` — 触发 WEDDING_CEREMONY（双触发点确保不遗漏）

**婚礼→婚宴链接**：WEDDING_CEREMONY 末尾设置 ADD_BANQUETS_START_TIME/DAY 为当前时间，调用 ADD_BANQUET_PROGRESS() 立即推进婚宴状态。

**天气控制**：WEDDING_CEREMONY 中 `TIME:5 = 0, WIND_VELOCITY = 0, FORBIDDEN_CHANGE_WEATHER = 1`，并调用 `qol_FORCESET_REGION_*` 同步区域天气/彩虹/风速。

### 宴会编号分配

| 编号 | 来源 | 宴会名 | 类别 |
|------|------|--------|------|
| 1 | pedy-tw | 灵梦即兴酒会 | banquet |
| 2 | pedy-tw | 忘年会 | banquet |
| 3 | pedy-tw | 永远亭赏月会 | banquet |
| 4 | pedy-tw | 丰收祭 | banquet |
| 5 | pedy-tw | 白莲读经Live | concert |
| 6 | pedy-tw | 蕾米莉亚即兴派对 | banquet |
| 7 | chs | 畜生界的和平亲睦会 | banquet |
| 8 | chs | 住所不定者的集会 | banquet |
| 9 | chs | 自机聚会 | banquet |
| 10 | chs | 姐姐聚会 | banquet |
| 11 | pedy-tw | 鸟兽伎乐演唱会 | concert |
| 12 | pedy-tw | 天子的天界宴会 | banquet |
| 13 | pedy-tw | 幽香的友好聚会 | banquet |
| 14 | pedy-tw | 勇仪的喧闹酒会 | banquet |
| 15 | pedy-tw | 秘密佛教酒会 | banquet |
| 16 | pedy-tw | 月人宴会 | banquet |
| 21 | pedy-tw | 幻想乡网球俱乐部 | sports |
| 22 | pedy-tw | 湖畔夏日狂欢 | swimming |
| 23 | pedy-tw | 月兔祭 | festival |
| 31 | pedy-tw | 婚礼宴会 | wedding |
| 41 | chs | 正邪的一人宴会 | banquet |
| 42 | chs | 疯狂木曜日 | banquet |

chs ENKAI 11/12 与 pedy ADD_BANQUET 11/12 冲突，重编号为 41/42。7~10 无冲突。

### COM 编号映射（pedy→chs）

| pedy | 用途 | chs | 用途 |
|------|------|-----|------|
| 0 | Play Game | **0** | Play Game（变态服挪至 COM19） |
| 11 | Propose | **13** | 求婚（chs COM11=换衣服） |
| 13 | Wedding Planning | **14** | 婚礼策划 |
| 18 | Discuss Concubinage | **18** | 商议纳妾 |
| 19 | Concubinage Labor | **19** | 妾室劳作（chs COM19→变态服，原19暂缓） |

### Phase 0 前置验证记录

| # | 问题 | 回答 |
|---|------|------|
| 1 | Add_Banquet.ERB 被 SKIP 包裹？ | 是，两段 SKIP 块（1~692行 + 708~942行），ADD_BANQUET_IS_PERFORMING（694行）不在内 |
| 2 | Add_Banquet.ERH 不存在？ | 是，Banquets 目录下仅 1 个文件 |
| 3 | CLASS_NUM 25 已满？ | 是，25 个 CLASS 已注册，无空位 |
| 4 | CFLAG:BANQUET 缺失？ | 是，CFLAG.csv 无定义，anon-tw 定义在 9106/9107/9108 |
| 5 | ADD_GAME_INFO 必须加？ | 不必须，Phase 0~1 不涉及 |
| 6 | TCVAR:DRESSED_FOR_BANQUET 存在？ | 存在，TCVAR 906 |
| 7 | JOB_宴会準備/宴会参加 常量存在？ | 存在，48/49/50 |
| 8 | MARRIAGE_NEW_GAME CVARSET 被注释？ | 是，三行全部注释 |
| 9 | GET_INT/GET_STR 替换处数？ | 约 23 处（10+13） |

### 知识库修正

| 原断言 | 修正 | 原因 |
|--------|------|------|
| CLASS_NUM 25→27 | 25→26（仅加 ADD_BANQUET） | ADD_GAME_INFO Phase 0~1 不涉及 |
| "chs 有部分变量定义" | CFLAG:BANQUET/ROLE/CLEANUP 完全缺失 | 移植时遗漏 CFLAG.csv 定义 |
