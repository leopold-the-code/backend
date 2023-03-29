"""
Neural networks for feed generation
"""
from random import random

import torch
from torch.utils.data import TensorDataset, DataLoader
from torch import nn

from backend import models, geo
from backend.config import logger
import datetime


LossHistory = list[float]


async def load_data() -> TensorDataset:
    """
    Load user data from database
    """
    swipes = await models.Swipe.all().prefetch_related(
        "swiper__tag_objects",
        "subject__tag_objects",
    )
    current_year = datetime.datetime.now().year
    xs = []
    ys = []
    for swipe in swipes:
        age_swiper = current_year - int(swipe.swiper.birth_date)
        age_subject = current_year - int(swipe.subject.birth_date)
        distance = geo.calculate_distance(
            swipe.swiper.latitude,
            swipe.swiper.longitude,
            swipe.subject.latitude,
            swipe.subject.longitude,
        )
        tag_swiper = set(swipe.swiper.tag_objects)
        tag_subject = set(swipe.subject.tag_objects)
        tag_intersection = tag_swiper.intersection(tag_subject)
        similarity = 2 * len(tag_intersection) / (len(tag_swiper) + len(tag_subject))
        side = float(swipe.side)

        xs.append([age_swiper, age_subject, distance, similarity])
        ys.append([side])

    xs_tensor = torch.tensor(xs, dtype=torch.float32)
    ys_tensor = torch.tensor(ys, dtype=torch.float32)

    dataset = TensorDataset(xs_tensor, ys_tensor)

    return dataset


def fake_data() -> TensorDataset:
    """
    Fake data for ml to check model training
    """
    xs = []
    ys = []

    for _ in range(10000):
        sim = random()
        xs.append([random() * 70, random() * 70, random() * 15, sim])
        ys.append([1.0 if sim > 0.5 else 0])

    xs_tensor = torch.tensor(xs, dtype=torch.float32)
    ys_tensor = torch.tensor(ys, dtype=torch.float32)

    dataset = TensorDataset(xs_tensor, ys_tensor)

    return dataset


class SwipeNN(nn.Module):
    """
    Neural Network to predict swipe
    It takes [user1.age, user2.age, distance, tag_similarity]
    Ex: [22, 22, 5.77, 0.33]

    And output single value:
    0.0 - Left swipe
    0.5 - Uncertain
    1.0 - Right swipe
    ...and everything in between
    """

    def __init__(self):
        super().__init__()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(4, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        out = self.linear_relu_stack(x)
        return out


def train_epoch(dataloader, model, loss_fn, optimizer, device) -> LossHistory:
    size = len(dataloader.dataset)
    model.train()

    loss_history = []

    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)
        pred = model(X)

        loss = loss_fn(pred, y)

        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (batch) % 20 == 0:
            loss, current = loss.item(), (batch + 1) * len(X)
            logger.info(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")
            loss_history.append(loss)

    return loss_history


def train(dataset: TensorDataset, epochs: int = 25) -> tuple[SwipeNN, LossHistory]:
    # TODO split data to train and test
    dataloader = DataLoader(dataset, batch_size=100)

    device = "cpu"
    logger.info(f"Using {device} device for training")

    model = SwipeNN().to(device)

    loss_fn = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    global_loss_history = []

    for t in range(epochs):
        print(f"Epoch {t+1}\n-------------------------------")
        loss_history = train_epoch(dataloader, model, loss_fn, optimizer, device)
        global_loss_history.extend(loss_history)

        # TODO test_epoch
        # test(test_dataloader, model, loss_fn)

    return model, global_loss_history


def eval(model: SwipeNN, record: list[float]):
    model.eval()
    with torch.no_grad():
        output = model.forward(torch.tensor(record))
        return output.item()


def store_on_disk(model: SwipeNN):
    torch.save(model.state_dict(), "model.pth")
