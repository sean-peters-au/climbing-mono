## Climbers

- Climber CRUD
- Ticking
- Climber specific recordings and analysis

## Holds & Image Recognition

- bb-cv should probably be refactored out of flask into a pure lambda. We can trigger it via SQS, and the backend hit SQS to get the results.
- Hold highlighting should just be a border
- Improve Hold Management UI/UX
- Fine-tuning to improve model performance?

## Route Analytics

- Add AI summary
- Add recording comparison analysis

## Board Analytics

- Hold usage heatmap

## Routes

- Add delete

# Sensors

- Add mechanism to add a sensor to a hold

# Code

- Clean up CRUD
- Better error handling
- Tests
- Deployment

# Skeletal Frame

- Skeletal frame recognition
- Incorporate into recording analysis

# 3D View

- Model builder via backend and bb-cv
- Model viewer in frontend