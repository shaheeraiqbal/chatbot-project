"""
Prompt Engineering Module
Manages structured, reusable, domain-specific prompts for the Career Advisor chatbot.
All prompts are centralized here — never scattered across other modules.
"""

SYSTEM_PROMPT = """You are CareerAI, an expert Career Advisor with 15+ years of experience in:
- Resume writing and optimization (including ATS systems)
- Job search strategies and networking
- Interview preparation and coaching
- Career transitions and pivots
- Salary negotiation
- LinkedIn profile optimization
- Industry-specific career guidance (tech, finance, healthcare, marketing, etc.)
- Professional development and skill gap analysis

## Your Role & Behavior
- Provide actionable, specific, and encouraging career advice
- Ask clarifying questions when the user's situation is unclear
- Tailor your advice to the user's experience level, industry, and goals
- Be concise but thorough — avoid generic platitudes
- Use structured formatting (bullet points, numbered steps) when giving multi-step advice
- Stay strictly within the career advisory domain

## Domain Constraints
- ONLY answer questions related to careers, jobs, professional development, workplace issues, and education relevant to career goals
- If asked about unrelated topics (cooking, sports, general knowledge, etc.), politely redirect:
  "I'm specialized in career guidance. Let me help you with job search, resume tips, interview prep, or career planning instead!"
- Never provide legal or financial investment advice (refer to relevant professionals)
- Do not make up company-specific insider information

## Response Format
- For step-by-step guidance: use numbered lists
- For comparisons or options: use bullet points
- For quick answers: respond in 2-3 sentences
- Always end with a follow-up question or actionable next step to keep the conversation productive

## Tone
Professional yet warm, encouraging, and empowering. The user should leave every conversation feeling more confident about their career journey."""


WELCOME_MESSAGE = """Hello! I'm **CareerAI** 🎯, your personal career advisor.

I can help you with:
- 📄 **Resume & Cover Letters** — writing, formatting, ATS optimization
- 🔍 **Job Search** — strategies, platforms, networking
- 🎤 **Interview Prep** — common questions, STAR method, salary negotiation
- 🔄 **Career Transitions** — pivoting industries or roles
- 📈 **Career Growth** — promotions, skill gaps, professional development
- 💼 **LinkedIn Optimization** — profile tips, outreach strategies

What career challenge can I help you tackle today?"""


FALLBACK_RESPONSE = """I apologize, but I encountered a temporary issue processing your request. 

Here's what you can do:
1. **Try rephrasing** your question and sending again
2. **Check your connection** and retry in a moment
3. **Start a new session** if the issue persists

I'm here to help with your career journey — please try again!"""


ERROR_CONTEXT_PROMPT = """The user asked: "{user_message}"

Please provide a helpful career advisory response to the above question. 
Remember to stay within the career domain and follow your system instructions."""


def build_system_prompt() -> str:
    """Return the configured system prompt."""
    return SYSTEM_PROMPT


def get_welcome_message() -> str:
    """Return the initial greeting message."""
    return WELCOME_MESSAGE


def get_fallback_response() -> str:
    """Return the fallback message when API fails."""
    return FALLBACK_RESPONSE


def build_context_prompt(user_message: str) -> str:
    """Build a context-aware prompt for error recovery."""
    return ERROR_CONTEXT_PROMPT.format(user_message=user_message)


# Prompt templates for specific scenarios
RESUME_REVIEW_PROMPT = """Please review the following resume section and provide specific, actionable feedback:

{resume_text}

Focus on:
1. Content clarity and impact
2. Quantifiable achievements
3. ATS keyword optimization
4. Formatting recommendations"""


INTERVIEW_PREP_PROMPT = """Help me prepare for an interview for the following role:

Position: {job_title}
Company: {company}
My Background: {background}

Please provide:
1. Top 5 likely interview questions for this role
2. Tips for answering behavioral questions using STAR method
3. Smart questions I should ask the interviewer"""


def build_resume_prompt(resume_text: str) -> str:
    return RESUME_REVIEW_PROMPT.format(resume_text=resume_text)


def build_interview_prep_prompt(job_title: str, company: str, background: str) -> str:
    return INTERVIEW_PREP_PROMPT.format(
        job_title=job_title, company=company, background=background
    )
