***REMOVED***!/bin/bash
***REMOVED*** 等待测试完成并进行分析

LOG_FILE="multi_test_with_improvements.log"
MAX_WAIT=3600  ***REMOVED*** 最多等待1小时
CHECK_INTERVAL=30
WAITED=0

echo "================================================================"
echo "等待测试完成..."
echo "================================================================"
echo "日志文件: $LOG_FILE"
echo "检查间隔: ${CHECK_INTERVAL}秒"
echo "最大等待: ${MAX_WAIT}秒"
echo "================================================================"
echo ""

while [ $WAITED -lt $MAX_WAIT ]; do
    ***REMOVED*** 检查进程
    if ! pgrep -f "run_multi_test_workflow.py" > /dev/null; then
        echo ""
        echo "✓ 测试进程已完成"
        break
    fi
    
    ***REMOVED*** 显示等待时间
    minutes=$((WAITED / 60))
    seconds=$((WAITED % 60))
    printf "\r等待中... %02d:%02d" $minutes $seconds
    
    sleep $CHECK_INTERVAL
    WAITED=$((WAITED + CHECK_INTERVAL))
done

echo ""
echo ""
echo "================================================================"
echo "开始分析记忆数据..."
echo "================================================================"

***REMOVED*** 运行分析脚本
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/root/data/AI/creator/src')
from py2neo import Graph
from collections import defaultdict, Counter
import json
from datetime import datetime

graph = Graph("bolt://localhost:7680", auth=('neo4j', 'seeme_db'), name='neo4j')

print("\n【记忆数据统计】")
print("="*70)

***REMOVED*** 总记忆数
total = graph.run("MATCH (m:Memory) RETURN count(m) as count").data()[0]['count']
print(f"总记忆数: {total}")

***REMOVED*** Source统计
source_stats = graph.run("""
    MATCH (m:Memory)
    WHERE m.source IS NOT NULL AND m.source <> ""
    RETURN m.source as source, count(m) as count
    ORDER BY count DESC
""").data()

print(f"\n按Source分布:")
for s in source_stats:
    print(f"  {s['source']}: {s['count']} ({s['count']/total*100:.1f}%)")

***REMOVED*** 类型统计
type_stats = graph.run("""
    MATCH (m:Memory)
    RETURN m.memory_type as type, count(m) as count
    ORDER BY count DESC
""").data()

print(f"\n按类型分布:")
for t in type_stats:
    print(f"  {t['type'] or 'None'}: {t['count']} ({t['count']/total*100:.1f}%)")

***REMOVED*** 关系统计
relations = graph.run("MATCH ()-[r:RELATED_TO]->() RETURN count(r) as count").data()[0]['count']
print(f"\n记忆关联数: {relations}")

***REMOVED*** 获取所有记忆内容进行分析
all_memories = graph.run("""
    MATCH (m:Memory)
    RETURN m.id as id, m.content as content, m.source as source, 
           m.memory_type as type, m.metadata as metadata
    ORDER BY m.created_at DESC
""").data()

print(f"\n【内容分析】")
print("="*70)

***REMOVED*** 关键词分析
keywords = []
for mem in all_memories:
    content = mem.get('content', '') or ''
    ***REMOVED*** 简单关键词提取
    if '视频' in content or '脚本' in content:
        keywords.append('视频脚本')
    if '反馈' in content or '建议' in content:
        keywords.append('用户反馈')
    if '优化' in content or '改进' in content:
        keywords.append('优化改进')
    if '开场' in content:
        keywords.append('开场')
    if '结尾' in content:
        keywords.append('结尾')
    if '产品' in content:
        keywords.append('产品')
    if '体验' in content or '效果' in content:
        keywords.append('体验效果')

keyword_counter = Counter(keywords)
print("关键词频率 (Top 10):")
for word, count in keyword_counter.most_common(10):
    print(f"  {word}: {count}")

***REMOVED*** 分析重复模式
print(f"\n【改进建议】")
print("="*70)

***REMOVED*** 1. 检查是否有重复记忆
if total > 0:
    contents = [m.get('content', '')[:100] for m in all_memories if m.get('content')]
    unique_contents = len(set(contents))
    duplicate_rate = (len(contents) - unique_contents) / len(contents) * 100 if contents else 0
    print(f"1. 内容重复度: {duplicate_rate:.1f}%")
    if duplicate_rate > 10:
        print("   ⚠️  建议：启用更严格的去重机制")

***REMOVED*** 2. 检查经验记忆占比
experience_count = sum(1 for t in type_stats if t['type'] == 'experience')
experience_rate = experience_count / total * 100 if total > 0 else 0
print(f"\n2. 经验记忆占比: {experience_rate:.1f}%")
if experience_rate < 10:
    print("   ⚠️  建议：增强REFLECT功能，提取更多经验模式")

***REMOVED*** 3. 检查记忆关联
if relations == 0:
    print(f"\n3. 记忆关联: 0条")
    print("   ⚠️  建议：检查向量检索是否正常工作，建立记忆关联网络")

***REMOVED*** 4. Source覆盖度
with_source = sum(s['count'] for s in source_stats)
source_coverage = with_source / total * 100 if total > 0 else 0
print(f"\n4. Source字段覆盖度: {source_coverage:.1f}%")
if source_coverage == 100:
    print("   ✅ 所有记忆都有Source标识")

print(f"\n分析完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
PYEOF

echo ""
echo "================================================================"
echo "分析完成"
echo "================================================================"
