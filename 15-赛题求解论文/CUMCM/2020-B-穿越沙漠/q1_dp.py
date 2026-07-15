"""
Q1: 单人游戏，全程天气已知 —— 确定性动态规划（正向、"资金坍缩"技巧）
======================================================================
状态: (t, v, w, f)  —— 第 t 天开始时所在区域 v、持有水 w 箱、食物 f 箱
值函数: J(t,v,w,f) = 到达该状态时，历史上能达到的【最大现金】
        （由"状态占优"引理保证：同一 (t,v,w,f) 下现金越多严格不劣，
         故只需保留每个物理状态下现金最大的那条历史，无需枚举全部现金水平）

本脚本使用的地图、天气序列、价格、消耗量等全部是【示例数据】，
用于验证模型与算法的正确性，不代表官方"第一关/第二关"的真实数据
（官方附件缺失，无法获得真实地图与关卡参数）。
"""

import itertools
import json

# ---------------------- 示例地图（说明性数据） ----------------------
# 节点: 0=起点S, 1=A, 2=矿山M, 3=B, 4=村庄Vil, 5=C, 6=终点E
NODES = {0: "S(起点)", 1: "A", 2: "M(矿山)", 3: "B", 4: "Vil(村庄)", 5: "C", 6: "E(终点)"}
START, MINE, VILLAGE, END = 0, 2, 4, 6

EDGES = [(0, 1), (1, 2), (2, 5), (5, 6), (0, 3), (3, 4), (4, 6), (1, 3), (2, 4)]
ADJ = {n: set() for n in NODES}
for a, b in EDGES:
    ADJ[a].add(b)
    ADJ[b].add(a)

# ---------------------- 示例参数（说明性数据，非官方真实数值） ----------------------
R_W, R_F = 1, 1          # 基础消耗量：水1箱/天，食物1箱/天
MOVE_MULT = 2             # 行走消耗 = 基础消耗量的 2 倍（题目给定的真实倍数）
MINE_MULT = 3             # 挖矿消耗 = 基础消耗量的 3 倍（题目给定的真实倍数）
MINE_INCOME = 30          # 基础收益（示例数值）
CAP = 16                  # 负重上限 L（箱，水+食物之和）（示例数值）
P0 = 10                   # 起点基准价格（元/箱）（示例数值）
P_VIL = 2 * P0            # 村庄价格 = 基准价格的 2 倍（题目给定）
P_REFUND = 0.5 * P0       # 终点退回价格 = 基准价格的一半（题目给定）
FUNDS0 = 200              # 初始资金（示例数值）

# 天气序列（示例数据，长度=可用天数），'S'=晴朗,'H'=高温,'D'=沙暴（沙暴日强制停留）
WEATHER = ['S', 'S', 'H', 'D', 'S', 'S', 'D', 'H', 'S', 'S']
DEADLINE = len(WEATHER) - 1  # 行动日索引 0..DEADLINE 共 len(WEATHER) 天可用；
                              # 第 t 天行动后到达 t+1，故允许的到达日范围是 1..len(WEATHER)


