require 'cutorch'
require 'cunn'
require 'torch'
data = require 'data'
dir = 'data/all_images/'
X,Y = data.storeXY(dir,50,300,'')
X,Y = data.loadXY(dir)
Xt,Yt,Xv,Yv = data.split(X,Y,200)
models = require 'models'
net,ct = models.resnet(34)
net = net:cuda()
ct = ct:cuda()
batchSize = 16
train = require 'train'
sgd_config = {
           learningRate = 0.1,
              momentum = 0.9,
}
trans = require 'transforms'
proc = trans.Compose({
--              trans.CropHW(50,110),
                trans.CenterCropHW(50,200),
              --  trans.Rotation(1)
        })
net = torch.load('data/model_v3.t7')
--train.sgd(net,ct,Xt,Yt,Xv,Yv,100,sgd_config,batchSize,proc)
net = net:float()
torch.save('data/model_v3_cpu.t7',net)
ct:float()
torch.save('data/ct_v3_cpu.t7',ct)
timer = torch.Timer()
train.accuracy(Xv,Yv,net,batchSize,proc)

print('Time elapsed for 200 samples: ' .. timer:time().real .. ' seconds')
hash = data.getHash()
Xp = data.loadX('data/12001_13000_png/','',10,50,300,12000)
out = io.open('data/predicted_12001_13000.txt','w')
--out:write('check')
--output = train.prediction(Xp,net,1,proc,hash,out)

require 'string'
--print(output)

