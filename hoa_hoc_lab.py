#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""⚗ HÓA HỌC LAB - game học & giải bài toán Hóa học (tkinter, không cần cài thêm gì).
Chạy:  python hoa_hoc_lab.py
4 chế độ: Phòng thí nghiệm (hữu cơ, ẩn số, bài toán nhiều bước) | Cân bằng phương trình | Bài toán mol & phản ứng | Tính pH
"""
import tkinter as tk, random, re, math, itertools
from math import gcd, log10
from functools import reduce, lru_cache
from fractions import Fraction

W, H = 900, 680
LW, LH = 1120, 720          # kích thước mặc định (sẽ tính lại khi mở fullscreen)
BG, PANEL, ACC, OK, BAD, GOLD = '#0b1020', '#161d38', '#2dd4bf', '#34d399', '#fb7185', '#fbbf24'
AM = {'H': 1, 'C': 12, 'N': 14, 'O': 16, 'F': 19, 'Na': 23, 'Mg': 24, 'Al': 27, 'P': 31, 'S': 32, 'Cl': 35.5,
      'K': 39, 'Ca': 40, 'Mn': 55, 'Fe': 56, 'Cu': 64, 'Zn': 65, 'Br': 80, 'Ag': 108, 'I': 127, 'Ba': 137, 'Pb': 207}
COL = {'H': '#e8f1ff', 'C': '#6b7280', 'N': '#4d7cff', 'O': '#ff4d5e', 'F': '#a3e635', 'Na': '#b36bff',
       'Mg': '#3fd17a', 'Al': '#c0c8d4', 'P': '#ff9f43', 'S': '#ffd23f', 'Cl': '#6cf06c', 'K': '#d88cff',
       'Ca': '#ffa06a', 'Mn': '#c084fc', 'Fe': '#c8742c', 'Cu': '#e08a4a', 'Zn': '#7fa6c9', 'Br': '#c2410c',
       'Ag': '#e5e7eb', 'I': '#a855f7', 'Ba': '#84cc16', 'Pb': '#6b7280'}
SUB = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')


def sub(f): return f.translate(SUB)
def F(s, b=True): return ("Helvetica", s, "bold" if b else "normal")
def g(x): return f"{x:.2f}".rstrip('0').rstrip('.')


def mix(a, b, t):
    A = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; B = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02x%02x%02x' % tuple(int(A[i] * t + B[i] * (1 - t)) for i in range(3))


def parse(f):
    """'Al2(SO4)3' -> {'Al':2,'S':3,'O':12}"""
    st, i = [{}], 0
    while i < len(f):
        if f[i] == '(':
            st.append({}); i += 1
        elif f[i] == ')':
            i += 1; m = re.match(r'\d+', f[i:]); n = int(m.group()) if m else 1
            i += len(m.group()) if m else 0
            for k, v in st.pop().items(): st[-1][k] = st[-1].get(k, 0) + v * n
        else:
            m = re.match(r'([A-Z][a-z]?)(\d*)', f[i:]); i += len(m.group())
            st[-1][m.group(1)] = st[-1].get(m.group(1), 0) + int(m.group(2) or 1)
    return st[0]


def mass(f): return sum(AM[e] * n for e, n in parse(f).items())


EQS = [(["H2", "O2"], ["H2O"]), (["Fe", "O2"], ["Fe3O4"]), (["Al", "HCl"], ["AlCl3", "H2"]),
       (["C2H6", "O2"], ["CO2", "H2O"]), (["Fe2O3", "CO"], ["Fe", "CO2"]), (["Al", "O2"], ["Al2O3"]),
       (["Ca(OH)2", "HCl"], ["CaCl2", "H2O"]), (["C3H8", "O2"], ["CO2", "H2O"]),
       (["Na", "H2O"], ["NaOH", "H2"]), (["Al2(SO4)3", "NaOH"], ["Al(OH)3", "Na2SO4"]),
       (["KClO3"], ["KCl", "O2"]), (["Fe(OH)3"], ["Fe2O3", "H2O"]),
       (["N2", "H2"], ["NH3"]), (["P", "O2"], ["P2O5"]), (["FeS2", "O2"], ["Fe2O3", "SO2"]),
       (["Al", "Fe2O3"], ["Al2O3", "Fe"]), (["MnO2", "HCl"], ["MnCl2", "Cl2", "H2O"]),
       (["Cu", "HNO3"], ["Cu(NO3)2", "NO", "H2O"]), (["Fe", "H2SO4"], ["Fe2(SO4)3", "SO2", "H2O"]),
       (["NH3", "O2"], ["NO", "H2O"]), (["KMnO4"], ["K2MnO4", "MnO2", "O2"]),
       (["FeO", "HNO3"], ["Fe(NO3)3", "NO2", "H2O"]), (["Fe3O4", "HNO3"], ["Fe(NO3)3", "NO", "H2O"])]
RX = [([("Mg", 1), ("HCl", 2)], [("MgCl2", 1), ("H2", 1)]),
      ([("Zn", 1), ("HCl", 2)], [("ZnCl2", 1), ("H2", 1)]),
      ([("Fe", 1), ("HCl", 2)], [("FeCl2", 1), ("H2", 1)]),
      ([("Al", 2), ("HCl", 6)], [("AlCl3", 2), ("H2", 3)]),
      ([("CaCO3", 1), ("HCl", 2)], [("CaCl2", 1), ("H2O", 1), ("CO2", 1)]),
      ([("Na", 2), ("H2O", 2)], [("NaOH", 2), ("H2", 1)])]
GAS = ("H2", "CO2")


def counts(items, co=None):
    t = {}
    for i, (f, c) in enumerate(items):
        for e, n in parse(f).items(): t[e] = t.get(e, 0) + n * (co[i] if co else c)
    return t


def solve_eq(eq):
    sp = eq[0] + eq[1]; k = len(eq[0]); best = None
    for co in itertools.product(range(1, 9), repeat=len(sp)):
        if reduce(gcd, co) != 1: continue
        l = counts([(f, 1) for f in eq[0]], co[:k]); r = counts([(f, 1) for f in eq[1]], co[k:])
        if l == r and (best is None or sum(co) < sum(best)): best = co
    return best


def eqstr(items):
    return " + ".join(f"{c if c > 1 else ''}{sub(f)}" for f, c in items)


# ---------------- Bộ sinh bài toán ----------------
def q_mol():
    t = random.choice('nmVc')
    if t in 'nm':
        f = random.choice(["H2O", "NaCl", "CaCO3", "H2SO4", "NaOH", "CO2", "Fe2O3", "Al2(SO4)3", "Mg(OH)2"])
        M = mass(f); n = random.choice([0.1, 0.2, 0.25, 0.5, 1, 1.5, 2, 3]); m = round(n * M, 2)
        if t == 'n':
            return dict(text=f"Tính số mol của {g(m)} gam {sub(f)}.", ans=n, unit="mol",
                        steps=[f"M({sub(f)}) = {g(M)} g/mol", f"n = m / M = {g(m)} / {g(M)} = {g(n)} mol"])
        return dict(text=f"Tính khối lượng của {g(n)} mol {sub(f)}.", ans=m, unit="gam",
                    steps=[f"M({sub(f)}) = {g(M)} g/mol", f"m = n × M = {g(n)} × {g(M)} = {g(m)} gam"])
    if t == 'V':
        f = random.choice(["H2", "O2", "CO2", "N2", "SO2", "NH3"]); M = mass(f)
        n = random.choice([0.1, 0.25, 0.5, 1, 2]); m = round(n * M, 2)
        return dict(text=f"Tính thể tích (đktc) của {g(m)} gam khí {sub(f)}.", ans=n * 22.4, unit="lít",
                    steps=[f"M({sub(f)}) = {g(M)} → n = {g(m)} / {g(M)} = {g(n)} mol",
                           f"V = n × 22,4 = {g(n)} × 22,4 = {g(n * 22.4)} lít"])
    V = random.choice([2.24, 4.48, 6.72, 11.2, 22.4, 44.8]); f = random.choice(["H2", "CO2", "O2", "Cl2"])
    return dict(text=f"Có {g(V)} lít khí {sub(f)} (đktc). Tính số mol khí.", ans=V / 22.4, unit="mol",
                steps=[f"n = V / 22,4 = {g(V)} / 22,4 = {g(V / 22.4)} mol"])


def q_rx():
    R, P = random.choice(RX); (gf, gc) = R[0]; M = mass(gf)
    ng = random.choice([0.1, 0.2, 0.25, 0.5, 1, 2]); m = round(ng * M, 2)
    tf, tc = random.choice([p for p in P if p[0] != "H2O"]); nt = ng * tc / gc
    steps = [f"n({sub(gf)}) = {g(m)} / {g(M)} = {g(ng)} mol",
             f"Theo PT: n({sub(tf)}) = n({sub(gf)}) × {tc}/{gc} = {g(nt)} mol"]
    if tf in GAS:
        ans, unit, what = nt * 22.4, "lít", f"thể tích khí {sub(tf)} (đktc)"
        steps.append(f"V({sub(tf)}) = {g(nt)} × 22,4 = {g(ans)} lít")
    else:
        Mt = mass(tf); ans, unit, what = nt * Mt, "gam", f"khối lượng {sub(tf)} tạo thành"
        steps.append(f"m({sub(tf)}) = {g(nt)} × {g(Mt)} = {g(ans)} gam")
    return dict(text=f"Cho {g(m)} gam {sub(gf)} phản ứng hoàn toàn (chất kia dư). Tính {what}.",
                ans=ans, unit=unit, steps=steps, rx=(R, P))


def q_ph():
    C = random.choice([1, 0.1, 0.01, 0.001, 0.0001, 0.05, 0.02, 0.005, 0.002])
    if random.random() < .5:
        return dict(text=f"Tính pH của dung dịch HCl {C:g} M.", ans=-log10(C), unit="pH", tol=.05,
                    steps=[f"HCl điện li hoàn toàn: [H⁺] = {C:g} M", f"pH = -log[H⁺] = {g(-log10(C))}"])
    return dict(text=f"Tính pH của dung dịch NaOH {C:g} M.", ans=14 + log10(C), unit="pH", tol=.05,
                steps=[f"[OH⁻] = {C:g} M → pOH = -log[OH⁻] = {g(-log10(C))}", f"pH = 14 - pOH = {g(14 + log10(C))}"])


# =====================  ĐỘNG CƠ PHẢN ỨNG (Phòng thí nghiệm tự do)  =====================
# Chất được sinh tự động từ bảng ion + quy tắc tan; phản ứng được SUY RA từ quy tắc hóa học
# (trao đổi ion, dãy hoạt động kim loại, axit-bazơ-oxit...) rồi tự cân bằng bằng đại số tuyến tính.
CAT = {'H+': ('H', 1, 'Axit'), 'Na+': ('Na', 1, 'Natri'), 'K+': ('K', 1, 'Kali'), 'NH4+': ('NH4', 1, 'Amoni'),
       'Ag+': ('Ag', 1, 'Bạc'), 'Ca2+': ('Ca', 2, 'Canxi'), 'Mg2+': ('Mg', 2, 'Magie'), 'Ba2+': ('Ba', 2, 'Bari'),
       'Zn2+': ('Zn', 2, 'Kẽm'), 'Cu2+': ('Cu', 2, 'Đồng(II)'), 'Fe2+': ('Fe', 2, 'Sắt(II)'),
       'Fe3+': ('Fe', 3, 'Sắt(III)'), 'Al3+': ('Al', 3, 'Nhôm')}
AN = {'Cl-': ('Cl', 1, 'clorua'), 'Br-': ('Br', 1, 'bromua'), 'NO3-': ('NO3', 1, 'nitrat'), 'OH-': ('OH', 1, 'hiđroxit'),
      'SO42-': ('SO4', 2, 'sunfat'), 'CO32-': ('CO3', 2, 'cacbonat'), 'PO43-': ('PO4', 3, 'photphat'), 'CH3COO-': ('CH3COO', 1, 'axetat')}
MET = {'Na': 'Na+', 'K': 'K+', 'Ca': 'Ca2+', 'Ba': 'Ba2+', 'Mg': 'Mg2+', 'Al': 'Al3+', 'Zn': 'Zn2+',
       'Fe': 'Fe2+', 'Cu': 'Cu2+', 'Ag': 'Ag+'}
CATM = {v: k for k, v in MET.items()}
ACT = ['K', 'Ba', 'Ca', 'Na', 'Mg', 'Al', 'Zn', 'Fe', 'H', 'Cu', 'Ag']          # dãy hoạt động hóa học
OXM = {'Na': 'Na2O', 'K': 'K2O', 'Ca': 'CaO', 'Ba': 'BaO', 'Mg': 'MgO', 'Al': 'Al2O3', 'Zn': 'ZnO', 'Cu': 'CuO', 'Fe': 'Fe3O4'}
OXIDES = {'Na2O': 'Na+', 'K2O': 'K+', 'CaO': 'Ca2+', 'BaO': 'Ba2+', 'MgO': 'Mg2+', 'ZnO': 'Zn2+', 'CuO': 'Cu2+',
          'FeO': 'Fe2+', 'Fe2O3': 'Fe3+', 'Al2O3': 'Al3+'}
SPECIAL = {('H+', 'OH-'), ('H+', 'CO32-'), ('NH4+', 'OH-'), ('Ag+', 'OH-'), ('Al3+', 'CO32-'), ('Fe3+', 'CO32-')}
CCOL = {'Cu2+': ('#38bdf8', 'xanh lam'), 'Fe2+': ('#86efac', 'lục nhạt'), 'Fe3+': ('#f59e0b', 'vàng nâu')}
PCOL = {('Cu2+', 'OH-'): ('#3b82f6', 'xanh lam'), ('Fe3+', 'OH-'): ('#b45309', 'nâu đỏ'),
        ('Fe2+', 'OH-'): ('#6b8e5a', 'xanh rêu'), ('Cu2+', 'CO32-'): ('#2dd4bf', 'xanh lục'),
        ('Ag+', 'Br-'): ('#fde68a', 'vàng nhạt'), ('Ag+', 'PO43-'): ('#fde047', 'vàng')}
ACIDN = {'Cl-': 'Axit clohiđric', 'Br-': 'Axit bromhiđric', 'NO3-': 'Axit nitric',
         'SO42-': 'Axit sunfuric', 'PO43-': 'Axit photphoric', 'CH3COO-': 'Axit axetic'}
STN = {'s': 'rắn', 'l': 'lỏng', 'g': 'khí', 'aq': 'dung dịch'}
BASE = '#5b8db8'
SUBS, ION = {}, {}


def sdef(f, n, st, col, cn=''): SUBS[f] = dict(n=n, st=st, col=col, cn=cn)
def fm(x): return f"{x:.4g}"


def mk(c, a):
    cs, cq, _ = CAT[c]; as_, aq, _ = AN[a]; k = gcd(cq, aq); nc, na = aq // k, cq // k
    part = lambda x, n: x if n == 1 else (f"({x}){n}" if sum(parse(x).values()) > 1 else f"{x}{n}")
    if a == 'CH3COO-': return 'CH3COOH' if c == 'H+' else part(as_, na) + cs     # CH3COONa, (CH3COO)2Ca...
    return part(cs, nc) + part(as_, na)


def soluble(c, a):
    if c in ('H+', 'Na+', 'K+', 'NH4+') or a in ('NO3-', 'CH3COO-'): return True
    if a == 'Cl-': return c != 'Ag+'
    if a == 'Br-': return c != 'Ag+'
    if a == 'SO42-': return c not in ('Ba2+', 'Ca2+')
    if a == 'OH-': return c in ('Ca2+', 'Ba2+')
    if a == 'PO43-': return False
    return False


for _c in CAT:
    for _a in AN:
        if (_c, _a) in SPECIAL: continue
        _f = mk(_c, _a); ION[_f] = (_c, _a); _nm = f"{CAT[_c][2]} {AN[_a][2]}"
        if _c == 'H+': sdef(_f, ACIDN[_a], 'aq', '#cbd5e1')
        elif soluble(_c, _a):
            _col, _cn = CCOL.get(_c, ('#cbd5e1', '')); sdef(_f, _nm, 'aq', _col, _cn)
        else:
            _col, _cn = PCOL.get((_c, _a), ('#f1f5f9', 'trắng')); sdef(_f, _nm, 's', _col, _cn)
for _m, _n, _col, _cn in [('Na', 'Natri', '#e5e7eb', 'trắng bạc'), ('K', 'Kali', '#e5e7eb', 'trắng bạc'),
                          ('Ca', 'Canxi', '#e5e7eb', 'trắng bạc'), ('Ba', 'Bari', '#e5e7eb', 'trắng bạc'),
                          ('Mg', 'Magie', '#e5e7eb', 'trắng bạc'), ('Al', 'Nhôm', '#cbd5e1', 'trắng bạc'),
                          ('Zn', 'Kẽm', '#94a3b8', 'xám bạc'), ('Fe', 'Sắt', '#a1a1aa', 'xám'),
                          ('Cu', 'Đồng', '#e08a4a', 'đỏ'), ('Ag', 'Bạc', '#f1f5f9', 'trắng bạc')]: sdef(_m, _n, 's', _col, _cn)
for _o, _cat in OXIDES.items():
    _col, _cn = {'CuO': ('#374151', 'đen'), 'Fe2O3': ('#b45309', 'nâu đỏ'), 'FeO': ('#374151', 'đen')}.get(_o, ('#f1f5f9', 'trắng'))
    sdef(_o, f"{CAT[_cat][2]} oxit", 's', _col, _cn)
for _a in [('H2', 'Khí hiđro', 'g', '#e8f1ff', ''), ('O2', 'Khí oxi', 'g', '#bfdbfe', ''),
           ('N2', 'Khí nitơ', 'g', '#94a3b8', ''),
           ('Cl2', 'Khí clo', 'g', '#bef264', 'vàng lục'), ('C', 'Cacbon (than)', 's', '#4b5563', 'đen'),
           ('S', 'Lưu huỳnh', 's', '#facc15', 'vàng'), ('P', 'Photpho đỏ', 's', '#ff9f43', 'đỏ'),
           ('H2O', 'Nước', 'l', '#7dd3fc', ''),
           ('CO2', 'Khí cacbonic', 'g', '#e2e8f0', ''), ('CO', 'Khí cacbon oxit', 'g', '#e2e8f0', ''),
           ('SO2', 'Khí lưu huỳnh đioxit', 'g', '#e2e8f0', ''), ('SO3', 'Lưu huỳnh trioxit', 'l', '#e2e8f0', ''),
           ('H2S', 'Khí hiđro sunfua', 'g', '#facc15', ''),
           ('NH3', 'Khí amoniac', 'g', '#e2e8f0', ''),
           ('NO', 'Khí nitơ monoxit', 'g', '#e2e8f0', ''), ('NO2', 'Khí nitơ đioxit', 'g', '#d97706', 'nâu đỏ'),
           ('N2O', 'Khí đinitơ oxit', 'g', '#e2e8f0', ''), ('CH4', 'Khí metan', 'g', '#e2e8f0', ''),
           ('C2H5OH', 'Ancol etylic', 'l', '#e0f2fe', ''), ('Fe3O4', 'Oxit sắt từ', 's', '#374151', 'đen'),
           ('P2O5', 'Điphotpho pentaoxit', 's', '#f1f5f9', 'trắng'),
           ('MnO2', 'Mangan đioxit', 's', '#374151', 'đen'),
           ('KMnO4', 'Kali pemanganat', 'aq', '#a855f7', 'tím'),
           ('Na2O2', 'Natri peoxit', 's', '#fde68a', 'vàng nhạt'),
           ('FeS2', 'Pirit sắt', 's', '#fbbf24', 'vàng'),
           ('I2', 'Iot', 's', '#a855f7', 'tím đen'), ('HI', 'Axit iothiđric', 'aq', '#cbd5e1', ''),
           ('NaHCO3', 'Natri hiđrocacbonat', 'aq', '#cbd5e1', ''), ('Ca(HCO3)2', 'Canxi hiđrocacbonat', 'aq', '#cbd5e1', ''),
           ('Na2SO3', 'Natri sunfit', 'aq', '#cbd5e1', ''), ('NaClO', 'Natri hipoclorit', 'aq', '#cbd5e1', ''),
           ('NaAlO2', 'Natri aluminat', 'aq', '#cbd5e1', ''),
           ('NH4NO3', 'Amoni nitrat', 'aq', '#cbd5e1', ''), ('Ag2SO4', 'Bạc sunfat', 's', '#f1f5f9', 'trắng'),
           ('MnCl2', 'Mangan(II) clorua', 'aq', '#cbd5e1', ''),
           ('MnSO4', 'Mangan(II) sunfat', 'aq', '#fecaca', 'hồng nhạt'),
           ('K2MnO4', 'Kali manganat', 'aq', '#22c55e', 'xanh lục'),
           ('HCOONa', 'Natri fomat', 'aq', '#cbd5e1', ''),
           ('HCOONH4', 'Amoni fomat', 'aq', '#cbd5e1', ''),
           ('CH3COONH4', 'Amoni axetat', 'aq', '#cbd5e1', '')]: sdef(*_a)

for _a in [('C2H6', 'Khí etan', 'g', '#e2e8f0', ''), ('C3H8', 'Khí propan', 'g', '#e2e8f0', ''),
           ('C2H4', 'Khí etilen', 'g', '#e2e8f0', ''), ('C3H6', 'Khí propilen', 'g', '#e2e8f0', ''),
           ('C2H2', 'Khí axetilen', 'g', '#e2e8f0', ''), ('CH3Cl', 'Khí metyl clorua', 'g', '#e2e8f0', ''),
           ('C6H6', 'Benzen', 'l', '#fde68a', ''), ('CH3OH', 'Ancol metylic', 'l', '#e0f2fe', ''),
           ('HCHO', 'Fomanđehit', 'g', '#e2e8f0', ''), ('CH3CHO', 'Anđehit axetic', 'l', '#e0f2fe', ''),
           ('HCOOH', 'Axit fomic', 'l', '#e0f2fe', ''),
           ('CH3COOC2H5', 'Etyl axetat', 'l', '#e0f2fe', ''),
           ('HCOOCH3', 'Metyl fomat', 'l', '#e0f2fe', ''),
           ('C6H5OH', 'Phenol', 'aq', '#cbd5e1', ''), ('C6H12O6', 'Glucozơ', 'aq', '#cbd5e1', ''),
           ('C12H22O11', 'Saccarozơ', 's', '#f1f5f9', 'trắng'),
           ('C6H5NH2', 'Anilin', 'l', '#e0f2fe', ''),
           ('C6H5NH3Cl', 'Phenylamoni clorua', 'aq', '#cbd5e1', ''),
           ('C6H2Br3NH2', '2,4,6-tribromanilin', 's', '#f1f5f9', 'trắng'),
           ('Br2', 'Brom (dung dịch brom)', 'aq', '#f97316', 'da cam'), ('HBr', 'Axit bromhiđric', 'aq', '#cbd5e1', ''),
           ('C2H4Br2', 'Đibrometan', 'l', '#e0f2fe', ''), ('C3H6Br2', 'Đibrompropan', 'l', '#e0f2fe', ''),
           ('C2H2Br2', 'Đibrometen', 'l', '#e0f2fe', ''), ('C2H2Br4', 'Tetrabrometan', 'l', '#e0f2fe', ''),
           ('C6H5Br', 'Brombenzen', 'l', '#e0f2fe', ''), ('C6H2Br3OH', '2,4,6-tribromphenol', 's', '#f1f5f9', 'trắng'),
           ('Ag2C2', 'Bạc axetilua', 's', '#fde047', 'vàng'), ('C2H5ONa', 'Natri etylat', 'aq', '#cbd5e1', ''),
           ('C6H5ONa', 'Natri phenolat', 'aq', '#cbd5e1', ''), ('CaC2', 'Canxi cacbua', 's', '#9ca3af', 'xám'),
           ('Al4C3', 'Nhôm cacbua', 's', '#ca8a04', 'vàng')]: sdef(*_a)

_CATS = [c for c in CAT if c != 'H+']
def _salts(a): return [mk(c, a) for c in _CATS if mk(c, a) in SUBS]
TABS = [("Kim loại", list(MET)),
        ("Phi kim", ['C', 'S', 'P', 'I2', 'Br2', 'Cl2']),
        ("Khí/dd", ['H2', 'O2', 'N2', 'H2O', 'CO2', 'CO', 'SO2', 'SO3', 'H2S', 'NH3', 'NO', 'NO2']),
        ("Axit", ['HCl', 'HBr', 'HI', 'H2SO4', 'HNO3', 'H3PO4', 'CH3COOH', 'HCOOH']),
        ("Bazơ", [mk(c, 'OH-') for c in _CATS if mk(c, 'OH-') in SUBS]),
        ("Oxit", list(OXIDES) + ['Fe3O4', 'P2O5', 'MnO2']),
        ("Muối Cl⁻", _salts('Cl-')), ("Muối Br⁻", _salts('Br-')),
        ("Muối SO₄²⁻", _salts('SO42-')), ("Muối NO₃⁻", _salts('NO3-')),
        ("Muối CO₃²⁻", _salts('CO32-')), ("Muối PO₄³⁻", _salts('PO43-')),
        ("Muối axetat", _salts('CH3COO-')),
        ("Hiđrocacbon", ['CH4', 'C2H6', 'C3H8', 'C2H4', 'C3H6', 'C2H2', 'C6H6']),
        ("Hữu cơ O", ['CH3OH', 'C2H5OH', 'HCHO', 'CH3CHO', 'HCOOH', 'CH3COOH', 'HCOOCH3', 'CH3COOC2H5', 'C6H5OH', 'C6H12O6', 'C12H22O11', 'C6H5NH2']),
        ("Khác", ['NaHCO3', 'Ca(HCO3)2', 'Na2SO3', 'NaClO', 'NaAlO2', 'KMnO4', 'Na2O2', 'FeS2', 'CaC2', 'Al4C3', 'NH4NO3'])]

CTCT = {
    'CH4': ('CH₄', 'ankan', []),
    'C2H6': ('CH₃–CH₃', 'ankan', []),
    'C3H8': ('CH₃–CH₂–CH₃', 'ankan', []),
    'C2H4': ('CH₂=CH₂', 'anken', ['C=C']),
    'C3H6': ('CH₂=CH–CH₃', 'anken', ['C=C']),
    'C2H2': ('CH≡CH', 'ankin', ['C≡C']),
    'C6H6': ('vòng 6C (Kekulé)', 'aren', ['C=C']),
    'CH3OH': ('CH₃–OH', 'ancol', ['O–H(ancol)', 'C–O']),
    'C2H5OH': ('CH₃–CH₂–OH', 'ancol', ['O–H(ancol)', 'C–O']),
    'HCHO': ('H–CH=O', 'anđehit', ['C=O(anđehit)']),
    'CH3CHO': ('CH₃–CH=O', 'anđehit', ['C=O(anđehit)']),
    'HCOOH': ('H–COOH', 'axit cacboxylic', ['O–H(axit)', 'C=O(axit)']),
    'CH3COOH': ('CH₃–COOH', 'axit cacboxylic', ['O–H(axit)', 'C=O(axit)']),
    'HCOOCH3': ('H–COO–CH₃', 'este', ['C=O(este)', 'C–O']),
    'CH3COOC2H5': ('CH₃–COO–C₂H₅', 'este', ['C=O(este)', 'C–O']),
    'C6H5OH': ('C₆H₅–OH', 'phenol', ['O–H(ancol)', 'C=C']),
    'C6H12O6': ('CH₂OH–(CHOH)₄–CHO', 'glucozơ (monosaccarit)', ['O–H(ancol)', 'C=O(anđehit)']),
    'C12H22O11': ('C₆H₁₁O₅–O–C₆H₁₁O₅', 'saccarozơ (đisaccarit)', ['O–H(ancol)', 'C–O']),
    'C6H5NH2': ('C₆H₅–NH₂', 'amin thơm bậc 1', ['N–H']),
    'CH3Cl': ('CH₃–Cl', 'dẫn xuất halogen', ['C–Cl']),
    'C6H5Br': ('C₆H₅–Br', 'dẫn xuất halogen', ['C–Br']),
    'C2H4Br2': ('CH₂Br–CH₂Br', 'dẫn xuất halogen', ['C–Br']),
    'C6H2Br3OH': ('Br₃C₆H₂–OH', 'phenol (tribrom)', ['O–H(ancol)', 'C–Br']),
}
IR_BANDS = {
    'O–H(ancol)':   (3650, 3200, 'rộng, mạnh'),
    'O–H(axit)':    (3300, 2500, 'rất rộng, mạnh'),
    'N–H':          (3500, 3300, 'trung bình'),
    'C–H(sp3)':     (3000, 2850, 'mạnh'),
    'C–H(sp2)':     (3100, 3000, 'trung bình'),
    'C≡C–H':        (3300, 3200, 'mạnh, nhọn'),
    'C=O(anđehit)': (1740, 1720, 'rất mạnh'),
    'C=O(xeton)':   (1725, 1705, 'rất mạnh'),
    'C=O(axit)':    (1725, 1700, 'rất mạnh'),
    'C=O(este)':    (1780, 1735, 'rất mạnh'),
    'C=C':          (1680, 1620, 'trung bình'),
    'C≡C':          (2260, 2100, 'yếu–t.bình'),
    'C–O':          (1300, 1000, 'mạnh'),
    'C–Cl':         (800, 600, 'mạnh'),
    'C–Br':         (600, 500, 'mạnh'),
}

CUR_TXT = """C+O2>CO2|t°
S+O2>SO2|t°
H2+O2>H2O|t°
H2+Cl2>HCl|t°
CH4+O2>CO2+H2O|t°
C2H5OH+O2>CO2+H2O|t°
CO+O2>CO2|t°
C+CO2>CO|t°
CuO+H2>Cu+H2O|t°
Fe2O3+H2>Fe+H2O|t°
Fe2O3+CO>Fe+CO2|t°
Fe3O4+CO>Fe+CO2|t°
CuO+CO>Cu+CO2|t°
CuO+C>Cu+CO2|t°
CaCO3>CaO+CO2|t°
MgCO3>MgO+CO2|t°
Cu(OH)2>CuO+H2O|t°
Fe(OH)3>Fe2O3+H2O|t°
Al(OH)3>Al2O3+H2O|t°
NaHCO3>Na2CO3+CO2+H2O|t°
Ca(HCO3)2>CaCO3+CO2+H2O|t°
Na2CO3+CO2+H2O>NaHCO3
CaCO3+CO2+H2O>Ca(HCO3)2
NaHCO3+HCl>NaCl+CO2+H2O
NaHCO3+H2SO4>Na2SO4+CO2+H2O
NaHCO3+NaOH>Na2CO3+H2O
Ca(HCO3)2+Ca(OH)2>CaCO3+H2O
Ca(HCO3)2+HCl>CaCl2+CO2+H2O
Al+NaOH+H2O>NaAlO2+H2
Al(OH)3+NaOH>NaAlO2+H2O
Al2O3+NaOH>NaAlO2+H2O
SO2+NaOH>Na2SO3+H2O
Na2SO3+HCl>NaCl+SO2+H2O
Cl2+NaOH>NaCl+NaClO+H2O
Cu+FeCl3>CuCl2+FeCl2
Fe+FeCl3>FeCl2
Cu+Fe2(SO4)3>CuSO4+FeSO4
Fe+Fe2(SO4)3>FeSO4
Fe+Fe(NO3)3>Fe(NO3)2
Fe(NO3)2+AgNO3>Fe(NO3)3+Ag
FeCl2+Cl2>FeCl3
NaCl+H2O>NaOH+Cl2+H2|đp
CuSO4+H2O>Cu+O2+H2SO4|đp
CuCl2>Cu+Cl2|đp
H2O>H2+O2|đp
Al2O3>Al+O2|đp
Cu+2H2SO4>CuSO4+SO2+2H2O|đn:H₂SO₄ đặc, nóng
2Ag+2H2SO4>Ag2SO4+SO2+2H2O|đn:H₂SO₄ đặc, nóng
2Fe+6H2SO4>Fe2(SO4)3+3SO2+6H2O|đn:H₂SO₄ đặc, nóng
Zn+2H2SO4>ZnSO4+SO2+2H2O|đn:H₂SO₄ đặc, nóng
Mg+2H2SO4>MgSO4+SO2+2H2O|đn:H₂SO₄ đặc, nóng
2Al+6H2SO4>Al2(SO4)3+3SO2+6H2O|đn:H₂SO₄ đặc, nóng
C+2H2SO4>CO2+2SO2+2H2O|đn:H₂SO₄ đặc, nóng
S+2H2SO4>3SO2+2H2O|đn:H₂SO₄ đặc, nóng
3Cu+8HNO3>3Cu(NO3)2+2NO+4H2O|lo:HNO₃ loãng
8Al+30HNO3>8Al(NO3)3+3NH4NO3+9H2O|lo:HNO₃ rất loãng
3Mg+8HNO3>3Mg(NO3)2+2NO+4H2O|lo:HNO₃ loãng
3Zn+8HNO3>3Zn(NO3)2+2NO+4H2O|lo:HNO₃ loãng
Fe+4HNO3>Fe(NO3)3+NO+2H2O|lo:HNO₃ loãng
3Fe+8HNO3>3Fe(NO3)2+2NO+4H2O|lo:HNO₃ loãng (dư Fe)
8Fe+30HNO3>8Fe(NO3)3+3NH4NO3+9H2O|lo:HNO₃ rất loãng
3Ag+4HNO3>3AgNO3+NO+2H2O|lo:HNO₃ loãng
Cu+4HNO3>Cu(NO3)2+2NO2+2H2O|đn:HNO₃ đặc, nóng
Fe+6HNO3>Fe(NO3)3+3NO2+3H2O|đn:HNO₃ đặc, nóng
Al+6HNO3>Al(NO3)3+3NO2+3H2O|đn:HNO₃ đặc, nóng
Mg+4HNO3>Mg(NO3)2+2NO2+2H2O|đn:HNO₃ đặc, nóng
Zn+4HNO3>Zn(NO3)2+2NO2+2H2O|đn:HNO₃ đặc, nóng
Ag+2HNO3>AgNO3+NO2+H2O|đn:HNO₃ đặc, nóng
3FeO+10HNO3>3Fe(NO3)3+NO+5H2O|lo
3Fe3O4+28HNO3>9Fe(NO3)3+NO+14H2O|lo
FeO+4HNO3>Fe(NO3)3+NO2+2H2O|đn
2FeO+4H2SO4>Fe2(SO4)3+SO2+4H2O|đn:H₂SO₄ đặc, nóng
Fe3O4+4H2SO4>FeSO4+Fe2(SO4)3+4H2O|lo
N2+3H2>2NH3|t°:Fe, t° cao, p cao
4NH3+5O2>4NO+6H2O|t°:Pt, 850°C
2NO+O2>2NO2
4NO2+O2+2H2O>4HNO3
S+H2>H2S|t°
2H2S+SO2>3S+2H2O
H2S+Cl2>S+2HCl
2SO2+O2>2SO3|t°:V₂O₅, 450°C
SO3+H2O>H2SO4
4P+5O2>2P2O5|t°
P2O5+3H2O>2H3PO4
Cl2+2NaBr>2NaCl+Br2
Cl2+2KBr>2KCl+Br2
Cl2+2KI>2KCl+I2
Br2+2KI>2KBr+I2
MnO2+4HCl>MnCl2+Cl2+2H2O|t°
2KMnO4>K2MnO4+MnO2+O2|t°
2Na2O2+2H2O>4NaOH+O2
4FeS2+11O2>2Fe2O3+8SO2|t°
2FeCl2+Cl2>2FeCl3
2FeSO4+2H2SO4>Fe2(SO4)3+SO2+2H2O|đn:H₂SO₄ đặc, nóng
10FeSO4+2KMnO4+8H2SO4>5Fe2(SO4)3+2MnSO4+K2SO4+8H2O|:chuẩn độ
CH4+H2O>CO+3H2|t°:900°C, xt
CO+H2O>CO2+H2|t°:xt, t°"""
CUR_TXT2 = """C2H4+Br2>C2H4Br2
C3H6+Br2>C3H6Br2
C2H2+Br2>C2H2Br2
C2H2Br2+Br2>C2H2Br4
C6H5OH+Br2>C6H2Br3OH+HBr
C2H4+H2>C2H6|t°:Ni, t°
C3H6+H2>C3H8|t°:Ni, t°
C2H2+H2>C2H4|t°:Pd, t°
C2H4+H2O>C2H5OH|t°:H₂SO₄ loãng, t°
C2H2+H2O>CH3CHO|t°:HgSO₄, 80°C
C2H2+AgNO3+NH3>Ag2C2+NH4NO3
CH3CHO+2AgNO3+3NH3+H2O>CH3COONH4+2Ag+2NH4NO3|t°
CH3CHO+H2>C2H5OH|t°:Ni, t°
C2H5OH+CuO>CH3CHO+Cu+H2O|t°
C2H5OH+Na>C2H5ONa+H2
C6H5OH+Na>C6H5ONa+H2
C6H5OH+NaOH>C6H5ONa+H2O
C2H5OH+CH3COOH>CH3COOC2H5+H2O|t°:H₂SO₄ đặc, t°
CH3COOC2H5+NaOH>CH3COONa+C2H5OH|t°
C6H12O6>C2H5OH+CO2|t°:men rượu, 30°C
CH4+Cl2>CH3Cl+HCl|t°:ánh sáng
C6H6+Br2>C6H5Br+HBr|t°:Fe, t°
CH3COOH+NaHCO3>CH3COONa+CO2+H2O
CH3COONa+NaOH>CH4+Na2CO3|t°:CaO, t°
CaC2+H2O>C2H2+Ca(OH)2
Al4C3+H2O>Al(OH)3+CH4
HCHO+2AgNO3+3NH3+H2O>HCOONH4+2Ag+2NH4NO3|t°:tráng gương
HCOOH+2AgNO3+3NH3>CO2+2Ag+2NH4NO3+H2O|t°:tráng gương
C12H22O11+H2O>2C6H12O6|t°:H₂SO₄ loãng, t°
HCOOCH3+NaOH>HCOONa+CH3OH|t°
HCOOH+NaOH>HCOONa+H2O
HCOOH+Na>HCOONa+H2
C6H5NH2+HCl>C6H5NH3Cl
C6H5NH2+Br2>C6H2Br3NH2+HBr"""
_ORG = ['CH4', 'C2H6', 'C3H8', 'C2H4', 'C3H6', 'C2H2', 'C6H6', 'CH3OH', 'C2H5OH', 'HCHO', 'CH3CHO', 'HCOOH',
        'CH3COOH', 'HCOOCH3', 'CH3COOC2H5', 'C6H5OH', 'C6H12O6', 'C12H22O11', 'C6H5NH2']
LAB, COEF, CUR, _seen = {}, {}, [], set()
for _ln in (CUR_TXT + "\n" + CUR_TXT2 + "".join(f"\n{_f}+O2>CO2+H2O|t°" for _f in _ORG)).splitlines():
    _b, _, _cd = _ln.partition('|'); _cd, _, _lab = _cd.partition(':'); _l, _r = _b.split('>')
    _cf = [int(re.match(r'\d*', x).group() or 1) for x in _l.split('+') + _r.split('+')]
    _R, _P = tuple(re.sub(r'^\d+', '', x) for x in _l.split('+')), tuple(re.sub(r'^\d+', '', x) for x in _r.split('+'))
    if any(c > 1 for c in _cf): COEF[(_R, _P)] = tuple(_cf)
    if (_R, _P) in _seen: continue
    _seen.add((_R, _P)); CUR.append((_R, _P, _cd))
    if _lab: LAB[(_R, _P)] = _lab


@lru_cache(None)
def balance(R, P):
    """Cân bằng tự động: giải hệ phương trình bảo toàn nguyên tố (khử Gauss với phân số)."""
    sp = list(R + P); n = len(sp); els = sorted({e for f in sp for e in parse(f)})
    M = [[Fraction(parse(f).get(e, 0) * (1 if i < len(R) else -1)) for i, f in enumerate(sp)] for e in els]
    piv, r = [], 0
    for c in range(n):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; M[r] = [x / M[r][c] for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0: M[i] = [a - M[i][c] * b for a, b in zip(M[i], M[r])]
        piv.append(c); r += 1
    free = [c for c in range(n) if c not in piv]
    if len(free) != 1: return None
    v = [Fraction(0)] * n; v[free[0]] = Fraction(1)
    for i, c in enumerate(piv): v[c] = -M[i][free[0]]
    L = reduce(lambda a, b: a * b // gcd(a, b), [x.denominator for x in v]); v = [int(x * L) for x in v]
    if all(x < 0 for x in v): v = [-x for x in v]
    return tuple(v) if all(x > 0 for x in v) else None


def bal(R, P): return COEF.get((R, P)) or balance(R, P)


def comb(c, a):
    if (c, a) == ('H+', 'OH-'): return ['H2O']
    if (c, a) == ('H+', 'CO32-'): return ['CO2', 'H2O']
    if (c, a) == ('NH4+', 'OH-'): return ['NH3', 'H2O']
    f = mk(c, a); return [f] if f in SUBS else None


def meta(X, Y):
    """Phản ứng trao đổi ion: xảy ra khi tạo kết tủa, chất khí hoặc nước."""
    (c1, a1), (c2, a2) = ION[X], ION[Y]
    if c1 == c2 or a1 == a2: return None
    p1, p2 = comb(c1, a2), comb(c2, a1)
    if not p1 or not p2: return None
    P = []
    for f in p1 + p2:
        if f not in P: P.append(f)
    s1, s2 = SUBS[X]['st'], SUBS[Y]['st']
    if not ((s1 == 'aq' and s2 == 'aq') or ('H+' in (c1, c2) and 'aq' in (s1, s2))): return None
    if not any(SUBS[f]['st'] in 'sgl' for f in P): return None
    return (X, Y), tuple(P)


@lru_cache(None)
def candidates(pres, cond, hasw):
    """Phản ứng khả dĩ theo thứ tự ưu tiên: trao đổi ion → oxit/khí → kim loại (khử mạnh + oxi hóa mạnh trước) → còn lại."""
    out = []; ion = [f for f in pres if f in ION]
    for i, X in enumerate(ion):
        for Y in ion[i + 1:]:
            r = meta(X, Y)
            if r: out.append(r + ('',))
    acids = [f for f in ion if ION[f][0] == 'H+']
    for ox, cat in OXIDES.items():
        if ox not in pres: continue
        for ac in acids:
            an = ION[ac][1]
            if ox == 'FeO' and (an == 'NO3-' or (an == 'SO42-' and cond == 'đn')): continue
            out.append(((ox, ac), (mk(cat, an), 'H2O'), ''))
        if cat in ('Na+', 'K+', 'Ca2+', 'Ba2+') and hasw: out.append(((ox, 'H2O'), (mk(cat, 'OH-'),), ''))
    if 'CO2' in pres:
        for b in ion:
            if ION[b][1] == 'OH-' and ION[b][0] in ('Na+', 'K+', 'Ca2+', 'Ba2+'):
                out.append((('CO2', b), (mk(ION[b][0], 'CO32-'), 'H2O'), ''))
    if 'NH3' in pres:
        for ac in acids: out.append((('NH3', ac), (mk('NH4+', ION[ac][1]),), ''))
    rh = ACT.index('H'); _cur_early = set()
    for m in sorted((m for m in MET if m in pres), key=ACT.index):
        cat = MET[m]; ox = []
        if cond == 'đng' and m in ('Fe', 'Al'): continue
        if cond in ('đn', 'lo'):
            for ci, (R, P, cd) in enumerate(CUR):
                if cd == cond and m in R and all(f in pres or (f == 'H2O' and hasw) for f in R):
                    out.append((R, P, cd)); _cur_early.add(ci)
        for ac in acids:
            an = ION[ac][1]
            if (cond == 'đn' and an in ('NO3-', 'SO42-')) or (cond == 'lo' and an == 'NO3-'):
                pass
            elif an == 'NO3-' and m in ('Mg', 'Al', 'Zn', 'Fe', 'Cu', 'Ag'):
                ox.append((99, (m, ac), (mk('Fe3+' if m == 'Fe' else cat, 'NO3-'), 'NO', 'H2O')))
            elif ACT.index(m) < rh: ox.append((rh, (m, ac), (mk(cat, an), 'H2')))
        for sl in ion:
            cs = ION[sl][0]
            if cs in CATM and SUBS[sl]['st'] == 'aq' and m not in ('K', 'Na', 'Ca', 'Ba') and ACT.index(m) < ACT.index(CATM[cs]):
                ox.append((ACT.index(CATM[cs]), (m, sl), (mk(cat, ION[sl][1]), CATM[cs])))
        for _, R, P in sorted(ox, key=lambda t: -t[0]): out.append((R, P, ''))
        if m in ('K', 'Na', 'Ca', 'Ba') and hasw: out.append(((m, 'H2O'), (mk(cat, 'OH-'), 'H2'), ''))
        if m in OXM: out.append(((m, 'O2'), (OXM[m],), 't°'))
        out.append(((m, 'Cl2'), (mk('Fe3+' if m == 'Fe' else cat, 'Cl-'),), 't°'))
    for ci, (R, P, cd) in enumerate(CUR):
        if ci not in _cur_early and all(f in pres or (f == 'H2O' and hasw) for f in R): out.append((R, P, cd))
    ok = {'', cond}
    if cond == 'đn': ok |= {'t°'}
    if cond == 'lo': ok |= {''}
    return tuple(x for x in out if x[2] in ok)


def eqtxt(R, P, co, cd):
    aq = any(SUBS[f]['st'] == 'aq' for f in R); k = len(R); lab = LAB.get((R, P), cd)
    def t(f, c, prod):
        st = SUBS[f]['st']; mark = '↑' if prod and st == 'g' else '↓' if prod and st == 's' and aq else ''
        return (str(c) if c > 1 else '') + sub(f) + mark
    return (" + ".join(t(f, c, 0) for f, c in zip(R, co)) + (f"  →({lab})  " if lab else "  →  ")
            + " + ".join(t(f, c, 1) for f, c in zip(P, co[k:])))


def observe(R, P):
    o = []; aq = any(SUBS[f]['st'] == 'aq' for f in R)
    for f in R:
        d = SUBS[f]
        if d['st'] == 's' and f not in P: o.append(f"{d['n']} tan dần / bị tiêu hao")
        if d['st'] == 'aq' and d['cn'] and f not in P: o.append(f"dung dịch {sub(f)} nhạt dần màu {d['cn']}")
    for f in P:
        d = SUBS[f]; cl = f" màu {d['cn']}" if d['cn'] else ""
        if d['st'] == 'g' and f not in R: o.append(f"thoát ra {d['n'][0].lower() + d['n'][1:]}{cl}")
        elif d['st'] == 's' and f not in R:
            o.append(f"xuất hiện {'kết tủa' if aq and f not in MET else 'chất rắn'} {d['n'][0].lower() + d['n'][1:]}{cl}")
        elif d['st'] == 'aq' and d['cn'] and f not in R: o.append(f"dung dịch chuyển sang màu {d['cn']}")
    return "; ".join(o) or "phản ứng xảy ra, không có dấu hiệu nhìn thấy rõ"


def liquid_color(m):
    cs = [(n, SUBS[f]['col']) for f, n in m.items() if n > 1e-9 and SUBS[f]['st'] == 'aq' and SUBS[f]['cn']]
    return mix(max(cs)[1], BASE, .8) if cs else BASE


# ---------- Biểu thức tuyến tính theo ẩn số (x, y, z...) ----------
class LE:
    """Biểu thức tuyến tính: khóa '' = hằng số, 'x' = ẩn số, (hàm, chất, k) = đại lượng quan sát (n, m, V...)."""
    def __init__(s, d=None): s.d = {k: v for k, v in (d or {}).items() if v != 0}

    @staticmethod
    def num(x): return LE({'': Fraction(x)})

    @staticmethod
    def var(k): return LE({k: Fraction(1)})

    def __add__(s, o):
        d = dict(s.d)
        for k, v in o.d.items(): d[k] = d.get(k, 0) + v
        return LE(d)

    def scale(s, c): return LE({k: v * Fraction(c) for k, v in s.d.items()})
    def __neg__(s): return s.scale(-1)
    def __sub__(s, o): return s + (-o)
    def const(s): return s.d.get('', Fraction(0))
    def isconst(s): return all(k == '' for k in s.d)
    def vars(s): return {k for k in s.d if k and isinstance(k, str)}
    def ev(s, a): return sum(float(v) * (1 if k == '' else a[k]) for k, v in s.d.items() if not isinstance(k, tuple))

    def __str__(s):
        if not s.d: return '0'
        out = ''
        ks = sorted(s.d, key=lambda k: (k != '', str(k)))
        pos = [k for k in ks if s.d[k] > 0]
        if pos and s.d[ks[0]] < 0: ks.remove(pos[0]); ks.insert(0, pos[0])
        for i, k in enumerate(ks):
            v = s.d[k]; neg = v < 0; v = abs(v)
            nm = k if isinstance(k, str) else f"{k[0]}({k[1]})"
            body = fm(float(v)) if k == '' else ('' if v == 1 else fm(float(v))) + nm
            out += (('−' if neg else '') + body) if i == 0 else ((' − ' if neg else ' + ') + body)
        return out


def mul_le(a, b):
    if a.isconst(): return b.scale(a.const())
    if b.isconst(): return a.scale(b.const())
    raise ValueError("Chỉ được nhân ẩn với hằng số (không nhân ẩn với ẩn)")


def inv_le(a):
    if not a.isconst() or a.const() == 0: raise ValueError("Chỉ chia cho hằng số khác 0")
    return LE.num(1 / a.const())


UNSUB = str.maketrans('₀₁₂₃₄₅₆₇₈₉', '0123456789')
_TOK = re.compile(r'(\d+\.?\d*|\.\d+)|([nmvNMV]0?)\(((?:[^()]|\([^()]*\))+)\)(?:@(\d+))?|([a-z])|([+\-*/])')


def parse_form(t):
    """'2x+0.5y', 'm0(Fe)+m0(Cu)', 'n(H2)@2'... → LE."""
    t = t.replace(',', '.').replace('−', '-').replace('×', '*').replace(' ', '').translate(UNSUB)
    if not t: raise ValueError("Biểu thức trống")
    tot, cur, op, sign, pos = LE(), None, '*', 1, 0
    while pos < len(t):
        m = _TOK.match(t, pos)
        if not m: raise ValueError(f"Không hiểu '{t[pos:]}'")
        pos = m.end(); g_ = m.groups()
        if g_[5]:
            if g_[5] in '*/': op = g_[5]; continue
            if cur is not None: tot = tot + cur.scale(sign); cur = None
            sign = 1 if g_[5] == '+' else -1; op = '*'; continue
        f = (LE.num(Fraction(g_[0])) if g_[0] else
             LE({(g_[1].lower(), g_[2], int(g_[3]) if g_[3] else None): Fraction(1)}) if g_[1] else LE.var(g_[4]))
        cur = f if cur is None else (mul_le(cur, f) if op == '*' else mul_le(cur, inv_le(f))); op = '*'
    if cur is not None: tot = tot + cur.scale(sign)
    if any(k in ('n', 'm', 'v') for k in tot.d): raise ValueError("Tên ẩn không được là n, m, v")
    return tot


def parse_cons(text):
    t = text.strip().replace('≥', '>=').replace('≤', '<=')
    ms = re.match(r'^(rắn|khí|dd)(?:@(\d+))?\s*=\s*(.+)$', t)
    if ms:
        return dict(kind='set', what=ms.group(1), k=int(ms.group(2)) if ms.group(2) else None, text=text.strip(),
                    names={x.strip().translate(UNSUB) for x in re.split(r'[,;]', ms.group(3)) if x.strip()})
    m = re.match(r'^(.+?)(>=|<=|=|>|<)(.+)$', t)
    if not m: raise ValueError("Giả thiết cần có dấu =, >, < …  VD: m0(Fe)+m0(Cu)=7.28")
    return dict(kind='rel', e=parse_form(m.group(1)) - parse_form(m.group(3)), op=m.group(2), text=text.strip())


def build_add(f, text, unit):
    """Đổi lượng nhập (mol / gam / lít khí / C_M·V / C%·m_dd; số hoặc ẩn) thành số mol dạng LE."""
    st = SUBS[f]['st']; M = Fraction(mass(f)).limit_denominator(1000)
    if unit == 'lít' and st != 'g': raise ValueError("Đơn vị 'lít' chỉ dùng cho chất khí")
    if unit in ('M·ml', '%·g') and st != 'aq': raise ValueError("Dạng dung dịch chỉ dùng cho chất tan trong nước (nhóm 'aq')")
    parts = [p for p in re.split(r'[\s;]+', text.strip()) if p]; fl = [parse_form(p) for p in parts]
    need = 2 if unit in ('M·ml', '%·g') else 1
    if len(fl) != need: raise ValueError("Cần nhập 2 số cách nhau bằng dấu cách" if need == 2 else "Cần nhập đúng 1 giá trị")
    if unit == 'mol': e, d = fl[0], f"{parts[0]} mol"
    elif unit == 'gam': e, d = fl[0].scale(1 / M), f"{parts[0]} g"
    elif unit == 'lít': e, d = fl[0].scale(Fraction(10, 224)), f"{parts[0]} lít (đktc)"
    elif unit == 'M·ml': e, d = mul_le(fl[0], fl[1]).scale(Fraction(1, 1000)), f"dd {parts[0]} M × {parts[1]} ml"
    else: e, d = mul_le(fl[0], fl[1]).scale(Fraction(1, 100) / M), f"dd {parts[0]}% × {parts[1]} g"
    if e.isconst() and e.const() <= 0: raise ValueError("Lượng chất phải dương")
    return e, d


# ---------- Mô phỏng chuỗi phản ứng (lượng chất dạng biểu thức) ----------
def simulate(mx, cond, assign):
    """Mỗi bước: chọn phản ứng ưu tiên cao nhất, tính theo chất hết (so sánh bằng giá trị số của `assign`,
    còn lượng chất được ghi lại DƯỚI DẠNG BIỂU THỨC theo ẩn x, y, z)."""
    ev = lambda e: e.ev(assign); Z = LE(); mx = dict(mx); steps = []; used = set()
    for _ in range(25):
        pres = tuple(f for f, e in mx.items() if ev(e) > 1e-9)
        aqs = any(SUBS[f]['st'] == 'aq' for f in pres); hit = None
        for R, P, cd in candidates(pres, cond, aqs or 'H2O' in pres):
            if (R, P) in used: continue
            co = bal(R, P)
            if not co: continue
            q = [(9e9 if (f == 'H2O' and aqs) else ev(mx.get(f, Z)) / c, f, c) for f, c in zip(R, co)]
            ext = min(x[0] for x in q)
            if 1e-9 < ext < 1e8: hit = (R, P, cd, co, ext, q); break
        if not hit: break
        R, P, cd, co, ext, q = hit; k = len(R); lq = min(q, key=lambda x: x[0])
        e_le = mx[lq[1]].scale(Fraction(1, lq[2])); tab = []
        for f, c in zip(R, co):
            if f == 'H2O' and aqs: continue
            b = mx.get(f, Z); a = b - e_le.scale(c); tab.append((f, b, -e_le.scale(c), a)); mx[f] = a
        nr = len(tab)
        for f, c in zip(P, co[k:]):
            b = mx.get(f, Z); a = b + e_le.scale(c); tab.append((f, b, e_le.scale(c), a)); mx[f] = a
        mx = {f: e for f, e in mx.items() if e.d}; used.add((R, P))
        steps.append(dict(eq=eqtxt(R, P, co, cd), R=R, P=P, nR=nr, tab=tab, obs=observe(R, P),
                          lim=", ".join(sub(f) for x, f, c in q if x - ext < 1e-9 and x < 1e8)))
    return steps, mx


def execute(prog, assign):
    """Chạy cả kịch bản: ('add', chất, LE, mô tả) | ('run', điều kiện) | ('keep', 'solid'|'dd')."""
    mx, tr, nrun = {}, [], 0
    for a in prog:
        if a[0] == 'add':
            mx = dict(mx); mx[a[1]] = mx.get(a[1], LE()) + a[2]; tr.append(dict(k='add', f=a[1], e=a[2], desc=a[3]))
        elif a[0] == 'run':
            steps, mx2 = simulate(mx, a[1], assign); nrun += 1
            tr.append(dict(k='run', n=nrun, cond=a[1], before=dict(mx), steps=steps, after=dict(mx2))); mx = dict(mx2)
        else:
            ok = (lambda st: st == 's') if a[1] == 'solid' else (lambda st: st in ('aq', 'l'))
            kept = {f: e for f, e in mx.items() if ok(SUBS[f]['st'])}
            tr.append(dict(k='keep', kind=a[1], kept=kept, lost={f: e for f, e in mx.items() if f not in kept})); mx = kept
    return tr, mx


def signature(tr):
    return tuple(tuple((st['R'], st['P'], st['lim']) for st in t['steps']) for t in tr if t['k'] == 'run')


# ---------- Giả thiết (ràng buộc) & giải ẩn ----------
def _state(tr, fin, k):
    runs = [t['after'] for t in tr if t['k'] == 'run']
    if k:
        if k > len(runs): raise ValueError(f"Chưa có phản ứng thứ {k} (hiện có {len(runs)})")
        return runs[k - 1]
    return runs[-1] if runs else fin


def obs_le(key, tr, fin):
    fn, arg, k = key; f0 = fn.rstrip('0')
    w = lambda f: (Fraction(mass(f)).limit_denominator(1000) if f0 == 'm' else Fraction(224, 10) if f0 == 'v' else Fraction(1))
    if arg not in SUBS and arg not in ('rắn', 'khí'): raise ValueError(f"Không biết chất '{arg}'")
    if fn.endswith('0'):
        if arg not in SUBS: raise ValueError('n0/m0/V0 chỉ dùng cho một chất cụ thể')
        return sum((t['e'].scale(w(arg)) for t in tr if t['k'] == 'add' and t['f'] == arg), LE())
    st = _state(tr, fin, k)
    sp = [f for f in st if SUBS[f]['st'] == ('s' if arg == 'rắn' else 'g')] if arg in ('rắn', 'khí') else [arg]
    return sum((st.get(f, LE()).scale(w(f)) for f in sp), LE())


def resolve(e, tr, fin):
    out = LE({k: v for k, v in e.d.items() if not isinstance(k, tuple)})
    for k, v in e.d.items():
        if isinstance(k, tuple): out = out + obs_le(k, tr, fin).scale(v)
    return out


def cons_ok(c, tr, fin, a, tol=1e-6):
    if c['kind'] == 'set':
        st = _state(tr, fin, c['k']); stt = {'rắn': 's', 'khí': 'g', 'dd': 'aq'}[c['what']]
        return {f for f, e in st.items() if SUBS[f]['st'] == stt and e.ev(a) > 1e-9} == c['names']
    v = resolve(c['e'], tr, fin).ev(a); op = c['op']
    return (abs(v) <= tol if op == '=' else v > 1e-9 if op == '>' else v < -1e-9 if op == '<'
            else v >= -tol if op == '>=' else v <= tol)


def is_filter(c):
    if c['kind'] == 'set' or c['op'] != '=': return True
    return len(c['e'].d) == 1 and isinstance(next(iter(c['e'].d)), tuple)      # dạng n(X)=0


def solve_lin(rows, vs):
    n = len(vs); M = [[r.d.get(v, Fraction(0)) for v in vs] + [-r.const()] for r in rows]; piv, r = [], 0
    for c in range(n):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]; M[r] = [x / M[r][c] for x in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0: M[i] = [a - M[i][c] * b for a, b in zip(M[i], M[r])]
        piv.append(c); r += 1
    if any(all(x == 0 for x in row[:n]) and row[n] != 0 for row in M): return 'bad', {}
    return ('ok' if r == n else 'under'), {vs[c]: M[i][n] for i, c in enumerate(piv)}


def analyze(prog, cons):
    """Tìm nghiệm các ẩn: lấy mẫu để tìm 'kịch bản' (chất nào hết/dư) thỏa các giả thiết định tính,
    rồi giải hệ phương trình tuyến tính của kịch bản đó và kiểm chứng lại bằng mô phỏng."""
    vs = sorted({k for a in prog if a[0] == 'add' for k in a[2].d if k and isinstance(k, str)}
                | {k for c in cons if c['kind'] == 'rel' for k in c['e'].d if k and isinstance(k, str)})
    info = dict(vs=vs, assign={v: .1 for v in vs}, solved=not vs, msg=[])
    flt = [c for c in cons if is_filter(c)]; eqs = [c for c in cons if not is_filter(c)]

    def run(a): info['tr'], info['fin'] = execute(prog, a)

    def attempt(sigs):
        for _, (a, _n) in sorted(sigs.items(), key=lambda kv: -kv[1][1]):
            tr, fin = execute(prog, a); st, sol = solve_lin([resolve(c['e'], tr, fin) for c in eqs], vs)
            if st == 'ok':
                asg = {v: float(sol[v]) for v in vs}
                if all(x > 1e-9 for x in asg.values()):
                    tr2, fin2 = execute(prog, asg)
                    if all(cons_ok(c, tr2, fin2, asg) for c in cons): return asg, tr2, fin2
        return None
    try:
        if not vs:
            run({}); info['msg'] += [f"⚠ Giả thiết chưa thỏa: {c['text']}" for c in cons if not cons_ok(c, info['tr'], info['fin'], {})]
            return info
        need = bool(flt) or any(isinstance(k, tuple) for c in eqs for k in c['e'].d); sigs, r = {}, None
        if not need: sigs = {None: [{v: .1 for v in vs}, 1]}; r = attempt(sigs)
        else:
            for seed in (7, 11, 13):
                rnd = random.Random(seed)
                for _ in range(160):
                    a = {v: 10 ** rnd.uniform(-2.3, .3) for v in vs}; tr, fin = execute(prog, a)
                    if all(cons_ok(c, tr, fin, a) for c in flt): sigs.setdefault(signature(tr), [a, 0])[1] += 1
                r = attempt(sigs) if eqs and sigs else None
                if r or not eqs: break
        if r: info.update(assign=r[0], solved=True, tr=r[1], fin=r[2]); return info
        if sigs:
            info['assign'] = max(sigs.values(), key=lambda v: v[1])[0]; run(info['assign'])
            info['msg'].append("ℹ Chưa đủ dữ kiện để tính giá trị các ẩn → hiển thị lời giải TỔNG QUÁT theo ẩn (số trong ngoặc vuông là minh họa)."
                               if not eqs else "⚠ Không tìm được nghiệm dương thỏa mãn các phương trình đã cho – hãy kiểm tra giả thiết.")
        else:
            run(info['assign']); info['msg'].append("⚠ Không có kịch bản nào thỏa mãn các giả thiết – hãy kiểm tra lại.")
    except ValueError as ex:
        run(info['assign']); info['msg'].append(f"⚠ {ex}")
    return info


def analyze_multi(beaker_progs, cons):
    """Joint analysis: solve unknowns shared across multiple beakers.
    Each constraint has c['bk'] = beaker index it should be resolved against."""
    nb = len(beaker_progs)
    vs = sorted({k for prog in beaker_progs for a in prog if a[0] == 'add'
                 for k in a[2].d if k and isinstance(k, str)}
                | {k for c in cons if c['kind'] == 'rel' for k in c['e'].d if k and isinstance(k, str)})
    infos = [dict(vs=vs, assign={v: .1 for v in vs}, solved=not vs, msg=[]) for _ in range(nb)]
    def run_all(a): return [execute(prog, a) for prog in beaker_progs]
    def _bi(c): bi = c.get('bk', 0); return min(bi, nb - 1) if bi >= 0 else 0
    def cok(c, traces, a): bi = _bi(c); return cons_ok(c, traces[bi][0], traces[bi][1], a)
    if not vs:
        traces = run_all({})
        for i in range(nb):
            infos[i]['tr'], infos[i]['fin'] = traces[i]
            infos[i]['msg'] += [f"⚠ Giả thiết chưa thỏa: {c['text']}" for c in cons
                                if _bi(c) == i and not cons_ok(c, traces[i][0], traces[i][1], {})]
        return infos
    flt = [c for c in cons if is_filter(c)]; eqs = [c for c in cons if not is_filter(c)]
    need = bool(flt) or any(isinstance(k, tuple) for c in eqs for k in c['e'].d); sigs, r = {}, None
    def attempt(sigs):
        for _, (a, _n) in sorted(sigs.items(), key=lambda kv: -kv[1][1]):
            traces = run_all(a)
            rows = [resolve(c['e'], traces[_bi(c)][0], traces[_bi(c)][1]) for c in eqs]
            st, sol = solve_lin(rows, vs)
            if st == 'ok':
                asg = {v: float(sol[v]) for v in vs}
                if all(x > 1e-9 for x in asg.values()):
                    t2 = run_all(asg)
                    if all(cok(c, t2, asg) for c in cons): return asg, t2
        return None
    if not need: sigs = {None: [{v: .1 for v in vs}, 1]}; r = attempt(sigs)
    else:
        for seed in (7, 11, 13):
            rnd = random.Random(seed)
            for _ in range(200):
                a = {v: 10 ** rnd.uniform(-2.3, .3) for v in vs}
                traces = run_all(a)
                if all(cok(c, traces, a) for c in flt):
                    sig = tuple(signature(tr) for tr, fin in traces)
                    sigs.setdefault(sig, [a, 0])[1] += 1
            r = attempt(sigs) if eqs and sigs else None
            if r or not eqs: break
    if r:
        asg, traces = r
        for i in range(nb): infos[i].update(assign=asg, solved=True, tr=traces[i][0], fin=traces[i][1])
    else:
        ba = max(sigs.values(), key=lambda v: v[1])[0] if sigs else {v: .1 for v in vs}
        traces = run_all(ba)
        for i in range(nb): infos[i].update(assign=ba, tr=traces[i][0], fin=traces[i][1])
        infos[0]['msg'].append("ℹ Chưa đủ dữ kiện → hiển thị lời giải TỔNG QUÁT theo ẩn (số trong ngoặc vuông là minh họa)."
                               if not eqs else "⚠ Không tìm được nghiệm dương thỏa mãn các phương trình – hãy kiểm tra giả thiết.")
    return infos


# ---------- Trình bày toàn bộ "flow" của bài toán ----------
def scen_conds(steps):
    cs, seen = [], set()
    for st in steps:
        for f, b, d, a in st['tab'][:st['nR']]:
            if not a.isconst() and str(a) not in seen:
                seen.add(str(a)); cs.append(f"{a} > 0   ({sub(f)} còn dư sau bước)")
    return cs[:8]


def flow_lines(tr, info):
    asg, solved = info['assign'], info['solved']; cap = lambda t: t[0].upper() + t[1:]
    fe = lambda e, num=True: str(e) + (f" [{fm(e.ev(asg))}]" if num and solved and e.vars() else "")
    sg = lambda d: ('' if str(d).startswith('−') else '+') + str(d)
    gm = lambda f, e: f" ≈ {fm(e.ev(asg) * mass(f))} g" if (solved or e.isconst()) else ""
    out = []
    if info['vs']:
        out.append(("ẨN SỐ\n", 'h'))
        out.append((("  " + "    ".join(f"{v} = {fm(asg[v])}" for v in info['vs']) + "    ✔ đã giải\n") if solved
                    else "  Chưa xác định: " + ", ".join(info['vs']) + "\n", 'new' if solved else 'warn'))
    out += [("  " + m + "\n", 'warn') for m in info['msg']]
    for t in tr:
        if t['k'] == 'add': out.append((f"\n＋ {sub(t['f'])}: {t['desc']}  ⇒ n = {fe(t['e'])} mol\n", 'add'))
        elif t['k'] == 'keep':
            names = ", ".join(f"{sub(f)} ({fe(e)} mol)" for f, e in t['kept'].items()) or "(không có gì)"
            out.append((f"\n\n{'🧲 Lọc lấy chất rắn B' if t['kind'] == 'solid' else '💧 Lấy dung dịch A'}: {names}\n", 'keep'))
            rest = ", ".join(sub(f) for f in t['lost']) or "—"; out.append((f"   (phần bỏ đi / thoát ra: {rest})\n", 'dim'))
        else:
            out.append(("", 'mark'))
            _cdn = {'': 'điều kiện thường', 't°': 'đun nóng', 'đp': 'điện phân', 'đn': 'axit đặc nóng', 'đng': 'axit đặc nguội', 'lo': 'axit loãng'}
            out.append((f"\n\n▶ PHẢN ỨNG {t['n']}  ({_cdn.get(t['cond'], t['cond'])})\n", 'h'))
            if not t['steps']: out.append(("  Không có phản ứng nào xảy ra.\n", 'dim'))
            for i, st in enumerate(t['steps']):
                out.append((f"Bước {i + 1}:  {st['eq']}\n", 'step')); out.append((f"   ⚗ Chất hết: {st['lim']}\n", 'dim'))
                for f, b, d, a in st['tab']:
                    out.append((f"   n({sub(f)}): {fe(b, False)} → {fe(a)}   ({sg(d)})\n", 'tab'))
                out.append((f"   👁 {cap(st['obs'])}\n\n", 'dim'))
            if t['steps']:
                out.append((f"KẾT QUẢ SAU PHẢN ỨNG {t['n']}\n", 'h'))
                for f, e in t['after'].items():
                    new = any(f in st['P'] for st in t['steps']); mk_ = '↑' if SUBS[f]['st'] == 'g' and new else '↓' if SUBS[f]['st'] == 's' and new else ''
                    out.append((f"• {sub(f)}{mk_}: {fe(e)} mol{gm(f, e)}\n", 'new' if new else 'dim'))
                if not solved and info['vs']:
                    cs = scen_conds(t['steps'])
                    if cs: out.append(("\nĐIỀU KIỆN CỦA KỊCH BẢN NÀY\n", 'h')); out += [(f"  • {c}\n", 'cond') for c in cs]
    if not tr: out.append(("Chọn chất → nhập lượng (số hoặc ẩn x, y, z) → ➕ Thêm.\nSau đó bấm ▶ PHẢN ỨNG.\nBấm 📚 Ví dụ để xem các bài toán mẫu.\n", 'dim'))
    return out


PRESETS = [
    ("Al, Fe + Cu(NO₃)₂ → rắn B (2 kim loại); B + HCl → khí",
     [('Al', 'mol', 'x'), ('Fe', 'mol', 'y'), ('Cu(NO3)2', 'mol', 'z'), 'run', ('keep', 'solid'), ('HCl', 'M·ml', '2 500'), 'run'],
     ["rắn@1=Cu,Fe", "n(H2)@2>0"]),
    ("7,28 g hỗn hợp Fe, Cu + HCl dư → 2,24 lít H₂",
     [('Fe', 'mol', 'x'), ('Cu', 'mol', 'y'), ('HCl', 'M·ml', '1 500'), 'run'], ["m0(Fe)+m0(Cu)=7.28", "V(H2)=2.24"]),
    ("7,8 g Mg, Al + hỗn hợp HCl 1M & H₂SO₄ 0,5M → 8,96 lít H₂",
     [('Mg', 'mol', 'x'), ('Al', 'mol', 'y'), ('HCl', 'M·ml', '1 500'), ('H2SO4', 'M·ml', '0.5 500'), 'run'],
     ["m0(Mg)+m0(Al)=7.8", "V(H2)=8.96"]),
    ("0,1 mol C₂H₄, C₂H₂ + dung dịch Br₂ (đã dùng 0,16 mol Br₂)",
     [('C2H4', 'mol', 'x'), ('C2H2', 'mol', 'y'), ('Br2', 'mol', '0.5'), 'run'],
     ["n0(C2H4)+n0(C2H2)=0.1", "n0(Br2)-n(Br2)=0.16"]),
    ("Cu + H₂SO₄ đặc nóng → CuSO₄ + SO₂ + H₂O",
     [('Cu', 'mol', '0.1'), ('H2SO4', 'M·ml', '1 500'), 'run:đn'], ["V(SO2)=2.24"]),
    ("Halogen: Cl₂ + NaBr → NaCl + Br₂",
     [('Cl2', 'mol', '0.1'), ('NaBr', 'mol', '0.3'), 'run'], ["n(Br2)>0"]),
    ("Nitơ: N₂ + H₂ → NH₃ (t°, xt)",
     [('N2', 'mol', '0.1'), ('H2', 'mol', '0.3'), 'run:t°'], ["n(NH3)>0"]),
    ("FeO + HNO₃ loãng → Fe(NO₃)₃ + NO",
     [('FeO', 'mol', '0.1'), ('HNO3', 'M·ml', '2 500'), 'run:lo'], ["n(NO)>0"]),
    ("Thủy phân: Saccarozơ + H₂O → Glucozơ",
     [('C12H22O11', 'mol', '0.1'), ('H2O', 'M·ml', '1 500'), 'run:t°'], ["n(C6H12O6)>0"]),
    ("Photpho: P → P₂O₅ → H₃PO₄ → Ca₃(PO₄)₂ ↓",
     [('P', 'mol', '0.1'), ('O2', 'mol', '0.5'), 'run:t°', ('H2O', 'M·ml', '1 500'), 'run', ('Ca(OH)2', 'mol', '0.2'), 'run'],
     ["n(P2O5)@1>0"]),
    ("Thủy luyện: Zn + CuSO₄ → Cu + ZnSO₄ (đề 2025 câu 14)",
     [('Zn', 'mol', 'x'), ('CuSO4', 'mol', 'y'), 'run'],
     ["n(Cu)>0"]),
    ("Chuẩn độ: FeSO₄ + KMnO₄ + H₂SO₄ (đề 2025)",
     [('FeSO4', 'M·ml', '0.1 250'), ('KMnO4', 'M·ml', '0.022 10.7'), ('H2SO4', 'M·ml', '2 5'), 'run'],
     ["n(MnSO4)>0"]),
    ("Kiểm tra Ca²⁺: Ca(NO₃)₂ + Na₂CO₃ → CaCO₃ ↓ trắng (đề 2025 câu 16)",
     [('Ca(NO3)2', 'M·ml', '0.1 100'), ('Na2CO3', 'M·ml', '0.1 100'), 'run'],
     ["n(CaCO3)>0"]),
    ("Thuốc kháng acid: CaCO₃ + HCl → CaCl₂ + CO₂ + H₂O (đề 2026)",
     [('CaCO3', 'g', '0.256'), ('HCl', 'M·ml', '0.1017 25'), 'run'],
     ["V(CO2)>0"]),
    ("Haber-Bosch: CH₄ → CO+H₂ → NH₃ (đề 2026 Phần III)",
     [('CH4', 'mol', '0.1'), ('H2O', 'mol', '0.1'), 'run:t°', ('O2', 'mol', '0.05'), 'run:t°'],
     ["n(H2)@1>0"]),
    ("Ester hóa: C₂H₅OH + CH₃COOH → CH₃COOC₂H₅ (đề 2026 câu 11)",
     [('C2H5OH', 'mol', '0.1'), ('CH3COOH', 'mol', '0.1'), 'run:t°'],
     ["n(CH3COOC2H5)>0"]),
    ("Điện phân NaCl có màng ngăn (đề 2025 Phần II)",
     [('NaCl', 'M·ml', '1 500'), ('H2O', 'M·ml', '1 500'), 'run:đp'],
     ["n(NaOH)>0", "n(Cl2)>0"]),
    ("MnO₂ + HCl → Cl₂ (điều chế clo trong PTN)",
     [('MnO2', 'mol', '0.1'), ('HCl', 'M·ml', '2 500'), 'run:t°'],
     ["n(Cl2)>0"]),
    ("Na + H₂O → NaOH + H₂ (thí nghiệm SGK lớp 12)",
     [('Na', 'mol', '0.05'), ('H2O', 'M·ml', '1 500'), 'run'],
     ["n(H2)>0"]),
    ("Fe + CuSO₄ → Cu (thí nghiệm SGK dãy hoạt động)",
     [('Fe', 'mol', '0.1'), ('CuSO4', 'M·ml', '0.5 200'), 'run'],
     ["n(Cu)>0"]),
    ("AgNO₃ + NaCl → AgCl ↓ trắng (nhận biết ion Cl⁻)",
     [('AgNO3', 'M·ml', '0.1 100'), ('NaCl', 'M·ml', '0.1 100'), 'run'],
     ["n(AgCl)>0"]),
    ("Al + NaOH + H₂O → NaAlO₂ + H₂ (tính lưỡng tính Al)",
     [('Al', 'mol', '0.1'), ('NaOH', 'M·ml', '1 500'), 'run'],
     ["n(H2)>0"]),
    ("Tráng gương: CH₃CHO + AgNO₃/NH₃ → Ag ↓ (SGK lớp 11)",
     [('CH3CHO', 'mol', '0.05'), ('AgNO3', 'mol', '0.2'), ('NH3', 'mol', '0.6'), ('H2O', 'M·ml', '1 100'), 'run:t°'],
     ["n(Ag)>0"]),
    ("Chuẩn độ acid-base: HCl + NaOH (phenolphtalein)",
     [('HCl', 'M·ml', '0.1 25'), ('NaOH', 'M·ml', '0.1 25'), 'run'],
     ["n(HCl)=0"]),
    ("Chuẩn độ: NaHCO₃ + HCl → NaCl + CO₂ + H₂O",
     [('NaHCO3', 'g', '0.256'), ('HCl', 'M·ml', '0.1017 25'), 'run'],
     ["V(CO2)>0"]),
    ("Chuẩn độ oxi hóa khử: Fe²⁺ + KMnO₄ (H₂SO₄)",
     [('FeSO4', 'M·ml', '0.1 10'), ('H2SO4', 'M·ml', '2 5'), ('KMnO4', 'M·ml', '0.022 10.7'), 'run'],
     ["n(MnSO4)>0"])]


class Game:
    def __init__(s):
        global W, H, LW, LH
        s.root = tk.Tk(); s.root.title("⚗ HÓA HỌC LAB")
        s.root.state('zoomed')
        s.root.update_idletasks()
        SW = s.root.winfo_width() or s.root.winfo_screenwidth()
        SH = s.root.winfo_height() or s.root.winfo_screenheight()
        W, H = SW, SH; LW, LH = SW, SH
        s.c = tk.Canvas(s.root, bg=BG, highlightthickness=0); s.c.pack(fill='both', expand=True)
        s.entry = s.enter = None; s.ws = []; s.bub = []; s.best = 0; s.t = 0; s.screen = 'menu'; s.parts = []
        for _ in range(40):
            r = random.randint(6, 18); x, y = random.randint(0, SW), random.randint(0, SH)
            col = mix(random.choice(list(COL.values())), BG, .22)
            s.parts.append([s.c.create_oval(x - r, y - r, x + r, y + r, fill=col, outline='', tags='bg'),
                            x, y, random.uniform(-.8, .8), random.uniform(-.8, .8), r])
        s.root.bind('<Return>', lambda e: s.enter and s.enter())
        s.root.bind('<Escape>', lambda e: s.root.state('zoomed') if s.root.attributes('-fullscreen') else None)
        s.root.bind('<F11>', lambda e: s.root.attributes('-fullscreen', not s.root.attributes('-fullscreen')))
        s.menu(); s.tick(); s.root.mainloop()

    # ---------- tiện ích vẽ ----------
    def rr(s, x, y, w, h, r=14, **kw):
        p = [x + r, y, x + w - r, y, x + w, y, x + w, y + r, x + w, y + h - r, x + w, y + h, x + w - r, y + h,
             x + r, y + h, x, y + h, x, y + h - r, x, y + r, x, y]
        return s.c.create_polygon(p, smooth=True, **kw)

    def txt(s, x, y, t, size=14, col='white', b=True, **kw):
        return s.c.create_text(x, y, text=t, fill=col, font=F(size, b), tags='ui', **kw)

    def btn(s, x, y, w, h, t, cmd, col=ACC, fs=15, fg=BG):
        tag = f"b{random.random()}"
        s.rr(x + 2, y + 4, w, h, fill=mix(col, BG, .35), tags=('ui', tag))
        s.rr(x, y, w, h, fill=col, tags=('ui', tag))
        s.c.create_text(x + w / 2, y + h / 2, text=t, fill=fg, font=F(fs), tags=('ui', tag))
        s.c.tag_bind(tag, '<Button-1>', lambda e: cmd())
        s.c.tag_bind(tag, '<Enter>', lambda e: s.c.config(cursor='hand2'))
        s.c.tag_bind(tag, '<Leave>', lambda e: s.c.config(cursor=''))

    def clear(s):
        s.c.delete('ui'); s.c.delete('anim')
        for w in s.ws + ([s.entry] if s.entry else []): w.destroy()
        s.ws = []; s.entry = s.enter = None

    def header(s):
        s.c.create_rectangle(0, 0, W, 56, fill=PANEL, outline='', tags='ui')
        cx = W // 2
        s.txt(20, 28, "⚗ HÓA HỌC LAB", 16, ACC, anchor='w')
        s.txt(cx - 100, 28, f"★ {s.score}", 16, GOLD)
        s.txt(cx, 28, f"🔥 x{s.streak}", 14, '#fb923c')
        s.txt(cx + 120, 28, "♥ " * s.lives + "♡ " * (3 - s.lives), 18, BAD)
        s.btn(W - 110, 12, 90, 32, "☰ Menu", s.menu, '#334155', 12, 'white')

    def mol(s, cx, cy, f):
        atoms = [e for e, n in sorted(parse(f).items(), key=lambda kv: kv[1]) for _ in range(n)]
        pos = [(cx + 15 * math.sqrt(k) * math.cos(k * 2.39996), cy + 15 * math.sqrt(k) * math.sin(k * 2.39996))
               for k in range(len(atoms))]
        for x, y in pos[1:]: s.c.create_line(cx, cy, x, y, fill='#64748b', width=3, tags='ui')
        for (x, y), e in zip(pos, atoms):
            s.c.create_oval(x - 11, y - 11, x + 11, y + 11, fill=COL[e], outline=mix(COL[e], '#000000', .5), width=2, tags='ui')
            s.c.create_text(x, y, text=e, font=F(8), fill='#0b1020', tags='ui')

    def row(s, items, nleft, ymol, ytxt, ctrl=False):
        slot = (W - 40) / len(items)
        for i, (f, c) in enumerate(items):
            cx = 20 + slot * (i + .5); s.mol(cx, ymol, f)
            s.txt(cx, ytxt, sub(f) if ctrl else f"{c if c > 1 else ''}{sub(f)}", 22)
            if ctrl:
                s.btn(cx - 58, ytxt + 28, 32, 32, "−", lambda i=i: s.bump(i, -1), '#475569', 18, 'white')
                s.txt(cx, ytxt + 44, str(c), 22, GOLD)
                s.btn(cx + 26, ytxt + 28, 32, 32, "+", lambda i=i: s.bump(i, 1), ACC, 18)
            if i < len(items) - 1:
                s.txt(20 + slot * (i + 1), ytxt, "→" if i == nleft - 1 else "+", 26, ACC)

    def reset(s, mode):
        s.mode, s.score, s.lives, s.streak = mode, 0, 3, 0; s.next_q()

    # ---------- màn hình ----------
    def menu(s):
        s.clear(); s.screen = 'menu'
        cx, cy = W / 2, H / 2
        s.txt(cx, cy - 230, "⚗ HÓA HỌC LAB", 48, ACC)
        s.txt(cx, cy - 180, "Chơi – Học – Giải bài toán Hóa học", 16, '#94a3b8', False)
        for k, (t, m, col) in enumerate([("🧫  Phòng thí nghiệm TỰ DO", 'lab', '#fb7185'),
                                         ("⚖  Cân bằng phương trình", 'bal', '#2dd4bf'),
                                         ("🧮  Bài toán mol & phản ứng", 'rx', '#a78bfa'),
                                         ("🧪  Tính pH dung dịch", 'ph', '#fbbf24')]):
            s.btn(cx - 200, cy - 50 + k * 72, 400, 58, t, lambda m=m: s.lab_open() if m == 'lab' else s.reset(m), col, 19)
        s.txt(cx, cy + 260, f"Điểm cao nhất: {s.best}", 14, GOLD)
        s.txt(cx, cy + 288, "Chế độ thử thách: sai 3 lần là thua • Phòng thí nghiệm: tự do không giới hạn  |  F11 = toàn màn hình", 11, '#64748b', False)

    def atom(s):
        s.c.delete('anim'); cx, cy = W / 2, H / 2 - 80
        for k in range(3):
            phi = k * math.pi / 3
            pts = []
            for j in range(0, 361, 10):
                a = math.radians(j)
                pts += [cx + 85 * math.cos(a) * math.cos(phi) - 28 * math.sin(a) * math.sin(phi),
                        cy + 85 * math.cos(a) * math.sin(phi) + 28 * math.sin(a) * math.cos(phi)]
            s.c.create_line(pts, fill='#334155', width=2, tags='anim')
            a = s.t * (.07 + .02 * k) + k * 2
            x = cx + 85 * math.cos(a) * math.cos(phi) - 28 * math.sin(a) * math.sin(phi)
            y = cy + 85 * math.cos(a) * math.sin(phi) + 28 * math.sin(a) * math.cos(phi)
            s.c.create_oval(x - 7, y - 7, x + 7, y + 7, fill=ACC, outline='white', tags='anim')
        r = 16 + 2 * math.sin(s.t * .15)
        s.c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=GOLD, outline='#fff7d6', width=3, tags='anim')

    def tick(s):
        s.t += 1
        for p in s.parts:
            s.c.move(p[0], p[3], p[4]); p[1] += p[3]; p[2] += p[4]
            if p[1] < -30: s.c.move(p[0], W + 60, 0); p[1] += W + 60
            if p[1] > W + 30: s.c.move(p[0], -W - 60, 0); p[1] -= W + 60
            if p[2] < -30: s.c.move(p[0], 0, H + 60); p[2] += H + 60
            if p[2] > H + 30: s.c.move(p[0], 0, -H - 60); p[2] -= H + 60
        if s.screen == 'menu': s.atom()
        elif s.screen == 'lab': s.lab_anim()
        s.root.after(40, s.tick)

    def next_q(s):
        if s.lives <= 0: return s.over()
        s.msg = None; s.done = False
        if s.mode == 'bal':
            s.screen = 'bal'; old = getattr(s, 'eq', None)
            s.eq = random.choice([e for e in EQS if e != old]); s.co = [1] * (len(s.eq[0]) + len(s.eq[1])); s.draw_bal()
        else:
            s.screen = 'calc'; s.q = random.choice([q_mol, q_rx])() if s.mode == 'rx' else q_ph()
            s.val, s.res = "", None; s.draw_calc()

    # ----- Cân bằng phương trình -----
    def bump(s, i, d):
        if s.done: return
        s.co[i] = max(1, min(9, s.co[i] + d)); s.msg = None; s.draw_bal()

    def draw_bal(s):
        s.clear(); s.header(); k = len(s.eq[0])
        s.txt(W / 2, 84, "Cân bằng phương trình hóa học", 20, ACC)
        s.txt(W / 2, 108, "Chỉnh hệ số sao cho số nguyên tử mỗi vế bằng nhau (hệ số tối giản)", 12, '#94a3b8', False)
        items = list(zip(s.eq[0] + s.eq[1], s.co)); s.row(items, k, 205, 295, True)
        L, R = counts(items[:k]), counts(items[k:])
        s.txt(W / 2, 392, "Số nguyên tử mỗi vế", 13, '#94a3b8')
        for j, e in enumerate(L):
            y = 420 + j * 28; ok = L[e] == R.get(e)
            col = OK if ok else BAD
            s.rr(440 - L[e] * 12, y - 9, L[e] * 12, 18, 8, fill=col, tags='ui')
            if R.get(e): s.rr(460, y - 9, R.get(e, 0) * 12, 18, 8, fill=col, tags='ui')
            s.txt(450, y, e, 12, COL[e]); s.txt(436 - L[e] * 12, y, str(L[e]), 11, 'white', anchor='e')
            s.txt(464 + R.get(e, 0) * 12, y, str(R.get(e, 0)), 11, 'white', anchor='w')
        if s.done: s.btn(360, 548, 180, 46, "Tiếp →" if s.lives else "Kết thúc", s.next_q, GOLD, 16); s.enter = s.next_q
        else: s.btn(360, 548, 180, 46, "✔ Kiểm tra", s.check_bal, ACC, 16); s.enter = s.check_bal
        if s.msg: s.txt(W / 2, 622, s.msg[0], 15, s.msg[1], width=800, justify='center')

    def check_bal(s):
        k = len(s.eq[0]); items = list(zip(s.eq[0] + s.eq[1], s.co))
        if counts(items[:k]) == counts(items[k:]):
            if reduce(gcd, s.co) == 1:
                s.score += 10 + 2 * s.streak; s.streak += 1; s.done = True
                s.msg = ("✅ Chính xác! " + eqstr(items[:k]) + " → " + eqstr(items[k:]), OK)
            else: s.msg = ("Đã cân bằng nhưng chưa tối giản – hãy chia các hệ số cho ước chung!", GOLD)
        else:
            s.lives -= 1; s.streak = 0; s.msg = ("❌ Chưa cân bằng – nhìn các thanh đỏ để biết nguyên tố nào lệch!", BAD)
            if s.lives <= 0:
                sol = solve_eq(s.eq); k = len(s.eq[0]); a = list(zip(s.eq[0] + s.eq[1], sol))
                s.msg = ("Đáp án: " + eqstr(a[:k]) + " → " + eqstr(a[k:]), BAD); s.done = True
        s.draw_bal()

    # ----- Bài toán tính toán -----
    def draw_calc(s):
        s.clear(); s.header(); q = s.q
        s.txt(W / 2, 84, {'rx': "Bài toán Hóa học", 'ph': "Tính pH dung dịch"}[s.mode], 20, ACC)
        s.rr(40, 110, 820, 90, fill=PANEL, tags='ui')
        s.txt(W / 2, 155, q['text'], 17, width=770, justify='center')
        if 'rx' in q:
            R, P = q['rx']; s.row(R + P, len(R), 275, 345)
        s.e = tk.Entry(s.root, font=F(22), width=9, justify='center', bg='#1e293b', fg='white',
                       insertbackground='white', relief='flat')
        s.e.insert(0, s.val); s.entry = s.e
        s.c.create_window(430, 415, window=s.e, tags='ui'); s.txt(540, 415, q['unit'], 18, GOLD, anchor='w')
        if s.res is None:
            s.e.focus_set(); s.btn(360, 450, 180, 44, "✔ Kiểm tra", s.check_calc, ACC, 16); s.enter = s.check_calc
        else:
            s.e.config(state='disabled'); s.enter = s.next_q
            s.rr(40, 510, 820, 120, fill=PANEL, tags='ui')
            s.txt(60, 528, ("✅ Chính xác!" if s.res else f"❌ Sai rồi! Đáp án: {g(q['ans'])} {q['unit']}"), 15,
                  OK if s.res else BAD, anchor='w')
            s.txt(60, 575, "\n".join(q['steps']), 13, '#cbd5e1', False, anchor='w', width=780)
            s.btn(710, 450, 150, 44, "Tiếp →" if s.lives else "Kết thúc", s.next_q, GOLD, 16)
        if s.msg: s.txt(W / 2, 485, s.msg[0], 12, BAD)

    def check_calc(s):
        s.val = s.e.get().strip(); s.msg = None
        try: x = float(s.val.replace(',', '.'))
        except ValueError:
            s.msg = ("Hãy nhập một con số (ví dụ 2.24)", BAD); return s.draw_calc()
        tol = s.q.get('tol', max(.02, .01 * abs(s.q['ans'])))
        s.res = abs(x - s.q['ans']) <= tol
        if s.res: s.score += 10 + 2 * s.streak; s.streak += 1
        else: s.lives -= 1; s.streak = 0
        s.draw_calc()

    # ================= PHÒNG THÍ NGHIỆM: KỊCH BẢN BÀI TOÁN =================
    UNITS = ['mol', 'gam', 'lít', 'M·ml', '%·g']
    HINT = {'mol': "Số mol, VD: 0.1  •  hoặc ẩn: x, 2y", 'gam': "Khối lượng (g), VD: 7.28  •  hoặc ẩn: x",
            'lít': "Thể tích khí đktc (lít), VD: 2.24", 'M·ml': "Dung dịch: C_M rồi V(ml), VD: 0.5 200",
            '%·g': "Dung dịch: C% rồi m_dd(g), VD: 20 150"}
    CONDN = {'': "thường", 't°': "🔥 đun nóng", 'đp': "⚡ điện phân",
              'đn': "🧪 đặc nóng", 'đng': "🧊 đặc nguội", 'lo': "💧 loãng"}

    def _mk_beaker(s, name="Bình 1"):
        return dict(name=name, prog=[], cond='', lc0=BASE, lc1=BASE, t0=-999, ppt=[], gasfx=False, vm={}, info=None, flow=[])

    def lab_open(s):
        s.mode = 'lab'; s.bub = []
        s.lab = dict(beakers=[s._mk_beaker("Bình 1")], cur_bk=0,
                     cons=[], tab=0, sel=None, amt='0.1', unit='mol', cx='', note=None, preset=-1)
        s.refresh()

    def _bk(s): return s.lab['beakers'][s.lab['cur_bk']]

    def lab_add_beaker(s):
        s.sv(); L = s.lab; n = len(L['beakers']) + 1
        L['beakers'].append(s._mk_beaker(f"Bình {n}")); L['cur_bk'] = n - 1; s.refresh()

    def lab_switch_bk(s, i):
        s.sv(); s.lab['cur_bk'] = i; s.draw_lab()

    def lab_del_beaker(s, i):
        s.sv(); L = s.lab
        if len(L['beakers']) <= 1: return
        del L['beakers'][i]
        L['cons'] = [c for c in L['cons'] if c.get('bk', 0) != i]
        for c in L['cons']:
            if c.get('bk', 0) > i: c['bk'] -= 1
        if L['cur_bk'] >= len(L['beakers']): L['cur_bk'] = len(L['beakers']) - 1
        s.refresh()

    def refresh(s, run=False):
        """Chạy lại toàn bộ kịch bản cho tất cả bình (giải ẩn chung, mô phỏng) rồi vẽ lại."""
        L = s.lab; nb = len(L['beakers'])
        if nb == 1:
            L['beakers'][0]['info'] = analyze(L['beakers'][0]['prog'], L['cons'])
        else:
            progs = [bk['prog'] for bk in L['beakers']]
            infos = analyze_multi(progs, L['cons'])
            for i, bk in enumerate(L['beakers']): bk['info'] = infos[i]
        for bk in L['beakers']:
            info = bk['info']; a = info['assign']
            bk['vm'] = {f: v for f, v in ((f, e.ev(a)) for f, e in info['fin'].items()) if v > 1e-9}
            bk['lc0'] = bk['lc1']; bk['lc1'] = liquid_color(bk['vm']); runs = [t for t in info['tr'] if t['k'] == 'run']
            is_cur = bk is s._bk()
            if run and is_cur and runs:
                sts = runs[-1]['steps']
                bk['ppt'] = [SUBS[f]['col'] for st in sts if any(SUBS[x]['st'] == 'aq' for x in st['R']) for f in st['P'] if SUBS[f]['st'] == 's']
                bk['gasfx'] = any(SUBS[f]['st'] == 'g' and f not in st['R'] for st in sts for f in st['P']); bk['t0'] = s.t
            elif not (is_cur and run):
                bk['lc0'] = bk['lc1']; bk['ppt'] = []; bk['gasfx'] = False; bk['t0'] = -999
            bk['flow'] = flow_lines(info['tr'], info)
        s.draw_lab()

    def sv(s):
        for e, k in ((s.entry, 'amt'), (getattr(s, 'e2', None), 'cx')):
            try:
                if e: s.lab[k] = e.get()
            except tk.TclError: pass

    def note(s, msg): s.sv(); s.lab['note'] = msg; s.draw_lab()
    def lab_tab(s, i): s.sv(); s.lab['tab'] = i; s.draw_lab()
    def lab_pick(s, f): s.sv(); s.lab['sel'] = f; s.draw_lab()
    def lab_unit(s): s.sv(); u = s.UNITS; s.lab['unit'] = u[(u.index(s.lab['unit']) + 1) % len(u)]; s.draw_lab()
    def lab_cond(s):
        s.sv(); bk = s._bk(); c = ['', 'lo', 'đn', 'đng', 't°', 'đp']
        cur = bk.get('cond', ''); bk['cond'] = c[(c.index(cur) + 1) % len(c)]; s.draw_lab()

    def lab_show_ir(s, f):
        ct = CTCT.get(f)
        if not ct or not ct[2]: return
        lines = [f"── Phổ hồng ngoại (IR) của {sub(f)} ──\n"]
        lines.append(f"CTCT: {ct[0]}   Loại: {ct[1]}\n")
        lines.append(f"{'Liên kết':<16} {'Số sóng (cm⁻¹)':<20} {'Cường độ'}")
        lines.append("─" * 50)
        for grp in ct[2]:
            if grp in IR_BANDS:
                hi, lo, strength = IR_BANDS[grp]
                lines.append(f"{grp:<16} {lo}–{hi:<20} {strength}")
        s.note("\n".join(lines))

    def lab_lookup(s):
        s.sv(); s.clear(); s.screen = 'lookup'; c = s.c
        c.create_rectangle(0, 0, LW, 56, fill=PANEL, outline='', tags='ui')
        s.txt(16, 28, "📖 TRA CỨU CHẤT HỮU CƠ • CÔNG THỨC CẤU TẠO & PHỔ IR", 14, ACC, anchor='w')
        s.btn(LW - 118, 12, 102, 32, "← Quay lại", s.draw_lab, '#334155', 12, 'white')
        y = 74; col1, col2, col3 = 20, 160, 380
        s.txt(col1, y, "Công thức", 11, GOLD, anchor='w')
        s.txt(col2, y, "CTCT  •  Loại", 11, GOLD, anchor='w')
        s.txt(col3, y, "Phổ IR đặc trưng (cm⁻¹)", 11, GOLD, anchor='w')
        y += 24
        c.create_line(14, y - 4, LW - 14, y - 4, fill='#334155', tags='ui')
        for f, (ctct, loai, groups) in sorted(CTCT.items(), key=lambda x: x[1][1]):
            if y > LH - 30: break
            s.txt(col1, y, sub(f), 10, 'white', anchor='w')
            s.txt(col2, y, f"{ctct}  •  {loai}", 9, '#c4b5fd', False, anchor='w', width=210)
            if groups:
                ir_txt = "  ".join(f"{g}: {IR_BANDS[g][1]}–{IR_BANDS[g][0]}" for g in groups if g in IR_BANDS)
                s.txt(col3, y, ir_txt, 8, '#a5b4fc', False, anchor='w', width=LW - col3 - 20)
            y += 22
        y += 16; c.create_line(14, y, LW - 14, y, fill='#334155', tags='ui'); y += 12
        s.txt(20, y, "── Bảng tham chiếu phổ IR ──", 12, GOLD, anchor='w'); y += 26
        s.txt(20, y, f"{'Nhóm chức':<20} {'Số sóng (cm⁻¹)':<20} {'Đặc điểm'}", 10, '#94a3b8', False, anchor='w'); y += 18
        for grp, (hi, lo, desc) in IR_BANDS.items():
            if y > LH - 20: break
            s.txt(20, y, f"{grp:<20} {lo}–{hi:<20} {desc}", 9, '#cbd5e1', False, anchor='w')
            y += 17

    def lab_enter(s):
        if s.root.focus_get() is getattr(s, 'e2', None): s.lab_cons_add()
        else: s.lab_add()

    def lab_add(s):
        s.sv(); L = s.lab; bk = s._bk(); f = L['sel']
        if not f: return s.note("⚠ Hãy chọn một chất ở bảng phía trên.")
        try: e, d = build_add(f, L['amt'], L['unit'])
        except ValueError as ex: return s.note(f"⚠ {ex}")
        bk['prog'].append(('add', f, e, d)); L['note'] = None; s.refresh()

    def lab_cons_add(s):
        s.sv(); L = s.lab
        if not L['cx'].strip(): return s.note("⚠ Hãy nhập giả thiết, VD: m0(Fe)+m0(Cu)=7.28")
        try: c = parse_cons(L['cx'])
        except ValueError as ex: return s.note(f"⚠ {ex}")
        c['bk'] = L['cur_bk']
        L['cons'].append(c); L['cx'] = ''; L['note'] = None; s.refresh()

    def lab_run(s):
        s.sv(); L = s.lab; cur = L['cur_bk']; bk = L['beakers'][cur]
        if not any(a[0] == 'add' for a in bk['prog']): return s.note("⚠ Bình đang trống – hãy thêm chất trước.")
        bk['prog'].append(('run', bk.get('cond', ''))); L['note'] = None; L['cur_bk'] = cur; s.refresh(run=True)

    def lab_keep(s, kind):
        s.sv(); bk = s._bk()
        if not any(a[0] == 'run' for a in bk['prog']): return s.note("⚠ Cần chạy phản ứng trước khi lọc/tách.")
        bk['prog'].append(('keep', kind)); s.lab['note'] = None; s.refresh()

    def lab_del(s, i): s.sv(); del s._bk()['prog'][i]; s.refresh()
    def lab_cdel(s, i): s.sv(); del s.lab['cons'][i]; s.refresh()
    def lab_undo(s):
        s.sv(); bk = s._bk()
        if bk['prog']: bk['prog'].pop()
        s.refresh()

    def lab_clear(s):
        s.sv(); s._bk()['prog'] = []; s.lab['note'] = None; s.refresh()

    def lab_clear_all(s):
        s.sv(); s.lab['beakers'] = [s._mk_beaker("Bình 1")]; s.lab['cur_bk'] = 0; s.lab['cons'] = []; s.lab['note'] = None; s.refresh()

    def lab_preset(s):
        s.sv(); L = s.lab; L['preset'] = (L['preset'] + 1) % len(PRESETS); _, steps, cons = PRESETS[L['preset']]
        bk = s._bk(); bk['prog'] = []; bk['cond'] = ''
        for it in steps:
            if isinstance(it, str) and it.startswith('run'):
                cd = it.split(':')[1] if ':' in it else ''
                bk['prog'].append(('run', cd))
            elif isinstance(it, str) and it == 'run': bk['prog'].append(('run', ''))
            elif isinstance(it, tuple) and len(it) == 2: bk['prog'].append(('keep', it[1]))
            else: e, d = build_add(it[0], it[2], it[1]); bk['prog'].append(('add', it[0], e, d))
        L['cons'] = [parse_cons(x) for x in cons]
        for c_ in L['cons']: c_['bk'] = 0
        L['note'] = None; s.refresh(run=True)

    def draw_lab(s):
        s.clear(); s.screen = 'lab'; L = s.lab; bk = s._bk(); info = bk['info']; c = s.c
        PW = 386; BKW = min(400, (LW - PW - 20) // 2); TXW = LW - PW - BKW - 30
        c.create_rectangle(0, 0, LW, 56, fill=PANEL, outline='', tags='ui')
        s.txt(16, 28, "🧫 PHÒNG THÍ NGHIỆM • GIẢI BÀI TOÁN HÓA HỌC", 15, ACC, anchor='w')
        if L['preset'] >= 0: s.txt(520, 28, "📚 " + PRESETS[L['preset']][0], 11, '#c4b5fd', False, anchor='w', width=430)
        s.btn(LW - 350, 12, 106, 32, "📖 Tra cứu", s.lab_lookup, '#6366f1', 12, 'white')
        s.btn(LW - 232, 12, 106, 32, "📚 Ví dụ", s.lab_preset, '#7c3aed', 12, 'white')
        s.btn(LW - 118, 12, 102, 32, "☰ Menu", s.menu, '#334155', 12, 'white')
        for i, (_bkd) in enumerate(L['beakers']):
            on = i == L['cur_bk']; bx = PW + 10 + i * 90
            s.btn(bx, 62, 84, 26, f"Bình {i+1}", lambda i=i: s.lab_switch_bk(i), GOLD if on else '#334155', 11, BG if on else 'white')
            if len(L['beakers']) > 1:
                s.btn(bx + 68, 62, 16, 16, "✕", lambda i=i: s.lab_del_beaker(i), '#7f1d1d', 7, 'white')
        nb = len(L['beakers']); bx_add = PW + 10 + nb * 90
        if nb < 5: s.btn(bx_add, 62, 84, 26, "+ Thêm bình", s.lab_add_beaker, '#0ea5e9', 10, 'white')
        for i, (nm, _) in enumerate(TABS):
            on = i == L['tab']
            s.btn(14 + (i % 5) * 72, 62 + (i // 5) * 28, 68, 24, nm, lambda i=i: s.lab_tab(i), ACC if on else '#334155', 8, BG if on else 'white')
        for k, f in enumerate(TABS[L['tab']][1]):
            on = f == L['sel']
            s.btn(14 + (k % 3) * 120, 150 + (k // 3) * 32, 114, 28, sub(f), lambda f=f: s.lab_pick(f), GOLD if on else mix(SUBS[f]['col'], '#1e293b', .4), 12, BG if on else 'white')
        d = SUBS.get(L['sel']); _ct = CTCT.get(L['sel'])
        s.txt(14, 290, "Chọn một chất ở trên, nhập lượng rồi bấm ➕ Thêm" if not d else
              f"{sub(L['sel'])} – {d['n']} • M = {g(mass(L['sel']))} g/mol • {STN[d['st']]}" + (f" • màu {d['cn']}" if d['cn'] else ""),
              10, '#cbd5e1', False, anchor='w', width=360)
        if _ct:
            s.txt(14, 308, f"CTCT: {_ct[0]}  •  Loại: {_ct[1]}", 9, '#a5b4fc', False, anchor='w', width=300)
            if _ct[2]: s.btn(320, 300, 50, 20, "Phổ IR", lambda: s.lab_show_ir(L['sel']), '#6366f1', 8, 'white')
        e = tk.Entry(s.root, font=F(15), width=12, justify='center', bg='#1e293b', fg='white', insertbackground='white', relief='flat')
        e.insert(0, L['amt']); s.entry = e; c.create_window(110, 340, window=e, tags='ui')
        s.btn(206, 322, 70, 36, L['unit'], s.lab_unit, '#475569', 13, 'white'); s.btn(282, 322, 92, 36, "➕ Thêm", s.lab_add, ACC, 13)
        s.txt(14, 370, s.HINT[L['unit']], 10, '#94a3b8', False, anchor='w')
        _ht = "🎯 Giả thiết gán cho bình đang chọn • VD: V(H2)=8.96" if nb > 1 else "🎯 Giả thiết: m0(Fe)+m0(Cu)=7.28 • V(H2)=2.24 • rắn@1=Cu,Fe"
        s.txt(14, 392, _ht, 9, '#94a3b8', False, anchor='w')
        e2 = tk.Entry(s.root, font=F(11), width=27, bg='#1e293b', fg='white', insertbackground='white', relief='flat')
        e2.insert(0, L['cx']); s.e2 = e2; s.ws.append(e2); c.create_window(146, 420, window=e2, tags='ui')
        s.btn(282, 404, 92, 32, "＋ Giả thiết", s.lab_cons_add, '#a78bfa', 11)
        for i, cn in enumerate(L['cons'][:5]):
            y = 454 + i * 18; btag = f"[B{cn.get('bk',0)+1}] " if nb > 1 else ""
            s.txt(18, y, "• " + btag + cn['text'], 10, '#ddd6fe', False, anchor='w', width=310)
            s.btn(344, y - 8, 28, 16, "✕", lambda i=i: s.lab_cdel(i), '#7f1d1d', 8, 'white')
        s.rr(14, 548, 360, 54, fill=PANEL, tags='ui')
        if info and info['vs']:
            a = info['assign']
            st = ("  ".join(f"{v} = {fm(a[v])}" for v in info['vs']) + "  ✔") if info['solved'] else "Ẩn chưa xác định: " + ", ".join(info['vs'])
            s.txt(24, 563, "🧮 " + st, 11, OK if info['solved'] else GOLD, anchor='w', width=340)
        else: s.txt(24, 563, "🧮 Không có ẩn số (mọi lượng chất đã biết)", 10, '#94a3b8', False, anchor='w')
        msg = L['note'] or (info['msg'][0] if info and info['msg'] else "")
        if msg: s.txt(24, 585, msg, 9, BAD if msg.startswith('⚠') else '#94a3b8', False, anchor='w', width=345)
        _cd = bk.get('cond', '')
        _ccol = {'': '#334155', 't°': '#ea580c', 'đp': '#7c3aed', 'đn': '#dc2626', 'đng': '#0369a1', 'lo': '#0d9488'}
        _runcol = GOLD if _cd == '' else _ccol.get(_cd, GOLD)
        _runtxt = "▶  PHẢN ỨNG" if _cd == '' else f"▶ PƯ ({s.CONDN[_cd]})"
        s.btn(14, 610, 176, 40, _runtxt, s.lab_run, _runcol, 13 if _cd else 16)
        s.btn(196, 610, 130, 40, "Đk: " + s.CONDN[_cd], s.lab_cond, _ccol.get(_cd, '#334155'), 11, 'white')
        s.btn(332, 610, 42, 40, "🗑", s.lab_clear, '#7f1d1d', 15, 'white')
        s.btn(14, 658, 118, 38, "🧲 Lọc rắn B", lambda: s.lab_keep('solid'), '#0ea5e9', 11)
        s.btn(138, 658, 118, 38, "💧 Giữ dd A", lambda: s.lab_keep('dd'), '#38bdf8', 11)
        s.btn(262, 658, 112, 38, "↶ Hoàn tác", s.lab_undo, '#475569', 11, 'white')
        bkx = PW + 10; bky = 94
        s.rr(bkx, bky, BKW, 280, fill=PANEL, tags='ui')
        s.txt(bkx + 10, bky + 16, f"Bình {L['cur_bk']+1}", 12, '#94a3b8', anchor='w')
        sx = bkx + 10; sy = bky + 280 + 14
        s.rr(bkx, sy, BKW, LH - sy - 10, fill=PANEL, tags='ui')
        s.txt(bkx + 10, sy + 16, f"📋 Kịch bản bình {L['cur_bk']+1}", 12, ACC, anchor='w')
        prog = bk['prog']
        if not prog: s.txt(bkx + BKW // 2, sy + 100, "Chưa có bước nào", 12, '#64748b', False)
        max_lines = max(1, (LH - sy - 50) // 22)
        start = max(0, len(prog) - max_lines)
        for j, a in enumerate(prog[start:]):
            i = start + j; y = sy + 42 + j * 22
            txt, col = ((f"＋ {sub(a[1])}   {a[3]}", 'white') if a[0] == 'add' else
                        (f"▶ Phản ứng ({s.CONDN[a[1]]})", GOLD) if a[0] == 'run' else
                        ("🧲 Lọc lấy chất rắn B" if a[1] == 'solid' else "💧 Lấy dung dịch A", '#7dd3fc'))
            s.txt(bkx + 8, y, f"{i + 1}. {txt}", 10, col, False, anchor='w', width=BKW - 40)
            s.btn(bkx + BKW - 32, y - 9, 24, 18, "✕", lambda i=i: s.lab_del(i), '#7f1d1d', 8, 'white')
        tx = bkx + BKW + 10; ty = 94
        t = tk.Text(s.root, bg='#10172e', fg='#cbd5e1', font=F(11, False), wrap='word', relief='flat', padx=10, pady=8,
                    highlightthickness=0, cursor='arrow')
        for tg, kw in (('h', dict(foreground=GOLD, font=F(12), spacing1=4)), ('step', dict(foreground='white', font=F(11))),
                       ('tab', dict(foreground='#cbd5e1', font=("Courier", 10))), ('dim', dict(foreground='#94a3b8')),
                       ('new', dict(foreground=OK)), ('warn', dict(foreground=BAD)), ('add', dict(foreground='#5eead4')),
                       ('keep', dict(foreground='#7dd3fc', font=F(11))), ('cond', dict(foreground='#c4b5fd'))): t.tag_config(tg, **kw)
        for txt_, tag in bk.get('flow', []):
            if tag == 'mark': t.mark_set('lastrun', 'end-1c'); t.mark_gravity('lastrun', 'left')
            else: t.insert('end', txt_, tag)
        t.config(state='disabled'); s.ws.append(t)
        if 'lastrun' in t.mark_names(): t.yview('lastrun')
        c.create_window(tx, ty, window=t, anchor='nw', width=TXW, height=LH - ty - 10, tags='ui'); s.enter = s.lab_enter

    def lab_anim(s):
        c, L = s.c, s.lab; c.delete('anim'); bk = s._bk(); m = bk['vm']; age = s.t - bk['t0']
        PW = 386; BKW = min(400, (LW - PW - 20) // 2)
        cx, top, nk, bot = PW + 10 + BKW // 2, 110, 180, 356
        hw = lambda y: 24 + max(0, y - nk) * 71 / (bot - nk)
        gas = [f for f in m if SUBS[f]['st'] == 'g']
        gc = mix(SUBS[gas[0]]['col'], PANEL, .3) if gas and SUBS[gas[0]]['cn'] else '#12193a'
        body = [cx - 24, top, cx + 24, top, cx + 24, nk, cx + 95, bot, cx - 95, bot, cx - 24, nk]
        c.create_polygon(body, fill=gc, outline='', tags='anim')
        liq = [f for f in m if SUBS[f]['st'] in ('aq', 'l')]; yl = bot
        if liq:
            yl = bot - min(150, 70 + 26 * len(liq)); col = mix(bk['lc1'], bk['lc0'], min(1, age / 30))
            c.create_polygon(cx - hw(yl), yl, cx + hw(yl), yl, cx + 95, bot, cx - 95, bot, fill=col, outline='', tags='anim')
            c.create_line(cx - hw(yl) + 3, yl, cx + hw(yl) - 3, yl, fill=mix('#ffffff', col, .45), width=2, tags='anim')
        for f in m:
            if SUBS[f]['st'] == 's':
                rd = random.Random(f)
                for k in range(min(10, 2 + int(m[f] * 25))):
                    x, y, r = cx + rd.uniform(-76, 76), bot - 9 - rd.uniform(0, 16), rd.uniform(4, 9)
                    c.create_oval(x - r, y - r, x + r, y + r, fill=SUBS[f]['col'], outline=mix(SUBS[f]['col'], '#000000', .5), tags='anim')
        if bk['ppt'] and 0 <= age < 70 and liq:
            for k in range(16):
                ph = ((age * 2.2 + k * 23) % 100) / 100; y = yl + ph * (bot - 14 - yl)
                x = cx + (((k * 37) % 100) - 50) / 100 * hw(y) * 1.5
                c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=bk['ppt'][k % len(bk['ppt'])], outline='', tags='anim')
        if bk['gasfx'] and 0 <= age < 130 and liq and random.random() < .6:
            s.bub.append([cx + random.uniform(-65, 65), bot - 10, random.uniform(2, 5), random.uniform(1.5, 3.2)])
        for b in s.bub:
            b[1] -= b[3]; b[0] += math.sin(s.t * .3 + b[2]) * .7
            c.create_oval(b[0] - b[2], b[1] - b[2], b[0] + b[2], b[1] + b[2], outline='white', width=1.5, tags='anim')
        s.bub = [b for b in s.bub if b[1] > yl + 2]
        _cd = bk.get('cond', '')
        if _cd in ('t°', 'đn'):
            for i in range(-2, 3):
                x = cx + i * 30; h = 16 + 9 * math.sin(s.t * .5 + i * 1.7)
                c.create_polygon(x - 10, bot + 22, x, bot + 22 - h - 6, x + 10, bot + 22, fill=['#f97316', '#fbbf24'][i % 2], outline='', tags='anim')
        elif _cd == 'đng':
            c.create_text(cx, bot + 14, text="❄ đặc nguội", font=F(10), fill='#7dd3fc', tags='anim')
        elif _cd == 'lo':
            c.create_text(cx, bot + 14, text="💧 loãng", font=F(10), fill='#0d9488', tags='anim')
        elif _cd == 'đp':
            for sx, lb in ((-12, '+'), (12, '−')):
                c.create_line(cx + sx, top - 16, cx + sx, bot - 34, fill='#cbd5e1', width=4, tags='anim')
                c.create_text(cx + sx, top - 24, text=lb, fill=ACC if lb == '+' else BAD, font=F(13), tags='anim')
            if s.t % 6 < 3: c.create_text(cx, bot - 46, text="⚡", font=F(16), fill=GOLD, tags='anim')
        c.create_line(body + body[:2], fill=ACC if 0 <= age < 14 else '#94a3b8', width=3, joinstyle='round', tags='anim')
        if 0 <= age < 14:
            r = 40 + age * 9; c.create_oval(cx - r, 230 - r, cx + r, 230 + r, outline=GOLD, width=3, tags='anim')

    def over(s):
        s.clear(); s.screen = 'over'; s.best = max(s.best, s.score); cx = W // 2; cy = H // 2
        s.txt(cx, cy - 100, "GAME OVER", 52, BAD); s.txt(cx, cy - 10, f"Điểm của bạn: {s.score}", 26, GOLD)
        s.txt(cx, cy + 35, f"Điểm cao nhất: {s.best}", 16, '#94a3b8')
        s.btn(cx - 150, cy + 70, 300, 56, "↻ Chơi lại", lambda: s.reset(s.mode), ACC, 18)
        s.btn(cx - 150, cy + 145, 300, 56, "☰ Về menu", s.menu, '#334155', 18, 'white')


if __name__ == "__main__":
    Game()