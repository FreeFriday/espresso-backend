import io
import numpy as np
from PIL import Image
import torch
from torchvision import transforms
from .models import Generator


class Model:
    def __init__(self, config):
        self.size = config['size']
        self.input_nc = config['input_nc']
        self.output_nc = config['output_nc']
        self.model = Generator(self.input_nc, self.output_nc).cuda()
        state = torch.load(config['model_path'])
        self.model.load_state_dict(state['netG_A2B'])

    def transform(self, sample):
        transforms_sample_ = [ transforms.Resize(self.size, Image.BOX),
                               transforms.ToTensor(),
                               transforms.Normalize((0.5,0.5,0.5), (0.5,0.5,0.5)) ]
        for transform in transforms_sample_:
            sample = transform(sample)
        sample = torch.unsqueeze(sample, 0)

        return sample

    def denormalize(self, tensor):
        return (127.5 * (tensor.float() + 1.0)).permute((1, 2, 0)).numpy().astype(np.uint8)

    def inference(self, img_bytes):
        _input = self.transform(Image.open(io.BytesIO(img_bytes)).convert('RGB')).cuda()
        _output = self.model(_input).detach()
        output_img = Image.fromarray(self.denormalize(_output))

        return output_img
