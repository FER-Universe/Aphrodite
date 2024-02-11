from abc import ABC, abstractmethod


class DrawingBase(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def generate_images(self) -> None:
        pass

    @abstractmethod
    def save_images(self) -> None:
        pass