def feasible_purchases(cap_left_funds, cap_left_weight, price):
    """给定可用资金与剩余负重，枚举 (dw, df) 的所有可行购买组合。"""
    max_total = min(cap_left_weight, cap_left_funds // price if price > 0 else cap_left_weight)
    for total in range(0, max_total + 1):
        for dw in range(0, total + 1):
            df = total - dw
            yield dw, df


def run_q1():
    # layer: dict{(v,w,f): max_cash}
    # 第0天：先在起点购买（起点购买必须先于当天消耗，否则 0 箱水食物无法生存）
    layer0 = {}
    for dw, df in feasible_purchases(FUNDS0, CAP, P0):
        cash = FUNDS0 - P0 * (dw + df)
        key = (START, dw, df)
        if key not in layer0 or layer0[key] < cash:
            layer0[key] = cash

    layer = layer0
    best_final = None  # (day, cash+refund, v,w,f,cash)
    history_best_actions = []  # 记录每天状态数用于留痕

    trace = []
    for t in range(0, DEADLINE + 1):
        q = WEATHER[t]
        trace.append((t, q, len(layer)))
        next_layer = {}
        for (v, w, f), cash in layer.items():
            actions = []
            # 停留不挖矿
            cw, cf = R_W, R_F
            if w >= cw and f >= cf:
                actions.append((v, w - cw, f - cf, cash, 0))
            # 停留挖矿（仅矿山，且沙暴日也可挖矿）
            if v == MINE:
                cw3, cf3 = MINE_MULT * R_W, MINE_MULT * R_F
                if w >= cw3 and f >= cf3:
                    actions.append((v, w - cw3, f - cf3, cash + MINE_INCOME, 0))
            # 移动（非沙暴日）
            if q != 'D':
                cw2, cf2 = MOVE_MULT * R_W, MOVE_MULT * R_F
                if w >= cw2 and f >= cf2:
                    for u in ADJ[v]:
                        actions.append((u, w - cw2, f - cf2, cash, 0))

            for (v2, w2, f2, cash2, _) in actions:
                # 到达终点：立即结算退款并结束游戏
                if v2 == END:
                    score = cash2 + P_REFUND * (w2 + f2)
                    if best_final is None or score > best_final[1]:
                        best_final = (t + 1, score, v2, w2, f2, cash2)
                    continue  # 终点是吸收态，不再进入 next_layer 继续游戏
                # 村庄购买（当天消耗结算完毕后，若在村庄可购买供以后使用）
                if v2 == VILLAGE:
                    best_here = cash2
                    best_wf = (w2, f2)
                    room = CAP - (w2 + f2)
                    for dw, df in feasible_purchases(cash2, room, P_VIL):
                        c3 = cash2 - P_VIL * (dw + df)
                        # 购买不会让 cash 变大，只是为未来囤货；此处仍需记录该 (w2+dw,f2+df) 状态
                        key = (v2, w2 + dw, f2 + df)
                        if key not in next_layer or next_layer[key] < c3:
                            next_layer[key] = c3
                    # 不购买也是一种合法选择
                    key0 = (v2, w2, f2)
                    if key0 not in next_layer or next_layer[key0] < cash2:
                        next_layer[key0] = cash2
                else:
                    key = (v2, w2, f2)
                    if key not in next_layer or next_layer[key] < cash2:
                        next_layer[key] = cash2
        layer = next_layer

    return best_final, trace


if __name__ == "__main__":
    best_final, trace = run_q1()
    print("=== Q1 天数-状态数 轨迹 ===")
    for t, q, n in trace:
        print(f"day={t:2d} weather={q} reachable_states={n}")
    print()
    if best_final is None:
        print("无可行方案：在给定天数内无法到达终点（示例参数下）")
    else:
        day, score, v, w, f, cash = best_final
        print(f"=== 最优解 (示例数据) ===")
        print(f"到达终点日期: day {day} （可用天数共 {len(WEATHER)} 天，允许到达日 1..{len(WEATHER)}）")
        print(f"最终得分(现金+退款): {score:.1f}")
        print(f"到达时现金: {cash:.1f}, 剩余水: {w}, 剩余食物: {f}, 退款: {P_REFUND*(w+f):.1f}")

    # ---- 压力测试：把可用天数收紧到 2 天，验证"无可行方案"分支能正确触发 ----
    saved_weather, saved_deadline = WEATHER, DEADLINE
    WEATHER = ['S', 'S']
    DEADLINE = len(WEATHER) - 1
    bf2, _ = run_q1()
    print()
    print("=== 压力测试：仅给 2 天（地图最短路径需 3 天）===")
    print("结果:", "无可行方案（符合预期，因最短路径需3天）" if bf2 is None else f"意外找到解 {bf2}")
    WEATHER, DEADLINE = saved_weather, saved_deadline
