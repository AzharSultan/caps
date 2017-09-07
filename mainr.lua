require 'cutorch'
require 'cunn'
require 'torch'
timer = torch.Timer()
data = require 'data'
dir = 'data/all_images/'
X,Y = data.storeXY(dir,50,300,'')
X,Y = data.loadXY(dir)
Xt,Yt,Xv,Yv = data.split(X,Y,300)
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
--	        trans.CropHW(50,110),
	        trans.CenterCropHW(50,200),
	      --  trans.Rotation(1)
	})
--net = torch.load('data/model_v2.t7')
print('Time elapsed for loading data: ' .. timer:time().real .. ' seconds')
train.sgd(net,ct,Xt,Yt,Xv,Yv,100,sgd_config,batchSize,proc)
torch.save('data/model_v4.t7',net)
net2 = net:float()
torch.save('data/model_v4_cpu.t7',net2)
timer = torch.Timer()
train.accuracy(Xv,Yv,net,batchSize,proc)

print('Time elapsed for 200 samples: ' .. timer:time().real .. ' seconds')
hash = data.getHash()
Xp = data.loadX('data/12001_13000_png/','',1000,50,300,12000)
out = io.open('data/predicted_12001_13000.txt','w')
--out:write('check')
output = train.prediction(Xp,net,1,proc,hash,out)
print('Time elapsed for 4 samples: ' .. timer:time().real .. ' seconds')
require 'string'
--print(output)
