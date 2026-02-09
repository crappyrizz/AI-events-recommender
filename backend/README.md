# AI Events Recommendation System

This project is an AI-powered event recommendation system that personalizes event suggestions based on user preferences and contextual factors.

## Features
- Personalized recommendations (budget, genre, distance, food)
- Temporal relevance (event timing)
- Weather-aware scoring (mocked context)
- Crowd-aware intelligence using user interactions
- Explainable recommendation scores
- REST API with Swagger documentation

## API Endpoints

### POST /recommendations
Returns ranked events based on user preferences and context.

### POST /interactions
Stores user interaction signals (e.g., interested in an event).

### GET /crowd/{event_id}
Estimates crowd level for an event based on interactions.

## Tech Stack
- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## Future Work
- Replace CSV event data with a database
- Integrate live weather APIs
- Personalize crowd tolerance per user
- Add frontend interface
- Apply machine learning for weight optimization
- integrate cabs function, like uber
- integrate tracking function
- Filter distance based on current location
- remove ridiculous suggestions
- recommendations not interdependent
- preferences should not allow any identifiers
- events to be stored in db