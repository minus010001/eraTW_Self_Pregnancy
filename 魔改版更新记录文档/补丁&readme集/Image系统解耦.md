# Image 系统解耦项目

> Feature 介绍 · 开发日志 · 源码索引

## Feature 介绍

### 问题

ADDCOPYCHARA（妄想自慰等场景）后，部分存档中角色立绘不显示。根因：复制角色运行时 ID 与 NO 不同，组装式立绘用运行时 ID 构造函数名/精灵名，导致函数查找失败。

### 解决方案

采用 α+γ 组合方案，分四个阶段实施 Image 系统的"逻辑角色"与"视觉角色"解耦：

- **Phase 1（α：对齐上游签名）**：GET_BASE_RESOURCE 增加 VIS_C 参数，与 eratohotw 的 SPRITE_CHARA 对齐
- **Phase 2（γ：构建层双参数）**：SPIRIT/EagloV_GET_BASE_RESOURCE 增加 TARGET_CHARA 参数，构建层内部状态查询改用 TARGET_CHARA
- **Phase 3（NO 修复收尾）**：SPIRIT_GET_BASE_RESOURCE 中 `{CHARA}` → `{NO:CHARA}` 全量修复
- **Phase 4（拼接图系统全函数解耦）**：EagloV/SPIRIT 内部函数 VIS_C + TARGET_CHARA 双参数分离

### 核心设计

```
参数语义：
  VIS_C = 视觉角色（资源索引用，函数名后缀/sprite名）
  TARGET_CHARA = 实际角色（状态查询用，默认=VIS_C）
  NO:VIS_C = CSV编号（函数名/sprite名构造）

TARGET_CHARA 默认值 = -1 → 自动回退为 VIS_C，旧调用无需修改，零回归风险
```

### 三版解耦架构对比

| 维度 | eratohotw（dry新方案） | anon-tw（_TRANS旧方案） | eratw-chs（VIS_C方案） |
|------|----------------------|----------------------|----------------------|
| **解耦方式** | SPRITE_CHARA 单参数 | _TRANS 函数族双参数 | QOL 层 VIS_C + 构建层 TARGET_CHARA |
| **核心入口** | `GET_BASE_RESOURCE(CHARA, ..., SPRITE_CHARA=-1)` | `GET_BASE_RESOURCE(CHARA)` + `_TRANS(CHARA, CHARATRANS)` | `QOL_GET_BASE_RESOURCE(CHARA, ..., VIS_C=-1)` |
| **构建层双参数** | ❌ 只传 SPRITE_CHARA | ❌ 只传 CHARATRANS | ✅ VIS_C + TARGET_CHARA |
| **IMAGE_CHARA_OVERRIDE** | 有，5参数含 TARGET_CHARA | 无，直接 CALLFORM | 有，5参数含 TARGET_CHARA |

### 已完成解耦的系统

- **COMPOSE_SPRITE 系统**（リソース作成.ERB）：资源索引已全部使用 `NO:CHARA`，无需修改
- **CALC_EXPRESSION_CORE 表情路由**：已有 VIS_C 参数且内部正确分离
- **IMAGE_CHARA_DISPATCH / IMAGE_KOJO_OVERRIDE**：签名已有 CHARA + TARGET_CHARA 双参数分离

### 遗留项

- CFLAG:{NO}:差し替え適用 硬编码问题（~996处/100文件，方案D数据暂存已作为临时方案）
- IMAGE_CHARA_OVERRIDE B类调用点（10处）补全 TARGET_CHARA 参数（非必要）

## 开发日志

### Phase 1：对齐上游签名 ✅

- GET_BASE_RESOURCE 增加 VIS_C 参数
- 与 eratohotw 的 SPRITE_CHARA 对齐

### Phase 2：构建层双参数 ✅

- SPIRIT/EagloV_GET_BASE_RESOURCE 增加 TARGET_CHARA 参数
- 构建层内部 CHECK_NUDE/妊肚判定/IMAGE_CHARA_OVERRIDE 改用 TARGET_CHARA
- QOL_GET_BASE_RESOURCE 调用构建层时传 TARGET_CHARA = CHARA

### Phase 3：NO 修复收尾 ✅

- GRAPH系.ERB(61处)、EagloV_ImgFunc.ERB(290处)、STAND_COM_IMAGE.ERB(7处) 中 `{CHARA}` → `{NO:CHARA}`

### Phase 4：拼接图系统全函数解耦 ✅

**分类 A（仅资源索引，~40个函数）**：CHARA 仅用于 `NO:CHARA` 拼 SPRITE 名，已重命名 CHARA→VIS_C。
- SPIRIT：BUILD_BASE_IMAGE/颜像生成/全图索引/体图索引/表情索引 等 ~20个
- EagloV：BUILD_BASE_IMAGE/颜像生成/全图索引/体图索引/表情索引/BUILD_差分 等 ~20个

