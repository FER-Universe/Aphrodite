# -*- coding: utf-8 -*-
import pretrainedmodels
import pretrainedmodels.utils as utils
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.autograd import Variable
from torch.autograd import grad as torch_grad
from torch.optim import lr_scheduler

device = "cuda" if torch.cuda.is_available() else "cpu"

model_name = "alexnet"  # 'bninception'
# resnext = pretrainedmodels.__dict__[model_name](num_classes=1000, pretrained='imagenet').cuda()
alexnet = pretrainedmodels.__dict__[model_name](
    num_classes=1000, pretrained="imagenet"
).to(device)


def set_models(device: str):
    encoder, regressor, header = nn_output()

    encoder.load_state_dict(
        torch.load("backend/weights/enc2.t7", map_location=torch.device(device)),
        strict=False,
    )
    regressor.load_state_dict(
        torch.load("backend/weights/reg2.t7", map_location=torch.device(device)),
        strict=False,
    )
    header.load_state_dict(
        torch.load("backend/weights/header2.t7", map_location=torch.device(device)),
        strict=False,
    )

    encoder.eval()
    regressor.eval()
    header.eval()
    return encoder, regressor, header


def normalize_feature(input_tensor: torch.Tensor) -> torch.Tensor:
    return input_tensor / input_tensor.norm(dim=-1, keepdim=True)


def map_discrete_emotion_from_va(valence: float, arousal: float) -> str:
    """
    Map emotions from continuous(va-domain) to discrete label(Happy, Sad, Neutral, Angry)
    The mapping is based on quadrants, with a distance of 0.3 or less defined as "Neutral".
    Args:
        valence(float): The degree to which an emotion is positive or negative, [-1,1]
        arousal(float): Level of emotional excitement, [-1,1]

    Output:
        emotion class(str): one of ["Happy", "Sad", "Neutral", "Angry", "Peaceful"]
    """
    result = ""
    emotion_strength = torch.norm(torch.FloatTensor([valence, arousal]))
    if emotion_strength <= 0.15:
        result = "Neutral"
        return result
    elif emotion_strength > 0.15 and emotion_strength < 0.3:
        result = "Slightly "
    elif emotion_strength >= 0.7:
        result = "Very "

    if valence >= 0 and arousal >= 0:
        result += "Happy"
    elif valence >= 0 and arousal < 0:
        result += "Peaceful"
    elif valence < 0 and arousal >= 0:
        result += "Angry"
    else:
        result += "Sad"

    return result


def _encoder2():
    return Encoder_AL_ELIM()


def _regressor():
    return Regressor_AL_ELIM(64)


def _header():
    return Task_Header(64, 2)


def nn_output():  # remove cuda
    encoder2 = _encoder2().to(device)
    regressor = _regressor().to(device)
    task_header = _header().to(device)
    return encoder2, regressor, task_header


class Encoder2(nn.Module):
    def __init__(self):
        super(Encoder2, self).__init__()

        self.features = alexnet._features

    def forward(self, x):
        x = self.features(x)
        return x


class Regressor(nn.Module):
    def __init__(self):
        super(Regressor, self).__init__()

        self.avgpool = alexnet.avgpool
        self.lin0 = alexnet.linear0
        self.lin1 = alexnet.linear1
        self.relu0 = alexnet.relu0
        self.relu1 = alexnet.relu1
        self.drop0 = alexnet.dropout0
        self.drop1 = alexnet.dropout0
        self.last_linear = alexnet.last_linear
        self.va_regressor = nn.Linear(1000, 2)

    def forward(self, x):
        x = torch.flatten(self.avgpool(x), 1)
        x = self.relu0(self.lin0(self.drop0(x)))
        x = self.relu1(self.lin1(self.drop1(x)))

        x = self.last_linear(x)
        x = self.va_regressor(x)
        return x


class Regressor_light(nn.Module):
    def __init__(self):
        super(Regressor_light, self).__init__()

        self.avgpool = alexnet.avgpool
        self.lin0 = nn.Linear(9216, 64)  # 64
        self.lin1 = nn.Linear(64, 8)
        self.relu0 = alexnet.relu0
        self.relu1 = alexnet.relu1
        self.drop0 = alexnet.dropout0
        self.drop1 = alexnet.dropout0
        #        self.last_linear = alexnet.last_linear
        self.va_regressor = nn.Linear(8, 2)

    def forward(self, x):
        x = torch.flatten(self.avgpool(x), 1)
        x = self.relu0(self.lin0(self.drop0(x)))
        x = self.relu1(self.lin1(self.drop1(x)))

        #        x = self.last_linear(x)
        x = self.va_regressor(x)
        return x


