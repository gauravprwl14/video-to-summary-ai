import torch
from torch import nn

if torch.cuda.is_available():
    print("CUDA is available. Using GPU.")
    # Create a random tensor and move it to GPU
    data = torch.randn([1000, 1000]).cuda()
    # Perform a matrix multiplication
    result = data @ data.t()
    print("Performed matrix multiplication on GPU.")
else:
    print("CUDA is not available. Using CPU.")

m = nn.Conv1d(16, 33, 3, stride=2)
m=m.to('cuda')
input = torch.randn(20, 16, 50)
input=input.to('cuda')
output = m(input)
print(output)