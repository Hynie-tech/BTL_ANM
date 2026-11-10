"""Ve so do he thong va so do phan luong canh bao -> docs/04_design/diagrams/*.png"""
from _common import *  # noqa: F401,F403
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = ROOT / "docs" / "04_design" / "diagrams"
COL = {"data": "#dbe8f7", "model": "#d9f0e3", "ops": "#fdebd0", "human": "#f9d9d9", "mon": "#e8dff5"}


def box(ax, x, y, w, h, text, kind, fs=8.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=COL[kind], ec="#555", lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, a, b, text="", dy=0.0, rad=0.0):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#333",
                                                    connectionstyle=f"arc3,rad={rad}"))
    if text:
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + dy, text, fontsize=7, ha="center", color="#444")


def system_flow():
    fig, ax = plt.subplots(figsize=(13, 6.2)); ax.set_xlim(0, 13); ax.set_ylim(0, 6.2); ax.axis("off")
    box(ax, 0.2, 4.6, 2.0, 1.0, "Flow có nhãn\n(parquet)\ndata/input", "data")
    box(ax, 2.7, 4.6, 2.2, 1.0, "Kiểm tra & chia tập\ntrain / val / test\n(stratified)", "data")
    box(ax, 5.4, 4.6, 2.3, 1.0, "Pipeline tiền xử lý\nInf/NaN, bỏ cột hằng,\nlog + chuẩn hoá", "model")
    box(ax, 8.2, 5.0, 2.2, 0.8, "Random Forest\n(mô hình chính)", "model")
    box(ax, 8.2, 4.0, 2.2, 0.8, "Logistic Regression\n(mô hình phụ)", "model")
    box(ax, 10.9, 4.6, 2.0, 1.0, "Ngưỡng từ validation\nALERT / REVIEW /\noperating", "ops")
    box(ax, 10.9, 3.0, 2.0, 1.0, "Registry + Quality gate\nv1 → v2, rollback\n(checkpoints)", "ops")
    box(ax, 8.2, 2.9, 2.2, 1.0, "Production\ndự đoán điểm số\ntrên flow mới", "ops")
    box(ax, 5.4, 2.9, 2.3, 1.0, "Hàng đợi 3 vùng\nP1 / P2 / P3 / AUDIT", "human")
    box(ax, 2.7, 2.9, 2.2, 1.0, "Analyst xác minh\n(SOP, 2 người duyệt\nkhi bác bỏ điểm cao)", "human")
    box(ax, 0.2, 2.9, 2.0, 1.0, "Nhãn đã xác minh\n(kho dữ liệu có\nkiểm soát)", "human")
    box(ax, 8.2, 0.9, 2.2, 1.2, "Giám sát\nPSI/KS, PSI dải điểm,\ntỉ lệ dự đoán, bất đồng", "mon")
    box(ax, 5.4, 0.9, 2.3, 1.2, "Hiệu năng có nhãn\n(nhãn trễ): F1, recall\nso với control", "mon")
    box(ax, 2.7, 0.9, 2.2, 1.2, "Kích hoạt retrain?\ndrift + F1 giảm\nhoặc quá tải analyst", "mon")
    for a, b in [((2.2, 5.1), (2.7, 5.1)), ((4.9, 5.1), (5.4, 5.1)), ((7.7, 5.1), (8.2, 5.4)), ((7.7, 5.1), (8.2, 4.4)),
                 ((10.4, 5.4), (10.9, 5.1)), ((10.4, 4.4), (10.9, 5.0)), ((11.9, 4.6), (11.9, 4.0)),
                 ((10.9, 3.5), (10.4, 3.4)), ((8.2, 3.4), (7.7, 3.4)), ((5.4, 3.4), (4.9, 3.4)),
                 ((2.7, 3.4), (2.2, 3.4)), ((9.3, 2.9), (9.3, 2.1)), ((8.2, 1.5), (7.7, 1.5)), ((5.4, 1.5), (4.9, 1.5))]:
        arrow(ax, a, b)
    arrow(ax, (1.2, 2.9), (3.8, 2.1), "nhãn mới", dy=-0.15, rad=-0.25)
    arrow(ax, (3.8, 0.9), (3.8, 0.55))
    ax.text(3.8, 0.35, "retrain → v2 → quality gate → shadow → promote / rollback", fontsize=8, ha="center", style="italic")
    ax.set_title("Quy trình huấn luyện - đánh giá - giám sát - con người xác minh", fontsize=12)
    fig.savefig(OUT / "system_flow.png", dpi=130, bbox_inches="tight"); plt.close(fig)


def triage_flow():
    fig, ax = plt.subplots(figsize=(11, 5.4)); ax.set_xlim(0, 11); ax.set_ylim(0, 5.4); ax.axis("off")
    box(ax, 0.2, 2.2, 1.8, 1.0, "Flow mới\n→ điểm số\nRF & LogReg", "data")
    box(ax, 2.6, 2.2, 2.0, 1.0, "Vùng theo điểm\nRF so với\nt_review, t_alert", "model")
    box(ax, 5.4, 4.2, 2.6, 0.9, "ALERT & LogReg đồng ý\n→ P1_alert", "human")
    box(ax, 5.4, 3.0, 2.6, 0.9, "ALERT nhưng LogReg không\nhoặc vùng REVIEW → P2_review", "human")
    box(ax, 5.4, 1.8, 2.6, 0.9, "IGNORE nhưng LogReg báo\n→ P3 (lấy mẫu / ghi log)", "ops")
    box(ax, 5.4, 0.6, 2.6, 0.9, "IGNORE → ghi log\n+ mẫu AUDIT ngẫu nhiên", "ops")
    box(ax, 8.6, 4.2, 2.2, 0.9, "Ticket ưu tiên\nSLA ≈ 15 phút", "human")
    box(ax, 8.6, 3.0, 2.2, 0.9, "Analyst xác minh\nSLA ≈ 4 giờ", "human")
    box(ax, 8.6, 1.8, 2.2, 0.9, "Tín hiệu bất đồng\n→ giám sát drift", "mon")
    box(ax, 8.6, 0.6, 2.2, 0.9, "Ước lượng tỉ lệ\nbỏ sót (giới hạn\nphát hiện ≈ 3/n)", "mon")
    arrow(ax, (2.0, 2.7), (2.6, 2.7))
    for y in (4.65, 3.45, 2.25, 1.05):
        arrow(ax, (4.6, 2.7), (5.4, y))
        arrow(ax, (8.0, y), (8.6, y))
    ax.set_title("Phân luồng cảnh báo theo ba vùng điểm số và đồng thuận hai mô hình", fontsize=12)
    fig.savefig(OUT / "hitl_triage_flow.png", dpi=130, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    system_flow(); triage_flow(); print("ok", OUT)
