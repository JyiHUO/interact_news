#!/usr/bin/env python3
"""Build and publish weekly digest 2026-05-17 ~ 2026-05-24 to Feishu via OpenAPI direct."""
import json, os, sys, urllib.request, urllib.error, time

# --- Load Feishu credentials from .env ---
APP_ID, APP_SECRET = None, None
with open("/home/ubuntu/.hermes/.env") as f:
    for line in f:
        if line.startswith("FEISHU_APP_ID="):
            APP_ID = line.strip().split("=", 1)[1]
        elif line.startswith("FEISHU_APP_SECRET="):
            APP_SECRET = line.strip().split("=", 1)[1]
assert APP_ID and APP_SECRET

BASE = "https://open.feishu.cn"

def http(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code} {method} {path}: {body}", file=sys.stderr)
        raise

# --- Auth ---
auth = http("POST", "/open-apis/auth/v3/tenant_access_token/internal",
            {"app_id": APP_ID, "app_secret": APP_SECRET})
TOKEN = auth["tenant_access_token"]
print(f"[ok] got token", file=sys.stderr)

# --- Block builders for OpenAPI direct mode ---
def text_run(content, bold=False, italic=False):
    style = {}
    if bold: style["bold"] = True
    if italic: style["italic"] = True
    el = {"text_run": {"content": content}}
    if style:
        el["text_run"]["text_element_style"] = style
    return el

def text_block(content):
    return {"block_type": 2, "text": {"elements": [text_run(content)]}}

def text_mixed(parts):
    # parts: list of (content, bold) tuples
    return {"block_type": 2, "text": {"elements": [text_run(c, bold=b) for c, b in parts]}}

def heading2(content):
    return {"block_type": 4, "heading2": {"elements": [text_run(content)]}}

def heading3(content):
    return {"block_type": 5, "heading3": {"elements": [text_run(content)]}}

def bullet(content):
    return {"block_type": 12, "bullet": {"elements": [text_run(content)]}}

def bullet_mixed(parts):
    return {"block_type": 12, "bullet": {"elements": [text_run(c, bold=b) for c, b in parts]}}

def ordered(content):
    return {"block_type": 13, "ordered": {"elements": [text_run(content)]}}

def divider():
    return {"block_type": 22, "divider": {}}

# --- Compose blocks ---
blocks = []

# Header
blocks.append(text_mixed([
    ("📋 本周复盘 ", True),
    ("(2026-05-17 ~ 2026-05-24)", True),
]))
blocks.append(text_block("生成时间: 2026-05-24 20:00"))
blocks.append(divider())

# 一句话总结
blocks.append(heading2("🔑 一句话总结"))
blocks.append(text_block(
    "本周三条主线交织：AI 算力链从「芯片」二阶传导到「电力/HBM/光纤/小金属」并出现首个反智能反弹（开发者切回小模型）；美伊霍尔木兹危机+长端美债破 5%「市场已自加息」让宏观叙事从「AI 资本开支」切换到「利率与供给」；Hermes 自身完成自主进化系统 v0.1 设计、横评 7 个 self-evolving agent，并在用户「承诺即代码」的高标准下把北交所打新流程数字化到 80%。"
))
blocks.append(divider())

# 本周大事
blocks.append(heading2("📊 本周大事 (按影响力排序)"))
events = [
    ("AI 算力链「电力资产化」升级", "NextEra 670 亿美元收购 Dominion Energy（美史上最大电力并购），Coatue 提出「from chasing GPUs to chasing Gigawatts」，电力成为算力新瓶颈被资本市场实质定价。"),
    ("长端美债收益率破 5%「市场已自加息」", "30Y 美债冲 5%，美银调查 62% 基金经理预计破 6%，「二次通胀」成最大尾部风险；高盛交易台公开切换主导逻辑为「利率与供给压力」。"),
    ("AI 巨头 IPO 与资金循环跑通", "SpaceX 提 S-1 估值 2 万亿、Anthropic Q2 营收 109 亿首次盈利估值 9000 亿、OpenAI 或秘密递交、软银 400 亿银团贷款全押 OpenAI、马斯克诉 OpenAI 败诉清除上市障碍。"),
    ("美伊霍尔木兹海峡进入临界点", "参院 50:47 限战权 + 特朗普「两三天」通牒 → 三国(卡/沙/阿)请求暂缓 → 5/24 晚停火延 60 天；油价 Brent 在 109-120 区间剧烈摆动。"),
    ("国产存储双雄登陆资本市场临门一脚", "长鑫 5/27 IPO 上会拟募 295 亿、长江存储启动辅导；陈老师警示「上市点可能即半导体周期顶」（融资+扩产→打崩价格）。"),
    ("Karpathy 加入 Anthropic + agentic IDE 三足鼎立", "Karpathy 离职去 Anthropic、Mistral 收 Emmi、Codex 新版 + Antigravity 2.0 + Claude Plugins 官方目录三国杀。AI 编程漏洞发现速度首次超过人类修补速度（AIGC Weekly Y26W20）。"),
    ("Token 经济三层全打通", "无锡 Token 工厂 + 中电信 Token 套餐 + Manus 月烧 130 万美元 token = 上游产能/资费/消费三层闭环；运营商把 LLM 调用打包成话费账单。"),
    ("AI 替代白领进入实战 + 反智能反弹", "Meta 扎克伯格首次明确承认裁员与 AI 直接挂钩；同期 HN/华尔街见闻报道工程师切回 GPT-4o-mini —「更聪明=更慢/更贵/更幻觉」遭用户层反弹。"),
]
for i, (title, desc) in enumerate(events, 1):
    blocks.append(bullet_mixed([(f"{title} — ", True), (desc, False)]))
