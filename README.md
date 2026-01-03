# 🤖 MAS-Automation

**Multi-Agent System Design Through Natural Language**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MAS-Automation is an intelligent framework that transforms natural language descriptions into fully-specified multi-agent systems. Design complex agent architectures through simple conversation—no manual configuration required.

<p align="center">
  <img src="https://raw.githubusercontent.com/aorogat/multi-agent-automation/main/images/arch.jpg" alt="MAS-Automation Architecture" width="800"/>
</p>

---

## ✨ Features

- **🗣️ Conversational Design** - Describe your system in plain English; let AI handle the architecture
- **📊 Live Visualization** - Real-time graph rendering of agent relationships and communication flows
- **🔄 Iterative Refinement** - Continuously evolve your design through interactive dialogue
- **🎯 Framework Agnostic** - Supports multiple MAS frameworks (LangGraph, CrewAI, Concordia)
- **📝 Automatic Specification** - Generates comprehensive system specifications with agents, tools, topology, and constraints
- **🎨 Modern UI** - Clean, professional interface built with NiceGUI and Cytoscape.js


![MAS Automation Demo](https://raw.githubusercontent.com/aorogat/multi-agent-automation/main/images/Automation.gif)


---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mas-automation.git
   cd mas-automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Launch the application**
   ```bash
   python run.py
   ```

   This starts both services:
   - **Backend API**: http://localhost:8000
   - **Frontend UI**: http://localhost:8080

### Alternative: Run Services Separately

**Backend:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Frontend:**
```bash
python webui/app.py
```

---

## 💡 Usage

1. Open your browser to http://localhost:8080
2. Start describing your multi-agent system:
   - *"Build a customer service system with a manager and three specialist agents"*
   - *"Create a simulation of a school with 200 students and 10 teachers"*
   - *"Design an anomaly detection system with monitoring and analysis agents"*
3. The AI assistant will:
   - Ask clarifying questions to gather missing requirements
   - Build and refine the MAS specification in real-time
   - Visualize the agent architecture dynamically
   - Generate a comprehensive design summary

---

## 🏗️ Architecture

```
mas-automation/
├── backend/
│   ├── main.py                      # FastAPI application entry point
│   ├── engine/
│   │   ├── mas_engine.py            # Core MAS automation engine
│   │   └── requirements_agent/
│   │       ├── agent.py             # LLM-powered requirements extractor
│   │       └── prompts/             # Prompt templates
│   └── models/                      # Data models and schemas
├── webui/
│   └── app.py                       # NiceGUI frontend application
├── run.py                           # Combined launcher script
├── requirements.txt                 # Python dependencies
├── .env                             # Environment configuration
└── README.md                        # This file
```

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | REST API for chat handling and MAS engine execution |
| **Frontend** | NiceGUI | Interactive conversational interface and visualization |
| **Visualization** | Cytoscape.js | Dynamic graph rendering of agent architectures |
| **AI Engine** | OpenAI GPT-4 | Natural language understanding and specification generation |
| **Runtime** | Python 3.10+ | Core application runtime |

---

## 📡 API Reference

### POST `/chat`

Processes user messages and returns updated system state.

**Request Body:**
```json
{
  "message": "string",
  "history": [
    {"role": "user", "content": "string"},
    {"role": "assistant", "content": "string"}
  ]
}
```

**Response:**
```json
{
  "reply": "Assistant response message",
  "graph": [
    {"data": {"id": "agent1", "label": "Manager"}},
    {"data": {"source": "agent1", "target": "agent2"}}
  ],
  "spec": {
    "task": "string",
    "goal": "string",
    "agents": ["string"],
    "tools": ["string"],
    "communication": "string",
    "topology": "string",
    "constraints": {}
  },
  "spec_text": "Natural language design summary"
}
```

---

## 🎯 Roadmap

- [x] Conversational MAS design interface
- [x] Real-time architecture visualization
- [x] Multi-framework specification generation
- [ ] **Code Generation** - Export runnable Python projects
- [ ] **Template Library** - Pre-built MAS patterns
- [ ] **Simulation Runner** - Execute and test generated systems
- [ ] **Multi-LLM Support** - Support for Claude, Gemini, and open-source models
- [ ] **Collaborative Design** - Multi-user system design sessions

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [NiceGUI](https://nicegui.io/)
- Visualization by [Cytoscape.js](https://js.cytoscape.org/)
- AI capabilities by [OpenAI](https://openai.com/)

---

## 📧 Contact

Project Link: [https://github.com/yourusername/mas-automation](https://github.com/yourusername/mas-automation)

---

<p align="center">Made with ❤️ by the MAS-Automation Team</p>