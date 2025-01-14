import torch
import torch.nn as nn
from abc import ABC, abstractmethod

class Brain(nn.Module, ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def forward(self, vision):
        ...
    
    @abstractmethod
    def mutate(self, mutation_prob, mutation_amount):
        ...

    @abstractmethod
    def _get_n_parameters(self):
        ...

class CNNBrain(Brain):
    def __init__(self, vision_width, vision_channels) -> None:
        super().__init__()
        self.conv = nn.Conv1d(vision_channels, 1, 1)
        # self.relu = nn.ReLU()
        self.pool = nn.AvgPool1d(2)
        self.fc = nn.Linear(vision_width // 2, 2)

    def forward(self, vision_buffer: torch.Tensor, energy: float, speed: float):
        vision = self.pool(self.conv(vision_buffer))
        # x = torch.hstack([vision, torch.tensor([energy, speed]).view(1, 2)])
        x = vision
        x = self.fc(x)
        x = torch.tanh(x)
        return x[0, 0], x[0, 1]

    def mutate(self, mutation_prob: float, mutation_amount: float):
        for p in self.parameters():
            mutation_mask = torch.distributions.Categorical(probs=torch.tensor([1 - mutation_prob, mutation_prob])).sample(p.size())
            mutation = torch.distributions.Normal(loc=0, scale=mutation_amount).sample(p.size())
            # print("----------------------------")
            # print(p.data)
            # print("mutation:", mutation*mutation_mask)
            p.data += mutation * mutation_mask
            # print(p.data)


    def __str__(self):
        return f"Vision Brain with {self._get_n_parameters(self.conv)} conv params and  {self._get_n_parameters(self.fc)} FC parameters."
    
    def _get_n_parameters(self, model: nn.Module):
        return sum(p.numel() for p in model.parameters())
    
class NeatBrain(Brain):
    def __init__(self, n_inputs, n_outputs):
        super().__init__()
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        
    def forward(self, vision):
        pass

    def mutate(self, mutation_prob, mutation_amount):
        pass

    def _get_n_parameters(self):
        pass

if __name__ == "__main__":
    b = Brain(10, 3)
    print(b)