# GenaiMediaplan Crew - Email-Based Presentation Generator

Welcome to the GenaiMediaplan Crew project, powered by [crewAI](https://crewai.com). This system automatically generates professional presentations from email content using AI agents. Simply provide an email subject and body, and the system will create a comprehensive business presentation with insights, stakeholder analysis, and strategic recommendations.

## Features

- **Email Content Processing**: Automatically extracts key information from email subject and body
- **AI-Powered Analysis**: Uses multiple AI agents to generate insights and recommendations
- **Professional Presentations**: Creates Google Slides presentations with structured content
- **Business Intelligence**: Generates stakeholder personas, strategic insights, and actionable recommendations
- **REST API**: Easy integration with existing systems

## Use Cases

- **Business Reviews**: Convert performance reports into presentation format
- **Meeting Preparation**: Transform email discussions into structured presentations
- **Stakeholder Communication**: Create professional presentations from email updates
- **Strategic Planning**: Generate insights and recommendations from business communications

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/genai_mediaplan/config/agents.yaml` to define your agents
- Modify `src/genai_mediaplan/config/tasks.yaml` to define your tasks
- Modify `src/genai_mediaplan/crew.py` to add your own logic, tools and specific args
- Modify `src/genai_mediaplan/main.py` to add custom inputs for your agents and tasks

## Running the Project

### Option 1: Command Line Interface

To run with example email content:
```bash
$ crewai run
```

To run with custom email content:
```bash
$ python src/genai_mediaplan/main.py "Your Email Subject" "Your email body content here"
```

### Option 2: REST API

Start the API server:
```bash
$ python -m src.genai_mediaplan.api_server
```

The API will be available at `http://localhost:8000`

### Option 3: Direct Python Usage

```python
from src.genai_mediaplan.main import run_with_email

# Generate presentation from email
email_subject = "Q4 Marketing Performance Review"
email_body = "Hi Team, I wanted to share our Q4 results..."

google_slides_url = run_with_email(email_subject, email_body)
print(f"Presentation created: {google_slides_url}")
```

## API Usage

### Generate Presentation from Email

```bash
curl -X POST "http://localhost:8000/generate-presentation-from-email" \
  -H "Content-Type: application/json" \
  -d '{
    "email_subject": "Q4 Marketing Performance Review",
    "email_body": "Hi Team, I wanted to share our Q4 results..."
  }'
```

### Python Client Example

```python
import requests

response = requests.post("http://localhost:8000/generate-presentation-from-email", 
                        json={
                            "email_subject": "Q4 Marketing Performance Review",
                            "email_body": "Hi Team, I wanted to share our Q4 results..."
                        })

result = response.json()
print(f"Presentation URL: {result['google_slides_url']}")
```

## Understanding Your Crew

The genai-mediaplan Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

### Agent Roles

1. **Definition Agent**: Creates compelling presentation definitions from email content
2. **Data Signals Agent**: Identifies actionable business insights and opportunities
3. **Persona Agent**: Generates stakeholder personas and target profiles
4. **Insight Agent**: Uncovers strategic insights and business opportunities
5. **Market Edge Synthesizer**: Creates coherent business value propositions
6. **Recommendation Agent**: Provides tactical business strategy recommendations
7. **Formatter Agent**: Assembles all outputs into structured presentation content

### Email Processing

The system automatically extracts:
- Key topics and themes
- Action items and next steps
- Performance metrics and KPIs
- Stakeholder information
- Timeline and deadlines
- Business context and objectives

## Support

For support, questions, or feedback regarding the GenaiMediaplan Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
