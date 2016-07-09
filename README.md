# Inferring Social Ties from Human Mobility Patterns
This repository contains code that was used in the thesis "Human mobility Patterns at Large-Scale Events".


![Alt text](/figures/pipeline.png?raw=true "Optional Title")

Folder structure:

```
.
|-- figures
|   `-- pipeline.png
|-- misc-scripts
|-- pipeline
|   |-- build-indexes
|   |   `-- setup-indexes.sql
|   |-- build-schema
|   |   `-- setup-db.sh
|   |-- build-social-graph
|   |   `-- build_social_graph.py
|   |-- graph-statistics
|   |   |-- build_graph_statistics.py
|   |   |-- build_infomap_from_pajek_file.py
|   |   |-- build_infomap_to_pajek_file.py
|   |   `-- build_temporal_graph.py
|   |-- sql-pipeline
|   |   |-- compute-co-occurrences.sql
|   |   |-- compute-consecutive-grids.sql
|   |   |-- compute-diversity-in-co-occurrences.sql
|   |   |-- compute-location-entropy.sql
|   |   |-- compute-max-time-together.sql
|   |   |-- compute-same-camp-score.sql
|   |   `-- compute-same-genre-score.sql
|   `-- train-models
|       `-- build_dbscan_clusters.py
`-- README.md
```