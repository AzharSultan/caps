require 'nn';

local train = {}

function train.prediction_single_cpu(Xp,net,batch,prep,hash,txt_path)

    net:evaluate()
    local batch = batch or 64
    local Nv = Xp:size(1)
    local output1 = torch.CharStorage(Nv*6)
    for i =1,Nv,batch do
        local j = math.min(i+batch-1,Nv)
        local Xb = (prep and prep(Xp[{{i,j}}]) or Xp[{{i,j}}]):float()
        local out = net:forward(Xb) -- N*k*C
        local tmp,YYb = out:max(3)
       -- print(YYb)
        outfile = io.open(txt_path,'w')
        for j = 1,6 do
            a = hash[YYb[1][j][1]]
           -- print(string.char(string.byte(a)))
            outfile:write(a)
            print(a)
            output1[(i-1)*6+j] = string.byte(a)
--            print(YYb[1][j][1],output1:string())
            --out.write(output[i*6+j]:string())
        end
        outfile:write('\n')
    end
    io.close(outfile)
    print(output)
    return output
end


function train.prediction_single(Xp,net,batch,prep,hash,txt_path)

    net:evaluate()
    local batch = batch or 64
    local Nv = Xp:size(1)
    local output1 = torch.CharStorage(Nv*6)
    for i =1,Nv,batch do
        local j = math.min(i+batch-1,Nv)
        local Xb = (prep and prep(Xp[{{i,j}}]) or Xp[{{i,j}}]):cuda()
        local out = net:forward(Xb) -- N*k*C
        local tmp,YYb = out:max(3)
       -- print(YYb)
        outfile = io.open(txt_path,'w')
        for j = 1,6 do
            a = hash[YYb[1][j][1]]
           -- print(string.char(string.byte(a)))
            outfile:write(a)
            print(a)
            output1[(i-1)*6+j] = string.byte(a)
--            print(YYb[1][j][1],output1:string())
            --out.write(output[i*6+j]:string())
        end
        outfile:write('\n')
    end
    io.close(outfile)
    print(output)
    return output
end

function train.accuracy(Xv,Yv,net,batch,prep)
    net:evaluate()
    local batch = batch or 64
    local Nv = Xv:size(1)
    local lloss = 0
    for i =1,Nv,batch do
        local j = math.min(i+batch-1,Nv)
        local Xb = (prep and prep(Xv[{{i,j}}]) or Xv[{{i,j}}]):float()
        local Yb = Yv[{{i,j}}]:float()
        local out = net:forward(Xb) -- N*k*C
        local tmp,YYb = out:max(3)
        lloss = lloss + YYb:float():eq(Yb):sum()
    end
    return (100*lloss/(6*Nv))
end


function train.prediction(Xp,net,batch,prep,hash,outfile)
    net:evaluate() 
    local batch = batch or 64
    local Nv = Xp:size(1)
    local output1 = torch.CharStorage(Nv*6)
    for i =1,Nv,batch do
        local j = math.min(i+batch-1,Nv)
        local Xb = (prep and prep(Xp[{{i,j}}]) or Xp[{{i,j}}]):cuda()
        local out = net:forward(Xb) -- N*k*C
        local tmp,YYb = out:max(3)
       -- print(YYb)
        for j = 1,6 do
            a = hash[YYb[1][j][1]]
           -- print(string.char(string.byte(a)))
            outfile:write(a)
            output1[(i-1)*6+j] = string.byte(a)
--            print(YYb[1][j][1],output1:string())
            --out.write(output[i*6+j]:string())
        end
        outfile:write('\n')
    end
    print(output)
    return output
end

function train.accuracy(Xv,Yv,net,batch,prep)
    net:evaluate()
    local batch = batch or 64
    local Nv = Xv:size(1)
    local lloss = 0
    for i =1,Nv,batch do
        local j = math.min(i+batch-1,Nv)
        local Xb = (prep and prep(Xv[{{i,j}}]) or Xv[{{i,j}}]):cuda()
        local Yb = Yv[{{i,j}}]:cuda()
        local out = net:forward(Xb) -- N*k*C
        local tmp,YYb = out:max(3)
        lloss = lloss + YYb:cuda():eq(Yb):sum()
    end
    return (100*lloss/(6*Nv))
end


function train.accuracyK(Xv,Yv,net,batch,prep)
    net:evaluate()
    local batch = batch or 64
    local Nv = Xv:size(1)
    local lloss = 0
    for i =1,Nv,batch do
        local j = math.min(i+batch-1,Nv)
        local Xb = (prep and prep(Xv[{{i,j}}]) or Xv[{{i,j}}]):cuda()
        local Yb = Yv[{{i,j}}]:cuda()
        local out = net:forward(Xb) -- N*k*C
        local tmp,YYb = out:max(3)
        lloss = lloss + YYb:cuda():eq(Yb):sum(2):eq(6):sum()
    end
    return (100*lloss/(Nv))
end


function train.sgd(net,ct,Xt,Yt,Xv,Yv,K,sgd_config,batch,prep)
    local x,dx = net:getParameters()
    require 'optim'
    local batch = batch or 64
    local Nt = Xt:size(1)
    print('parameters size ..')
    print(#x)
    for k=1,K do
        local lloss = 0
        net:training()

        for i=1,Nt,batch do
            if(i%(20*batch)==1) then print(i,Nt) end
            dx:zero()
            local j = math.min(i+batch-1,Nt)
            local Xb = ( prep and prep(Xt[{{i,j}}]) or Xt[{{i,j}}] ):cuda()
            local Yb = Yt[{{i,j}}]:cuda()
            local out = net:forward(Xb)
            local loss = ct:forward(out,Yb)
            local dout = ct:backward(out,Yb)
            net:backward(Xb,dout)
            dx:div(j-i+1)
            function feval()
                return loss,dx
            end
            local ltmp,tmp = optim.sgd(feval,x,sgd_config)
            --print(loss)
            lloss = lloss + loss
        end
        print('loss..'..lloss)
        print('valid .. '.. train.accuracy(Xv,Yv,net,batch,prep))
        print('train .. '.. train.accuracy(Xt,Yt,net,batch,prep))
        --print('valid .. '.. train.accuracyK(Xv,Yv,net,batch))
        --print('train .. '.. train.accuracyK(Xt,Yt,net,batch))
    end
end


return train