class Regressor_light_new(nn.Module):
    def __init__(self, is_attention):
        super(Regressor_light_new, self).__init__()
        self.avgpool = alexnet.avgpool
        self.lin0 = nn.Linear(9216, 32)
        self.lin1 = nn.Linear(32, 256)
        self.lin2 = nn.Linear(9216, 32)  # TODO(): add independent linear unit
        self.relu0 = alexnet.relu0
        self.relu1 = alexnet.relu1
        self.drop0 = alexnet.dropout0
        self.drop1 = alexnet.dropout0
        self.va_regressor = nn.Linear(256, 2)

        self.pw_conv = nn.Conv2d(512, 256, kernel_size=1)
        self.mpool = nn.MaxPool2d(2, stride=2, return_indices=False)
        self.apool = nn.AvgPool2d(2, stride=2)
        self.upsample = nn.UpsamplingBilinear2d(scale_factor=2)
        self.sigmoid = nn.Sigmoid()

        self.is_attention = is_attention

    def forward(self, x):
        if self.is_attention:
            x1 = torch.flatten(self.avgpool(x), 1)  # shape: [BS, 9216]
            x1 = self.relu0(self.lin0(self.drop0(x1)))
            x1 = self.relu1(self.lin1(self.drop1(x1)))
            x_va = self.va_regressor(x1)

            mout = self.mpool(x)
            aout = self.apool(x)  # shape: [BS, 256, 3, 3]
            x2_res = self.sigmoid(
                self.upsample(self.pw_conv(torch.cat([mout, aout], dim=1)))
            )
            #            x2 = x2_res * self.avgpool(x)
            x2 = x2_res + self.avgpool(x)  # GPU 2 (mul -> add)

            x2 = torch.flatten(x2, 1)  # shape: [BS, 9216]
            x_btl_1 = self.relu0(self.lin0(self.drop0(x2)))
        #            x_btl_1 = self.relu0(self.lin2(self.drop0(x2)))  # GPU 3 (independent linear unit)
        else:
            x = torch.flatten(self.avgpool(x), 1)  # shape: [BS, 9216]
            x_btl_1 = self.relu0(self.lin0(self.drop0(x)))
            x_btl_2 = self.relu1(self.lin1(self.drop1(x_btl_1)))
            x_va = self.va_regressor(x_btl_2)

        #        return x_va, x_btl_1
        return x_va


class Encoder_AL_ELIM(nn.Module):
    def __init__(self):
        super(Encoder_AL_ELIM, self).__init__()
        self.features = alexnet._features
        self.avgpool = alexnet.avgpool

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(self.avgpool(x), 1)
        return x


class Regressor_AL_ELIM(nn.Module):
    def __init__(self, no_domain):
        super(Regressor_AL_ELIM, self).__init__()
        self.avgpool = alexnet.avgpool
        self.lin0 = nn.Linear(9216, 256)  # 256
        self.lin1 = nn.Linear(256, no_domain)
        self.relu0 = alexnet.relu0
        self.relu1 = alexnet.relu1
        self.drop0 = alexnet.dropout0
        self.drop1 = alexnet.dropout0
        self.bn = nn.BatchNorm1d(no_domain, affine=True)

    def forward(self, x):
        x = self.relu0(self.lin0(self.drop0(x)))
        latent_variable = self.relu1(self.bn(self.lin1(self.drop1(x))))
        return latent_variable


class Task_Header(nn.Module):
    def __init__(self, erm_input_dim, erm_output_dim):
        super(Task_Header, self).__init__()

        self.erm_input_dim = erm_input_dim
        self.erm_hidden_dim = self.erm_input_dim * 20  # 10
        self.erm_output_dim = erm_output_dim
        self.linear1 = nn.Linear(self.erm_input_dim, self.erm_hidden_dim)
        self.linear2 = nn.Linear(self.erm_hidden_dim, self.erm_output_dim)
        self.bn1 = nn.BatchNorm1d(self.erm_hidden_dim, affine=True)

        self.layer_blocks = nn.Sequential(
            self.linear1,
            nn.ReLU(inplace=True),
            self.linear2,
        )

    def forward(self, inputs):
        return self.layer_blocks(inputs)
