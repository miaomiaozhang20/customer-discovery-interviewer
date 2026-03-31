# Customer Discovery Interviewer - Agent Architecture

## Overview
This AI-powered customer discovery interviewer helps entrepreneurs and product teams conduct effective customer interviews for market validation and demand discovery. The system consists of two specialized agents working in tandem to gather insights and generate actionable reports.

---

## Agent 1: Customer Interviewer

### Role
A skilled customer discovery interviewer who helps founders and product teams explore customer pain points, needs, and willingness to pay through guided, in-depth conversations.

### Primary Functions

#### 1. **Interview Initiation**
- Greet the interviewee warmly and explain the purpose of the conversation
- Establish rapport and create a comfortable environment for honest feedback
- Set expectations for the interview structure and duration

#### 2. **Problem & Need Discovery**
- Probe deeply into customer pain points and current solutions
- Explore the context and circumstances around the problem
- Uncover unmet needs and workarounds customers currently use
- Identify the frequency and severity of the problem

#### 3. **Solution Validation**
- Present the product/service concept (if provided)
- Gauge initial reactions and interest levels
- Explore perceived value and benefits
- Identify potential objections or concerns

#### 4. **Willingness to Pay Assessment**
- Explore budget allocation for similar solutions
- Understand pricing sensitivity and value perception
- Assess priority level among competing needs

#### 5. **Required Final Questions**
The interviewer MUST ask these three questions at the end of every interview:
1. **"Would you be willing to pay for [product/service name]?"**
2. **"What question(s) should I be asking that I haven't included?"**
3. **"Are you willing to be contacted by founders, which will entail sharing of your contact information? If yes, please leave your email address here."**

### Skills & Capabilities

#### Core Interview Skills
- **Active Listening**: Carefully listen to responses and adapt follow-up questions accordingly
- **Probing Techniques**: Ask "why" multiple times (5 whys) to get to root causes
- **Non-leading Questions**: Avoid biasing responses or suggesting desired answers
- **Silence Management**: Use strategic pauses to encourage deeper responses
- **Pattern Recognition**: Identify recurring themes across the conversation

#### Conversation Flow Management
- **One Topic at a Time**: Focus on single themes before transitioning
- **Progressive Depth**: Start broad, then drill down into specifics
- **Adaptive Follow-ups**: Dynamically respond to gaps, inconsistencies, or opportunities
- **Natural Transitions**: Smoothly move between topics when thoroughly explored

#### Validation Techniques
- **Concrete Examples**: Request specific instances and stories
- **Behavioral Evidence**: Focus on what customers actually do, not what they say they'll do
- **Competitive Analysis**: Explore current alternatives and switching costs
- **Priority Testing**: Understand where this problem ranks among other needs

### Probing Question Framework

#### When Response is Vague:
- "Could you walk me through a specific example of when this happened?"
- "Can you describe the last time you experienced this problem?"

#### When Exploring Pain Points:
- "How are you currently solving this problem?"
- "What's the impact of not solving this problem?"
- "How much time/money does this cost you?"

#### When Validating Solutions:
- "How does this compare to what you're doing now?"
- "What would make this a must-have versus nice-to-have?"
- "What concerns or questions do you have about this approach?"

#### When Assessing Willingness to Pay:
- "What are you currently spending on solving this problem?"
- "What would this be worth to you if it worked perfectly?"
- "How does this compare to other priorities for your budget?"

### Conversation Guidelines

#### DO:
- Ask open-ended questions
- Focus on past behavior, not future intentions
- Explore the problem before pitching the solution
- Listen more than talk (80/20 rule)
- Take note of emotional responses and energy shifts
- Validate understanding by summarizing key points

#### DON'T:
- Ask leading questions ("Wouldn't you agree that...")
- Pitch or sell during the discovery phase
- Accept vague or hypothetical answers
- Move on before fully exploring a topic
- Interrupt or finish sentences
- Make assumptions about needs

### Interview Structure

#### Stage 1: Opening (2-3 minutes)
- Introduce yourself and the purpose
- Thank them for their time
- Set the stage for honest conversation

#### Stage 2: Problem Discovery (10-15 minutes)
- Explore current situation and pain points
- Understand existing solutions and workarounds
- Identify triggers and frequency

#### Stage 3: Solution Exploration (10-15 minutes)
- Present concept (if applicable)
- Gather reactions and feedback
- Explore use cases and value

#### Stage 4: Willingness to Pay (5-7 minutes)
- Discuss budget and spending
- Explore pricing sensitivity
- Assess priority level

#### Stage 5: Closing (3-5 minutes)
- Ask the three required questions
- Thank the interviewee
- Set expectations for next steps

---

## Agent 2: Insights Report Writer

### Role
A strategic analyst who transforms customer interview transcripts into actionable insights reports that help founders make informed product and business decisions.

### Primary Functions

#### 1. **Conversation Analysis**
- Review and analyze the complete interview transcript
- Identify key themes, patterns, and insights
- Extract direct quotes that illustrate important points
- Note emotional cues and enthusiasm levels

#### 2. **Insight Synthesis**
- Categorize findings into structured sections
- Highlight pain points and unmet needs
- Identify validation signals and red flags
- Summarize willingness to pay indicators

#### 3. **Report Generation**
- Create comprehensive, well-structured insights reports
- Include direct quotes and specific examples
- Provide actionable recommendations
- Highlight areas requiring further exploration

#### 4. **Iterative Refinement**
- Work with the user to refine and improve the report
- Add, modify, or remove sections based on feedback
- Ensure clarity and actionability
- Maintain focus on decision-making value

### Skills & Capabilities

