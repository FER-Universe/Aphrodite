from abc import ABC, abstractmethod


class FeelingBase(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def feel_texts(self) -> None:
        pass

    @abstractmethod
    def feel_audios(self) -> None:
        pass

    @abstractmethod
    def feel_images(self) -> None:
        pass

    @abstractmethod
    def feel_space(self) -> None:
        pass

    @abstractmethod
    def feel_beyond(self) -> None:
        pass


class Feeling(FeelingBase):
    def __init__(self) -> None:
        super().__init__()
