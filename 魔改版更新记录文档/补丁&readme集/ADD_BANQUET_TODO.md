=====================================================
  ADD_BANQUET TODO — 临时待办（开发完成后删除）
=====================================================

## Phase 3b：ADD_GAME_INFO 系统（CUSTOM_COM0 Play Game） ✅ 已完成

> 基于 pedy-tw 源码调查，详见知识库 banquet-migration-handbook.md §4 Phase 3b

**前置条件**：无（独立系统，与宴会框架联动时需 Phase 3c）

**COM 编号决策**：pedy-tw 用 CUSTOM_COM0（Play Game），chs 的 COM0 原被"变态服"占用。
→ **变态服挪至 CUSTOM_COM19**（空位，紧邻 COM18 委托），**Play Game 占 COM0**（与 pedy-tw 对齐）

| # | 任务 | 说明 | 状态 |
|---|------|------|------|
| 0 | 变态服 COM0→COM19 | 重命名文件+函数名+COM_Name，更新所有引用 | ✅ |
| 1 | CLASS_NUM 26→28 | 预留 ADD_GAME_INFO + 1 个空位 | ✅ |
| 2 | 注册 ADD_GAME_INFO CLASS | qol_OBJ.ERB 添加 MAKE_OOP_MAP | ✅ |
| 3 | 创建 Add_CUSTOM_COM0 Play Game.ERH | 变量定义 | ✅ |
| 4 | 创建 Add_CUSTOM_COM0 Play Game.ERB | 主入口 | ✅ |
| 5 | 创建 Add_CUSTOM_COM0 Game List.ERB | Game 1/2/4（简单游戏） | ✅ |
| 6 | 创建 ADD_CUSTOM_COM0 Game 9 (Tennis Singles).ERB | 需要 TENNIS 标志 | ✅ |
| 7 | 创建 ADD_CUSTOM_COM0 Game 10 (Tennis Doubles).ERB | 需要 TENNIS 标志 | ✅ |
| 8 | 注册 COM0 到 USERSHOP/SHOW_SHOP | 命令列表可见 | ✅ |
| 9 | 移植 ADD_BANQUET_ACTIVITY_ALLOWED | Add_Banquet.ERB 中已存在 | ✅ |
| 10 | 翻译所有游戏文本 | Game 1/2/4/9/10 | ✅ |
| 11 | 后续移植 Game 5/8 | 羽根突/饮酒竞赛（互动型） | ⬜ |
| 12 | 后续移植 Game 3/6/7 | 双六/排球/游泳比赛（可后补） | ⬜ |
| 13 | ADD_GAME_INFO 旧模式→新模式 | @ADD_GAME_INFO→@FADD_GAME_INFO, GET_INT/GET_STR→GETMETH_INT/GETMETH_STR | ✅ |
| 14 | CHARISMA 翻译 | "魅力"→"筹码" | ✅ |

**验证清单**：
- [ ] 变态服在 COM19 正常工作
- [ ] COM0 出现在命令列表中
- [ ] 同室有角色时可选择游戏
- [ ] Game 1/2/4 可正常游玩
- [ ] 宴会中 TENNIS 标志生效时 Game 9/10 可选

---

## Phase 3c：宴会 21/22（网球俱乐部 + 湖畔嬉水） ✅ 已完成

> 详见知识库 banquet-migration-handbook.md §4 Phase 3c

**前置条件**：Phase 3b（至少 3b-6/7 网球游戏 + 3b-9 ACTIVITY_ALLOWED）

| # | 任务 | 说明 | 状态 |
|---|------|------|------|
| 1 | 创建 Add_Banquet_21.ERB | 网球俱乐部 | ✅ |
| 2 | 创建 Add_Banquet_22.ERB | 湖畔嬉水 | ✅ |
| 3 | ~~确认/新建 テニスウェアセット 衣装セット~~ | 衣装セット58=网球服套装，CLOTHES+METH 双文件已存在 | ✅ |
| 4 | 确认 ADD_BANQUET21_INVITE 变量可用 | ERH 中已有定义 | ✅ |
| 5 | 翻译宴会21/22文本 | | ✅ |
| 6 | 验证 ADD_START_SWIMMING 在宴会22中的行为 | chs 已存在 | ✅ |

**验证清单**：
- [ ] 宴会21 每周触发，白天/夜晚交替
- [ ] 宴会21 参与者换上网球服
- [ ] 宴会21 中可玩网球游戏（Game 9/10）
- [ ] 宴会22 夏季周日触发
- [ ] 宴会22 参与者换上泳装（ADD_START_SWIMMING）
- [ ] 宴会22 雨天取消（WEATHER_DEPENDENT=1）

---

## Phase 4：侧室系统（无限期推迟）

翻译已完成（~470行，Add_Marriage_Concubinage.ERB），SKIP 不解除，COM18/19 不激活。

---

## 宴会服整合 ✅ 已完成

> `宴会服决定`（宴会.ERB:442-458）已被 `ADD_BANQUET_DRESS_UP`（Add_Banquet.ERB:1053）和 `SET_OUTFIT11`（Add_Banquet_11:312）调用，映射集中管理，无需迁移到各 SET_OUTFIT 函数

| 角色 NO | 角色名 | 衣装セット | _Rename 宏 |
|---------|--------|-----------|-----------|
| 15 | 咲夜 | 晚宴礼服套装 | `[[晚宴礼服套装]]` |
| 77, 78, 134 | 小町+映姫+? | 浴衣穿搭 | `[[浴衣穿搭]]` |
| 88 | 響子 | 鸟兽伎乐套装 | `[[鸟兽伎乐套装]]` |
| 102 | 神綺 | 晚宴礼服套装 | `[[晚宴礼服套装]]` |
| 130 | 美鈴 | 生足美鈴套 | `[[生足美鈴套]]` |
