# Inferring Social Ties from Human Mobility Patterns
This repository contains code that was used in the thesis "Human mobility Patterns at Large-Scale Events".


![Alt text](/figures/pipeline.png?raw=true "Optional Title")

The figure above shows how the data pipeline that has been built to infer social ties.

*Basic flow of pipeline:* <br>
1. PostgreSQL database schema is built using bash scripts (see `pipeline/build-schema`)  
2. Data set is ingested into schema using `pg_dump`.  
3. Database schemas are setup using bash scripts (see `pipeline/build-indexes`)  
4. Features are computed using SQL stored procedures (see `pipeline/sql-pipeline`)  
5. Based on these features supervised learners are trained using Python and `sklearn` (see `pipeline/train-models`)  
6. Social graph is build using Python and `networkx` (see `pipeline/build-social-graph`)  
7. Community detection is applied using `infomap` (see `pipeline/graph-statistics`)  
8. Various graph statistics are applied using `networkx` (see `pipeline/graph-statistics`)  
 
Finally, we have throughout the process relied on smaller scripts to plot data and do smaller data tasks.

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