blocks.append(divider())

# 知识脉络演进
blocks.append(heading2("🧠 知识脉络演进"))

blocks.append(heading3("话题 A：AI 算力链二阶传导（持续主线）"))
blocks.append(bullet_mixed([("本周进展: ", True), ("芯片→存储/光纤/小金属/PCB/电力 配置链路全部坐实。具体节点：5/18 NextEra 670 亿购 Dominion；5/19 三星 HBM3E 92%/HBM4 75% 良率；5/20 三星罢工→DRAM/NAND 短期紧；5/21 伦锡 +6%、PCB/MLCC/ABF 链拆解；5/22 ARM +16% 存储概念领涨、光纤一年涨 6 倍。", False)]))
blocks.append(bullet_mixed([("因果推演: ", True), ("AI capex 不再只算 GPU 张数 → 算 Gigawatts、HBM 良率、铜锡焊料、PCB 层数、IDC 用电缺口。资金从「龙头」轮向「二阶 BOM」是必然，估值锚从 NVDA 收入扩到电网/小金属/HBM 三国杀。", False)]))
blocks.append(bullet_mixed([("我的判断: ", True), ("二阶传导仍在早期，但「反智能反弹」（开发者切回小模型）+「长鑫上市即周期顶」+ 长端利率压制是三个反向警报。本周内部分化（芯片股与软件股相关性首次跌破 0）已是早期信号。下周 5/27 长鑫上会 + Anthropic 9000 亿估值是估值锚的关键检验点。", False)]))

blocks.append(heading3("话题 B：宏观叙事切换 — 利率/供给压制 AI 资本开支"))
blocks.append(bullet_mixed([("本周进展: ", True), ("美 4 月 CPI 3.8%（2023/5 来新高）+ PPI +6%；30Y 美债破 5%；美银 62% 经理预计破 6%；高盛公开换叙事；霍尔木兹油价 95-120 摆动；Japan 10Y/20Y/30Y 同步破阶段高。", False)]))
blocks.append(bullet_mixed([("因果推演: ", True), ("能源通胀（伊朗）+ 财政供给（长债买家罢工）→ 长端利率上行 → AI 高估值股折现率提升 → 与 AI capex 叙事冲突。本周「不需要美联储表态、这已经是加息」是定价权切换的明确信号。", False)]))
blocks.append(bullet_mixed([("我的判断: ", True), ("AI 牛市后期典型组合：估值高+融资旺+供给上行+利率压制。陈老师「确定性 > 低价、降仓位而非加仓博反弹」框架本周得到主流验证。下周看霍尔木兹停火 60 天延期能否真兑现 + 长鑫上市定价。", False)]))

