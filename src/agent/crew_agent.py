from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileReadTool, SerperDevTool, WebsiteSearchTool
from datetime import datetime
from typing import List
import os

# Disable CrewAI telemetry and trace messages
os.environ['CREWAI_TELEMETRY_OPT_OUT'] = 'true'
os.environ['CREWAI_TRACE_ENABLED'] = 'false'


@CrewBase
class VoiceCourseAgent:
    """Voice-enabled MIT AI Studio Course Assistant - Full Capabilities"""

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

    @agent
    def topic_researcher(self) -> Agent:
        """Agent responsible for researching topics and speakers"""
        search_tool = SerperDevTool()
        web_tool = WebsiteSearchTool()

        return Agent(
            config=self.agents_config['topic_researcher'],
            tools=[search_tool, web_tool],
            verbose=False,
            allow_delegation=False
        )

    @agent
    def study_coordinator(self) -> Agent:
        """Agent responsible for creating study plans and tracking preparation"""
        preferences_file_tool = FileReadTool(file_path=self.preferences_path)
        schedule_file_tool = FileReadTool(file_path=self.schedule_path)

        return Agent(
            config=self.agents_config['study_coordinator'],
            tools=[preferences_file_tool, schedule_file_tool],
            verbose=False,
            allow_delegation=False
        )

    @task
    def next_class_briefing(self) -> Task:
        """Task to get information about the next upcoming class"""
        return Task(
            config=self.tasks_config['next_class_briefing']
        )

    @task
    def topic_primer(self) -> Task:
        """Task to research and create a primer on a specific topic"""
        return Task(
            config=self.tasks_config['topic_primer']
        )

    @task
    def weekly_preparation(self) -> Task:
        """Task to create a weekly preparation plan"""
        return Task(
            config=self.tasks_config['weekly_preparation']
        )

    @task
    def assignment_tracker(self) -> Task:
        """Task to track all assignments for a specific track"""
        return Task(
            config=self.tasks_config['assignment_tracker']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Voice Course Assistant crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,  # Less verbose for cleaner voice interaction
            memory=False,  # Disable memory for faster responses
            output_log_file=False  # Disable trace output
        )

    def get_next_class_info(self, user_question: str, current_date: str = None) -> str:
        """
        Get information about the next class.

        Args:
            user_question: The user's original question
            current_date: Optional date string (e.g., "10/15/2024")
                         If None, uses today's date

        Returns:
            String with next class information tailored to user's question
        """
        if current_date is None:
            current_date = datetime.now().strftime("%m/%d/%Y")

        # Create fresh crew with only schedule_navigator agent and next_class_briefing task
        crew = Crew(
            agents=[self.schedule_navigator()],
            tasks=[self.next_class_briefing()],
            process=Process.sequential,
            verbose=False,
            memory=False,
            output_log_file=False
        )

        # Run the crew
        result = crew.kickoff(inputs={
            'user_question': user_question,
            'current_date': current_date,
            'schedule_path': self.schedule_path
        })

        # Extract text from result
        if hasattr(result, 'raw'):
            return result.raw
        else:
            return str(result)

    def research_topic(self, user_question: str, topic: str, current_date: str = None) -> str:
        """
        Research a specific topic related to the course.

        Args:
            user_question: The user's original question
            topic: The topic to research
            current_date: Optional date string

        Returns:
            String with topic research tailored to user's question
        """
        if current_date is None:
            current_date = datetime.now().strftime("%m/%d/%Y")

        # Create fresh crew with only topic_researcher agent and topic_primer task
        crew = Crew(
            agents=[self.topic_researcher()],
            tasks=[self.topic_primer()],
            process=Process.sequential,
            verbose=False,
            memory=False,
            output_log_file=False
        )

        # Run the crew
        result = crew.kickoff(inputs={
            'user_question': user_question,
            'topic': topic,
            'current_date': current_date
        })

        # Extract text from result
        if hasattr(result, 'raw'):
            return result.raw
        else:
            return str(result)

    def get_weekly_plan(self, user_question: str, current_date: str = None) -> str:
        """
        Generate a weekly preparation plan.

        Args:
            user_question: The user's original question
            current_date: Optional date string

        Returns:
            String with weekly preparation plan tailored to user's question
        """
        if current_date is None:
            current_date = datetime.now().strftime("%m/%d/%Y")

        # Create fresh crew with only study_coordinator agent and weekly_preparation task
        crew = Crew(
            agents=[self.study_coordinator()],
            tasks=[self.weekly_preparation()],
            process=Process.sequential,
            verbose=False,
            memory=False,
            output_log_file=False
        )

        # Run the crew
        result = crew.kickoff(inputs={
            'user_question': user_question,
            'current_date': current_date,
            'schedule_path': self.schedule_path,
            'preferences_path': self.preferences_path
        })

        # Extract text from result
        if hasattr(result, 'raw'):
            return result.raw
        else:
            return str(result)

    def track_assignments(self, user_question: str, track: str, current_date: str = None) -> str:
        """
        Track assignments for a specific track.

        Args:
            user_question: The user's original question
            track: 'Tech' or 'Analyst'
            current_date: Optional date string

        Returns:
            String with assignment tracking information tailored to user's question
        """
        if current_date is None:
            current_date = datetime.now().strftime("%m/%d/%Y")

        # Validate track
        if track not in ['Tech', 'Analyst']:
            track = 'Tech'  # Default to Tech

        # Create fresh crew with only schedule_navigator agent and assignment_tracker task
        crew = Crew(
            agents=[self.schedule_navigator()],
            tasks=[self.assignment_tracker()],
            process=Process.sequential,
            verbose=False,
            memory=False,
            output_log_file=False
        )

        # Run the crew
        result = crew.kickoff(inputs={
            'user_question': user_question,
            'track': track,
            'current_date': current_date,
            'schedule_path': self.schedule_path
        })

        # Extract text from result
        if hasattr(result, 'raw'):
            return result.raw
        else:
            return str(result)

    def cleanup(self):
        """Clean up resources."""
        pass
