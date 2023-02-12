import torch
from brain import Brain

model = Brain(10, 3)
state_dict = torch.load("checkpoints/manual/net.pt")


state_dict["conv.weight"] = torch.tensor([[[-0.8], [-0.6], [1]]])
state_dict["fc.weight"] = torch.tensor([[ -1.000,  0.8000, 0.0, -0.8000, -1.000,  0.0000,  0.0000],
                                        [-0.8000,  -0.500,  1.0000, -0.5000, -0.8000,  0.0000, -0.4000]])
state_dict["fc.bias"] = torch.tensor([0.05, 0.5])
print(state_dict)


torch.save(state_dict, "checkpoints/manual/net2.pt")