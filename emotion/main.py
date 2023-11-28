from fer_util import nn_output
import torch
import torch.nn.functional as F
import numpy as np
from scipy.integrate import solve_ivp
import cv2

IMG_WIDTH = 224
IMG_HEIGHT = 224
IMG_CHANNEL = 3
IMG_PRESET = True

if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"


def lorenz_attractor():
    WIDTH, HEIGHT, DPI = 1000, 750, 100
    sigma, beta, rho = 10, 2.667, 28
    u0, v0, w0 = 0, 1, 1.05
    tmax, n = 100, IMG_WIDTH * IMG_HEIGHT

    def lorenz(t, X, sigma, beta, rho):
        """The Lorenz equations."""
        (
            u,
            v,
            w,
        ) = X
        up = -sigma * (u - v)
        vp = rho * u - v - u * w
        wp = -beta * w + u * v
        return up, vp, wp

    soln = solve_ivp(
        lorenz, (0, tmax), (u0, v0, w0), args=(sigma, beta, rho), dense_output=True
    )
    t = np.linspace(0, tmax, n)
    x, y, z = soln.sol(t)
    return x, y, z


def induce_uncertainty_to_img(lorenz_coords, img):
    x, y, z = lorenz_coords
    flatten_img = img.flatten(start_dim=2, end_dim=3)

    new_img = torch.zeros_like(flatten_img)
    for i in range(IMG_WIDTH * IMG_HEIGHT):
        for j in range(IMG_CHANNEL):  # rgb
            new_img[0, j, i] = lorenz_coords[j][i] * flatten_img[0, j, i]
    perturbed_img = new_img.reshape(1, IMG_CHANNEL, IMG_WIDTH, IMG_HEIGHT)
    return perturbed_img


def set_models():
    encoder, regressor, header = nn_output()

    encoder.load_state_dict(torch.load("emotion/weights/enc2.t7"), strict=False)
    regressor.load_state_dict(torch.load("emotion/weights/reg2.t7"), strict=False)
    header.load_state_dict(torch.load("emotion/weights/header2.t7"), strict=False)

    encoder.eval()
    regressor.eval()
    header.eval()
    return encoder, regressor, header


if __name__ == "__main__":
    encoder, regressor, header = set_models()

    if IMG_PRESET:
        img_np = cv2.imread("emotion/imgs/portrait.png")
        img = torch.from_numpy(img_np).permute(2, 0, 1).unsqueeze_(0)
        img = F.interpolate(img, size=IMG_WIDTH) / 255.0
    else:
        img = torch.randn(1, IMG_CHANNEL, IMG_WIDTH, IMG_HEIGHT).to(device)

    x, y, z = lorenz_attractor()
    perturbed_img = induce_uncertainty_to_img(lorenz_coords=[x, y, z], img=img)

    latent_feature = encoder(perturbed_img.type(torch.cuda.FloatTensor))
    va_output = header(regressor(latent_feature))
