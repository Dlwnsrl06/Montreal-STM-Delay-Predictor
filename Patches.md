06-09-2026-2: **Discovered that the Montreal STM API uses an exception-based protocol that filters out minor schedule deviations, resulting in highly sparse, zero-heavy data. I pivoted the project from a regression model to a Binary Classification Anomaly Detector to predict major service disruptions, engineering features around weather and rush-hour bottlenecks.**  
  
06-09-2026-1: Collecting too many "no-delays" -> created condition to take only a little no-delays  
  
06-08-2026: Try not to run this after evening since there are only few buses running - and less accurate data for those midnight buses
