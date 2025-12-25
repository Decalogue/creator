export CUDA_VISIBLE_DEVICES=0

***REMOVED*** 检查必要文件
if [ ! -f "config/global.yaml" ]; then
    echo "错误: config/global.yaml 不存在"
    exit 1
fi

if [ ! -f "config/policy.json" ]; then
    echo "错误: config/policy.json 不存在"
    exit 1
fi

echo "开始运行测试..."
python main.py Novel validation --data_limit 1

echo "测试完成！"
