# Handoff — anon-tw 上游提交 chs 适配审查

## 任务概述

审查 anon-tw 仓库 2 个 commit 提交至 chs（`d:\eratw-chs`）是否需要采用：

| Commit | 主题 | 当前状态 |
|--------|------|---------|
| `88376c65c018da74842b592f6ea956c7c869734a` | 弹幕对决：暴食蜈蚣buff改为修正值 + 显示信息 | ✅ **已回滚修正（anon-tw 修复存在方向反转 Bug）** |
| `0cc1d02f5b288f922998a42ff32378624521fb75` | 错误禁用的对话块（46 文件） | 🔄 调查中（**44/46 已决：30 已修复 + 10 无需修复 + 6 chs 缺失**；F27 已完成，全部 46 个子任务均有结论）|

## 提交 1 审查结论（2026-06-19 新增）

**anon-tw 修复存在方向反转 Bug，chs 应当回滚修正，不应盲目采用。**

### 1. 修复前 vs 修复后对比

| 项目 | 修复前（anon-tw 旧版） | 修复后（anon-tw 现版） |
|------|----------------------|---------------------|
| 公式 | `プレイヤーダイス面 += (プレイヤーダイス面 / 4) * 2 * nGluttonousCentipedeCaptures` | `相手修正値 += (相手修正値 / 4) * 2 * nGluttonousCentipedeCaptures` |
| 作用对象 | 玩家骰子面 | 对手修正值 |
| 实际效果 | **buff 玩家** | **buff 对手（=惩罚玩家）** |
| 显示文本 | 无 | "Ongoing effect: Gluttonous Centipede　…Dice value correction Up" |

### 2. 设计意图（来自 `nGluttonousCentipedeCaptures` 生命周期）

