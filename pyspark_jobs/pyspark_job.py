from pyspark.sql import SparkSession

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--project_id")
args = parser.parse_args()
project_id = args.project_id

spark = SparkSession.builder.getOrCreate()

spark.conf.set("viewsEnabled", "true")
spark.conf.set("materializationDataset", "spotify")


transform_data_query1 = f"""
    SELECT count(*) as top_count, CONCAT(artist, ' - ', title) as song FROM `{project_id}.spotify.spotify_data`
    where region = "Global" and rank = 1 and chart = "top200" group by title, artist, url order by count(*) desc;
    """

transform_data_query2 = f"""
    SELECT count(*) as top_count, artist FROM `{project_id}.spotify.spotify_data`
    where region = "Global" and rank = 1 and chart = "top200" group by artist order by count(*) desc;
    """

transform_data_query3 = f"""
    SELECT 
        count(*) as top_count, 
        CONCAT(artist, ' - ', title) as song, 
        artist, 
        title, 
        region 
    FROM `{project_id}.spotify.spotify_data`
    where rank = 1 and chart = "top200" 
    group by title, artist, url, region 
    order by count(*) desc;
    """

transform_data_query4 = f"""
    SELECT count(*) as top_count, artist, region FROM `{project_id}.spotify.spotify_data`
    where rank = 1 and chart = "top200" group by artist, region order by count(*) desc;
    """

queries_tuple = (
  (f'{project_id}.spotify.spotify_transform_data1', transform_data_query1),
  (f'{project_id}.spotify.spotify_transform_data2', transform_data_query2),
  (f'{project_id}.spotify.spotify_transform_data3', transform_data_query3),
  (f'{project_id}.spotify.spotify_transform_data4', transform_data_query4),
)

for write_table, transform_data_query in queries_tuple:
    data = spark.read.format('bigquery').option('query', transform_data_query).load()
    data.write.format('bigquery') \
      .option('table', write_table) \
      .option('writeMethod', 'direct') \
      .mode("overwrite") \
      .save()
