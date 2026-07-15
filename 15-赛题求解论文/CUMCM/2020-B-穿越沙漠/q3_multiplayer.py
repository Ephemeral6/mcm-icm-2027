"""
Q3: n 名玩家的合作/拥挤外部性验证 + 小规模联合调度演示（示例参数）
======================================================================
第一部分：直接用题目给出的真实倍数公式，验证"扎堆(k>=2)弱劣于错峰(单独行动)"
的三条引理——这是我们选择"避免碰撞的联合调度"这一建模路线的数学依据，
而不是凭空套用博弈论模板。

第二部分：在一张 3 节点小地图 S-M(矿山)-E 上，对比"2人全程同步行动(扎堆)"
与"2人错峰1天行动(各自独享独行/独享矿山)"两种联合方案的实际最终资金，
用真实的（虽是示例参数下的）算术核验引理在具体场景下的效果幅度。

所有数值均为说明性示例，用于验证模型逻辑，不代表官方"第五关/第六关"真实数据。
"""

# ---------------------- 第一部分：三条"拥挤外部性"引理的数值验证 ----------------------
print("=== 引理验证：多人共享同一行动 是否 弱劣于 单独行动 ===\n")

print("[引理1] 同一天同一条边上共同行走的消耗倍数 = 2k； 单独行走 = 2（题目 3(3)条真实倍数）")
for k in range(1, 6):
    mult = 2 if k == 1 else 2 * k
    print(f"  k={k}: 消耗倍数={mult}" + ("  <- 单独行走（基准）" if k == 1 else f"  是单独行走的 {mult/2:.1f} 倍"))
print("  结论：k>=2 时 2k > 2，移动应尽量错峰，避免与他人同边同日同行。\n")

print("[引理2] 同一天同一矿山共同挖矿：消耗恒为3倍（与k无关），但人均收益 = 基础收益/k；单独挖矿收益=基础收益")
M0 = 80  # 示例基础收益（挖矿子场景专用参数，与前文Q1/Q2示例参数相互独立）
for k in range(1, 6):
    income = M0 if k == 1 else M0 / k
    print(f"  k={k}: 消耗倍数=3（不变）, 人均收益={income:.1f}" + ("  <- 单独挖矿（基准）" if k == 1 else ""))
print("  结论：消耗不变但收益被稀释，k>=2 时人均净收益严格低于单独挖矿；\n"
      "         唯一例外是地图上矿山数量少于希望挖矿的人数，此时共享矿山不可避免。\n")

print("[引理3] 同一天同一村庄共同购买：单独购买价格=2倍基准价；k>=2 时统一为4倍基准价（跳变，与具体k值无关）")
for k in range(1, 6):
    price_mult = 2 if k == 1 else 4
    print(f"  k={k}: 每箱价格={price_mult}x基准价")
print("  结论：只要有>=1名同伴同日同村购买，价格立即翻倍(2x->4x)，应尽量错峰采购。\n")


# ---------------------- 第二部分：3节点小地图上的联合调度对比 ----------------------
print("=" * 70)
print("=== 联合调度演示：3节点地图 S(0)--M(矿山,1)--E(终点,2)，2名玩家 ===\n")

R = 1          # 基础消耗量（水=食物=1箱/天）
P0 = 10        # 基准价格
FUNDS0 = 200   # 每名玩家初始资金（示例参数，与前文Q1/Q2示例相互独立）
MINE_INCOME_BASE = 80  # 基础收益（示例参数，刻意选取使"单独挖矿"净收益为正）


def solo_move_cost():
    return 2 * R  # 单独行走：2倍


def group_move_cost(k):
    return 2 * k * R if k >= 2 else 2 * R


def solo_mine():
    return 3 * R, MINE_INCOME_BASE  # (consumption, income)


def group_mine(k):
    income = MINE_INCOME_BASE if k == 1 else MINE_INCOME_BASE / k
    return 3 * R, income  # 消耗恒为3倍，与k无关


def stay_cost():
    return 1 * R