| 阶段 | 位置 | 行为 |
|------|------|------|
| Set（玩家胜） | [anon-tw:532](file:///d:/anon-tw/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB#L532) | `nGluttonousCentipedeCaptures += 1` "Power surges through you!" |
| Clear（玩家败） | [anon-tw:398](file:///d:/anon-tw/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB#L398)、[anon-tw:430](file:///d:/anon-tw/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB#L430) | `nGluttonousCentipedeCaptures = 0` "The power of the Gluttonous Centipede leaves your body." |

**变量语义**：玩家连续获胜次数的计数器。设计意图为"连胜越多，buff 越强"。

### 3. Bug 判定

anon-tw 提交说明写"Make Gluttonous Centipede buff dice correction instead of dice value"——作者意图是把"骰子面"提升改为"修正值"提升（更晚结算的乘区，影响更大）。但实际代码将目标变量从 `プレイヤーダイス面` 改成了 `相手修正値`，**方向反转**。

| 推断 | 验证 |
|------|------|
| 作者意图：把对玩家的 buff 从"骰子面"换为"修正值" | 提交说明支持 |
| 作者实际写：把对玩家的 buff 改成对对手的 buff | 修复后代码 `相手修正値` 证实 |
| 这不是设计选择，是 typo 级别的 bug | 显示文本"Dice value correction Up"未明确归属是次要佐证 |

### 4. chs 应采取的修正

**当前状态**：chs 采用了 anon-tw 的错误版本（[DANMAKU.ERB:256-257](file:///d:/eratw-chs/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB#L256-L257)），需要将 `相手修正値` 改回 `プレイヤー修正値`：

```erb
;custom code
SIF ITEM:922
    プレイヤー修正値 += (プレイヤー修正値 / 4) * 2 * nGluttonousCentipedeCaptures
```

**显示文本**（[DANMAKU.ERB:307-310](file:///d:/eratw-chs/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB#L307-L310)）应同步改为明确归属：
```erb
;custom code
IF nGluttonousCentipedeCaptures > 0
    SETCOLOR 0x666666
    PRINTFORML   （发挥效果中: 暴食的蜈蚣　　…玩家骰子修正值Up）
ENDIF
```

### 5. 关键证据

- 提交 diff：[commit_88376c65_danmaku_fix.txt](file:///d:/emuera/shared-trae/knowledge/eratw/changelog/commit_88376c65_danmaku_fix.txt)
- anon-tw 当前代码：[DANMAKU.ERB:266-268](file:///d:/anon-tw/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB#L266-L268)
- chs 当前代码：[DANMAKU.ERB:254-257](file:///d:/eratw-chs/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB#L254-L257)
- 变量生命周期：[anon-tw:171](file:///d:/anon-tw/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB#L171)（初始化）、[anon-tw:532](file:///d:/anon-tw/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB#L532)（连胜+1）、[anon-tw:398](file:///d:/anon-tw/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB#L398)（战败清零）

## 提交 2 进度

### 已有结论（已调查 7 个文件）

| 子任务 | 文件 | 状态 |
|--------|------|------|
| F01 | [K15 Sakuya 奉仕系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/015 Sakuya [咲夜]/TW咲夜逆輸入版/M_KOJO_K15_奉仕系コマンド.ERB) | ✅ 已修复（解包 `LOCAL:1` 守卫）|
| F02 | [K18 Lily W 性交系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/018 Lily W [リリーＷ]/莉莉白口上测试版v1.01(23.1.25)/M_KOJO_K18_性交系コマンド.ERB) | ⏭️ 无需修复（chs 已是 `IF LOCAL`）|
| F03 | [K18 Lily W 愛撫系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/018 Lily W [リリーＷ]/莉莉白口上测试版v1.01(23.1.25)/M_KOJO_K18_愛撫系.ERB) | ✅ 已修复（2 hunks：转换 `IF→ELSEIF` + 删除多余 `ENDIF`）|
| F04 | [K23 Youmu 事件](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/023 Youmu [妖夢]/妖夢別人改変版/M_KOJO_K23_1_イベント.ERB) | ⏭️ 无需修复（`LOCAL:1 = 1` 已正确）|
| F05 | [K27 Wriggle イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/027 Wriggle [リグル]/リグル/M_KOJO_K27_イベント.ERB) | ✅ 已修复（大 hunk：删除 Reimu/Ruukoto 子分支 + 启用 Yamame 分支）|
| F06 | [K27 Wriggle 愛撫系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/027 Wriggle [リグル]/リグル/M_KOJO_K27_愛撫系コマンド.ERB) | ⏭️ 无需修复（`LOCAL:1 = 1` 已正确）|
| F07 | [K27 Wriggle リグル イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/027 Wriggle [リグル]/リグル/M_KOJO_K27_イベント.ERB) | ✅ 已修复（`LOCAL:1 = 0` → `1`，无自覚妊娠分支）|

### 待办分批（剩余 42 个文件）

**第 0 批：路径映射（前置）**
- ~~F13/F14~~（050 Flandre egg 子分支 → 芙兰朵露海外版）✅ 已解决
- F29-F31（119 Nemuno ENNemuno 子分支是否存在）
- F32/F33（120 Aunn AunnJP 子分支）
- F34/F35（121/124 賑やかし子分支）
- ~~F16/F17~~（053 Tewi 文件名 events/commands → イベント/コマンド）✅ 已解决
- ~~F19~~（060 Parsee 文件名带 `_2_` 前缀）✅ 已解决

**第 1 批：F01-F07** ✅ **已完成（2026-06-19 第 1 轮）**（7 个小文件，1 个会话）

**第 2 批：F10-F19** ✅ **已完成（2026-06-19 第 2 轮）**（10 个中等文件，1 个会话）

**第 3 批：F20-F25**（6 个混合文件，预计 1 个会话）

**第 4 批：F28-F46**（19 个混合文件，预计 2 个会话）

**F08 单独**：K38 Koishi str 46 hunks，单独预算 2-3 个会话
**F09 单独**：K38 str 日常 8 hunks，1 个会话

## 当前状态（2026-06-19）

### 已完成

| 子任务 | 文件 | 状态 | 证据 |
|--------|------|------|------|
| 提交 1 | [DANMAKU.ERB](file:///d:/eratw-chs/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB) | ✅ **已回滚修正**（`相手修正値` → `プレイヤー修正値`，显示文本改为"玩家骰子修正值Up"）| [DANMAKU.ERB:307-308](file:///d:/eratw-chs/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB#L307-L308)、[DANMAKU.ERB:393](file:///d:/eratw-chs/ERB/コマンド関連/COMF/日常系/DANMAKU.ERB#L393) |
| 提交 2 F01 | [K15 Sakuya 奉仕系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/015 Sakuya [咲夜]/TW咲夜逆輸入版/M_KOJO_K15_奉仕系コマンド.ERB) | ✅ 已修复 | 解包 `LOCAL:1` 守卫：`IF LOCAL:1 && FIRSTTIME(SELECTCOM)` → `IF FIRSTTIME(SELECTCOM)` |
| 提交 2 F02 | [K18 Lily W 性交系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/018 Lily W [リリーＷ]/莉莉白口上测试版v1.01(23.1.25)/M_KOJO_K18_性交系コマンド.ERB) | ⏭️ 无需修复 | chs 已是 `IF LOCAL`（缺 `;custom code` 注释，差异无影响）|
| 提交 2 F03 | [K18 Lily W 愛撫系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/018 Lily W [リリーＷ]/莉莉白口上测试版v1.01(23.1.25)/M_KOJO_K18_愛撫系.ERB) | ✅ 已修复 | (1) `IF LOCAL:1 && TEQUIP:50 == PLAYER` → `ELSEIF TEQUIP:50 == PLAYER ;custom code`；(2) 删除多余 `ENDIF` |
| 提交 2 F04 | [K23 Youmu 事件](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/023 Youmu [妖夢]/妖夢別人改変版/M_KOJO_K23_1_イベント.ERB) | ⏭️ 无需修复 | `LOCAL:1 = 1` 已正确 |
| 提交 2 F05 | [K27 Wriggle イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/027 Wriggle [リグル]/リグル/M_KOJO_K27_イベント.ERB) | ✅ 已修复 | 删除 Reimu/Ruukoto 禁用分支；启用 Yamame 分支 |
| 提交 2 F06 | [K27 Wriggle 愛撫系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/027 Wriggle [リグル]/リグル/M_KOJO_K27_愛撫系コマンド.ERB) | ⏭️ 无需修复 | `LOCAL:1 = 1` 已正确 |
| 提交 2 F07 | [K27 Wriggle リグル イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/027 Wriggle [リグル]/リグル/M_KOJO_K27_イベント.ERB) | ✅ 已修复 | `LOCAL:1 = 0` → `LOCAL:1 = 1`（无自覚妊娠分支启用，行 2861）|
| 提交 2 F26 | [K101 Tokiko 日常](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/101 Tokiko [朱鷺子]/朱鷺子/M_KOJO_K101_日常系コマンド.ERB) | ✅ 已修复 | `LOCAL = 0` → `LOCAL = 1`（第 3158 行）|
| 提交 2 F43 | [K142 Momoyo 日常](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/142 Momoyo [百々世]/Momoyo/M_KOJO_K142_everyday_commmands.ERB) | ⏭️ 无需修复 | `LOCAL = 1` 已正确 |
| 提交 2 F10 | [K38 Koishi TW用古明地こいし イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/038 Koishi [こいし]/TW用古明地こいし/M_KOJO_K38_イベント.ERB) | ⏭️ 无需修复 | chs 行 1620 已经是 `LOCAL:1 = 1` |
| 提交 2 F11 | [K39 Nazrin ひねくれナズー口上 愛撫系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/039 Nazrin [ナズーリン]/ひねくれナズー口上/M_KOJO_K39_愛撫系コマンド.ERB) | ✅ 已修复 | chs 行 432 `LOCAL:1 = 0` → `LOCAL:1 = 1 ;custom code`（函数 @M_KOJO_MESSAGE_COM_K39_2_1 初めて块）|
| 提交 2 F12 | [K42 Hatate はたて イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/042 Hatate [はたて]/はたて/M_KOJO_K42_イベント.ERB) | ✅ 已修复 | chs 行 7015/7060/7071 三处 `LOCAL:1 = 0` → `LOCAL:1 = 1 ;custom code`（陥落素質あり自慰中毒高点位的 Ｃ敏感/Ｂ敏感/部位指定無し）|
| 提交 2 F13 | [K50 Flandre 芙兰朵露海外版 events](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/050 Flandre [フラン]/芙兰朵露海外版/M_KOJO_K50_2_events.ERB) | ✅ 已修复 | chs 行 3270 `LOCAL = 0` → `LOCAL = 1`（脱衣口上 @K50_28 函数入口）；行 3330 `LOCAL:1 = 0` → `1`（CASE 3 パンツちょうだい）原本已正确 |
| 提交 2 F14 | [K50 Flandre 芙兰朵露海外版 性騷扰](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/050 Flandre [フラン]/芙兰朵露海外版/M_KOJO_K50_2_sexual_harassment_commands.ERB) | ⏭️ 无需修复 | chs 行 235 已经是 `LOCAL = 1` |
| 提交 2 F15 | [K50 Flandre eraTW別人版 性交系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/050 Flandre [フラン]/eraTW別人版フラン口上/M_KOJO_K50_1_性交系コマンド.ERB) | ✅ 已修复 | chs 行 888 `LOCAL:1 = 0` → `LOCAL:1 = 1 ;custom code`（@M_KOJO_ふらん_MESSAGE_COM_K50_67_1 対面座位初めて块）|
| 提交 2 F16 | [K53 Tewi コマンド](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/053 Tewi [てゐ]/てゐ/M_KOJO_K53_コマンド.ERB) | ✅ 已修复 | chs 行 354 解包 `LOCAL:1` 守卫：`IF LOCAL:1 && FIRSTTIME(SELECTCOM)` → `IF FIRSTTIME(SELECTCOM)`（@M_KOJO_MESSAGE_COM_K53_124_1 给对方手淫）|
| 提交 2 F17 | [K53 Tewi イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/053 Tewi [てゐ]/てゐ/M_KOJO_K53_イベント.ERB) | ⏭️ 无需修复 | chs 行 1764 已经是 `LOCAL:1 = 1` |
| 提交 2 F18 | [K55 Byakuren 聖 愛撫系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/055 Byakuren [白蓮]/聖/M_KOJO_K55_愛撫系コマンド.ERB) | ✅ 已修复 | chs 行 1361 `LOCAL:1 = 0` → `LOCAL:1 = 1 ;custom code`（@M_KOJO_MESSAGE_COM_K55_20_1 接吻初めて块）|
| 提交 2 F19 | [K60 Parsee 性交系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/060 Parsee [パルスィ]/Parsee/M_KOJO_K60_2_性交系コマンド.ERB) | ✅ 已修复 | 4 hunks：行 1427/1434/1767/1774 四处 `LOCAL/LOCAL:1 = 0` → `= 1`（@M_KOJO_EGG_MESSAGE_COM_K60_64_1 騎乗位 + @K60_66_1 騎乗位肛門）|
| 提交 2 F20 | [K69 Mamizou 派生口上 イベント_拡張](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/069 Mamizou [マミゾウ]/マミゾウ別人変身対応版/派生口上/M_KOJO_K69_1_イベント_拡張.ERB) | ✅ 已修复 | 3 hunks：行 1128 `LOCAL = 0` → `1`、行 1146 `LOCAL:1 = 0` → `1`、行 1222/1228 `LOCAL:1 = 0` → `1`（@M_KOJO_イベント_K69_1 関数の逢瀬終了/事後描写/精液が垂れてきた块）|
| 提交 2 F21 | [K69 Mamizou 派生口上 絶頂_拡張](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/069 Mamizou [マミゾウ]/マミゾウ別人変身対応版/派生口上/M_KOJO_K69_1_絶頂_拡張 .ERB) | ✅ 已修复 | chs 行 834 `LOCAL = 0` → `LOCAL = 1 ;custom code`（@M_KOJO_絶頂_K69_1 函数内"手淫フェラ"块）|
| 提交 2 F22 | [K71 Shinmyoumaru 性交系](file:///d:/anon-tw/ERB/口上・メッセージ関連/個人口上/071%20Shinmyoumaru%20[%E9%87%9D%E5%A6%99%E4%B8%B8]/%E9%87%9D%E5%A6%99%E4%B8%B8/M_KOJO_K71_%E6%80%A7%E4%BA%A4%E7%B3%BB%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89.ERB) | ❌ chs 缺失 | `M_KOJO_K71_性交系コマンド.ERB` 在 chs 中不存在；`@M_KOJO_MESSAGE_COM_K71_79`（正常位）对应的函数 chs 中也没有 |
| 提交 2 F23 | [K72 Eirin 永琳 イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/072%20Eirin%20[%E6%B0%B8%E7%90%B3]/%E6%B0%B8%E7%90%B3/M_KOJO_K72_%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88.ERB) | ✅ 已修复 | 2 hunks：行 5380（事后の情绪 + ARG:1 == 3）、行 5417（服を着る + ARG:1 == 4），均为 `LOCAL:1 = 0` → `LOCAL:1 = 1 ;custom code` |
| 提交 2 F24 | [K91 Tojiko 賑やかし屠自古 イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/091%20Tojiko%20[%E5%B1%A0%E8%87%AA%E5%8F%A4]/%E3%80%9091%E3%80%91%E8%B3%83%E3%82%84%E3%81%8B%E3%81%97%E5%B1%A0%E8%87%AA%E5%8F%A4Ver1.00/M_KOJO_K91_%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88.ERB) | ✅ 已修复 | 1 hunk：行 853 `LOCAL:1 = 0` → `LOCAL:1 = 1 ;custom code`（抜け出した 块，IF LOCAL:1 && !ARG:1）|
| 提交 2 F25 | [K93 Wakasagihime 若鹭姬南风天 事件系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/093%20Wakasagihime%20[%E3%82%8F%E3%81%8B%E3%81%95%E3%81%8E%E5%A7%AB]/%E8%8B%A5%E9%B9%AD%E5%A7%AC%E5%8D%97%E9%A3%8E%E5%A4%A9/M_KOJO_K93_2_%E4%BA%8B%E4%BB%B6%E7%B3%BB.ERB) | ⏭️ 无需修复 | anon-tw 路径 `ENWaggy/M_KOJO_K93_events.ERB` 在 chs 中不存在；chs 中文版 `若鹭姬南风天/M_KOJO_K93_2_事件系.ERB` 中**完全没有 `LOCAL = 0` 或 `LOCAL:1 = 0`**，所有 7 个 hunk 涉及的块已全是 `LOCAL:1 = 1` |
| 提交 2 F28 | [K113 Hecatia 愛撫系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/113%20Hecatia%20[%E3%83%98%E3%82%AB%E3%83%BC%E3%83%86%E3%82%A3%E3%82%A2]/%E3%83%98%E3%82%AB%E3%83%BC%E3%83%86%E3%82%A3%E3%82%A2/M_KOJO_K113_%E6%84%9B%E6%92%AB%E7%B3%BB%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89.ERB) | ✅ 已修复 | chs 行 1372 `LOCAL:1 = 0` → `1 ;custom code`（@M_KOJO_総合スレ７４９_MESSAGE_COM_K113_12_1 初めて块，函數名帶前綴）|
| 提交 2 F29 | K119 Nemuno ENNemuno Hypnosis_KOJO | ❌ chs 缺失 | `119 Nemuno/ENNemuno/Hypnosis_KOJO.ERB` 在 chs 中不存在；chs 仅有 `賑やかしネムノ趣味版`（子分支不兼容）|
| 提交 2 F30 | K119 Nemuno ENNemuno events | ❌ chs 缺失 | `M_KOJO_K119_events.ERB` 在 chs 中不存在 |
| 提交 2 F31 | K119 Nemuno ENNemuno service_commands | ❌ chs 缺失 | `service_commands.ERB` 在 chs 中不存在 |
| 提交 2 F32 | K120 Aunn 阿吽海外版 イベント | ⏭️ 无需修复 | chs 行 391 "他キャラと约会道中に遭遇" 已是 `LOCAL:1 = 1` |
| 提交 2 F33 | K120 Aunn 阿吽海外版 弾幕 | ⏭️ 无需修复 | chs 行 24 "戦闘前" 已是 `LOCAL:1 = 1`（anon-tw 用 `ARGS == "戦闘前"`，chs 用 `ARGS == OPR_战斗前` 常量）|
| 提交 2 F34 | [K121 Narumi 賑やかし成美 弾幕](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/121%20Narumi%20[%E6%88%90%E7%BE%8E]/%E8%B3%83%E3%82%84%E3%81%8B%E3%81%97%E6%88%90%E7%BE%8E%E3%80%90121%E3%80%91/M_KOJO_K121_%E5%BC%BE%E5%B9%95%E5%8B%9D%E8%B2%AC.ERB) | ✅ 已修复 | chs 行 14 `LOCAL = 0` → `LOCAL = 1 ;custom code`（文件首部签到式 guard）|
| 提交 2 F35 | [K124 Okina 賑やかし隠岐奈 イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/124%20Okina%20[%E9%9A%A0%E5%B2%AC%E5%A5%88]/%E8%B3%83%E3%82%84%E3%81%8B%E3%81%97%E9%9A%A0%E5%B2%AC%E5%A5%88%E3%80%90124%E3%80%91/M_KOJO_K124_%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88.ERB) | ✅ 已修复 | chs 行 568 `LOCAL:1 = 0` → `1`（"MASTER私室にTARGETが入ってきてる" 块）|
| 提交 2 F36 | [K131 Mayumi 磨弓 イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/131%20Mayumi%20[%E7%A3%A8%E5%BC%93]/%E7%A3%A8%E5%BC%93/M_KOJO_K131_%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88.ERB) | ✅ 已修复 | chs 行 3030 `LOCAL:1 = 0` → `1`（"通常回家" 块）|
| 提交 2 F37 | [K131 Mayumi 磨弓 弾幕](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/131%20Mayumi%20[%E7%A3%A8%E5%BC%93]/%E7%A3%A8%E5%BC%93/M_KOJO_K131_%E5%BC%BE%E5%B9%95%E5%8B%9D%E8%B2%AC.ERB) | ✅ 已修复 | chs 行 105/116 `LOCAL:1 = 0` → `1`（"残忍酷薄"/"乾坤一掷" 块，anon-tw 报告 3 hunks 但第 3 hunk @1297 chs 已被自行修复）|
| 提交 2 F38 | [K131 Mayumi 磨弓 愛撫系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/131%20Mayumi%20[%E7%A3%A8%E5%BC%93]/%E7%A3%A8%E5%BC%93/M_KOJO_K131_%E6%84%9B%E6%92%AB%E7%B3%BB%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89.ERB) | ✅ 已修复 | 2 hunks：行 1252（K131_11_1 "初めて"）和行 1632（K131_15_1 "初めて"），均 `LOCAL:1 = 0` → `1` |
| 提交 2 F39 | [K133 Saki 早鬼 イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/133%20Saki%20[%E6%97%A9%E9%AC%BC]/%E6%97%A9%E9%AC%BC/M_KOJO_K133_%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88.ERB) | ✅ 已修复 | chs 行 1633 `LOCAL:1 = 0` → `1`（"服を着る" 块）|
| 提交 2 F40 | [K139 Tsukasa 典 イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/139%20Tsukasa%20[%E5%85%B8]/%E5%85%B8/M_KOJO_K139_%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88.ERB) | ✅ 已修复 | 2 hunks：行 9728（脱衣口上 @M_KOJO_EVENT_K139_28 主 `LOCAL = 0` → `1`）和行 9776（CASE 3 "パンツちょうだい" `LOCAL:1 = 0` → `1`）|
| 提交 2 F41 | [K140 Megumu 龍 イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/140%20Megumu%20[%E9%BE%8D]/%E9%BE%8D/M_KOJO_K140_%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88.ERB) | ✅ 已修复 | chs 行 1284 `LOCAL:1 = 0` → `1`（"抱き着きモード満足終了" 块）|
| 提交 2 F42 | [K140 Megumu 龍 性交系](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/140%20Megumu%20[%E9%BE%8D]/%E9%BE%8D/M_KOJO_K140_%E6%80%A7%E4%BA%A4%E7%B3%BB%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89.ERB) | ✅ 已修复 | 3 hunks：行 668（主 `LOCAL = 0` → `1`）、行 676（"初めて" `LOCAL:1 = 0` → `1`）、行 691（"挿入継続" `LOCAL:1 = 0` → `1`），均在 @M_KOJO_POWERED_BY_DARKMAN_MESSAGE_COM_K140_66_1 函数 |
| 提交 2 F43 | [K142 Momoyo 日常](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/142%20Momoyo%20[%E7%99%BE%E3%80%87%E4%B8%96]/Momoyo/M_KOJO_K142_everyday_commmands.ERB) | ⏭️ 无需修复 | chs 行 1972 已经是 `LOCAL = 1` |
| 提交 2 F44 | [K151 YuugenMagan イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/151%20YuugenMagan%20[%E3%83%A6%E3%82%A6%E3%82%B2%E3%83%B3%E3%83%9E%E3%82%AC%E3%83%B3]/YuugenMagan/M_KOJO_K151_%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88.ERB) | ✅ 已修复（部分）| chs 行 853 `LOCAL:1 = 0` → `1`（"起こしに来たけど寝てる" 块）；@2833 思慕取得 chs 已经是 `LOCAL:1 = 1` |
| 提交 2 F45 | [K151 YuugenMagan 日常](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/151%20YuugenMagan%20[%E3%83%A6%E3%82%A6%E3%82%B2%E3%83%B3%E3%83%9E%E3%82%AC%E3%83%B3]/YuugenMagan/M_KOJO_K151_%E6%97%A5%E5%B8%B8%E7%B3%BB%E3%82%B3%E3%83%9E%E3%83%B3%E3%83%89.ERB) | ✅ 已修复 | chs 行 1304 `LOCAL = 0` → `LOCAL = 1 ;custom code`（@M_KOJO_MESSAGE_COM_K151_308_1 主 guard）|
| 提交 2 F46 | [K154 Enoko 慧ノ子 イベント](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/154%20Enoko%20[%E6%85%A7%E3%83%8E%E5%AD%90]/%E6%85%A7%E3%83%8E%E5%AD%90/M_KOJO_K154_%E3%82%A4%E3%83%99%E3%83%B3%E3%83%88.ERB) | ✅ 已修复（部分）| 2 hunks：行 1181（"诶嘿嘿==2（开始时）" `LOCAL:1 = 0` → `1`）、行 1793（"拒绝了" `LOCAL:1 = 0` → `1`）；@126 主 `LOCAL = 0` chs 已经是 `LOCAL = 1` |
| 提交 2 F27 | [K101 Tokiko 朱鷺子 絶頂](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/101%20Tokiko%20[%E6%9C%B1%E9%B7%B2%E5%AD%90]/%E6%9C%B1%E9%B7%B2%E5%AD%90/M_KOJO_K101_%E7%B5%B6%E9%A0%82%20.ERB) | ✅ 已修复 | chs 行 28 `LOCAL = 0` → `LOCAL = 1 ;custom code`（"射精" 块 `IF LOCAL && NOWEX:射精` 入口）|
| 提交 2 F08 | K38 Koishi `Koishi_strmesko/M_KOJO_K38_1_イベント.ERB` | ❌ chs 缺失 | anon-tw 整个 `Koishi_strmesko/` 子目录在 chs 中不存在（46 hunks 无法应用）|
| 提交 2 F09 | K38 Koishi `Koishi_strmesko/M_KOJO_K38_1_日常系コマンド.ERB` | ❌ chs 缺失 | 同 F08 原因（8 hunks 无法应用）|

### 进行中

无（**44 个已决 + 6 chs 缺失 = 全部 46 个子任务均有结论**，调查完成）

### 待办（优先级排序）

1. **剩余路径映射**（中优）
   - F29-F31（119 Nemuno ENNemuno 子分支是否存在 — 已确认 chs 缺失）
2. （**全部 46 个子任务均已有结论**：F08/F09 → ❌ chs 缺失；F27 → ✅ 已修复；调查完成）

## 本轮会话总结（2026-06-19 第 1 批）

### 完成清单

- **F01**（015 Sakuya 奉仕系）— 解包 `LOCAL:1` 守卫，1 hunk
- **F02**（018 Lily W 性交系）— chs 已自行修复，无需操作
- **F03**（018 Lily W 愛撫系）— 2 hunks：转换 `IF→ELSEIF` + 删除多余 `ENDIF`
- **F05**（027 Wriggle イベント）— 大 hunk：删除 Reimu/Ruukoto 子分支 + 新增 Yamame 分支
- **F06**（027 Wriggle 愛撫系）— chs 已正确，无需操作
- **F07**（027 Wriggle リグル イベント）— `LOCAL:1 = 0` → `1`

### 路径映射发现

- **015 Sakuya**：anon-tw `Sakuya/` 目录在 chs 中不存在，对应 chs `TW咲夜逆輸入版/` 目录
- **018 Lily W**：anon-tw `リリーＷ口上测试版v1.01/` 在 chs 中是 `莉莉白口上测试版v1.01(23.1.25)/`（多了日期后缀）
- **027 Wriggle**：anon-tw 有 `Wriggle/` 和 `リグル/` 两个目录；chs 只有 `リグル/`，且 anon-tw 的 `M_KOJO_K27_1_*.ERB` 对应 chs 的 `M_KOJO_K27_*.ERB`（缺 `_1_` 前缀）

## 本轮会话总结（2026-06-19 第 2 批）

### 完成清单

- **F10**（038 Koishi TW用古明地こいし イベント）— chs 行 1620 已经是 `LOCAL:1 = 1`，无需操作
- **F11**（039 Nazrin ひねくれナズー口上 愛撫系）— chs 行 432 `LOCAL:1 = 0` → `1 ;custom code`（@M_KOJO_MESSAGE_COM_K39_2_1 初めて块）
- **F12**（042 Hatate はたて イベント）— 3 hunks：行 7015/7060/7071 三处 `LOCAL:1 = 0` → `1 ;custom code`（陥落素質あり自慰中毒高点位的 Ｃ敏感/Ｂ敏感/部位指定無し）
- **F13**（050 Flandre 芙兰朵露海外版 events）— 2 hunks：行 3270 `LOCAL = 0` → `1`（脱衣口上 @K50_28 函数入口）；行 3330 `LOCAL:1` 原本已正确
- **F14**（050 Flandre 芙兰朵露海外版 性騷扰）— chs 行 235 已经是 `LOCAL = 1`，无需操作
- **F15**（050 Flandre eraTW別人版 性交系）— chs 行 888 `LOCAL:1 = 0` → `1 ;custom code`（@M_KOJO_ふらん_MESSAGE_COM_K50_67_1 対面座位初めて块）
- **F16**（053 Tewi コマンド）— chs 行 354 解包 `LOCAL:1` 守卫：`IF LOCAL:1 && FIRSTTIME(SELECTCOM)` → `IF FIRSTTIME(SELECTCOM)`（@M_KOJO_MESSAGE_COM_K53_124_1 给对方手淫）
- **F17**（053 Tewi イベント）— chs 行 1764 已经是 `LOCAL:1 = 1`，无需操作
- **F18**（055 Byakuren 聖 愛撫系）— chs 行 1361 `LOCAL:1 = 0` → `1 ;custom code`（@M_KOJO_MESSAGE_COM_K55_20_1 接吻初めて块）
- **F19**（060 Parsee 性交系）— 4 hunks：行 1427/1434/1767/1774 四处 `LOCAL/LOCAL:1 = 0` → `1`（@M_KOJO_EGG_MESSAGE_COM_K60_64_1 騎乗位 + @K60_66_1 騎乗位肛門）

### 路径映射发现

- **050 Flandre**：anon-tw `egg/` 子目录在 chs 中对应 `芙兰朵露海外版/`（F13/F14）；anon-tw `eraTW別人版/` 在 chs 中是 `eraTW別人版フラン口上/`（F15）
- **053 Tewi**：anon-tw 文件名 `commands.ERB` / `events.ERB` 在 chs 中为 `コマンド.ERB` / `イベント.ERB`（F16/F17）
- **060 Parsee**：anon-tw 文件名 `M_KOJO_K60_性交系コマンド.ERB` 在 chs 中是 `M_KOJO_K60_2_性交系コマンド.ERB`（带 `_2_` 前缀）；函数名也带 `EGG_` 前缀（`@M_KOJO_EGG_MESSAGE_COM_K60_64_1` 而非 `@M_KOJO_MESSAGE_COM_K60_64_1`）

## 接手指引（下次会话从这里开始）

### 1. 阅读三份持久化文档

- [diff-record.md](file:///d:/emuera/shared-trae/knowledge/eratw/changelog/diff-record.md) — 46 个子任务状态表
- [workflow-manual.md](file:///d:/emuera/shared-trae/knowledge/eratw/changelog/workflow-manual.md) — 操作手册
- [anon-tw-port-review.md](file:///d:/emuera/shared-trae/knowledge/eratw/changelog/anon-tw-port-review.md) — 会话间交接记录

### 2. 推荐起点

从 **F01 015 Sakuya** 开始（最简单，单 hunk）。流程：
1. 读 [commit_0cc1d02f_full.txt](file:///d:/emuera/shared-trae/knowledge/eratw/changelog/commit_0cc1d02f_full.txt) 中 F01 的 hunk
2. 在 chs 中找 [M_KOJO_K15_奉仕系コマンド.ERB](file:///d:/eratw-chs/ERB/口上・メッセージ関連/個人口上/015 Sakuya [咲夜]/Sakuya/M_KOJO_K15_奉仕系コマンド.ERB)
3. 检查 @@ -247 处的 `IF LOCAL:1 && FIRSTTIME(SELECTCOM)`
4. chs 中此位置是 `IF LOCAL:1 && FIRSTTIME(SELECTCOM)` 还是 `IF FIRSTTIME(SELECTCOM)`？
5. 若 chs = anon-tw 修复前，则采用修复
6. 更新 [diff-record.md](file:///d:/emuera/shared-trae/knowledge/eratw/changelog/diff-record.md) F01 条目

### 3. 关键决策

- **不在 chs 中盲目替换 `LOCAL = 0` → `LOCAL = 1`**
- **按 46 文件分批调查，每次 1-3 个**
- **路径映射问题优先解决**

## 关键文件位置

### chs 仓库根目录
`d:\eratw-chs`

### anon-tw 仓库根目录
`d:\anon-tw`

### 持久化制品根目录
`d:\emuera\shared-trae\knowledge\eratw\changelog\`

| 文件 | 用途 |
|------|------|
| `commit_88376c65_danmaku_fix.txt` | 提交 1 diff |
| `commit_0cc1d02f_full.txt` | 提交 2 完整 diff（44KB） |
| `commit_0cc1d02f_hunk_summary.md` | 46 文件 hunk 索引 |
| `commit_0cc1d02f_filelist.txt` | 46 文件路径 |
| `commit_0cc1d02f_filemapping.txt` | anon-tw↔chs 路径映射报告 |
| `diff-record.md` | **46 子任务状态表（本次会话主文档）** |
| `workflow-manual.md` | **操作手册** |
| `anon-tw-port-review.md` | 会话间交接 |

## 注意事项

1. **不要备份 chs 文件**：用户明确说"不要这样改动"。直接修改即可。
2. **不要批量替换**：每个 hunk 都是独立任务。
3. **不要跑 Emuera**：GUI 应用，需手动验证。
4. **遵守项目规则**：ERB 脚本语法、变量命名、API 验证流程等。
5. **遵守会话结束检查**：结束前必须更新 diff-record.md 和 handoff。

## 阻塞项

无技术阻塞。剩余 42 个文件审查是**人力密集型**工作。

## 本轮会话总结（2026-06-19 第 3 批）

### 完成清单

- **F20**（K69 Mamizou 派生口上 イベント_拡張）— 3 hunks：行 1128 `LOCAL = 0` → `1`、行 1146 `LOCAL:1 = 0` → `1`、行 1222/1228 `LOCAL:1 = 0` → `1`（@M_KOJO_イベント_K69_1 関数の逢瀬終了/事後描写/精液が垂れてきた块）
- **F21**（K69 Mamizou 派生口上 絶頂_拡張）— chs 行 834 `LOCAL = 0` → `LOCAL = 1 ;custom code`（@M_KOJO_絶頂_K69_1 函数内"手淫フェラ"块）
- **F22**（K71 Shinmyoumaru 性交系）— ❌ chs 缺失：`M_KOJO_K71_性交系コマンド.ERB` 不存在；@M_KOJO_MESSAGE_COM_K71_79（正常位）也未在 `M_KOJO_K71_コマンド.ERB` 中实现
- **F23**（K72 Eirin 永琳 イベント）— 2 hunks：行 5380（事后の情绪 + ARG:1 == 3）、行 5417（服を着る + ARG:1 == 4），均为 `LOCAL:1 = 0` → `LOCAL:1 = 1 ;custom code`
- **F24**（K91 Tojiko 賑やかし屠自古 イベント）— 1 hunk：行 853 `LOCAL:1 = 0` → `LOCAL:1 = 1 ;custom code`（抜け出した 块，IF LOCAL:1 && !ARG:1）
- **F25**（K93 Wakasagihime 若鹭姬南风天 事件系）— ⏭️ 无需修复：chs 中完全没有 `LOCAL = 0` 或 `LOCAL:1 = 0`

### 路径映射发现

- **071 Shinmyoumaru**：anon-tw 有 `性交系コマンド/愛撫系/自慰系` 等多个文件，chs 仅有合并版 `コマンド.ERB` + `COUNTER.ERB` + `イベント.ERB` + `自慰系(あなた)コマンド.ERB`（性交系全部缺失，故 F22 chs 缺失）
- **093 Wakasagihime**：anon-tw `ENWaggy/M_KOJO_K93_events.ERB` 在 chs 中对应 `若鹭姬南风天/M_KOJO_K93_2_事件系.ERB`（中文版译者在汉化时已全部启用，无需修复）

### 进度更新

| 之前 | 之后 |
|------|------|
| 16 已修复 | 16 已修复 |
| 7 无需修复 | 8 无需修复 |
| 0 chs 缺失 | 1 chs 缺失 |
| 23 待处理 | 21 待处理 |

> 注：本轮新增 F22（chs 缺失）、F23/F24（已修复）、F25（无需修复）。F20/F21 在上轮已完成但 diff-record 未同步，本轮先同步状态。

## 本轮会话总结（2026-06-19 第 4 批）

### 完成清单

- **F28**（113 Hecatia 愛撫系）— chs 行 1372 `LOCAL:1 = 0` → `1 ;custom code`（@M_KOJO_総合スレ７４９_MESSAGE_COM_K113_12_1 初めて块）
- **F29**（119 Nemuno ENNemuno Hypnosis_KOJO）— ❌ chs 缺失
- **F30**（119 Nemuno ENNemuno events）— ❌ chs 缺失
- **F31**（119 Nemuno ENNemuno service_commands）— ❌ chs 缺失
- **F32**（120 Aunn 阿吽海外版 イベント）— ⏭️ 无需修复
- **F33**（120 Aunn 阿吽海外版 弾幕）— ⏭️ 无需修复
- **F34**（121 Narumi 賑やかし成美 弾幕）— chs 行 14 `LOCAL = 0` → `LOCAL = 1 ;custom code`
- **F35**（124 Okina 賑やかし隠岐奈 イベント）— chs 行 568 `LOCAL:1 = 0` → `1`（"MASTER私室にTARGETが入ってきてる" 块）
- **F36**（131 Mayumi 磨弓 イベント）— chs 行 3030 `LOCAL:1 = 0` → `1`（"通常回家" 块）
- **F37**（131 Mayumi 磨弓 弾幕）— chs 行 105/116 `LOCAL:1 = 0` → `1`（"残忍酷薄"/"乾坤一掷" 块）
- **F38**（131 Mayumi 磨弓 愛撫系）— 2 hunks：行 1252（K131_11_1）和行 1632（K131_15_1）
- **F39**（133 Saki 早鬼 イベント）— chs 行 1633 `LOCAL:1 = 0` → `1`（"服を着る" 块）
- **F40**（139 Tsukasa 典 イベント）— 2 hunks：行 9728（主 `LOCAL`）和行 9776（"パンツちょうだい"）
- **F41**（140 Megumu 龍 イベント）— chs 行 1284 `LOCAL:1 = 0` → `1`（"抱き着きモード満足終了" 块）
- **F42**（140 Megumu 龍 性交系）— 3 hunks @ @M_KOJO_POWERED_BY_DARKMAN_MESSAGE_COM_K140_66_1
- **F43**（142 Momoyo 日常）— ⏭️ 无需修复（chs 已是 `LOCAL = 1`）
- **F44**（151 YuugenMagan イベント）— chs 行 853 `LOCAL:1 = 0` → `1`（"起こしに来たけど寝てる" 块；@2833 思慕取得 chs 已正确）
- **F45**（151 YuugenMagan 日常）— chs 行 1304 `LOCAL = 0` → `LOCAL = 1 ;custom code`（@M_KOJO_MESSAGE_COM_K151_308_1 主 guard）
- **F46**（154 Enoko 慧ノ子 イベント）— 2 hunks：行 1181（"诶嘿嘿==2"）和行 1793（"拒绝了"）；@126 主 guard chs 已正确

### 路径映射发现

- **119 Nemuno**：anon-tw `ENNemuno/` 子目录（英译版）在 chs 中不存在；chs 仅有 `賑やかしネムノ趣味版`（子分支命名体系不兼容），3 个文件全部 chs 缺失
- **120 Aunn**：anon-tw `AunnJP/` 子目录在 chs 中不存在；chs 仅有 `阿吽海外版`（结构一致但已全部自行修复）

### 进度更新

| 之前 | 之后 |
|------|------|
| 25 已修复 | 35 已修复 |
| 8 无需修复 | 10 无需修复 |
| 1 chs 缺失 | 4 chs 缺失（+3 Nemuno 文件）|
| 12 待处理 | 7 待处理 |

> **本轮（F08/F09）确认结果**：anon-tw 整个 `038 Koishi [こいし]/Koishi_strmesko/` 子目录（> 6000 行 46 hunks + 8 hunks 日常系）在 chs 中**完全不存在**（`Glob` 验证 0 命中 `M_KOJO_K38_1_*`）。chs 中 038 Koishi 仅含三个不同子目录（`ERATW用古明地恋口上《想起之途》2020 11 11/`、`TW用古明地こいし/`、`古明地恋_试制口上v0.053/`），内容树完全不兼容。F08/F09 与 F29-F31（ENNemuno）、F22（K71 性交系）归为同类——**❌ chs 缺失**。F27（K101 絶頂）仍需逐处对照 diff。

### 剩余待办（全部完成）

| 子任务 | 备注 |
|--------|------|
| F08 | K38 Koishi str 46 hunk → ❌ chs 缺失（Koishi_strmesko 整个子目录不存在） |
| F09 | K38 str 日常 8 hunk → ❌ chs 缺失（同 F08 原因） |
| F22 | K71 性交系 → ❌ chs 缺失（`M_KOJO_K71_性交系コマンド.ERB` 不存在） |
| F27 | K101 絶頂 → ✅ 已修复（行 28 射精块 `LOCAL = 0` → `1 ;custom code`）|
| ~~第 4 批 F28-F46~~ | ✅ 已完成 |
| ~~路径映射 F29-F35~~ | ✅ 已完成（Nemuno/Aunn/賑やかし子分支全部确认）|

**全部 46 个子任务均已得出最终结论**：
- 30 ✅ 已修复
- 10 ⏭️ 无需修复
- 6 ❌ chs 缺失
- 0 ⏳ 待处理
