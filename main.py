import streamlit as st
import sys
from orchestrator.graph import run_graph

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Agent Orchestrator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# 2. CUSTOM CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    /* GLOBAL */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        font-family: 'Inter', sans-serif;
        color: #e8eaed;
    }

    header, footer, .stDeployButton {display: none;}

    /* MAIN CONTAINER */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* GLASS CARD BASE */
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }

    /* AGENT CARD STATES */
    .agent-card {
        text-align: center;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }

    .agent-idle {
        opacity: 0.5;
        border-color: rgba(255, 255, 255, 0.05);
    }

    .agent-active {
        opacity: 1;
        border: 1px solid rgba(99, 179, 237, 0.5);
        box-shadow: 0 0 30px rgba(99, 179, 237, 0.15), inset 0 0 20px rgba(99, 179, 237, 0.05);
        animation: pulse-border 2s ease-in-out infinite;
    }

    .agent-complete {
        opacity: 1;
        border: 1px solid rgba(72, 187, 120, 0.5);
        box-shadow: 0 0 20px rgba(72, 187, 120, 0.1);
    }

    @keyframes pulse-border {
        0%, 100% { border-color: rgba(99, 179, 237, 0.5); }
        50% { border-color: rgba(99, 179, 237, 0.8); }
    }

    /* AGENT CONTENT */
    .agent-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        filter: grayscale(100%);
        transition: filter 0.3s;
    }

    .agent-active .agent-icon,
    .agent-complete .agent-icon {
        filter: grayscale(0%);
    }

    .agent-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #fff;
        margin-bottom: 0.25rem;
    }

    .agent-role {
        font-size: 0.75rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }

    .agent-status {
        font-size: 0.85rem;
        font-weight: 600;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        display: inline-block;
    }

    .status-idle {
        background: rgba(107, 114, 128, 0.2);
        color: #9ca3af;
    }

    .status-active {
        background: rgba(99, 179, 237, 0.2);
        color: #63b3ed;
        animation: pulse-text 1.5s ease-in-out infinite;
    }

    .status-complete {
        background: rgba(72, 187, 120, 0.2);
        color: #48bb78;
    }

    @keyframes pulse-text {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    /* TERMINAL */
    .terminal-container {
        background: #0a0a0f;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        position: relative;
    }

    .terminal-header {
        background: rgba(255, 255, 255, 0.03);
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .terminal-header-left {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .terminal-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
    }

    .dot-red { background: #ff5f56; }
    .dot-yellow { background: #ffbd2e; }
    .dot-green { background: #27c93f; }

    .terminal-title {
        color: #6b7280;
        font-size: 0.75rem;
        margin-left: 0.5rem;
        font-weight: 500;
    }

    .live-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.35rem 0.75rem;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 6px;
    }

    .live-dot {
        width: 10px;
        height: 10px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse-live 1.5s ease-in-out infinite;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.6);
    }

    @keyframes pulse-live {
        0%, 100% {
            opacity: 1;
            transform: scale(1);
            box-shadow: 0 0 12px rgba(16, 185, 129, 0.6);
        }
        50% {
            opacity: 0.7;
            transform: scale(1.3);
            box-shadow: 0 0 18px rgba(16, 185, 129, 0.8);
        }
    }

    .live-text {
        color: #10b981;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .terminal-body {
        font-family: 'JetBrains Mono', monospace;
        padding: 1rem;
        height: 600px;
        overflow-y: auto;
        font-size: 0.82rem;
        line-height: 1.5;
        color: #d1d5db;
    }

    .terminal-body::-webkit-scrollbar {
        width: 8px;
    }

    .terminal-body::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }

    .terminal-body::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }

    /* RAW TERMINAL OUTPUT */
    .terminal-line {
        margin: 0;
        padding: 2px 0;
        white-space: pre-wrap;
        word-wrap: break-word;
        font-family: 'JetBrains Mono', monospace;
    }

    /* COLOR CODING FOR DIFFERENT OUTPUT TYPES */
    .line-separator {
        color: #4b5563;
    }

    .line-agent-header {
        color: #fbbf24;
        font-weight: 600;
    }

    .line-search {
        color: #60a5fa;
    }

    .line-success {
        color: #34d399;
    }

    .line-error {
        color: #f87171;
    }

    .line-info {
        color: #a78bfa;
    }

    .line-default {
        color: #d1d5db;
    }

    /* HEADER GRADIENT */
    .app-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .app-subtitle {
        color: #9ca3af;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* INPUT STYLING */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e8eaed !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
    }

    .stTextInput input:focus {
        border-color: rgba(99, 179, 237, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(99, 179, 237, 0.1) !important;
    }

    /* BUTTON STYLING */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }

    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }

    /* SECTION HEADERS */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #fff;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* COMPLETION BANNER */
    .completion-banner {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        text-align: center;
        animation: slideIn 0.5s ease-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .completion-text {
        color: #6ee7b7;
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 3. STDOUT CAPTURE CLASS
# -----------------------------------------------------------------------------
class StreamCapture:
    """Captures stdout/stderr in real-time"""

    def __init__(self, placeholder, planner_ph=None, architect_ph=None, coder_ph=None):
        self.placeholder = placeholder
        self.lines = []
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        # Agent placeholders for real-time updates
        self.planner_ph = planner_ph
        self.architect_ph = architect_ph
        self.coder_ph = coder_ph

        # Track current agent states
        self.agent_states = {
            "planner": "idle",
            "architect": "idle",
            "coder": "idle"
        }

    def write(self, text):
        """Capture print statements"""
        # Write to original stdout too
        self.original_stdout.write(text)
        self.original_stdout.flush()

        # Add to our buffer
        if text and text.strip():
            self.lines.append(text.rstrip())

            # Update agent status BEFORE rendering terminal
            self.update_agent_status()

            # Then render terminal
            self.render()

    def update_agent_status(self):
        """Update agent cards based on latest terminal output"""
        if not (self.planner_ph and self.architect_ph and self.coder_ph):
            return

        # Get the current line being written
        current_line = self.lines[-1] if self.lines else ""
        current_line_lower = current_line.lower()

        # Get recent output for context
        recent_output = ' '.join(self.lines[-10:]).lower()

        # PLANNER AGENT
        if "planner agent in progress" in current_line_lower or "----- planner agent" in current_line_lower:
            self.agent_states["planner"] = "active"
            print(f"DEBUG: Setting Planner to ACTIVE", file=self.original_stdout)
        elif self.agent_states["planner"] == "active" and (
                "plan created" in current_line_lower or "architect agent" in current_line_lower):
            self.agent_states["planner"] = "complete"
            print(f"DEBUG: Setting Planner to COMPLETE", file=self.original_stdout)

        # ARCHITECT AGENT
        if "architect agent in progress" in current_line_lower or "----- architect agent" in current_line_lower:
            if self.agent_states["planner"] == "active":
                self.agent_states["planner"] = "complete"
            self.agent_states["architect"] = "active"
            print(f"DEBUG: Setting Architect to ACTIVE", file=self.original_stdout)
        elif self.agent_states["architect"] == "active" and (
                "created" in current_line_lower and "implementation steps" in current_line_lower):
            self.agent_states["architect"] = "complete"
            print(f"DEBUG: Setting Architect to COMPLETE", file=self.original_stdout)

        # CODER AGENT
        if ("coder agent in progress" in current_line_lower or
                "----- coder agent" in current_line_lower or
                ("coder agent -" in current_line_lower and "step" in current_line_lower)):
            if self.agent_states["architect"] == "active":
                self.agent_states["architect"] = "complete"
            self.agent_states["coder"] = "active"
            print(f"DEBUG: Setting Coder to ACTIVE", file=self.original_stdout)
        elif "all coding tasks completed" in current_line_lower:
            self.agent_states["coder"] = "complete"
            print(f"DEBUG: Setting Coder to COMPLETE", file=self.original_stdout)

        # Force update the UI with current states
        try:
            self.planner_ph.markdown(
                render_agent_card("Planner", "Research & Strategy", "🧠", self.agent_states["planner"]),
                unsafe_allow_html=True
            )
            self.architect_ph.markdown(
                render_agent_card("Architect", "System Design", "📐", self.agent_states["architect"]),
                unsafe_allow_html=True
            )
            self.coder_ph.markdown(
                render_agent_card("Coder", "Implementation", "👨‍💻", self.agent_states["coder"]),
                unsafe_allow_html=True
            )
        except Exception as e:
            print(f"DEBUG: Error updating agent cards: {e}", file=self.original_stdout)

    def flush(self):
        """Required for file-like object"""
        self.original_stdout.flush()

    def colorize_line(self, line):
        """Apply color coding based on the line content"""
        line_lower = line.lower()

        # Determine color class
        if '---' in line or '━' in line:
            css_class = 'line-separator'
        elif 'agent in progress' in line_lower or 'agent -' in line_lower:
            css_class = 'line-agent-header'
        elif 'searching' in line_lower or 'search' in line_lower:
            css_class = 'line-search'
        elif '✅' in line or 'created' in line_lower or 'complete' in line_lower:
            css_class = 'line-success'
        elif 'error' in line_lower or 'failed' in line_lower:
            css_class = 'line-error'
        elif 'planner agent' in line_lower or 'architect agent' in line_lower or 'coder agent' in line_lower:
            css_class = 'line-info'
        else:
            css_class = 'line-default'

        return f'<div class="terminal-line {css_class}">{self._escape_html(line)}</div>'

    def _escape_html(self, text):
        """Escape HTML special characters"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))

    def render(self):
        """Update the terminal display"""
        lines_html = ''.join(self.colorize_line(line) for line in self.lines)

        terminal_html = f"""
        <div class="terminal-container">
            <div class="terminal-header">
                <div class="terminal-header-left">
                    <span class="terminal-dot dot-red"></span>
                    <span class="terminal-dot dot-yellow"></span>
                    <span class="terminal-dot dot-green"></span>
                    <span class="terminal-title">Live Backend Output</span>
                </div>
                <div class="live-indicator">
                    <span class="live-dot"></span>
                    <span class="live-text">Live</span>
                </div>
            </div>
            <div class="terminal-body" id="terminal-body">
                {lines_html if lines_html else '<div class="terminal-line line-default">Waiting for execution...</div>'}
            </div>
        </div>
        <script>
            // Auto-scroll to bottom
            const terminal = document.getElementById('terminal-body');
            if (terminal) {{
                terminal.scrollTop = terminal.scrollHeight;
            }}
        </script>
        """

        self.placeholder.markdown(terminal_html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. UI COMPONENTS
# -----------------------------------------------------------------------------

def render_agent_card(name, role, icon, status="idle"):
    """Render agent card with current status"""

    status_config = {
        "idle": {
            "class": "agent-idle",
            "status_class": "status-idle",
            "text": "💤 Idle"
        },
        "active": {
            "class": "agent-active",
            "status_class": "status-active",
            "text": "⚡ Working..."
        },
        "complete": {
            "class": "agent-complete",
            "status_class": "status-complete",
            "text": "✓ Complete"
        }
    }

    config = status_config.get(status, status_config["idle"])

    return f"""
    <div class="glass-card agent-card {config['class']}">
        <div class="agent-icon">{icon}</div>
        <div class="agent-name">{name}</div>
        <div class="agent-role">{role}</div>
        <div class="agent-status {config['status_class']}">
            {config['text']}
        </div>
    </div>
    """


def detect_agent_from_output(lines):
    """Detect which agents are active based on terminal output"""
    recent_lines = ' '.join(lines[-10:]).lower()

    states = {
        "planner": "idle",
        "architect": "idle",
        "coder": "idle"
    }

    # Check for completion first
    if "all coding tasks completed" in recent_lines or "workflow finished" in recent_lines:
        states["planner"] = "complete"
        states["architect"] = "complete"
        states["coder"] = "complete"
    else:
        # Check active/complete states
        if "planner agent in progress" in recent_lines:
            states["planner"] = "active"
        elif "plan created" in recent_lines or "architect agent in progress" in recent_lines:
            states["planner"] = "complete"

        if "architect agent in progress" in recent_lines:
            states["architect"] = "active"
        elif "created" in recent_lines and "implementation steps" in recent_lines:
            states["architect"] = "complete"

        if "coder agent in progress" in recent_lines or "coder agent -" in recent_lines:
            states["coder"] = "active"
            if states["architect"] != "active":
                states["architect"] = "complete"

    return states


# -----------------------------------------------------------------------------
# 5. MAIN APPLICATION
# -----------------------------------------------------------------------------

# Header
st.markdown('<div class="app-title">🤖 AI Agent Orchestrator</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Autonomous multi-agent system for intelligent code generation</div>',
            unsafe_allow_html=True)

# Input Section
col1, col2 = st.columns([4, 1])

with col1:
    user_prompt = st.text_input(
        "Project Description",
        placeholder="e.g., Build a futuristic cyberpunk car rental site with neon gradients and animations",
        label_visibility="collapsed"
    )

with col2:
    start_button = st.button("🚀 Execute", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Agent Status Section
st.markdown('<div class="section-header">🧠 Agent Status</div>', unsafe_allow_html=True)
agent_cols = st.columns(3)

# Initialize agent placeholders
planner_ph = agent_cols[0].empty()
architect_ph = agent_cols[1].empty()
coder_ph = agent_cols[2].empty()

# Render initial idle state
planner_ph.markdown(render_agent_card("Planner", "Research & Strategy", "🧠", "idle"), unsafe_allow_html=True)
architect_ph.markdown(render_agent_card("Architect", "System Design", "📐", "idle"), unsafe_allow_html=True)
coder_ph.markdown(render_agent_card("Coder", "Implementation", "👨‍💻", "idle"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Terminal Section
st.markdown('<div class="section-header">🖥️ Live Backend Terminal</div>', unsafe_allow_html=True)
terminal_ph = st.empty()

# Completion banner placeholder
completion_ph = st.empty()

# -----------------------------------------------------------------------------
# 6. ORCHESTRATION WITH LIVE STDOUT CAPTURE
# -----------------------------------------------------------------------------

if start_button and user_prompt:
    try:
        # Create stream capture with agent placeholders for real-time updates
        stream_capture = StreamCapture(
            terminal_ph,
            planner_ph=planner_ph,
            architect_ph=architect_ph,
            coder_ph=coder_ph
        )

        # Redirect stdout to our capture
        sys.stdout = stream_capture
        sys.stderr = stream_capture

        # Run the graph - all print() statements will be captured
        result = run_graph(user_prompt)

        # Restore original stdout/stderr
        sys.stdout = stream_capture.original_stdout
        sys.stderr = stream_capture.original_stderr

        # Final update - mark all as complete
        stream_capture.agent_states["planner"] = "complete"
        stream_capture.agent_states["architect"] = "complete"
        stream_capture.agent_states["coder"] = "complete"
        stream_capture.update_agent_status()

        # Show completion banner
        completion_ph.markdown("""
            <div class="completion-banner">
                <div class="completion-text">✨ Orchestration Complete! ✨</div>
            </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        # Restore stdout/stderr on error
        sys.stdout = stream_capture.original_stdout if 'stream_capture' in locals() else sys.stdout
        sys.stderr = stream_capture.original_stderr if 'stream_capture' in locals() else sys.stderr

        st.error(f"❌ Error: {str(e)}")
        import traceback

        st.code(traceback.format_exc())

elif start_button:
    st.warning("⚠️ Please enter a project description")