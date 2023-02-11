import torch
import torch.nn as nn

class Brain(nn.Module):
    def __init__(self, vision_width, vision_channels) -> None:
        super().__init__()
        self.conv = nn.Conv1d(vision_channels, 1, 1)
        # self.relu = nn.ReLU()
        self.pool = nn.AvgPool1d(2)
        self.fc = nn.Linear(vision_width // 2 + 2, 2)

    def forward(self, vision_buffer: torch.Tensor, energy: float, speed: float):
        vision = self.pool(self.conv(vision_buffer))
        x = torch.hstack([vision, torch.tensor([energy, speed]).view(1, 2)])
        x = self.fc(x)
        x = torch.tanh(x)
        return x[0, 0], x[0, 1]

    def mutate(self, mutation_prob: float, mutation_amount: float):
        pass