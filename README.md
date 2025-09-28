# ECE535-PROJECT
## VLM-based Smart Baby Monitoring

### *Motivation*

### *Design Goals / Deliverables*

### *System Blocks (tentative)*
<ins>Input Acquisition</ins><br>
The data pipeline that allows raw audio/visual data to be fed into the system via datasets, and/or sensors.

<ins>Data Preprocessing</ins><br>
Ensure all input data is normalized, and follows a specific format.

<ins>Multi-Modal Language Model(s) & Activity Classification</ins><br>
Feed the raw data into respective Multi-Model Language Models (Visual Language Model, Audio Language Model, etc). We could fine-tune each model to output a low-level list of features in a format that is easy to parse (JSON, YAML, etc).

- If multiple modalities are used, we will need to aggregate the results for our final classification. 

<ins>Feature Aggregation & Summary Generation</ins><br>
Use the list of features to generate a high level summary of the current state of the scene. This could be done by inserting the features into an engineered prompt provided to a reasoning model for final analysis.

- We could potentially instruct the model to provide both a high level summary of the scene, and a final classification of the state of the baby within the scene.

<ins>Alerting / Reporting</ins><br>
Based on the feature list and final classification of the scene, we can create a simple script that will send an alert if certain conditions are met (e.g. alert if the baby is coughing, choking, etc).

### *Requirements*

### *Member Responsibilities*
<ins>Marshall Taylor</ins>
- Fine-Tuning Lead
- Configure and fine-tune the models such that they provide a formatted output.
- Curate the dataset required to teach the models their specific task.
- Test the accuracy and reliability of the feature extraction for all modalities.

<ins>Ivan Li</ins>
- Research / Writing Lead
- Refine the prompts for the final reasoning stage.
- Perform research on SoTA prompting and multi-modal feature aggregation teqniques.
- Manage project documentation.

<ins>Rivan Juthani</ins>
- Data Pipeline Lead
- Write the preprocessing scripts that format all incoming data.
- Implement the alerting script that provides notifications based on the systems final classification.

### *Timeline*

### *References*




