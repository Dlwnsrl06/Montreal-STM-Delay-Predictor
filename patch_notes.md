06-17-2026: Added route_id as a categorical feature, allowing the model to distinguish between bus routes and resolving sustained MAE drift
  
06-16-2026-2: Changed ML algorithm from Linear Regression to XGBoost because traffic congestion is not a linear function
  
06-16-2026: Previously fetched 10 days of weather on every single run, meaning training data was always a sliding window — the model kept forgetting old patterns. Now we only fetch what's missing and append it to a growing local CSV. First run grabs 30 days; every run after that just tops it up by a few hours.
  
06-10-2026-2: Completed building the ml-model, created piplines to automate the training, created logs to record the training process, built a Jupyter notbook to visualize results of this project 
  
06-10-2026: Further discovered that the API does not include a "delay" field, instead contains the actual arrival time. Since processing the scheduled time dataset along with calculating the delay will cost significant memory and storage, I have decided to shift the topic to **Predicting the travel time of STM transit based on the Montreal weather conditions**
  
06-09-2026-2: Discovered that the Montreal STM API uses an exception-based protocol that filters out minor schedule deviations, resulting in highly sparse, zero-heavy data. I pivoted the focus from a regression model to a **Binary Classification Anomaly Detector to predict major service disruptions, engineering features around weather and rush-hour bottlenecks**.
  
06-09-2026-1: Collecting too many "no-delays" -> created condition to take only a little no-delays  
  
06-08-2026: Try not to run this after evening since there are only few buses running - and less accurate data for those midnight buses

05-08-2026: Started the personal project to **Predict STM transit delays according to the Montreal weather conditions**
