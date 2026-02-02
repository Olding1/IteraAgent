import asyncio
import sys
from typing import List, Tuple
from pathlib import Path

from ..core.agent_factory import AgentFactory
from ..core.progress_callback import ProgressCallback
from ..schemas.graph_structure import GraphStructure
from ..schemas.simulation import SimulationResult
from ..utils.i18n import t


class CLIProgressCallback(ProgressCallback):
    """CLI 进度回调实现"""

    def on_step_start(self, step_name: str, step_num: int, total_steps: int):
        # Translate step name if it's a key
        step_display = (
            t(f'step_{step_name.lower().replace(" ", "_")}')
            if step_name in ["PM Agent", "Resource Config", "Design & Simulation", "Build & Evolve"]
            else step_name
        )
        print(f"\n🚀 [{t('step_complete')} {step_num}/{total_steps}] {step_display}...")

    def on_step_complete(self, step_name: str, result: any):
        step_display = (
            t(f'step_{step_name.lower().replace(" ", "_")}')
            if step_name in ["PM Agent", "Resource Config", "Design & Simulation", "Build & Evolve"]
            else step_name
        )
        complete_text = (
            t("step_complete")
            if t("step_complete") != "step_complete"
            else "完成" if "zh" in str(t("banner")) else "Complete"
        )
        print(f"✅ {step_display} {complete_text}。")

        # 打印详细信息
        if hasattr(result, "project_meta"):  # AgentResult
            print(f"   📋 构建结果:")
            print(f"      - Agent名称: {result.agent_name}")
            print(f"      - 构建状态: {'成功' if result.success else '失败'}")
            if result.test_results:
                print(f"      - 测试通过: {result.test_results.overall_status}")

        elif hasattr(result, "task_type"):  # ProjectMeta
            print(f"   📋 需求分析结果:")
            print(f"      - Agent名称: {result.agent_name}")
            print(f"      - 任务类型: {result.task_type}")
            print(f"      - RAG需求: {'是' if result.has_rag else '否'}")
            print(f"      - 用户意图: {result.user_intent_summary[:60]}...")

        elif isinstance(result, dict) and "rag" in result:  # Resource Config summary
            print(f"   🔧 资源配置:")
            print(f"      - RAG: {'启用' if result['rag'] else '禁用'}")
            print(f"      - 启用工具数: {result['tools']}")

    def on_step_error(self, step_name: str, error: Exception):
        print(f"❌ {step_name} 失败: {str(error)}")

    def on_clarification_needed(self, questions: List[str]):
        print("\n❓ 需要澄清:")
        for i, q in enumerate(questions, 1):
            print(f"   {i}. {q}")

    def on_blueprint_review(
        self, graph: GraphStructure, simulation_result: SimulationResult
    ) -> Tuple[bool, str]:
        """
        蓝图评审
        Retruns: (approved, feedback)
        """
        print(f"\n{t('blueprint_review')}")
        print("=" * 30)
        print(f"{t('pattern')}: {graph.pattern.pattern_type}")
        print(f"{t('nodes')}: {len(graph.nodes)} | {t('edges')}: {len(graph.edges)}")
        print(f"\n{t('simulation_result')}:")
        print(f"{t('success')}: {simulation_result.success}")
        print(f"{t('issues')}: {len(simulation_result.issues)}")
        for issue in simulation_result.issues:
            print(f"  - [{issue.severity}] {issue.issue_type}: {issue.description}")

        print(f"\n{t('commands')}:")
        print(f"  {t('approve_build')}")
        print(f"  {t('reject')}")
        print(f"  {t('provide_feedback')}")

        while True:
            choice = input("\n> ").strip()
            if not choice:
                continue

            if choice.lower() == "y":
                return True, ""
            elif choice.lower() == "n":
                return False, ""
            else:
                return False, choice

    def on_install_request(self) -> bool:
        print(f"\n{t('install_prompt')}")
        print(f"   {t('install_yes')}")
        print(f"   {t('install_no')}")
        while True:
            choice = input("> ").strip().lower()
            if choice == "y":
                return True
            if choice == "n":
                return False

    def on_log(self, message: str):
        print(f"   ℹ️  {message}")

    def on_api_key_missing(self, tool_name: str, env_var: str, help_text: str = "") -> str:
        print(f"\n⚠️  工具 '{tool_name}' 需要配置 API Key")
        if help_text:
            # 多行打印帮助信息，或者作为 prompt 的一部分
            print(f"   ℹ️  提示: {help_text}")

        prompt = f"🔑 请输入 {env_var}: "
        return input(prompt).strip()


async def run_interactive_factory():
    """Run the Agent Factory in interactive mode."""
    print(f"\n{t('factory_title')}")
    print("===================================\n")

    description = input(f"{t('factory_describe')}:\n> ")
    if not description.strip():
        print(t("factory_empty"))
        return

    callback = CLIProgressCallback()
    factory = AgentFactory(callback=callback)

    # Optional: Ask for file paths
    files_input = input(f"\n{t('factory_files')}:\n> ")
    file_paths = []
    if files_input.strip():
        import shlex

        # Use shlex to handle quotes correctly
        # Split by comma first to allow "file1", "file 2"
        # But if no comma, shlex handles space separation respecting quotes
        if "," in files_input:
            raw_paths = [p.strip() for p in files_input.split(",")]
        else:
            try:
                # Ensure paths with backslashes on Windows are handled by escaping them or using raw string logic
                # shlex.split might consume backslashes.
                # Safer approach for Windows paths: simple split if no quotes, or use regex for spaces outside quotes.
                # Actually, let's just use CSV-style parsing which is safer for file lists
                import csv

                reader = csv.reader([files_input], skipinitialspace=True)
                raw_paths = list(reader)[0]
            except Exception:
                # Fallback to simple split
                raw_paths = files_input.split()

        # Clean up quotes and empty strings
        valid_paths = []
        for p in raw_paths:
            cleaned_p = p.strip().strip('"').strip("'")
            if not cleaned_p:
                continue

            # Check for "None" / "No" / "无"
            if cleaned_p.lower() in ["无", "no", "none", "false", "n", "null"]:
                continue

            path_obj = Path(cleaned_p)
            if path_obj.exists():
                valid_paths.append(str(path_obj.absolute()))
            else:
                print(f"⚠️  警告: 文件不存在，已忽略: {cleaned_p}")

        file_paths = valid_paths

    print("\n开始构建... (这可能需要几分钟)")

    try:
        result = await factory.create_agent(
            user_input=description, file_paths=file_paths if file_paths else None
        )

        print("\n===================================")
        if result.success:
            print(f"🎉 Agent 构建成功!")
            print(f"📂 位置: {result.agent_dir}")
            print(f"⏱️  耗时: {result.total_time:.1f}s")
            print(f"🔄 迭代次数: {result.iteration_count}")
        else:
            print(f"⚠️  Agent 已创建但存在问题。")
            if result.judge_feedback:
                print(f"裁判反馈: {result.judge_feedback.feedback}")
    except Exception as e:
        print(f"\n❌ 严重错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_interactive_factory())
