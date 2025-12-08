# LLM Notes Enhancement Setup

This feature allows users to enhance their practice session notes using AI-powered improvements.

## Configuration

### Environment Variables

Add the following to your `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### API Setup

1. Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
2. Add the API key to your environment variables
3. Restart the Django application

## Usage

Users can now click the "Enhance Notes" button on the practice session form to:
- Improve clarity and add proper golf terminology
- Add relevant coaching insights and observations
- Structure information for better readability
- Maintain original meaning and key observations

## Features

- **Smart Enhancement**: Uses practice type context for better suggestions
- **Error Handling**: Graceful fallback when API is unavailable
- **Loading States**: Visual feedback during enhancement
- **Validation**: Ensures notes are not empty before enhancement
- **Retry Logic**: Automatic retries with exponential backoff

## Testing

The feature includes comprehensive tests:
- Unit tests for the enhancement service
- Integration tests for the API endpoint
- Mocked API responses for reliable testing

Run tests with:
```bash
rye run pytest src/birdie_buddy/practice/
```