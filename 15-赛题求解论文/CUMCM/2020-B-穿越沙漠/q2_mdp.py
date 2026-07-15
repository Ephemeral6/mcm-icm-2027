"""
Q2: 单人游戏，玩家仅知道当天天气 —— 有限时域马尔可夫决策过程 (MDP)，逆向归纳
======================================================================
状态: (t, v, w, f, q_t)  —— 第t天开始时所在区域、持有资源、【当天已实现的天气】
值函数: G(t,v,w,f,q) = 从该状态出发、按最优策略行动，直到游戏结束为止，
        【未来净现金流（挖矿收益-购买支出）之和 + 终点退款】的最大期望值

与 Q1 的关系：Q1 是"上帝视角"（全程天气已知）的确定性最优解，是 Q2 在
"天气不确定性=0"极限下的特例，因此 Q1 的最优值应【严格不低于】用同一条
实际天气路径去驱动 Q2 策略所得到的结果——这是本脚本用来做正确性检验的
关键不等式（信息价值非负）。

简化假设（为控制示例计算规模，仅用于本演示脚本，论文正文的一般模型
仍保留资金作为状态变量）：假设初始资金足够充裕，购买行为不受资金硬约束，
只受负重上限约束。在本例参数下（满载一次性购买 16 箱 × 10 元 = 160 元 ≤
初始资金 200 元）该假设是成立的，构成对该假设适用性的一个自检。

天气转移矩阵为【示例数据】，非官方真实统计规律。
"""

import random
from functools import lru_cache

NODES = {0: "S(起点)", 1: "A", 2: "M(矿山)", 3: "B", 4: "Vil(村庄)", 5: "C", 6: "E(终点)"}
START, MINE, VILLAGE, END = 0, 2, 4, 6
EDGES = [(0, 1), (1, 2), (2, 5), (5, 6), (0, 3), (3, 4), (4, 6), (1, 3), (2, 4)]
ADJ = {n: set() for n in NODES}
for a, b in EDGES:
    ADJ[a].add(b); ADJ[b].add(a)

R_W, R_F = 1, 1
MOVE_MULT = 2
MINE_MULT = 3
MINE_INCOME = 30
CAP = 16
P0 = 10
P_VIL = 2 * P0
P_REFUND = 0.5 * P0
FUNDS0 = 200

HORIZON = 10          # 总可用天数 (t=0..HORIZON-1)，需在 HORIZON 天内到达终点
STATES_Q = ['S', 'H', 'D']
# 天气转移矩阵（示例数据）：TRANS[q][q'] = P(明天天气=q' | 今天天气=q)
TRANS = {
    'S': {'S': 0.6, 'H': 0.3, 'D': 0.1},
    'H': {'S': 0.3, 'H': 0.5, 'D': 0.2},
    'D': {'S': 0.4, 'H': 0.3, 'D': 0.3},
}
NEG_INF = float('-1e9')   # 仅作为 max() 归约的哨兵初值，不应作为叶子/边界的真实取值
# 游戏失败（超时或资源耗尽）的记分约定，写成"从失败点起、未来净流为负的一个有限值"：
# 第一版尝试 FAIL_VALUE=-1e9 导致期望值被小概率尾部事件压制成不可解读的巨大负数
#（哪怕失败概率仅 0.02%，期望值也被拖到 -86万，这是一次真实的数值陷阱，见思考过程记录）；
# 第二版尝试 FAIL_VALUE=0 又导致"起点不购买任何资源、当场判负"反而被判定为最优
#（因为不购买=不花钱=保留全部200元本金，且失败不再额外扣分），这是目标函数设计的漏洞，
# 说明"失败"必须严格劣于任何真实完成路径的得分，而不能是0。
# 最终采用：失败记为 -500（低于本例中任何可行的成功得分区间 [0,190]），
# 且量级远小于 1e9，不会让期望值被极小概率事件不成比例地支配。这是一个建模约定，
# 不是官方规则给出的数值。
FAIL_VALUE = -500.0


def all_wf():
    for w in range(CAP + 1):
        for f in range(CAP + 1 - w):
            yield w, f


def purchase_options(room):
    """假设资金充裕：只受负重上限约束，枚举 (dw,df)。"""
    for total in range(0, room + 1):
        for dw in range(0, total + 1):
            yield dw, total - dw


