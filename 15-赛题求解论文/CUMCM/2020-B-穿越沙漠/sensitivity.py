"""
Q1 模型的敏感性分析：对负重上限 CAP、基准价格 P0、初始资金 FUNDS0、
截止天数、天气序列中的沙暴比例 等参数做扰动，观察最优得分的变化。
复用 q1_dp.py 中的地图与算法逻辑，仅将关键参数做成可传入的形式。
所有取值仍为示例数据。
"""
import copy

NODES = {0: "S", 1: "A", 2: "M", 3: "B", 4: "Vil", 5: "C", 6: "E"}
START, MINE, VILLAGE, END = 0, 2, 4, 6
EDGES = [(0, 1), (1, 2), (2, 5), (5, 6), (0, 3), (3, 4), (4, 6), (1, 3), (2, 4)]
ADJ = {n: set() for n in NODES}
for a, b in EDGES:
    ADJ[a].add(b); ADJ[b].add(a)

BASE_WEATHER = ['S', 'S', 'H', 'D', 'S', 'S', 'D', 'H', 'S', 'S']


def feasible_purchases(cap_left_funds, cap_left_weight, price):
    max_total = min(cap_left_weight, int(cap_left_funds // price) if price > 0 else cap_left_weight)
    for total in range(0, max_total + 1):
        for dw in range(0, total + 1):
            yield dw, total - dw


def run_q1_param(cap, p0, funds0, mine_income, weather, move_mult=2, mine_mult=3):
    p_vil, p_refund = 2 * p0, 0.5 * p0
    layer = {}
    for dw, df in feasible_purchases(funds0, cap, p0):
        cash = funds0 - p0 * (dw + df)
        key = (START, dw, df)
        if key not in layer or layer[key] < cash:
            layer[key] = cash

    best_final = None
    for t, q in enumerate(weather):
        next_layer = {}
        for (v, w, f), cash in layer.items():
            actions = []
            if w >= 1 and f >= 1:
                actions.append((v, w - 1, f - 1, cash))
            if v == MINE and w >= mine_mult and f >= mine_mult:
                actions.append((v, w - mine_mult, f - mine_mult, cash + mine_income))
            if q != 'D' and w >= move_mult and f >= move_mult:
                for u in ADJ[v]:
                    actions.append((u, w - move_mult, f - move_mult, cash))
            for v2, w2, f2, cash2 in actions:
                if v2 == END:
                    score = cash2 + p_refund * (w2 + f2)
                    if best_final is None or score > best_final:
                        best_final = score
                    continue
                if v2 == VILLAGE:
                    room = cap - (w2 + f2)
                    for dw, df in feasible_purchases(cash2, room, p_vil):
                        c3 = cash2 - p_vil * (dw + df)
                        key = (v2, w2 + dw, f2 + df)
                        if key not in next_layer or next_layer[key] < c3:
                            next_layer[key] = c3
                    key0 = (v2, w2, f2)
                    if key0 not in next_layer or next_layer[key0] < cash2:
                        next_layer[key0] = cash2
                else:
                    key = (v2, w2, f2)
                    if key not in next_layer or next_layer[key] < cash2:
                        next_layer[key] = cash2
        layer = next_layer
    return best_final


BASE = dict(cap=16, p0=10, funds0=200, mine_income=30, weather=BASE_WEATHER)

print("=== 基准情形 ===")
base_score = run_q1_param(**BASE)
print(f"CAP={BASE['cap']}, P0={BASE['p0']}, FUNDS0={BASE['funds0']}, MINE_INCOME={BASE['mine_income']}"
      f" -> 最优得分 = {base_score}")

print("\n=== 敏感性1：负重上限 CAP ===")
for cap in [8, 10, 12, 14, 16, 20, 24]:
    p = dict(BASE); p['cap'] = cap
    s = run_q1_param(**p)
    print(f"CAP={cap:3d} -> 最优得分={s}")

print("\n=== 敏感性2：基准价格 P0 ===")
for p0 in [5, 8, 10, 12, 15, 20]:
    p = dict(BASE); p['p0'] = p0
    s = run_q1_param(**p)
    print(f"P0={p0:3d} -> 最优得分={s}")

print("\n=== 敏感性3：初始资金 FUNDS0 ===")
for f0 in [80, 100, 120, 150, 200, 300]:
    p = dict(BASE); p['funds0'] = f0
    s = run_q1_param(**p)
    print(f"FUNDS0={f0:4d} -> 最优得分={s}")

print("\n=== 敏感性4：矿山基础收益 MINE_INCOME（其余不变，直接走最短路是否仍最优？）===")
for mi in [0, 20, 30, 50, 80, 120, 200]:
    p = dict(BASE); p['mine_income'] = mi
    s = run_q1_param(**p)
    print(f"MINE_INCOME={mi:4d} -> 最优得分={s}")

print("\n=== 敏感性5：天气序列中的沙暴比例（用不同的示例天气序列） ===")
weathers = {
    "无沙暴": ['S', 'S', 'H', 'S', 'S', 'S', 'H', 'H', 'S', 'S'],
    "基准(2个沙暴)": BASE_WEATHER,
    "较多沙暴(4个)": ['S', 'D', 'H', 'D', 'S', 'D', 'D', 'H', 'S', 'S'],
    "沙暴开局连续3天": ['D', 'D', 'D', 'S', 'S', 'S', 'H', 'S', 'S', 'S'],
}
for name, w in weathers.items():
    p = dict(BASE); p['weather'] = w
    s = run_q1_param(**p)
    print(f"{name:16s} -> 最优得分={s}")