**分类 B（两者兼有，~20个函数）**：CHARA 同时用于状态查询和资源索引，已增加 TARGET_CHARA 参数。
- 核心差分：`EagloV_GET_EFFECT_RESOURCE`（最复杂）、`EagloV_GET_左断/右断/精胃差分`、`EagloV_GET_吐息/面红/颊红/泪/目黑线/心眼/丁液/气泡差分`
- Bug 修复：`EagloV2_GET_BASE_RESOURCE`/`EagloV2_GET_EFFECT_RESOURCE` 已添加 TARGET_CHARA
- 角色专属：`EagloV_特殊效果_{N}`(~15个)、`EagloV_特殊表情_{N}`(~5个) 已添加 VIS_C + TARGET_CHARA

**分类 E（残留清理，2026-06-03）**：
- `EagloV_BUILD_BASE_IMAGE` / `EagloV2_BUILD_BASE_IMAGE`：删除未使用的 `#DIM TARGET_CHARA` 残留声明
- `EagloV_ImgChara.ERB` 全64个角色函数：统一签名 `(VIS_C, TARGET_CHARA = -1)` + 初始化逻辑
- `EagloV_表情判定`：签名添加 VIS_C 参数，TRYCALLFORM 后缀改用 `NO:VIS_C`，状态查询改用 TARGET_CHARA
- `EagloV2_BUILD_下着体差分`：签名添加 TARGET_CHARA
- `GET_EFFECT_RESOURCE`：`CFLAG:VIS_C:通用拟声词`/`NOWEX:VIS_C`/`PALAM:VIS_C`/`CSTR:VIS_C` 全部改为 CHARA（逻辑角色状态）
- `SPIRIT_GET_FACETYPE`：修复 CALC_EXPRESSION_CORE 调用方未正确传递 TARGET_CHARA/VIS_C

**差し替え適用归属回退**（2026-06-03）：
- 初始审计中错误地将 `CFLAG:VIS_C:差し替え適用` 改为 `CFLAG:CHARA:`/`CFLAG:TARGET_CHARA:`
- 与上游 eratohotw 的 `CFLAG:SPRITE_CHARA:差し替え適用` 语义冲突
- 已回退：差し替え適用是视觉角色属性（你看到的是视觉角色的脸，差分替换也作用于视觉角色的脸）

### 分支策略

```
develop
  └── feat/image-decouple
        ├── Phase 1: 对齐上游签名 ✅
        ├── Phase 2: 构建层双参数 ✅
        ├── Phase 3: NO修复收尾 ✅
        └── Phase 4: 拼接图系统全函数解耦 ✅
```

## 源码文件索引

| 文件 | 角色 | 修改内容 |
|------|------|---------|
| `ERB/ステータス表示関連/IMAGE.ERB` | 逻辑层+默认路径 | GET_BASE_RESOURCE 增加 VIS_C；GET_BASESTYLE/GET_EFFECT_RESOURCE 解耦 |
| `ERB/魔改内容/QOL_IMAGE.ERB` | 路由层 | QOL_GET_BASE_RESOURCE 传 TARGET_CHARA；BUILD_CHARA_IMAGE_BLOCK 解耦 |
| `ERB/魔改内容/GRAPH系.ERB` | SPIRIT 构建层 | SPIRIT_GET_BASE_RESOURCE 增加 TARGET_CHARA；内部函数 VIS_C 重命名；{NO:CHARA} 修复 |
| `ERB/ステータス表示関連/EagloV/EagloV_ImgFunc.ERB` | EagloV 构建层 | EagloV_GET_BASE_RESOURCE 增加 TARGET_CHARA；内部函数 VIS_C+TARGET_CHARA 解耦 |
| `ERB/ステータス表示関連/EagloV/EagloV_ImgChara.ERB` | EagloV 角色专属函数 | 64个函数统一签名 (VIS_C, TARGET_CHARA=-1) |
| `ERB/魔改内容/GRAPH系_ImgChara.ERB` | SPIRIT 路由函数 | SPECIAL_BASE_IMAGE/SPIRIT_Version 函数 |
| `ERB/口上・メッセージ関連/STAND_COM_IMAGE.ERB` | COM 立绘 | {NO:CHARA} 修复 |
| `ERB/魔改内容/qol/qol_graph_watchers.ERB` | QoL 图形监听 | 解耦适配 |
| `ERB/魔改内容/qol/qol_脱衣.ERB` | QoL 脱衣 | 解耦适配 |

## 知识库参考

详细的技术分析（三版对比、变量全链路、CFLAG归属分析、COMPOSE_SPRITE/CALC_EXPRESSION_CORE/DISPATCH解耦分析）已归档至知识库：
- [portrait-clothing-workflow.md](file:///d:/emuera/shared-trae/knowledge/eratw/portrait-clothing-workflow.md) — Image系统三层架构、角色ID体系、三版变身解耦对比、Phase1-4完整记录、CFLAG归属分析
- [portrait-diff-query.md](file:///d:/emuera/shared-trae/knowledge/eratw/portrait-diff-query.md) — 立绘差分查询系统、TCVAR:EVENT_CLOTHING_SET 全链路
