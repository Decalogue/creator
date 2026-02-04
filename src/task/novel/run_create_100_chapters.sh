***REMOVED***!/bin/bash
***REMOVED*** 启动脚本：在seeme环境中运行100章小说创作

***REMOVED*** 激活seeme conda环境
source /opt/miniconda/etc/profile.d/conda.sh
conda activate seeme

***REMOVED*** 切换到脚本目录
cd "$(dirname "$0")"  ***REMOVED*** task/novel

***REMOVED*** 运行创作脚本（后台运行，输出到日志文件）
nohup python3 create_100_chapters_novel.py > /tmp/novel_creation_完美之墙.log 2>&1 &

***REMOVED*** 获取进程ID
PID=$!
echo "创作进程已启动，PID: $PID"
echo "日志文件: /tmp/novel_creation_完美之墙.log"
echo "查看进度: tail -f /tmp/novel_creation_完美之墙.log"
echo "检查进程: ps aux | grep create_100_chapters_novel"
