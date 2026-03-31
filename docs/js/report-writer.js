// Report Writer Agent
class ReportWriter {
    constructor() {
        this.systemPrompt = SYSTEM_PROMPTS.REPORT_WRITER;
    }

    async generateInitialReport() {
        try {
            // Get interview transcript
            const messages = storage.getMessages();

            if (messages.length === 0) {
                throw new Error('No interview data available to generate report');
            }

            // Build conversation transcript
            let transcript = "Interview Transcript:\n\n";
            messages.forEach(msg => {
                const role = msg.role === 'ai' ? 'Interviewer' : 'Interviewee';
                transcript += `${role}: ${msg.content}\n\n`;
            });

            // Add product context if available
            const productDesc = storage.getProductDescription();
            if (productDesc) {
                transcript = `Product/Service Description:\n${productDesc}\n\n${transcript}`;
            }

            // Generate report prompt
            const prompt = `${transcript}\n\n---\n\nBased on the customer discovery interview above, generate a comprehensive insights report following this structure:

## Executive Summary
Brief overview (2-3 paragraphs) of key findings and critical decision points.

## Interviewee Profile
Background and context of the interviewee.

## Problem Analysis
Detailed analysis of pain points identified with:
- Specific problems mentioned
- Frequency and severity
- Current impact
- Supporting direct quotes

## Current Behavior & Spending
- What they're doing now to address problems
- Tools/services currently used
- Budget allocation and spending patterns
- Revealed preferences from actual behavior

## Solution Feedback
(If a solution was discussed)
- Initial reactions
- Perceived value and benefits
- Concerns or objections
- Assessment of genuine vs. polite interest

## Willingness to Pay Analysis
Detailed analysis of their response to the willingness to pay question including:
- Direct answer
- Reasoning and context
- Comparison to current spending
- Assessment of genuine willingness

## Required Questions Responses
Explicit responses to all three required questions:
1. Willingness to pay response and analysis
2. Missing questions they identified
3. Contact permission and email (if provided)

## Key Insights & Patterns
Top 3-5 takeaways from the conversation.

## Validation Signals (Green Flags) ✅
List positive indicators found:
- Specific pain points with examples
- Current spending on problem/solution
- Emotional responses
- Concrete use cases
- Willingness to pay with amounts
- Contact info shared

## Warning Signs (Red Flags) 🚩
List concerning indicators found:
- Vague or hypothetical responses
- Polite enthusiasm without specifics
- No current pain point
- Unwilling to pay
- Generic praise

## Recommendations
Actionable next steps based on evidence:
- Product development priorities
- Additional validation needed
- Pricing considerations
- Potential pivots or adjustments

---

Use clear markdown formatting. Include direct quotes in blockquotes. Be honest about both positive and negative signals. Base everything strictly on the interview content.`;

            // Get report from AI
            const report = await api.sendMessage(
                [{ role: 'user', content: prompt }],
                this.systemPrompt
            );

            // Save report
            storage.setReport(report);
            storage.addMessage('ai', report);

            return report;

        } catch (error) {
            console.error('Report generation error:', error);
            throw error;
        }
    }

    async refineReport(userFeedback) {
        try {
            const currentReport = storage.getReport();

            if (!currentReport) {
                throw new Error('No report available to refine');
            }

            // Add user feedback to messages
            storage.addMessage('user', userFeedback);

            // Prepare refinement prompt
            const messages = [
                { role: 'assistant', content: currentReport },
                { role: 'user', content: userFeedback }
            ];

            // Get refined report
            const refinedReport = await api.sendMessage(messages, this.systemPrompt);

            // Save refined report
            storage.setReport(refinedReport);
            storage.addMessage('ai', refinedReport);

            return refinedReport;

        } catch (error) {
            console.error('Report refinement error:', error);
            throw error;
        }
    }

    exportReportAsWord() {
        const report = storage.getReport();

        if (!report) {
            throw new Error('No report available to export');
        }

        // Convert markdown to simple HTML-like structure for Word
        let content = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Customer Discovery Insights Report</title>
    <style>
        body { font-family: Calibri, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; }
        h1 { color: #2C3E50; border-bottom: 3px solid #FF6B6B; padding-bottom: 10px; }
        h2 { color: #34495E; margin-top: 30px; border-bottom: 1px solid #BDC3C7; padding-bottom: 5px; }
        h3 { color: #7F8C8D; }
        blockquote { border-left: 4px solid #FF6B6B; padding-left: 15px; margin: 15px 0; font-style: italic; color: #555; }
        ul, ol { margin-left: 20px; }
        p { margin: 10px 0; }
        .metadata { color: #7F8C8D; font-size: 0.9em; margin-bottom: 30px; }
    </style>
</head>
<body>
    <h1>Customer Discovery Insights Report</h1>
    <div class="metadata">
        <p>Generated: ${new Date().toLocaleString()}</p>
        <p>Session ID: ${storage.currentSession.id}</p>
    </div>
    ${this.markdownToHTML(report)}
</body>
</html>`;

        // Create blob and download
        const blob = new Blob([content], { type: 'application/msword' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `customer_discovery_report_${new Date().toISOString().split('T')[0]}.doc`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    markdownToHTML(markdown) {
        let html = markdown;

        // Headers
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

        // Blockquotes
        html = html.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>');

        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Italic
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Lists
        html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

        // Numbered lists
        html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>');

        // Paragraphs
        html = html.split('\n\n').map(para => {
            if (!para.startsWith('<') && para.trim() !== '') {
                return `<p>${para}</p>`;
            }
            return para;
        }).join('\n');

        return html;
    }
}

// Global report writer instance
const reportWriter = new ReportWriter();
