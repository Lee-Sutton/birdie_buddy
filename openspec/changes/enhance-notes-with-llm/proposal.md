# Enhance Practice Notes with LLM

## Summary
Add an AI-powered enhancement feature to the practice session form that allows users to quickly add notes and have them enhanced by an LLM for better clarity, detail, and coaching insights.

## User Story
As a golfer tracking my practice sessions, I want to quickly jot down rough notes about my session and have an AI enhance them with better terminology, coaching insights, and structured feedback, so that I can maintain high-quality practice records without spending much time on documentation.

## Proposed Solution
Add an "Enhance Notes" button next to the notes textarea in the practice session form that:
1. Sends the current notes to an LLM service
2. Replaces the textarea content with the enhanced version
3. Maintains the original meaning while improving clarity and adding coaching insights

## Technical Approach
- Integrate with an LLM API (OpenAI GPT or similar)
- Add HTMX-powered button for seamless enhancement
- Create a new Django view endpoint for the enhancement service
- Add loading states and error handling
- Preserve user data and allow manual override

## Key Components
1. **Backend Service**: LLM integration service for note enhancement
2. **Frontend Button**: HTMX-powered enhancement button with loading state
3. **API Endpoint**: New Django view to handle enhancement requests
4. **Configuration**: LLM API key and settings management

## Benefits
- Reduces friction in practice logging
- Improves quality of practice records
- Provides coaching insights automatically
- Maintains user control over final content