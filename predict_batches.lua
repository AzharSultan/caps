require 'cutorch'
require 'cunn'
require 'torch'
timer = torch.Timer()
data = require 'data'
models = require 'models'
train = require 'train'
trans = require 'transforms'
proc = trans.Compose({
--              trans.CropHW(50,110),
                trans.CenterCropHW(50,200),
              --  trans.Rotation(1)
        })
net = torch.load('data/model_v4.t7')
print('Time elapsed for loading model: ' .. timer:time().real .. ' seconds')
timer = torch.Timer()
hash = data.getHash()
Xp = data.loadX('data/wrong_caps_png/','',5000,50,300)
out = io.open('data/predicted_wrong_caps_5000.txt','w')
--out:write('check')
output = train.prediction(Xp,net,1,proc,hash,out)
print('Time elapsed for 5000 samples: ' .. timer:time().real .. ' seconds')
require 'string'
--print(output)

