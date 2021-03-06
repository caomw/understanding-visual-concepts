require 'hdf5'
require 'paths'
require 'math'
require 'xlua'

--[[
    Usage: Need a .h5 file <dataset_name> below, generated from
        action_data_converter.py, which has been saved in <dataset_folder>


--]]


local dataset_name = 'actions_2_frame_subsample_5.h5'
local dataset_folder = '/om/data/public/mbchang/udcign-data/action/raw/hdf5'
local to_save_folder = '/om/data/public/mbchang/udcign-data/action/all'


-- local dataset_name = 'test_actions_2_frame_subsample_5.h5'
-- local dataset_folder = '/Users/MichaelChang/Documents/Researchlink/SuperUROP/Code/unsupervised-dcign/data/actions/raw/videos'
-- local to_save_folder = '/Users/MichaelChang/Documents/Researchlink/SuperUROP/Code/unsupervised-dcign/data/actions/float'

local bsize = 30

function load_data(dataset_name, dataset_folder)
    local dataset_file = hdf5.open(dataset_folder .. '/' .. dataset_name, 'r')
    local examples = {}
    for action,data in pairs(dataset_file:all()) do
        for j = 1,data:size(1)-bsize,bsize do  -- the frames in data re
            local batch = data[{{j,j+bsize-1}}]
            table.insert(examples, batch)  -- each batch is a contiguous sequence (bsize, height, width)
        end
    end
    return examples
end

function split_batches(examples, bsize)
    local num_test = math.floor(#examples * 0.15)
    local num_val = num_test
    local num_train = #examples - 2*num_test

    local test = {}
    local val = {}
    local train = {}

    -- shuffle examples
    local ridxs = torch.randperm(#examples)
    for i = 1, ridxs:size(1) do
        xlua.progress(i, ridxs:size(1))
        local batch = examples[ridxs[i]]
        if i <= num_train then
            table.insert(train, batch)
        elseif i <= num_train + num_val then
            table.insert(val, batch)
        else
            table.insert(test, batch)
        end
    end
    return {train, val, test}
end


function save_batches(datasets, savefolder)
    local train, val, test = unpack(datasets)
    local data_table = {train=train, val=val, test=test}
    for dname,data in pairs(data_table) do
        local subfolder = paths.concat(savefolder,dname)
        if not paths.dirp(subfolder) then paths.mkdir(subfolder) end
        local i = 1
        for _,b in pairs(data) do
            xlua.progress(i, #data)
            b = b:float()
            local batchname = paths.concat(subfolder, 'batch'..i)
            torch.save(batchname, b)
            i = i + 1
        end
    end
end

-- main
print('loading data')
local ex = load_data(dataset_name, dataset_folder)
print('splitting batches')
local train, val, test = unpack(split_batches(ex, bsize))
print('saving batches')
save_batches({train, val, test}, to_save_folder)