def evaluate_schedule(schedules):
    """schedules: list of per-player action lists，每个动作是
       ('move',) / ('mine',) / ('stay',)，长度可不同（玩家可提前结束）。
       在每个"日期槽"上，统计该日执行相同动作类型的人数 k，据此计算真实消耗/收益/价格。
       返回每位玩家的最终资金（假设资源随买随用、无冗余购买，仅用于对比总花费）。"""
    max_len = max(len(s) for s in schedules)
    n = len(schedules)
    total_boxes = [0] * n     # 累计消耗的箱数（水+食合计）
    total_income = [0.0] * n  # 累计挖矿收益

    for day in range(max_len):
        acts_today = [(i, schedules[i][day]) for i in range(n) if day < len(schedules[i])]
        movers = [i for i, a in acts_today if a == 'move']
        miners = [i for i, a in acts_today if a == 'mine']
        stayers = [i for i, a in acts_today if a == 'stay']

        k_move = len(movers)
        for i in movers:
            c = group_move_cost(k_move)
            total_boxes[i] += 2 * c  # c 是"倍数"，实际消耗=倍数*基础量(水+食物各R，合计2R)
        for i in stayers:
            total_boxes[i] += 2 * stay_cost()

        k_mine = len(miners)
        if k_mine >= 1:
            cons, inc = (solo_mine() if k_mine == 1 else group_mine(k_mine))
            for i in miners:
                total_boxes[i] += 2 * cons
                total_income[i] += inc

    final_funds = []
    for i in range(n):
        cost = total_boxes[i] * P0
        funds = FUNDS0 - cost + total_income[i]
        final_funds.append(funds)
    return final_funds, total_boxes, total_income


# 方案A：两人完全同步（扎堆）：day0 move(S->M), day1 mine, day2 move(M->E)
clustered = [
    ['move', 'mine', 'move'],
    ['move', 'mine', 'move'],
]
fundsA, boxesA, incomeA = evaluate_schedule(clustered)
print("方案A（扎堆：两人每天动作完全相同）")
for i, f in enumerate(fundsA):
    print(f"  玩家{i+1}: 消耗{boxesA[i]}箱, 挖矿收益{incomeA[i]:.1f}, 最终资金={f:.1f}")
print(f"  两人合计最终资金 = {sum(fundsA):.1f}\n")

# 方案B：错峰1天：玩家1立即出发；玩家2先stay一天再按相同路线走（全程避免与玩家1同日同动作）
staggered = [
    ['move', 'mine', 'move'],
    ['stay', 'move', 'mine', 'move'],
]
fundsB, boxesB, incomeB = evaluate_schedule(staggered)
print("方案B（错峰：玩家2延后1天出发，全程无碰撞）")
for i, f in enumerate(fundsB):
    print(f"  玩家{i+1}: 消耗{boxesB[i]}箱, 挖矿收益{incomeB[i]:.1f}, 最终资金={f:.1f}")
print(f"  两人合计最终资金 = {sum(fundsB):.1f}\n")

print(f"结论：错峰方案比扎堆方案，两人合计多保留资金 {sum(fundsB)-sum(fundsA):.1f} 元")
print("      （在本示例参数下，错峰仅比扎堆多用1天，却几乎是资金结果的数量级改善，")
print("       生动体现了'联合承诺阶段应优先安排错峰调度、把同场共用矿山/道路/村庄")
print("       作为地图结构强制不可避免时才接受的下策'这一策略结论。）\n")

# ---------------------- 第三部分：小规模穷举，确认错峰1天已是(近似)该地图上的最优解 ----------------------
print("=" * 70)
print("=== 穷举玩家2的出发延迟天数 (0~3天)，验证方案B（延迟1天）是否最优 ===\n")
best_delay, best_total = None, float('-inf')
for delay in range(0, 4):
    sched2 = ['stay'] * delay + ['move', 'mine', 'move']
    schedules = [['move', 'mine', 'move'], sched2]
    funds, boxes, income = evaluate_schedule(schedules)
    total = sum(funds)
    tag = "  <- 当前最优" if total > best_total else ""
    print(f"delay={delay}天: 玩家1={funds[0]:.1f}, 玩家2={funds[1]:.1f}, 合计={total:.1f}{tag}")
    if total > best_total:
        best_total, best_delay = total, delay
print(f"\n穷举结论：延迟 {best_delay} 天为该小场景下的合计资金最优解（合计={best_total:.1f}），"
      f"与方案B（延迟1天）一致，验证了'尽量错峰、避免不必要的同步扎堆'这一策略的有效性。")
