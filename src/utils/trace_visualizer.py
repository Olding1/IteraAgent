"""Trace visualizer for generating HTML visualization of simulation traces."""

from typing import List
from pathlib import Path
from ..schemas import SimulationResult, SimulationStep, SimulationIssue


def generate_trace_html(trace: SimulationResult, output_path: Path = None) -> str:
    """Generate HTML visualization of simulation trace.

    Args:
        trace: SimulationResult to visualize
        output_path: Optional path to save HTML file

    Returns:
        HTML string
    """
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulation Trace - {trace.simulated_at.strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            opacity: 0.9;
            font-size: 14px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .summary-card .label {{
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .summary-card .value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        
        .summary-card.success .value {{
            color: #10b981;
        }}
        
        .summary-card.error .value {{
            color: #ef4444;
        }}
        
        .issues {{
            padding: 30px;
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            margin: 0;
        }}
        
        .issues h2 {{
            color: #856404;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        
        .issue-item {{
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
            border-left: 4px solid #dc3545;
        }}
        
        .issue-item.warning {{
            border-left-color: #ffc107;
        }}
        
        .issue-item .issue-type {{
            font-weight: bold;
            color: #dc3545;
            margin-bottom: 5px;
        }}
        
        .issue-item.warning .issue-type {{
            color: #856404;
        }}
        
        .timeline {{
            padding: 30px;
        }}
        
        .timeline h2 {{
            margin-bottom: 20px;
            color: #333;
            font-size: 20px;
        }}
        
        .trace-entry {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        
        .trace-entry:hover {{
            background: #e9ecef;
            transform: translateX(5px);
        }}
        
        .trace-entry.success {{
            border-left: 4px solid #10b981;
        }}
        
        .trace-entry.failed {{
            border-left: 4px solid #ef4444;
        }}
        
        .trace-entry.skipped {{
            border-left: 4px solid #6b7280;
            opacity: 0.7;
        }}
        
        .step-number {{
            background: #667eea;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
            margin-right: 15px;
        }}
        
        .step-content {{
            flex: 1;
        }}
        
        .step-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }}
        
        .node-id {{
            font-weight: bold;
            color: #667eea;
            font-size: 16px;
        }}
        
        .node-type {{
            background: #e0e7ff;
            color: #4338ca;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
        
        .action {{
            color: #6b7280;
            font-size: 14px;
        }}
        
        .status-icon {{
            font-size: 20px;
            margin-left: auto;
        }}
        
        .description {{
            color: #4b5563;
            line-height: 1.6;
        }}
        
        .mermaid-section {{
            padding: 30px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
        }}
        
        .mermaid-section h2 {{
            margin-bottom: 20px;
            color: #333;
        }}
        
        .mermaid {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
        }}
        
        .footer {{
            padding: 20px;
            text-align: center;
            color: #6b7280;
            font-size: 14px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕹️ Simulation Trace</h1>
            <div class="meta">
                Generated at: {trace.simulated_at.strftime('%Y-%m-%d %H:%M:%S')} | 
                Total Steps: {trace.total_steps}
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-card {'success' if trace.success else 'error'}">
                <div class="label">Status</div>
                <div class="value">{'✅ Success' if trace.success else '❌ Failed'}</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Steps</div>
                <div class="value">{trace.total_steps}</div>
            </div>
            <div class="summary-card {'error' if trace.has_errors() else ''}">
                <div class="label">Issues</div>
                <div class="value">{len(trace.issues)}</div>
            </div>
        </div>
"""

    # Add issues section if there are any
    if trace.issues:
        html += """
        <div class="issues">
            <h2>⚠️ Issues Detected</h2>
"""
        for issue in trace.issues:
            html += f"""
            <div class="issue-item {issue.severity}">
                <div class="issue-type">[{issue.severity.upper()}] {issue.issue_type}</div>
                <div class="description">{issue.description}</div>
                {f'<div class="suggestion">💡 Suggestion: {issue.suggestion}</div>' if issue.suggestion else ''}
            </div>
"""
        html += """
        </div>
"""

    # Add timeline
    html += """
        <div class="timeline">
            <h2>📊 Execution Timeline</h2>
"""

    for step in trace.steps:
        status_icon = (
            "✅"
            if step.step_type.value == "success"
            else "❌" if step.step_type.value == "failed" else "⏭️"
        )
        status_class = step.step_type.value if hasattr(step.step_type, "value") else "success"

        html += f"""
            <div class="trace-entry {status_class}">
                <div class="step-number">{int(step.step_number)}</div>
                <div class="step-content">
                    <div class="step-header">
                        {f'<span class="node-id">{step.node_id}</span>' if step.node_id else ''}
                        <span class="node-type">{step.step_type.value}</span>
                        <span class="status-icon">{status_icon}</span>
                    </div>
                    <div class="description">{step.description}</div>
                </div>
            </div>
"""

    html += """
        </div>
"""

    # Add Mermaid diagram if available
    if trace.mermaid_trace:
        html += f"""
        <div class="mermaid-section">
            <h2>🗺️ Flow Diagram</h2>
            <div class="mermaid">
                {trace.mermaid_trace}
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
            mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        </script>
"""

    html += """
        <div class="footer">
            Generated by IteraAgent Simulator
        </div>
    </div>
</body>
</html>
"""

    # Save to file if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
        print(f"✅ Trace HTML saved to: {output_path}")

    return html


def generate_trace_summary(trace: SimulationResult) -> str:
    """Generate a text summary of the trace.

    Args:
        trace: SimulationResult to summarize

    Returns:
        Text summary
    """
    summary = f"""
📊 Simulation Trace Summary
{'='*50}
Status: {'✅ Success' if trace.success else '❌ Failed'}
Total Steps: {trace.total_steps}
Issues: {len(trace.issues)} ({'❌ ' + str(sum(1 for i in trace.issues if i.severity == 'error')) + ' errors' if trace.has_errors() else '✅ No errors'})

"""

    if trace.issues:
        summary += "\n⚠️ Issues:\n"
        for i, issue in enumerate(trace.issues, 1):
            summary += (
                f"  {i}. [{issue.severity.upper()}] {issue.issue_type}: {issue.description}\n"
            )
            if issue.suggestion:
                summary += f"     💡 {issue.suggestion}\n"

    summary += f"\n📝 Execution Trace:\n{trace.execution_trace}\n"

    return summary