def solve_q2():
    # G[t]: dict{(v,w,f,q): value}
    G = [dict() for _ in range(HORIZON + 1)]
    # 终止边界：t=HORIZON 时若不在终点，视为失败
    for v in NODES:
        for w, f in all_wf():
            for q in STATES_Q:
                G[HORIZON][(v, w, f, q)] = FAIL_VALUE if v != END else 0.0  # 已在终点的状态不会在此产生新增流

    for t in range(HORIZON - 1, -1, -1):
        Gt = {}
        for v in NODES:
            for w, f in all_wf():
                for q in STATES_Q:
                    best = NEG_INF
                    # 停留不挖矿
                    if w >= R_W and f >= R_F:
                        best = max(best, _continue(t, v, w - R_W, f - R_F, 0.0, q, G))
                    # 停留挖矿
                    if v == MINE and w >= MINE_MULT * R_W and f >= MINE_MULT * R_F:
                        best = max(best, _continue(t, v, w - MINE_MULT * R_W, f - MINE_MULT * R_F, MINE_INCOME, q, G))
                    # 移动（非沙暴日）
                    if q != 'D' and w >= MOVE_MULT * R_W and f >= MOVE_MULT * R_F:
                        for u in ADJ[v]:
                            best = max(best, _continue(t, u, w - MOVE_MULT * R_W, f - MOVE_MULT * R_F, 0.0, q, G))
                    if best == NEG_INF:
                        best = FAIL_VALUE  # 当天无任何可行动作（资源耗尽），按失败记 0 分
                    Gt[(v, w, f, q)] = best
        G[t] = Gt
    return G


def _continue(t, v2, w2, f2, flow, q, G):
    """给定当天行动后落点 v2、剩余资源 w2,f2、本日净现金流 flow，
    计算该分支的（含未来期望值的）总收益。"""
    if v2 == END:
        return flow + P_REFUND * (w2 + f2)
    if t + 1 > HORIZON:
        return FAIL_VALUE  # 超过截止日期仍未到达终点：失败
    if v2 == VILLAGE:
        room = CAP - (w2 + f2)
        best = NEG_INF
        for dw, df in purchase_options(room):
            cost = P_VIL * (dw + df)
            cont = _expected_next(t + 1, v2, w2 + dw, f2 + df, q, G)
            best = max(best, flow - cost + cont)
        return best
    else:
        return flow + _expected_next(t + 1, v2, w2, f2, q, G)


def _expected_next(t1, v, w, f, q, G):
    if t1 > HORIZON:
        return FAIL_VALUE if v != END else 0.0
    if t1 == HORIZON:
        return G[HORIZON][(v, w, f, 'S')]  # 边界值与 q 无关
    return sum(p * G[t1][(v, w, f, q2)] for q2, p in TRANS[q].items())


def best_start_purchase(G, q0):
    best_val, best_wf = NEG_INF, None
    for dw, df in purchase_options(CAP):
        cost = P0 * (dw + df)
        if cost > FUNDS0:
            continue
        val = FUNDS0 - cost + G[0].get((START, dw, df, q0), NEG_INF)
        if val > best_val:
            best_val, best_wf = val, (dw, df)
    return best_val, best_wf


