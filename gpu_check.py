import torch


if torch.cuda.is_available():
    print("CUDA is available. Using GPU.")
    # Create a random tensor and move it to GPU
    data = torch.randn([1000, 1000]).cuda()
    # Perform a matrix multiplication
    result = data @ data.t()
    print("Performed matrix multiplication on GPU.")
else:
    print("CUDA is not available. Using CPU.")