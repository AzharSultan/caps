--
-- Created by IntelliJ IDEA.
-- User: azhar
-- Date: 04/08/17
-- Time: 13:19
-- To change this template use File | Settings | File Templates.
--
require 'nn'
require 'torch'
require 'MultiCrossEntropyCriterion'
data = require 'data'
dir = 'data/all_images/'

function file_exists(name)
   local f=io.open(name,"r")
   if f~=nil then io.close(f) return true else return false end
end

batchSize = 1
train = require 'train'
trans = require 'transforms'
proc = trans.Compose({
--              trans.CropHW(50,110),
                trans.CenterCropHW(50,200),
              --  trans.Rotation(1)
        })

net = torch.load('data/model_v4_cpu.t7')
hash = data.getHash()
img_path = 'data/bot_testing/1.png'
jpg_path = 'data/bot_testing/1.jpg'
dummy = 'data/bot_testing/12.png'
txt_path = 'data/bot_testing/1.txt'
while 1 do
    for i = 1,5 do
        img_path = 'data/bot_testing/'..i..'/1.png'
        jpg_path = 'data/bot_testing/'..i..'/1.jpg'
        dummy = 'data/bot_testing/'..i..'/12.png'
        txt_path = 'data/bot_testing/'..i..'/1.txt'
        txt_dummy = 'data/bot_testing/'..i..'/12.txt'

        if file_exists(img_path) and file_exists(jpg_path) and file_exists(dummy) and not file_exists(txt_path) then
            timer = torch.Timer()

            Xp = data.loadX('data/bot_testing/'..i..'/','',1,50,300)

            --out:write('check')
            train.prediction_single_cpu(Xp,net,1,proc,hash,txt_path)
            d = io.open(txt_dummy,'w')
            d:write('w')
            io.close(d)
            print('Time elapsed for 1 sample: ' .. timer:time().real .. ' seconds')
        end
        if not file_exists(dummy) and file_exists(txt_path) then
            os.remove(txt_path)
            os.remove(txt_dummy)
            os.remove(img_path)
        end
    end
end
--require 'string'
--print(output)

