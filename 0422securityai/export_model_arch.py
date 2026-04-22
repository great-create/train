import os
import sys
import torch

# === 讓 Python 找得到 core 資料夾 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(BASE_DIR, "core")

if CORE_DIR not in sys.path:
    sys.path.append(CORE_DIR)

from cnn_autoencoder import CNNAutoencoder


def main():
    print("=== 開始建立 securityai 模型 ===")

    # 無 GPU 環境，強制使用 CPU
    device = torch.device("cpu")

    # 根據專案 settings 預設 latent_dim = 32
    model = CNNAutoencoder(latent_dim=32).to(device)
    model.eval()

    # 建立一個假的輸入，符合專案模型需求：1x32x32
    x = torch.randn(1, 1, 32, 32).to(device)

    # forward() 會回傳 (x_hat, z)
    x_hat, z = model(x)

    print("\n=== 模型文字架構 ===")
    print(model)

    print("\n=== 輸出尺寸 ===")
    print("reconstructed output x_hat shape:", x_hat.shape)
    print("latent vector z shape:", z.shape)

    # 1) torchinfo：輸出 layer summary
    try:
        from torchinfo import summary
        print("\n=== torchinfo summary ===")
        summary(model, input_size=(1, 1, 32, 32), device="cpu")
    except Exception as e:
        print("\n[略過 torchinfo]")
        print("原因：", e)

    # 2) 匯出 ONNX
    try:
        torch.onnx.export(
            model,
            x,
            "cnn_autoencoder.onnx",
            input_names=["input"],
            output_names=["reconstructed_output", "latent_vector"],
            opset_version=11
        )
        print("\n已輸出 ONNX：cnn_autoencoder.onnx")
    except Exception as e:
        print("\n[ONNX 匯出失敗]")
        print("原因：", e)

    # 3) 若有安裝 torchviz + Graphviz，就匯出 PNG
    try:
        from torchviz import make_dot

        dot = make_dot(
            x_hat,
            params=dict(model.named_parameters())
        )
        dot.render("cnn_autoencoder_architecture", format="png", cleanup=True)
        print("已輸出 PNG：cnn_autoencoder_architecture.png")
    except Exception as e:
        print("\n[略過 torchviz PNG 匯出]")
        print("原因：", e)

    print("\n=== 完成 ===")


if __name__ == "__main__":
    main()
