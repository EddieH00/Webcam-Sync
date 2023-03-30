# Laboratory for Intelligent & Safe Automobiles- Alcohol Impaired Driving Study
This study attempts to use neural networks to detect if drivers are alcohol impaired using various camera placements
## Data capture and syncrhonization repository
These scripts capture data from the cameras and then syncrhonizes them as needed
## Files
- "capture_participants.py": Captures from 4 webcams and 1 thermal camera to get data to train a network to recognize gaze and hand placement in this order:
⋅⋅* hands on wheel, hands on lap, hands on an ipad, hands in the air, gaze straight, gaze left mirror, gaze right mirror, gaze rearview mirror, gaze left window, gaze right window, gaze ipad
- "capture_training_data.py":
- "sync.py":
- "video_creation_script.py":
