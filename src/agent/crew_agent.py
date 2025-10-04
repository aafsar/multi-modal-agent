from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileReadTool
from datetime import datetime
from typing import List
import os


@CrewBase
class VoiceCourseAgent:
    """Voice-enabled MIT AI Studio Course Assistant (MVP: Next Class Briefing only)"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self):
        # Get the absolute path to the project root
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.schedule_path = os.path.join(self.base_path, "data", "schedule.csv")
        self.preferences_path = os.path.join(self.base_path, "knowledge", "user_preference.txt")

    @agent
    def schedule_navigator(self) -> Agent:
        """Agent responsible for navigating the course schedule"""
        file_tool = FileReadTool(file_path=self.schedule_path)

        return Agent(
            config=self.agents_config['schedule_navigator'],
            tools=[file_tool],
            verbose=False,  # Less verbose for voice interaction
            allow_delegation=False
        )

    @task
    def next_class_briefing(self) -> Task:
        """Task to get information about the next upcoming class"""
        return Task(
            config=self.tasks_config['next_class_briefing']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Voice Course Assistant crew (MVP: single task)"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,  # Less verbose for cleaner voice interaction
            memory=False  # Disable memory for faster responses in MVP
        )

    def get_next_class_info(self, current_date: str = None) -> str:
        """
        Get information about the next class.

        Args:
            current_date: Optional date string (e.g., "10/15/2024")
                         If None, uses today's date

        Returns:
            String with next class information
        """
        if current_date is None:
            current_date = datetime.now().strftime("%m/%d/%Y")

        # Update task description with current date
        task_config = self.tasks_config['next_class_briefing'].copy()
        if 'description' in task_config:
            task_config['description'] = task_config['description'].replace(
                "{current_date}", current_date
            )

        # Create and run crew
        result = self.crew().kickoff()

        # Extract text from result
        if hasattr(result, 'raw'):
            return result.raw
        else:
            return str(result)

    def cleanup(self):
        """Clean up resources."""
        pass