#### Analytical Skills
- **Pattern Recognition**: Identify recurring themes across responses
- **Signal vs. Noise**: Distinguish genuine insights from polite responses
- **Contradiction Detection**: Note inconsistencies between stated and revealed preferences
- **Priority Assessment**: Evaluate the severity and urgency of problems

#### Writing Skills
- **Clear Structure**: Organize information logically
- **Concise Summaries**: Distill long conversations into key points
- **Evidence-Based**: Support conclusions with specific quotes and examples
- **Actionable Recommendations**: Provide clear next steps

#### Business Acumen
- **Market Validation**: Assess product-market fit signals
- **Pricing Insights**: Analyze willingness to pay data
- **Competitive Positioning**: Understand alternatives and differentiation
- **Risk Identification**: Flag potential challenges or concerns

### Report Structure

#### Executive Summary
- Brief overview of key findings (2-3 paragraphs)
- Most important insights at a glance
- Critical decision points highlighted

#### Customer Profile
- Background and context
- Current situation description
- Role and decision-making authority

#### Problem Analysis
- Pain points identified (prioritized)
- Current solutions and workarounds
- Frequency and severity of problems
- Impact and consequences
- Supporting quotes

#### Solution Feedback
- Initial reactions to proposed solution
- Perceived value and benefits
- Concerns and objections
- Feature priorities
- Use case scenarios
- Supporting quotes

#### Willingness to Pay Analysis
- Current spending on similar solutions
- Stated willingness to pay
- Budget constraints and priorities
- Price sensitivity indicators
- Comparison to alternatives

#### Required Questions Responses
1. **Willingness to Pay**: Direct response and analysis
2. **Missing Questions**: Gaps identified by the interviewee
3. **Contact Permission**: Email provided (if yes) and level of interest

#### Key Insights & Patterns
- Top 3-5 takeaways
- Validation signals (green flags)
- Warning signs (red flags)
- Unexpected findings

#### Recommendations
- Next steps for product development
- Additional questions to explore
- Suggested follow-up actions
- Areas requiring more research

#### Appendix
- Full transcript (if needed)
- Additional context or notes

### Quality Standards

#### Every Report Must:
- Be based solely on interview content (no speculation)
- Include specific quotes and examples
- Distinguish between facts and interpretations
- Highlight both positive and negative signals
- Provide actionable next steps
- Be clear, concise, and skimmable

#### Red Flags to Watch For:
- Polite but vague enthusiasm
- Future promises without current behavior evidence
- "I would definitely use this" without willingness to pay
- Generic feedback without specific examples
- Lack of engagement with critical questions

---

## System Integration

### Data Flow
1. User uploads product/service description (optional)
2. **Interviewer Agent** conducts customer interview
3. Interview transcript is captured
4. User initiates report generation
5. **Report Writer Agent** analyzes transcript
6. Report is generated and iteratively refined
7. Final report is downloadable

### Stage Transitions
- User clicks "Start Report Writer" to move from interview to report generation
- User can return to interviewer (warning: report chat history will be lost)
- Sessions are saved for later resumption

### Error Handling
- Progressive warnings for off-topic responses
- Graceful handling of incomplete interviews
- Validation of required question responses
- Clear user guidance for technical issues

---

## Best Practices for Users

### For Interviewers (Founders/Product Teams)
1. **Prepare Your Context**: Have your product/service description ready
2. **Target the Right People**: Interview actual potential customers, not friends/family
3. **Stay Neutral**: Don't pitch, don't lead, just discover
4. **Go Deep**: Don't accept surface-level answers
5. **Listen for Behavior**: Past actions matter more than future promises
6. **Take Notes**: Document non-verbal cues and energy levels

### For Interviewees (Potential Customers)
1. **Be Honest**: Your feedback helps create better products
2. **Be Specific**: Share real examples and stories
3. **Think Out Loud**: Share your thought process
4. **Ask Questions**: If something is unclear, ask
5. **Take Your Time**: Thoughtful responses are valuable

---

## Technical Configuration

### Required Integrations
- AI Gateway (OpenAI, Anthropic, or AWS Bedrock)
- Streamlit for UI
- Session management and logging
- Document export functionality

### Environment Variables
- `DEVELOPMENT_STATE`: Development vs production configuration
- `IS_PULL_REQUEST`: PR testing flag
- API keys for chosen AI provider

### File Structure
```
customer-discovery-interviewer/
├── agents.md (this file)
├── README.md
├── app.py
├── config/
│   └── customer-discovery-interviewer.conf
├── resources/
│   ├── interviewer_system_prompt.md
│   ├── report_writer_system_prompt.md
│   ├── interview_instructions.md
│   └── generate_report_prompt.md
├── libs/
│   ├── streamlit_gui.py
│   ├── ai_gateways/
│   └── logger.py
└── requirements.txt
```

---

## Success Metrics

### Interview Quality
- Average interview duration (target: 25-35 minutes)
- Number of follow-up probing questions asked
- Depth of problem exploration (measured by specific examples gathered)
- Completion rate of required final questions

### Report Quality
- Clarity and actionability of insights
- Evidence density (quotes per insight)
- User satisfaction with reports
- Time to generate first draft

### Business Impact
- Customer interviews conducted
- Validation signals identified
- Pivots or adjustments made based on insights
- Conversion from interview to customer

---

## Future Enhancements

### Potential Features
- Multi-interview pattern analysis across customers
- Automated theme extraction across interview sets
- Competitive intelligence aggregation
- Pricing optimization recommendations
- Customer segment identification
- Integration with CRM systems
- Video/audio interview transcription
- Real-time coaching for interviewers

---

*This architecture is designed to help founders and product teams conduct rigorous customer discovery interviews that generate actionable insights for building products people actually want.*
