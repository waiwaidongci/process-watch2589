# 青砧涂层过程观察席 · PROCESS WATCH

冻结一段独立的工艺参考数据，用 I/MR 和 EWMA 观察后续膜厚；在说明稳定性、正态近似前提后计算 Cp/Cpk，再把调查交给负责人复核。

## 业务背景

模拟客户青砧精密涂层组有16位工艺与质量分析员。原流程把每10分钟一次的膜厚复制到表格，拿18–22μm规格线当控制线，漂移发现迟，并在过程失稳时仍引用能力指数。上游是按测量流、时间序号记录的涂层样本；本应用替代冻结参考、控制图计算、调查和复核环节；下游是工艺质量会议，不自动控制生产设备。

| 角色 | 权限 | 典型动作 |
|---|---|---|
| admin / 质量负责人 | 所有阅读、创建、调查、审批；修改来源备注 | 复核记录并批准导出 |
| analyst / 工艺分析师 | 阅读、冻结基线、创建运行、提交调查；无法审批或改来源备注 | 解释信号、提出复查动作 |
| viewer / 工艺观察员 | 所有页面只读；仅获批运行可导出 | 阅读结果和批准记录 |

所有角色导出前均须有同一运行的获批调查记录。批准代表允许研究证据归档，不代表产品合格或过程能力保证。

## 启动

```bash
cp .env.example .env
docker compose up -d --build
docker compose ps
docker compose exec -T backend python -m scripts.seed_demo
```

