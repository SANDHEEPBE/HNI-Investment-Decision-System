# visualization/utils.py

import os
import matplotlib.pyplot as plt

def save_and_show(fig, filename):

    os.makedirs("charts", exist_ok=True)

    if not filename.endswith(".png"):
        filename += ".png"

    path = os.path.join("charts", filename)

    fig.savefig(path, bbox_inches="tight")
    print(f"📊 Saved: {path}")

    plt.show()
