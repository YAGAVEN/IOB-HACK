import torch
import torch.nn as nn
import torch.nn.functional as F

# 🔹 Step 1: Create Graph (Adjacency Matrix)
# Example: 4 nodes
A = torch.tensor([
    [1, 1, 0, 0],  # Node 0 connected to 1
    [1, 1, 1, 0],  # Node 1 connected to 0,2
    [0, 1, 1, 1],  # Node 2 connected to 1,3
    [0, 0, 1, 1]   # Node 3 connected to 2
], dtype=torch.float32)

# 🔹 Step 2: Node Features (4 nodes, 3 features each)
X = torch.tensor([
    [1, 0, 1],
    [0, 1, 1],
    [1, 1, 0],
    [0, 0, 1]
], dtype=torch.float32)

# 🔹 Step 3: Normalize Adjacency Matrix
def normalize_adj(A):
    D = torch.diag(torch.sum(A, dim=1))
    D_inv_sqrt = torch.inverse(torch.sqrt(D))
    return D_inv_sqrt @ A @ D_inv_sqrt

A_hat = normalize_adj(A)

# 🔹 Step 4: Define GCN Layer
class GCNLayer(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.W = nn.Parameter(torch.randn(in_features, out_features))

    def forward(self, A, X):
        return F.relu(A @ X @ self.W)

# 🔹 Step 5: Build GNN Model
class GNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.gcn1 = GCNLayer(3, 4)
        self.gcn2 = GCNLayer(4, 2)

    def forward(self, A, X):
        h = self.gcn1(A, X)
        h = self.gcn2(A, h)
        return h

# 🔹 Step 6: Labels (Node classification example)
labels = torch.tensor([0, 1, 0, 1])  # 2 classes

# 🔹 Step 7: Train
model = GNN()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(100):
    model.train()
    out = model(A_hat, X)

    loss = F.cross_entropy(out, labels)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item()}")

# 🔹 Step 8: Predictions
model.eval()
pred = model(A_hat, X)
predicted_classes = torch.argmax(pred, dim=1)

print("Predictions:", predicted_classes)