def simulate_policy(G, weather_path, w0, f0):
    """用逆向归纳得到的最优策略，在给定的一条【已实现天气路径】上前向模拟，
    返回实际得到的最终得分（用于与 Q1 的"上帝视角"最优解做比较）。"""
    v, w, f = START, w0, f0
    cash = FUNDS0 - P0 * (w0 + f0)
    for t, q in enumerate(weather_path):
        if t >= HORIZON:
            return None, "超出预设时域"
        if v == END:
            return cash, "已到达"
        candidates = []
        if w >= R_W and f >= R_F:
            candidates.append(('stay', v, w - R_W, f - R_F, 0.0))
        if v == MINE and w >= MINE_MULT * R_W and f >= MINE_MULT * R_F:
            candidates.append(('mine', v, w - MINE_MULT * R_W, f - MINE_MULT * R_F, MINE_INCOME))
        if q != 'D' and w >= MOVE_MULT * R_W and f >= MOVE_MULT * R_F:
            for u in ADJ[v]:
                candidates.append(('move', u, w - MOVE_MULT * R_W, f - MOVE_MULT * R_F, 0.0))
        if not candidates:
            return None, f"day{t}: 无可行动作，游戏失败"

        best_c, best_score = None, NEG_INF
        for name, v2, w2, f2, flow in candidates:
            score = _continue(t, v2, w2, f2, flow, q, G)
            if score > best_score:
                best_score, best_c = score, (name, v2, w2, f2, flow)
        name, v2, w2, f2, flow = best_c
        cash += flow
        v, w, f = v2, w2, f2

        if v == VILLAGE:
            room = CAP - (w + f)
            best_p, best_val = (0, 0), NEG_INF
            for dw, df in purchase_options(room):
                cost = P_VIL * (dw + df)
                cont = _expected_next(t + 1, v, w + dw, f + df, q, G)
                val = -cost + cont
                if val > best_val:
                    best_val, best_p = val, (dw, df)
            dw, df = best_p
            cash -= P_VIL * (dw + df)
            w, f = w + dw, f + df

        if v == END:
            refund = P_REFUND * (w + f)
            return cash + refund, f"day{t+1} 到达终点"
    return None, "天气路径耗尽仍未到达终点"


if __name__ == "__main__":
    print("求解 Q2 逆向归纳 MDP（示例参数，天气转移矩阵为示例数据）...")
    G = solve_q2()

    print("\n=== 检验 1：期望意义下的最优得分（对天气分布取期望） ===")
    for q0 in STATES_Q:
        val, wf = best_start_purchase(G, q0)
        print(f"若第0天天气={q0}: 起点最优购买(水,食)={wf}, 期望最终得分={val:.2f}")

    print("\n=== 检验 2：信息价值非负性检验 ===")
    print("用 Q1 中同一条确定性天气路径驱动 Q2 的（仅知当天）策略，")
    print("并与 Q1 的全知最优解 80.0 比较，验证 Q2结果 <= Q1结果。")
    weather_path_q1 = ['S', 'S', 'H', 'D', 'S', 'S', 'D', 'H', 'S', 'S']
    q0 = weather_path_q1[0]
    val0, wf0 = best_start_purchase(G, q0)
    dw0, df0 = wf0
    score, info = simulate_policy(G, weather_path_q1, dw0, df0)
    print(f"起点购买: 水={dw0},食={df0}；实际路径下最终得分={score}；({info})")
    print(f"Q1(全知)最优解 = 80.0； Q2(仅知当天)在同一天气路径下 = {score}")
    print("=> " + ("通过：Q2 <= Q1，符合信息价值非负" if (score is not None and score <= 80.0 + 1e-6) else "异常：需检查模型"))

    print("\n=== 检验 3：蒙特卡洛模拟，估计 Q2 策略的样本期望得分 ===")
    random.seed(42)
    q0_fix = 'S'
    val0, wf0 = best_start_purchase(G, q0_fix)
    dw0, df0 = wf0
    scores = []
    fails = 0
    N_MC = 20000
    for _ in range(N_MC):
        path = [q0_fix]
        for _ in range(HORIZON - 1):
            q_prev = path[-1]
            r = random.random()
            cum = 0.0
            for q2, p in TRANS[q_prev].items():
                cum += p
                if r <= cum:
                    path.append(q2)
                    break
        s, info = simulate_policy(G, path, dw0, df0)
        if s is None:
            fails += 1
            scores.append(FAIL_VALUE)  # 与理论期望值口径一致：失败按 FAIL_VALUE 计入总体均值
        else:
            scores.append(s)
    succ_scores = [s for s in scores if s != FAIL_VALUE]
    print(f"蒙特卡洛 {N_MC} 次抽样（初始天气={q0_fix}）：成功 {len(succ_scores)} 次，失败 {fails} 次")
    if succ_scores:
        print(f"仅成功样本均值={sum(succ_scores)/len(succ_scores):.2f}（不含失败惩罚，口径与理论值不同，仅供参考）")
    overall_mean = sum(scores) / len(scores)
    print(f"全样本均值（含失败记 FAIL_VALUE={FAIL_VALUE:.0f}）={overall_mean:.2f}，"
          f"与逆向归纳理论期望值 {val0:.2f} 比较，相对误差 {abs(overall_mean-val0)/abs(val0)*100:.2f}%")
