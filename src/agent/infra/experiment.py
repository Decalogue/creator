"""
实验管理框架

支持 A/B 测试、策略对比、快速迭代优化
"""
import json
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExperimentVariant:
    """实验变体"""
    name: str
    params: Dict[str, Any]
    description: str = ""


@dataclass
class ExperimentResult:
    """实验结果"""
    variant_name: str
    success: bool
    metrics: Dict[str, Any]
    duration: float
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Experiment:
    """实验定义"""
    name: str
    description: str
    variants: List[ExperimentVariant]
    metrics: List[str]  ***REMOVED*** 要收集的指标名称
    results: List[ExperimentResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class ExperimentManager:
    """
    实验管理框架
    
    支持：
    - A/B 测试不同策略
    - 对比不同参数配置
    - 自动收集和分析结果
    - 结果导出和可视化
    """
    
    def __init__(self, experiments_dir: Optional[Path] = None):
        """
        初始化实验管理器
        
        Args:
            experiments_dir: 实验结果存储目录
        """
        if experiments_dir is None:
            experiments_dir = Path(__file__).parent.parent / "experiments"
        self.experiments_dir = Path(experiments_dir)
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        
        self.experiments: Dict[str, Experiment] = {}
    
    def create_experiment(
        self,
        name: str,
        description: str,
        variants: List[Dict[str, Any]],
        metrics: List[str]
    ) -> Experiment:
        """
        创建实验
        
        Args:
            name: 实验名称
            description: 实验描述
            variants: 变体列表，每个变体是 {"name": str, "params": dict}
            metrics: 要收集的指标名称列表
        
        Returns:
            Experiment 对象
        """
        experiment_variants = [
            ExperimentVariant(
                name=v["name"],
                params=v.get("params", {}),
                description=v.get("description", "")
            )
            for v in variants
        ]
        
        experiment = Experiment(
            name=name,
            description=description,
            variants=experiment_variants,
            metrics=metrics
        )
        
        self.experiments[name] = experiment
        logger.info(f"创建实验: {name}，包含 {len(experiment_variants)} 个变体")
        
        return experiment
    
    def run_experiment(
        self,
        experiment_name: str,
        test_fn: Callable,
        extract_metrics: Optional[Callable[[Any], Dict[str, Any]]] = None
    ) -> Dict[str, ExperimentResult]:
        """
        运行实验
        
        Args:
            experiment_name: 实验名称
            test_fn: 测试函数，接受 variant_params 作为参数
            extract_metrics: 从测试结果中提取指标的函数（可选）
        
        Returns:
            每个变体的实验结果
        """
        if experiment_name not in self.experiments:
            raise ValueError(f"实验不存在: {experiment_name}")
        
        experiment = self.experiments[experiment_name]
        results = {}
        
        logger.info(f"开始运行实验: {experiment_name}")
        
        for variant in experiment.variants:
            logger.info(f"运行变体: {variant.name}")
            start_time = time.time()
            
            try:
                ***REMOVED*** 运行测试函数
                test_result = test_fn(**variant.params)
                
                ***REMOVED*** 提取指标
                if extract_metrics:
                    metrics = extract_metrics(test_result)
                else:
                    ***REMOVED*** 默认：如果 test_result 是字典，直接使用
                    metrics = test_result if isinstance(test_result, dict) else {}
                
                duration = time.time() - start_time
                
                result = ExperimentResult(
                    variant_name=variant.name,
                    success=True,
                    metrics=metrics,
                    duration=duration
                )
                
                logger.info(
                    f"变体 {variant.name} 完成: "
                    f"成功={result.success}, 耗时={duration:.2f}s"
                )
                
            except Exception as e:
                duration = time.time() - start_time
                result = ExperimentResult(
                    variant_name=variant.name,
                    success=False,
                    metrics={},
                    duration=duration,
                    error=str(e)
                )
                logger.error(f"变体 {variant.name} 失败: {e}")
            
            results[variant.name] = result
            experiment.results.append(result)
        
        ***REMOVED*** 保存实验结果
        self._save_experiment(experiment)
        
        return results
    
    def compare_results(
        self,
        experiment_name: str
    ) -> Dict[str, Any]:
        """
        对比实验结果
        
        Args:
            experiment_name: 实验名称
        
        Returns:
            对比分析结果
        """
        if experiment_name not in self.experiments:
            raise ValueError(f"实验不存在: {experiment_name}")
        
        experiment = self.experiments[experiment_name]
        
        if not experiment.results:
            return {"error": "实验尚未运行"}
        
        ***REMOVED*** 按指标对比
        comparison = {
            "experiment_name": experiment_name,
            "variants": {},
            "best_variant": None,
            "comparison_by_metric": {}
        }
        
        ***REMOVED*** 收集每个变体的指标
        for result in experiment.results:
            if result.success:
                comparison["variants"][result.variant_name] = {
                    "metrics": result.metrics,
                    "duration": result.duration,
                }
        
        ***REMOVED*** 按每个指标找出最佳变体
        for metric_name in experiment.metrics:
            best_variant = None
            best_value = None
            
            for variant_name, variant_data in comparison["variants"].items():
                value = variant_data["metrics"].get(metric_name)
                if value is not None:
                    if best_value is None or value > best_value:
                        best_value = value
                        best_variant = variant_name
            
            if best_variant:
                comparison["comparison_by_metric"][metric_name] = {
                    "best_variant": best_variant,
                    "best_value": best_value,
                }
        
        ***REMOVED*** 找出总体最佳变体（基于第一个指标）
        if experiment.metrics and comparison["comparison_by_metric"]:
            first_metric = experiment.metrics[0]
            if first_metric in comparison["comparison_by_metric"]:
                comparison["best_variant"] = comparison["comparison_by_metric"][first_metric]["best_variant"]
        
        return comparison
    
    def _save_experiment(self, experiment: Experiment):
        """保存实验到文件"""
        file_path = self.experiments_dir / f"{experiment.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        experiment_dict = {
            "name": experiment.name,
            "description": experiment.description,
            "variants": [
                {
                    "name": v.name,
                    "params": v.params,
                    "description": v.description
                }
                for v in experiment.variants
            ],
            "metrics": experiment.metrics,
            "results": [
                {
                    "variant_name": r.variant_name,
                    "success": r.success,
                    "metrics": r.metrics,
                    "duration": r.duration,
                    "error": r.error,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in experiment.results
            ],
            "created_at": experiment.created_at.isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(experiment_dict, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"实验已保存到: {file_path}")
    
    def load_experiment(self, file_path: Path) -> Experiment:
        """从文件加载实验"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        experiment = Experiment(
            name=data["name"],
            description=data["description"],
            variants=[
                ExperimentVariant(
                    name=v["name"],
                    params=v["params"],
                    description=v.get("description", "")
                )
                for v in data["variants"]
            ],
            metrics=data["metrics"],
            created_at=datetime.fromisoformat(data["created_at"])
        )
        
        ***REMOVED*** 加载结果
        for r in data.get("results", []):
            experiment.results.append(ExperimentResult(
                variant_name=r["variant_name"],
                success=r["success"],
                metrics=r["metrics"],
                duration=r["duration"],
                error=r.get("error"),
                timestamp=datetime.fromisoformat(r["timestamp"])
            ))
        
        self.experiments[experiment.name] = experiment
        return experiment
