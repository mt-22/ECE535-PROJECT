# ECE535-PROJECT
## VLM-based Smart Baby Monitoring

### *Motivation*

### *Design Goals / Deliverables*

### *System Blocks (tentative)*
<u>Input Acquisition</u>
The data pipeline that allows raw audio/visual data to be fed into the system via datasets, and/or sensors.

<u>Data Preprocessing</u>
Ensure all input data is normalized, and follows a specific format.

<u>Multi-Modal Language Model(s) & Activity Classification</u>
Feed the raw data into respective Multi-Model Language Models (Visual Language Model, Audio Language Model, etc). We could fine-tune each model to output a low-level list of features in a format that is easy to parse (JSON, YAML, etc).

- If multiple modalities are used, we will need to aggregate the results for our final classification. 

<u>Feature Aggregation & Summary Generation</u>
Use the list of features to generate a high level summary of the current state of the scene. This could be done by inserting the features into an engineered prompt provided to a reasoning model for final analysis.

- We could potentially instruct the model to provide both a high level summary of the scene, and a final classification of the state of the baby within the scene.

<u>Alerting / Reporting</u>
Based on the feature list and final classification of the scene, we can create a simple script that will send an alert if certain conditions are met (e.g. alert if the baby is coughing, choking, etc.)

### *Requirements*

### *Member Responsibilities*

### *Timeline*

### *References*