[前端](http://localhost:18210)，[接口文档](http://localhost:19210/docs)。前端调用`/api/`，Nginx去掉该前缀代理到FastAPI；直接访问后端不加`/api`。

| 账号 | 密码 | 角色 |
|---|---|---|
| admin@qingzhen.demo | Qingzhen2026! | admin |
| analyst@qingzhen.demo | Qingzhen2026! | analyst |
| viewer@qingzhen.demo | Qingzhen2026! | viewer |

恰好5服务：frontend / backend / worker / db / redis，全部有健康检查与依赖。数据库和Redis分别使用命名卷，backend/worker共享artifacts卷；worker阻塞轮询Redis并每2秒写心跳。后端初次通过ORM metadata建表；`migrations/001_initial.sql`是索引迁移示例，结构升级需自行审查迁移。

## 数据与一天的剧本

`qt-coating-202611.csv`为固定种子生成的960条合成膜厚：T-01稳定示例(seed605)、T-02低位示例(seed502)、T-03后段漂移(seed802)、T-04较大波动(seed504)，每流240点。T-03第151点开始加0.85μm。每流预置前80点冻结基线，T-01和T-03已有真实计算的历史运行，T-01有批准研究档案。为清楚展示方法，演示随机种子专门选择了T-01无本工具越界和T-03前段无越界的样本；这不是对随机误报概率的验证。

seed以邮箱、stream.code、measurement.source_key、baseline.name及预置run.name作自然键，只补不存在的数据，不覆盖已经存在的来源备注或观测。`SEED_DEMO=true`启动自动执行；失败记录日志不阻塞服务。

1. 09:00 沈微以analyst登录，核对T-03的240个时间序号与外部规格18–22μm。
2. 09:05 查看前80点，创建“T-03夜班复核基线”；快照冻结原始点、均值、MR均值、σ估计和输入指纹。
3. 09:10 选择冻结基线，设λ=.2、L=3，创建“夜班涂层观察”。
4. worker只监测基线结束之后的160点，不把后段漂移反算进控制线。
5. 09:12 在I/MR/EWMA之间切换，确认控制界限与外部规格是两套线。
6. 检查首个触发位置、Cp/Cpk数值及“不可作能力结论”提示；正态性、自相关未检验。
7. 提交“后段均值偏移”调查，记录温控、量具和追加独立采样的复查动作。
8. 09:30 程砚以admin审阅，记录至少8字意见，批准或退回；重复审批409拒绝。
9. 顾远以viewer打开获批档案，下载160点CSV和每点信号/输入SHA256，不能修改研究。

## 算法和口径

- **I/MR**：基线均值μ，连续点绝对差的均值MRbar，σ̂=MRbar/1.128。I控制线μ±3σ̂，MR线[0,3.267×MRbar]；基线本身先做I/MR越界检查。监测首点MR与冻结基线最后一点比较，后续比较相邻监测点。仅使用单点越界规则，不包含全部Nelson/Western Electric规则。
- **EWMA**：以z₀=冻结基线μ起算，zₜ=λxₜ+(1−λ)zₜ₋₁；时间变化界限μ±Lσ̂√{λ/(2−λ)×[1−(1−λ)²ᵗ]}。λ∈(0,1]，L∈[1,5]，每个监测任务从t=1重新开始，未使用后续样本重估基线。
- **Cp/Cpk**：在后续监测段重新估计组内σ=MRbar_monitor/1.128，Cp=(USL−LSL)/(6σ)，Cpk=min(USL−均值,均值−LSL)/(3σ)。后续至少50个点。基线I/MR或后续I/MR/EWMA有任何信号时`interpretable=false`；数值保留用于复算，界面禁止解读为能力结论。正态近似、独立采样是未验证的假设，不输出良率承诺。
- 失败态：空/太少样本、重复序号、常量MR、非有限/非数值/过大测量值、非法λ/L、无效规格明确拒绝。API基线要求至少30点、最多190点且保留至少50个监测点。常量后续段无法估计能力σ，任务以failed及明确错误结束。
- 冻结基线保留原始快照；来源的基线段后续若改动，仍使用快照计算并标记baseline_source_changed。输入SHA256按测量时间序号稳定排序，包含所有来源点的自然键/序号/时间/值、完整基线快照、流的规格与标识、λ/L和方法版本。顺序倒置不改变结果，时间/数值等变化改变指纹。

公式参考：[NIST个体控制图](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc322.htm)、[NIST EWMA](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm)、[NIST过程能力](https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm)。本实现使用EWMA启动期的有限时间方差，并非只用稳态界限。

## 页面与工程

六页：观察总览、测量来源、基线与运行、信号与能力、调查与复核、操作留痕。五个业务实体MeasurementStream / Measurement / Baseline / ControlRun / Investigation分别有模型、schema、service、route、前端API/store与界面；User/Audit是横切实体。

| 部分 | 技术 |
|---|---|
| Backend | Python3.11 / FastAPI / SQLAlchemy / 标准库统计计算 |
| Frontend | React18 / TypeScript / Vite6.4.6 / Lucide |
| 数据 | PostgreSQL16 / Redis7 AOF |
| UI | 石墨工业记录纸、氧化红警戒线；IBM Plex Mono + Noto Sans SC |

```
backend/src/{models,schemas,services,controllers,routes,middlewares,utils,constants,config}
backend/src/{main.py,worker.py}
backend/scripts/seed_demo.py
backend/migrations/001_initial.sql
frontend/src/{api,stores,types,components,hooks,pages,router,utils,constants}
```

共享业务组件：RunSummary、ControlChart在首页/结果复用；StreamSelector在来源/配置复用。通用DataTable/Notice/StatusBadge、useProcessData/useAction和format独立。共享枚举位置：角色`backend/src/constants/roles.py`、运行`status.py`、复核`review.py`对应`frontend/src/constants/enums.ts`；运行与权限实际使用同名值。两中间件独立处理全局错误与登录限流；审计覆盖登录、来源备注、冻结、队列完成、调查和审批。JWT8小时、PBKDF2-SHA256密码、每次按数据库角色授权。

## 配置与开发

| 变量 | 默认 | 说明 |
|---|---|---|
| COMPOSE_PROJECT_NAME | process-watch | 名称隔离 |
| FRONTEND_PORT | 18210 | 前端 |
| BACKEND_PORT | 19210 | API |
| DB_PORT | 17710 | PostgreSQL宿主端口 |
| JWT_SECRET | local-process-watch-change-this-key | 本地演示值，部署前更换 |
| SEED_DEMO | true | 启动自动seed |

本地后端：安装requirements，设置DATABASE_URL/REDIS_URL，`cd backend && uvicorn src.main:app --reload`，另起`python -m src.worker`；前端`npm install && npm run dev`，为`/api`配置本地后端代理。标准启动以Compose为准。

```bash
docker compose down -v --remove-orphans
```

测试脚本、真实截图和TESTING在项目外`../../test-artifacts/gb-0006/`。源码不包含日志、测试报告或截图；`.env`、缓存和日志忽略提交。

## 已知边界

合成冻结数据，没有真实仪器接入或CSV上传。单worker不提供running任务自动恢复、事务outbox或多实例执行锁；崩溃需重新提交。登录限流为单进程内存级。未做正态性/自相关/测量系统分析、能力置信区间或多变量控制，任何审批都不控制设备。初次建表不是完整迁移链。Google Fonts不可用时回退字体。

## License

MIT，见LICENSE。