blocks.append(heading3("话题 C：Self-Evolving Agent 与 Hermes 自主进化"))
blocks.append(bullet_mixed([("本周进展: ", True), ("5/19 AHE 自进化论文 deep-research → 5/21 Hermes 进化系统 v0.1 设计稿（Q1-Q5 等用户拍板）→ 5/22 MOSS 论文重读+横评设计 → 5/23 7 个工作横评报告（MOSS/Voyager/Gödel/SEAL/DSPy/Darwin Gödel/SICA）。本次 dreaming 完成防截断 L1 patch。", False)]))
blocks.append(bullet_mixed([("因果推演: ", True), ("用户对 ad-hoc 答案不耐烦（5/22 北交所 4 轮纠正） + 主动 commission 横评 → 隐含要求 Hermes 像 MOSS 一样能「扫日志改 skill」。「承诺即代码」原则的本质就是这套。", False)]))
blocks.append(bullet_mixed([("我的判断: ", True), ("调研已充分，瓶颈在工程化路径选型。本地化路径「扫日志 + 外挂 CLI」已写进 dreaming 灵感库。Q1-Q5 拍板后预计 2 周内可落地最小可用版本。本周稳定性事故（周报 cron 连续 6 天 error）反过来证明：自检/自修循环是必需，不是可选。", False)]))

blocks.append(heading3("话题 D：北交所打新流程数字化"))
blocks.append(bullet_mixed([("本周进展: ", True), ("5/19 bse_apply_amount.py 落地（4 信号打分+区间预测）；5/20 新天力首日 +425% 中性预测；5/22 N朗信上市未提醒卖出 → 暴露「已申购未上市」追踪缺失；5/22-23 新睿电子 4 轮答疑（顶格资金/稳获 X 股/经验值 vs 计算值）。", False)]))
blocks.append(bullet_mixed([("因果推演: ", True), ("T-2 申购日历 ✓ → T-1 顶格资金/稳获测算 ✓ → T 日申购 ✓ → T+5 上市卖出提醒 ❌（断点）。流程 80% 数字化但最关键的退出环节缺失。", False)]))
blocks.append(bullet_mixed([("我的判断: ", True), ("下周必须补上 T+1/T+5 上市日历 + 卖出窗口。这不是「优化」是「漏环」—— N朗信事件已暴露代价。同时 stock-analysis skill 加「禁止纯参考值」硬约束，把用户「自己算 ≠ 经验值」标准固化进 skill。", False)]))

blocks.append(divider())

# 趋势观察
blocks.append(heading2("📈 趋势观察"))
trends = [
    ("持续", "AI 算力二阶传导（连续 2 周）— 走向：从「论点」走到资产负债表事件（NextEra 收购 / HBM 良率 / 罢工 / 伦锡）"),
    ("持续", "美伊霍尔木兹危机（连续 12 天）— 走向：5/24 晚停火延 60 天，从「打不打」转入「能不能真延」窗口"),
    ("持续", "北交所打新（连续 11 天用户系统化追问）— 走向：从「散点答疑」到「流程数字化」，缺退出环"),
    ("新兴", "长端利率重定价 +「反智能反弹」— 第一次出现 AI 叙事的反向力量，需高优追踪"),
    ("新兴", "Feed 利用率审计（5/23 用户主动 TODO）— 第一次用户系统性提「长期未做项」，是质量审视升级"),
    ("消退", "中东地缘油价单边上行叙事 — 已被「停火/制裁暂停」反向打破，进入双向波动"),
    ("拐点", "AI 巨头叙事从「大模型竞赛」转向「搜索/合规/Stack 整合」（Karpathy 跳槽 + Mistral 收购 + Google Search 改入口 + OpenAI 用 SynthID）"),
    ("拐点", "agentic IDE 三足鼎立成形（Codex / Antigravity / Claude Plugins）— 开发者工具链 2026 大重构正式启动"),
]
for tag, content in trends:
    blocks.append(bullet_mixed([(f"{tag}: ", True), (content, False)]))

blocks.append(divider())

# 本周洞察
blocks.append(heading2("💡 本周洞察"))
blocks.append(bullet_mixed([
    ("洞察 1：", True),
    ("AI 牛市后期的「自反性顶部信号」三件套同时出现 ——（a）龙头融资潮（SpaceX 2 万亿、OpenAI 秘密递表、长鑫上会）；（b）开发者层反智能反弹（切回 4o-mini）；（c）长端利率「市场已自加息」。这三件历史上从不孤立发生。这意味着 6 月份估值方向比方向判断更重要。", False),
]))
blocks.append(bullet_mixed([
    ("洞察 2：", True),
    ("「承诺即代码」是 Hermes 自主进化的真正起点，不是治理框架。用户对 ad-hoc 答案的零容忍（5/22 北交所 4 轮纠正）本质是要求 agent 像 MOSS 一样把每次回答的 ad-hoc 计算固化进流水线。Hermes 进化系统 v0.1 的核心 KPI 应该是「ad-hoc 计算→脚本化」的转化率，不是「skill 数量」。", False),
]))
blocks.append(bullet_mixed([
    ("洞察 3：", True),
    ("「长期跟踪信息但行动断点」是本周浮现的元问题。北交所「已申购未上市」（信息有但卖出未提醒）、Feed 利用率审计（抓但未用）、watchlist 上 ⏳卡死回显连续 4 天未做 —— 三件事是同构的。Hermes 的瓶颈不在「采集」也不在「分析」，而在「闭环触发」。下一步系统设计应优先解决触发器，而不是新增源。", False),
]))

