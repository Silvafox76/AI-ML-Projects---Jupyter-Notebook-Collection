
.items():
    # Read file as Pyspark DataFrame
    source_data_df = spark.read        .option("header", "true")        .option("delimiter", ";")        .option("lineSep", "\t")        .csv(f"s3://{data_lake_bucket}/landing_zone/rds/{table_name}")
    # Convert to Pandas DataFrame
    source_data_pd = source_data_df.toPandas()
    # Enforce schema
    source_data_pd = enforce_schema(source_data_pd, table_schema)
    logger.info(f"enforced schema done for {table_name}")
    # Add metadata
    target_pd, target_schema = add_metadata(source_data_pd, table_schema)
    logger.info(f"add metadata done for {table_name}")
    # Convert back to PySpark DataFrame with the schema
    target_data_df = spark.createDataFrame(target_pd, schema=target_schema)
    # Write data into silver location and glue catalog
    target_data_path = f"s3://{data_lake_bucket}/curated_zone/{table_name}"
    target_data = DynamicFrame.fromDF(target_data_df, glueContext, "target_data")
    sink = glueContext.getSink(connection_type="s3", path=target_data_path,
                               enableUpdateCatalog=True,
                               updateBehavior="UPDATE_IN_DATABASE",
                               partitionKeys=[],
                               compression="snappy")
    sink.setFormat("parquet", useGlueParquetWriter=True)
    sink.setCatalogInfo(catalogDatabase='curated_zone',
                        catalogTableName=table_name)
    sink.writeFrame(target_data)
    logger.info(f"write done for {table_name}")

job.commit()
