from graphviz import Digraph

dot = Digraph("CNNAutoencoder", format="png")
dot.attr(rankdir="TB", fontsize="20")

# 節點樣式
dot.attr("node", shape="box", style="rounded,filled", fillcolor="lightblue", fontsize="16")

nodes = [
    ("input", "Input\n1×32×32"),
    ("conv1", "Conv2d\n1→16\n3×3 + BN + ReLU"),
    ("conv2", "Conv2d\n16→32\n3×3 + BN + ReLU"),
    ("pool1", "MaxPool\n2×2"),
    ("conv3", "Conv2d\n32→64\n3×3 + BN + ReLU"),
    ("pool2", "MaxPool\n2×2"),
    ("conv4", "Conv2d\n64→64\n3×3 + BN + ReLU"),
    ("pool3", "MaxPool\n2×2"),
    ("flatten", "Flatten\n64×4×4 = 1024"),
    ("fc1", "Linear\n1024→128\nReLU + Dropout"),
    ("latent", "Latent Vector\n128→32"),
    ("fc2", "Linear\n32→128\nReLU"),
    ("fc3", "Linear\n128→1024\nReLU"),
    ("reshape", "Reshape\n64×4×4"),
    ("deconv1", "ConvTranspose2d\n64→64\n2×2 + BN + ReLU"),
    ("deconv2", "ConvTranspose2d\n64→32\n2×2 + BN + ReLU"),
    ("deconv3", "ConvTranspose2d\n32→16\n2×2 + BN + ReLU"),
    ("outconv", "ConvTranspose2d\n16→1\n3×3 + Sigmoid"),
    ("output", "Output\n1×32×32"),
]

for name, label in nodes:
    dot.node(name, label)

edges = [
    ("input", "conv1"),
    ("conv1", "conv2"),
    ("conv2", "pool1"),
    ("pool1", "conv3"),
    ("conv3", "pool2"),
    ("pool2", "conv4"),
    ("conv4", "pool3"),
    ("pool3", "flatten"),
    ("flatten", "fc1"),
    ("fc1", "latent"),
    ("latent", "fc2"),
    ("fc2", "fc3"),
    ("fc3", "reshape"),
    ("reshape", "deconv1"),
    ("deconv1", "deconv2"),
    ("deconv2", "deconv3"),
    ("deconv3", "outconv"),
    ("outconv", "output"),
]

for a, b in edges:
    dot.edge(a, b)

dot.render("cnn_autoencoder_simple_arch", cleanup=True)
print("已輸出 cnn_autoencoder_simple_arch.png")
