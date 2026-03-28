# import sys
# from agents.research_agent import research


# def main():
#     if len(sys.argv) > 1:
#         topic = " ".join(sys.argv[1:])
#     else:
#         topic = input("Enter research topic: ").strip()

#     if not topic:
#         print("No topic provided.")
#         sys.exit(1)

#     report = research(topic)
#     print("\n" + "="*50)
#     print(report)
#     print("="*50)

#     with open("output_report.md", "w") as f:
#         f.write(f"# Research: {topic}\n\n{report}")
#     print("\nReport saved to output_report.md")


# if __name__ == "__main__":
#     main()


"""
main.py — CLI entry point for DeepResearch Agent

Usage:
    python main.py "What are the latest developments in LLM reasoning?"
    python main.py  (interactive mode)
"""

# import sys
# from agents.multi_agent import run_multi_agent


# def main():
#     if len(sys.argv) > 1:
#         topic = " ".join(sys.argv[1:])
#     else:
#         topic = input("Enter research topic: ").strip()

#     if not topic:
#         print("No topic provided.")
#         sys.exit(1)

#     print(f"\nRunning multi-agent research on: {topic}\n")
#     report = run_multi_agent(topic)

#     print("\n" + "="*50)
#     print(report)
#     print("="*50)

#     with open("output_report.md", "w") as f:
#         f.write(f"# Research: {topic}\n\n{report}")
#     print("\nReport saved to output_report.md")


# if __name__ == "__main__":
#     main()


# 


import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


def run(topic: str) -> None:
    from agents.multi_agent import run_multi_agent

    console.print(Panel(
        f"[bold]Topic:[/bold] {topic}",
        title="DeepResearch Agent — Week 3",
        border_style="purple",
    ))

    report = run_multi_agent(topic)

    console.print("\n")
    console.print(Panel(
        Markdown(report),
        title="Research Report",
        border_style="green",
    ))

    output_path = "output_report.md"
    with open(output_path, "w") as f:
        f.write(f"# Research: {topic}\n\n{report}")
    console.print(f"\n[dim]Report saved to {output_path}[/dim]")


def main():
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        console.print("[bold]DeepResearch Agent[/bold] — Interactive Mode")
        topic = console.input("\n[purple]Enter research topic:[/purple] ").strip()
        if not topic:
            console.print("[red]No topic provided. Exiting.[/red]")
            sys.exit(1)

    run(topic)


if __name__ == "__main__":
    main()