"""
Runner - DeepEval 测试执行器

负责:
1. 检查 DeepEval 是否已安装 (应该在 Compiler 阶段预安装)
2. 运行 pytest 测试
3. 解析 JSON 报告
4. 返回执行结果
5. 🆕 Phase 5: 支持 HITL 暂停/继续/停止控制

优化点:
- 不再运行时安装 DeepEval (优化 2)
- 只检查是否已安装,未安装则提示用户
- 🆕 线程安全的执行控制
"""

import subprocess
import json
import threading
import time
from pathlib import Path
from typing import Optional
from enum import Enum
from queue import Queue
from pydantic import BaseModel, Field

from src.schemas.execution_result import ExecutionResult, ExecutionStatus


class ExecutionControl(Enum):
    """执行控制状态"""
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class DeepEvalTestResult(BaseModel):
    """DeepEval 测试结果"""
    total_tests: int = Field(description="总测试数")
    passed: int = Field(description="通过数")
    failed: int = Field(description="失败数")
    skipped: int = Field(default=0, description="跳过数")
    duration: float = Field(description="执行时间(秒)")
    test_details: list = Field(default_factory=list, description="测试详情")


class Runner:
    """Agent 执行器 (DeepEval 版本)

    优化点:
    - 不再运行时安装 DeepEval
    - 使用 pytest-json-report 获取结构化结果
    - 🆕 Phase 5: 支持 HITL 控制 (暂停/继续/停止)
    """

    def __init__(self, agent_dir: Path):
        """初始化 Runner

        Args:
            agent_dir: Agent 项目目录
        """
        self.agent_dir = Path(agent_dir).absolute()  # 确保使用绝对路径
        self.venv_python = self._find_python_executable()

        # 🆕 Phase 5: HITL 控制
        self.control = ExecutionControl.RUNNING
        self.status_queue = Queue()  # 状态队列，供 UI 轮询
        self.log_queue = Queue()     # 日志队列
        self.current_process: Optional[subprocess.Popen] = None  # 当前运行的进程
    
    # 🆕 Helper to print trace
    def _print_trace(self, agent_dir: Path):
        try:
            # 尝试加载最新的 trace
            trace_dir = agent_dir / ".trace"
            if trace_dir.exists():
                trace_files = sorted(trace_dir.glob("*.json"), key=os.path.getmtime, reverse=True)
                if trace_files:
                    latest_trace = trace_files[0]
                    from src.utils.trace_visualizer import print_trace_summary
                    
                    # Load json
                    with open(latest_trace, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Mock SimulationResult object for compatibility if needed, 
                    # or just pass dict if supported.
                    # Assuming print_trace_summary takes a dict or we need to construct object.
                    # For simplicity, let's implement a simple printer here or use the util if adapted.
                    print("\n" + "="*50)
                    print("📊 Agent Execution Trace Summary")
                    print("="*50)
                    
                    steps = data.get("steps", [])
                    print(f"Total Steps: {len(steps)}")
                    print(f"Status: {'✅ Success' if data.get('success') else '❌ Failed'}")
                    
                    print("\nExecution Flow:")
                    for step in steps:
                        icon = "✅" if step.get('step_type') == 'success' else "❌" if step.get('step_type') == 'failed' else "➡️"
                        print(f"  {icon} [{step.get('node_id')}] {step.get('description')}")
                        if step.get('tool_calls'):
                             for tc in step['tool_calls']:
                                 print(f"     🔨 Tool: {tc.get('tool_name')}")
                    
                    if data.get("issues"):
                        print("\n⚠️  Issues Detected:")
                        for issue in data['issues']:
                            print(f"  - [{issue.get('severity')}] {issue.get('description')}")
                    print("="*50 + "\n")
                    
        except Exception as e:
            print(f"⚠️ Failed to print trace summary: {e}")
    
    def _find_python_executable(self) -> Path:
        """查找 Python 可执行文件
        
        Returns:
            Python 可执行文件路径
        """
        # 🆕 Debug: 显示 agent_dir
        print(f"🔍 [Runner] Agent 目录: {self.agent_dir}")
        print(f"🔍 [Runner] Agent 目录存在: {self.agent_dir.exists()}")
        
        # 检查是否有虚拟环境
        venv_paths = [
            self.agent_dir / "venv" / "Scripts" / "python.exe",  # Windows
            self.agent_dir / "venv" / "bin" / "python",  # Linux/Mac
        ]
        
        for venv_path in venv_paths:
            # 🆕 Debug: 显示每个检查的路径
            print(f"🔍 [Runner] 检查路径: {venv_path}")
            print(f"🔍 [Runner] 路径存在: {venv_path.exists()}")
            
            if venv_path.exists():
                print(f"✅ [Runner] 找到 venv Python: {venv_path}")
                return venv_path
        
        # 使用系统 Python
        import sys
        print(f"⚠️ [Runner] 未找到 venv,使用系统 Python: {sys.executable}")
        return Path(sys.executable)

    # 🆕 Phase 5: HITL 控制方法
    def pause(self):
        """暂停执行"""
        self.control = ExecutionControl.PAUSED
        self.status_queue.put({"status": "paused", "message": "执行已暂停"})
        self.log_queue.put({"level": "WARNING", "message": "执行已暂停"})

    def resume(self):
        """继续执行"""
        self.control = ExecutionControl.RUNNING
        self.status_queue.put({"status": "running", "message": "执行已继续"})
        self.log_queue.put({"level": "INFO", "message": "执行已继续"})

    def stop(self):
        """停止执行"""
        self.control = ExecutionControl.STOPPED
        self.status_queue.put({"status": "stopped", "message": "执行已停止"})
        self.log_queue.put({"level": "ERROR", "message": "执行已停止"})

        # 终止当前进程
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            try:
                self.current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.current_process.kill()

    def get_status(self) -> str:
        """获取当前状态"""
        return self.control.value

    def _check_control_state(self):
        """检查控制状态（在关键点调用）"""
        # 如果暂停，等待恢复
        while self.control == ExecutionControl.PAUSED:
            time.sleep(0.1)

        # 如果停止，抛出异常
        if self.control == ExecutionControl.STOPPED:
            raise RuntimeError("执行已被用户停止")
    
    def setup_environment(self) -> bool:
        """设置运行环境 (安装依赖)"""
        install_script = "install.bat" if subprocess.os.name == "nt" else "./install.sh"
        script_path = self.agent_dir / install_script
        
        if not script_path.exists():
            return False
            
        try:
            cmd = str(script_path.absolute()) if subprocess.os.name == "nt" else str(script_path.absolute())
            # For subprocess run, we might need shell=True on windows for bat files? 
            # Usually .bat needs shell=True or direct full path execution.
            print(f"Executing {cmd}...")
            subprocess.run(
                [cmd], 
                cwd=str(self.agent_dir), 
                check=True, 
                shell=(subprocess.os.name == "nt")
            )
            return True
        except Exception as e:
            print(f"Installation failed: {e}")
            return False
    
    def run_deepeval_tests(
        self,
        test_file: str = "tests/test_deepeval.py",
        timeout: int = 1200
    ) -> ExecutionResult:
        """运行 DeepEval 测试
        
        Args:
            test_file: 测试文件路径 (相对于 agent_dir)
            timeout: 超时时间(秒)
        
        Returns:
            ExecutionResult 包含测试结果
        """
        # 🆕 优化: 检查 DeepEval 是否已安装 (不再运行时安装)
        if not self._check_deepeval_installed():
            return ExecutionResult(
                overall_status=ExecutionStatus.ERROR,
                test_results=[],
                stderr="DeepEval 未安装! 请先运行安装脚本:\n"
                      "  Linux/Mac: ./install.sh\n"
                      "  Windows: install.bat\n"
                      "或手动安装: pip install -r requirements.txt"
            )
        
        # 检查测试文件是否存在
        test_path = self.agent_dir / test_file
        if not test_path.exists():
            return ExecutionResult(
                overall_status=ExecutionStatus.ERROR,
                test_results=[],
                stderr=f"测试文件不存在: {test_file}"
            )
        
        # 运行 pytest
        try:
            result = self._run_pytest(test_file, timeout)
            
            # 🆕 Print trace summary after execution
            self._print_trace(self.agent_dir)
            
            return result
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                overall_status=ExecutionStatus.TIMEOUT,
                test_results=[],
                stderr=f"测试执行超时 ({timeout}秒)"
            )
        except Exception as e:
            return ExecutionResult(
                overall_status=ExecutionStatus.ERROR,
                test_results=[],
                stderr=f"测试执行失败: {str(e)}"
            )
    
    def _check_deepeval_installed(self) -> bool:
        """🆕 检查 DeepEval 是否已安装
        
        Returns:
            True if installed, False otherwise
        """
        try:
            # 使用 venv 中的 Python 检查
            print(f"🔍 [Runner] 检查 Python 路径: {self.venv_python}")
            print(f"🔍 [Runner] Python 是否存在: {self.venv_python.exists()}")
            
            result = subprocess.run(
                [str(self.venv_python), "-c", "import deepeval; print('OK')"],
                cwd=self.agent_dir,
                capture_output=True,
                text=True,
                timeout=60  # 🔧 增加到 60 秒 (首次导入 deepeval 可能需要下载模型)
            )
            
            # 🆕 Debug logging
            print(f"🔍 [Runner] DeepEval 检查:")
            print(f"   - 返回码: {result.returncode}")
            print(f"   - Stdout: {result.stdout.strip()}")
            if result.stderr:
                print(f"   - Stderr: {result.stderr.strip()}")
            
            return result.returncode == 0 and "OK" in result.stdout
        except subprocess.TimeoutExpired:
            print(f"🔍 [Runner] DeepEval 检查超时 (60秒)")
            return False
        except Exception as e:
            print(f"🔍 [Runner] DeepEval 检查失败: {e}")
            return False
    
    def _run_pytest(self, test_file: str, timeout: int) -> ExecutionResult:
        """运行 pytest 并解析结果
        
        Args:
            test_file: 测试文件路径
            timeout: 超时时间
        
        Returns:
            ExecutionResult
        """
        import time
        start_time = time.time()
        
        # 构造 pytest 命令
        report_file = self.agent_dir / "deepeval_results.json"
        cmd = [
            str(self.venv_python),
            "-m", "pytest",
            test_file,
            "--json-report",
            f"--json-report-file={report_file.name}",
            "-v", "-s"
        ]
        
        # 🆕 Debug logging
        print(f"🔍 [Runner] 执行命令: {' '.join(cmd)}")
        print(f"🔍 [Runner] 工作目录: {self.agent_dir}")
        print(f"🔍 [Runner] Python: {self.venv_python}")
        
        # 运行命令
        result = subprocess.run(
            cmd,
            cwd=self.agent_dir,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        execution_time = time.time() - start_time
        
        # 🆕 Debug logging
        print(f"🔍 [Runner] 返回码: {result.returncode}")
        print(f"🔍 [Runner] 执行时间: {execution_time:.2f}s")
        print(f"🔍 [Runner] Stderr: {result.stderr[:300] if result.stderr else 'None'}")
        
        # 解析 JSON 报告
        if report_file.exists():
            print(f"🔍 [Runner] ✅ 报告文件存在: {report_file}")
            print(f"🔍 [Runner] 报告文件大小: {report_file.stat().st_size} bytes")
            
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                print(f"🔍 [Runner] JSON 解析成功")
                print(f"🔍 [Runner] 报告键: {list(report_data.keys())}")
                
                # 显示 summary 信息
                if 'summary' in report_data:
                    print(f"🔍 [Runner] Summary: {report_data['summary']}")
                
                # 显示测试数量
                if 'tests' in report_data:
                    print(f"🔍 [Runner] 测试数量: {len(report_data['tests'])}")
                    if report_data['tests']:
                        print(f"🔍 [Runner] 第一个测试: {report_data['tests'][0].get('nodeid', 'unknown')}")
                
                test_result = self._parse_json_report(report_file)
                
                print(f"🔍 [Runner] 解析结果类型: {type(test_result)}")
                print(f"🔍 [Runner] 解析成功 - Status: {test_result.overall_status}, Tests: {len(test_result.test_results)}")
                
                return test_result
                
            except Exception as e:
                print(f"🔍 [Runner] ❌ JSON解析失败: {e}")
                import traceback
                traceback.print_exc()
                # JSON 解析失败,回退到 stdout 解析
                return self._parse_pytest_stdout(
                    result.stdout,
                    result.stderr,
                    execution_time
                )
        else:
            # 没有 JSON 报告,解析 stdout
            return self._parse_pytest_stdout(
                result.stdout,
                result.stderr,
                execution_time
            )
    
    def _parse_json_report(self, report_file: Path) -> "DeepEvalTestResult":
        """解析 pytest-json-report 生成的 JSON 文件
        
        Args:
            report_file: JSON 报告文件路径
            
        Returns:
            DeepEvalTestResult 对象
        """
        with open(report_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"🔍 [_parse_json_report] 开始解析 JSON 报告")
        print(f"🔍 [_parse_json_report] 报告键: {list(data.keys())}")
        
        # 提取汇总信息
        summary = data.get('summary', {})
        print(f"🔍 [_parse_json_report] Summary 内容: {summary}")
        
        total = summary.get('total', 0)
        passed = summary.get('passed', 0)
        failed = summary.get('failed', 0)
        skipped = summary.get('skipped', 0)
        duration = data.get('duration', 0.0)
        tests = data.get('tests', [])
        
        print(f"🔍 [_parse_json_report] 统计: Total={total}, Passed={passed}, Failed={failed}, Skipped={skipped}, Duration={duration:.2f}s")
        print(f"🔍 [_parse_json_report] 发现 {len(tests)} 个测试详情")
        
        # 创建 TestResult 列表
        from ..schemas.execution_result import TestResult, ExecutionStatus
        
        test_results = []
        for test in tests:
            # 确定状态
            outcome = test.get('outcome', 'failed')
            if outcome == 'passed':
                status = ExecutionStatus.PASS
            elif outcome == 'failed':
                status = ExecutionStatus.FAIL
            elif outcome == 'skipped':
                status = ExecutionStatus.SKIPPED
            else:
                status = ExecutionStatus.ERROR
            
            # 提取错误信息
            error_msg = None
            if 'call' in test and 'crash' in test['call']:
                error_msg = test['call']['crash'].get('message', '')
            
            test_results.append(TestResult(
                test_id=test.get('nodeid', 'unknown'),
                status=status,
                actual_output=None,
                error_message=error_msg,
                duration_ms=int(test.get('call', {}).get('duration', 0) * 1000) if 'call' in test else 0
            ))
        
        # 确定整体状态
        if failed == 0 and total > 0:
            overall_status = ExecutionStatus.SUCCESS
        elif total == 0:
            overall_status = ExecutionStatus.ERROR
        else:
            overall_status = ExecutionStatus.FAILED
        
        print(f"🔍 [_parse_json_report] 创建 ExecutionResult: status={overall_status}, total={total}")
        
        from ..schemas.execution_result import ExecutionResult
        return ExecutionResult(
            overall_status=overall_status,
            test_results=test_results,
            stderr=None
        )
    
    def _parse_pytest_stdout(
        self,
        stdout: str,
        stderr: str,
        execution_time: float
    ) -> ExecutionResult:
        """解析 pytest 的 stdout 输出 (回退方案)
        
        Args:
            stdout: 标准输出
            stderr: 标准错误
            execution_time: 执行时间
        
        Returns:
            ExecutionResult
        """
        # 简单的启发式解析
        passed = stdout.count(" PASSED")
        failed = stdout.count(" FAILED")
        
        if failed == 0 and passed > 0:
            status = ExecutionStatus.SUCCESS
        elif failed > 0:
            status = ExecutionStatus.FAILED
        else:
            status = ExecutionStatus.ERROR
        
        return ExecutionResult(
            overall_status=status,  # 使用 overall_status
            test_results=[],  # 简化版
            stderr=stderr if stderr else None
        )