blocks.append(divider())

# 下周关注
blocks.append(heading2("🎯 下周关注"))
focus = [
    ("5/27 (周二) 长鑫存储科创板 IPO 上会", "拟募 295 亿，国产存储龙头。陈老师警示「上市点可能即半导体周期顶」。具体看：发行价、超额认购倍数、上市首日涨幅。是半导体设备/存储仓位的关键减仓窗口。"),
    ("5/27 前后 OpenAI 秘密递表传闻验证", "若属实将是 AI 巨头 IPO 季的下一个引爆点；若证伪则需重估 Anthropic 9000 亿估值的合理性。"),
    ("霍尔木兹停火 60 天延期能否真兑现", "5/24 晚最新进展是延 60 天，但 WTI 仍跌 2% 反映市场不信任。下周看伊朗对 5/17 美方 5 项苛刻条件（25%资产解冻 vs 交出 400kg 浓缩铀）的回应窗口。"),
    ("北交所新睿电子(920211) 5/25 申购 + T+5 上市卖出提醒", "本周下周连续金融实操日；新睿首日预测 +280%~+450%（中性 +365%）。配套必须补上 T+5 上市日历提醒。"),
    ("30Y 美债是否再破阶段高 / 是否首次破 5.2%", "若再上行将进一步压制 AI 高估值股。同步看美方 5/29 PCE 数据（4 月数）。"),
    ("Hermes 自主进化系统 Q1-Q5 用户拍板", "等用户回 5/21 设计稿。一旦拍板启动 2 周内最小可用版本（本地化路径：扫日志 + 外挂 CLI）。"),
    ("Feed 利用率审计需启动", "5/23 用户主动 TODO，已加入 watchlist P0。需主对话 + 用户参与定义「用过」标准。"),
]
for title, desc in focus:
    blocks.append(bullet_mixed([(f"{title} — ", True), (desc, False)]))

blocks.append(divider())

# 自我优化记录
blocks.append(heading2("🔧 自我优化记录"))
blocks.append(heading3("本周改进"))
improvements = [
    "✅ weekly-digest skill 加「防截断硬约束」段（final response ≤ 800 字 + 数据脚本超时不全废 + block 数 ≤ 50/批分批写入）— 本次周报即首次验证（本应 5/17 起跑、连续 6 天 cron error）",
    "✅ 7 天 GitHub Trending 跨播报去重池上线（seen_github_repos.json，19 条记录）",
    "✅ bp-review cron 沙箱路径 bug 修复（5/22）",
    "✅ bse_apply_amount.py 落地（4 信号打分 + 顶格资金 + 稳获 X 股口径），北交所 skill v2.2→v2.3，串入 fetch_all.sh",
    "✅ 知识图谱 ~/knowledge_threads.md 重建（新环境/丢失状态后），追踪 6 条独立时间线 + 跨话题关联",
    "✅ user_signals.md / dreaming_log.md / watchlist.md / fetch_issues.md 全套脚手架重建",
    "✅ L0 修复 read_inbox.py 路径 fallback（cron 下 $HOME=.hermes/home 时找不到 feed_silo state.db）— 本次周报数据采集已验证",
]
for item in improvements:
    blocks.append(bullet(item))

blocks.append(heading3("效果指标"))
blocks.append(bullet_mixed([("覆盖度: ", True), ("用户主动 commission ≥ 6 次（self-evolving 横评、Feed 审计、周报缺失、北交所多轮、容器逃逸、CLI-Anything、MOCHA） — 良", False)]))
blocks.append(bullet_mixed([("质量: ", True), ("高频追问 + 多轮纠正（北交所 4 轮、self-evolving 二轮）— 良", False)]))
blocks.append(bullet_mixed([("噪音率: ", True), ("1 次明确不满（5/22 「应该是自己计算的啊」）— 1/30+ 互动可控", False)]))
blocks.append(bullet_mixed([("稳定性: ", True), ("⚠️ 风险点：周报 cron 连续 6 天 error 才修复 — 本周最弱环节", False)]))
blocks.append(bullet_mixed([("创新度: ", True), ("self-evolving agent 横评 + 容器逃逸调研 + Hermes 进化系统 v0.1 三份 deep-research 是亮点", False)]))

