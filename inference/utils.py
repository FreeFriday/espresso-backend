import random
from torch.autograd import Variable
import torch
from torchvision import utils as vutils
import numpy as np
from PIL import Image


def save_image(tensor, path, nrow=4):
    grid = vutils.make_grid(tensor.cpu(), nrow=nrow)
    img= (127.5*(grid.float() + 1.0)).permute((1,2,0)).numpy().astype(np.uint8)
    Image.fromarray(img).save(path)


def read_image(path, mode='RGB'):
    img = Image.open(path)
    return np.array(img.convert(mode))


def tensor2image(tensor):
    image = 127.5*(tensor[0].cpu().float().numpy() + 1.0)
    if image.shape[0] == 1:
        image = np.tile(image, (3,1,1))  # 4
    return image.astype(np.uint8)


class Logger:
    def __init__(self, writer):
        self.writer = writer
      
    def log(self, loss_dict, itrs):
        members = [attr for attr in dir(loss_dict)
                  if ((not callable(getattr(loss_dict, attr))
                        and not attr.startswith("__"))
                      and ('loss' in attr
                            or 'grad' in attr
                            or 'nwd' in attr
                            or 'accuracy' in attr))]
        for m in members:
            self.writer.add_scalar(m, getattr(loss_dict, m), itrs + 1)

class ReplayBuffer():
    def __init__(self, max_size=50):
        assert (max_size > 0), 'Empty buffer or trying to create a black hole. Be careful.'
        self.max_size = max_size
        self.data = []

    def push_and_pop(self, data):
        to_return = []
        for element in data.data:
            element = torch.unsqueeze(element, 0)
            if len(self.data) < self.max_size:
                self.data.append(element)
                to_return.append(element)
            else:
                if random.uniform(0,1) > 0.5:
                    i = random.randint(0, self.max_size-1)
                    to_return.append(self.data[i].clone())
                    self.data[i] = element
                else:
                    to_return.append(element)
        return Variable(torch.cat(to_return))

class LambdaLR():
    def __init__(self, n_epochs, offset, decay_start_epoch):
        assert ((n_epochs - decay_start_epoch) > 0), "Decay must start before the training session ends!"
        self.n_epochs = n_epochs
        self.offset = offset
        self.decay_start_epoch = decay_start_epoch

    def step(self, epoch):
        return 1.0 - max(0, epoch + self.offset - self.decay_start_epoch)/(self.n_epochs - self.decay_start_epoch)

def weights_init_normal(m):
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        torch.nn.init.normal_(m.weight.data, 0.0, 0.02)
    elif classname.find('BatchNorm2d') != -1:
        torch.nn.init.normal_(m.weight.data, 1.0, 0.02)
        torch.nn.init.constant(m.bias.data, 0.0)

