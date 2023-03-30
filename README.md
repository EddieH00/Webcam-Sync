# Laboratory for Intelligent & Safe Automobiles- Alcohol Impaired Driving Study
This study attempts to use neural networks to detect if drivers are alcohol impaired using various camera placements
## Data capture and syncrhonization repository
These scripts capture data from the cameras and then syncrhonizes them as needed
## Files
- "capture_participants.py": Captures from 4 webcams and 1 thermal camera to get data to train a network to recognize gaze and hand placement in specified order
  -  order: hands on wheel, hands on lap, hands on an ipad, hands in the air, gaze straight, gaze left mirror, gaze right mirror, gaze rearview mirror, gaze left window, gaze right window, gaze ipad

- "capture_training_data.py": captures from 4 webcams, thermal camera in microphone for participants driving the simulator both sober and impaired
  - order: capture entering vehicle, audio only capture, driving session

- "sync.py": Script that takes the data and synchronizes the frames together
- 
- "video_creation_script.py": Script takes the synchronized data, and additional simulator footage, and creates a video that displays all cameras and a custom text overlay