blocks.append(heading3("下周计划优化"))
blocks.append(bullet("1. 「已申购未上市」追踪清单（北交所 skill 加 T+1/T+5 上市日历 + 自动卖出提醒）— P0"))
blocks.append(bullet("2. stock-analysis skill 加「禁止纯参考值」硬约束（金融数字必须自己算 + 中性/乐观/悲观三档）— P1"))
blocks.append(bullet("3. ⏳ 卡死回显（feishu_comment 入口 prompt 加 90s follow-up 硬约束）— 已连续 4 天未动，必须本周对话窗口推进"))
blocks.append(bullet("4. Feed 利用率审计 — 等主对话 + 用户参与定义「用过」标准"))
blocks.append(bullet("5. 旧 dedup 文件清理（~/.hermes/state/repo_dedup_7d.json 已被 cron/state/seen_github_repos.json 替代）"))

blocks.append(divider())

# 本周产出文档索引
blocks.append(heading2("📚 本周产出文档索引"))
blocks.append(text_block("（来自 ~/broadcast_docs.md，2026-05-17 ~ 2026-05-24）"))

blocks.append(heading3("Deep Research / 调研类"))
blocks.append(bullet("Search API 生态调研 (5/18) — https://lwhssbxtkfpf.feishu.cn/docx/KWbndF3p6oh8fpx99cqc0DSanBb"))
blocks.append(bullet("（其他 deep-research 文档本周由主对话生成，未全部回写 broadcast_docs.md，包括：AHE 自进化论文调研 5/19、Hermes 进化系统 v0.1 设计 5/21、self-evolving agent 7 横评 5/23、MOSS 论文重读 5/22、容器逃逸调研 5/22。）"))

blocks.append(heading3("Daily News (本周完整 18 篇)"))
blocks.append(bullet("早间播报 5/17-5/24 共 7 篇 ｜ 午间 5/17 / 5/18 共 2 篇 ｜ 晚间 5/17-5/24 共 7 篇 ｜ 夜间补播 5/24 00:36"))
blocks.append(bullet("（具体 doc_id 见 ~/broadcast_docs.md，本段不展开避免文档膨胀）"))

blocks.append(heading3("BP-Review / Dreaming"))
blocks.append(bullet("dreaming 5/17 02:05 / 5/20 02:0X / 5/24 02:08 共 3 次"))
blocks.append(bullet("bp-review 5/18-5/23 共 6 次"))
blocks.append(bullet("cost-report 5/23 12:01 / 5/24 12:02"))

blocks.append(divider())
blocks.append(text_mixed([
    ("OKR 自检：", True),
    ("如果你读完追问/讨论 → 周报有价值；如果觉得「这个我早知道了」→ 洞察不够深，请评论指出；下周预判命中/全错 → 周日 dreaming 复盘推理链。", False),
]))

# --- Create document (no folder_token; falls to root) ---
print(f"[info] composing {len(blocks)} blocks", file=sys.stderr)
doc = http("POST", "/open-apis/docx/v1/documents",
           {"title": "📋 周报 05/17-05/24"}, token=TOKEN)
doc_id = doc["data"]["document"]["document_id"]
print(f"[ok] doc created: {doc_id}", file=sys.stderr)

# --- Write blocks in batches of 35 ---
BATCH = 35
for i in range(0, len(blocks), BATCH):
    chunk = blocks[i:i+BATCH]
    res = http("POST", f"/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
               {"children": chunk, "index": -1}, token=TOKEN)
    print(f"[ok] wrote batch {i//BATCH+1} ({len(chunk)} blocks)", file=sys.stderr)
    time.sleep(0.5)

# --- Set link share to tenant_readable ---
try:
    http("PATCH", f"/open-apis/drive/v1/permissions/{doc_id}/public?type=docx",
         {"link_share_entity": "tenant_readable"}, token=TOKEN)
    print(f"[ok] set tenant_readable", file=sys.stderr)
except Exception as e:
    print(f"[warn] permission set failed: {e}", file=sys.stderr)

URL = f"https://lwhssbxtkfpf.feishu.cn/docx/{doc_id}"
print(f"[done] {URL}")
print(doc_id)
