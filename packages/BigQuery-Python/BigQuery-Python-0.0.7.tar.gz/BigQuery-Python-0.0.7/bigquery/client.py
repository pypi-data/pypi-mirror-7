import calendar
from collections import defaultdict
from datetime import datetime
from time import sleep, time
from hashlib import sha256
import json

from apiclient.discovery import build
from apiclient.errors import HttpError
import httplib2

from bigquery import logger
from bigquery.errors import UnfinishedQueryException
from bigquery.schema_builder import schema_from_record


BIGQUERY_SCOPE = 'https://www.googleapis.com/auth/bigquery'
BIGQUERY_SCOPE_READ_ONLY = 'https://www.googleapis.com/auth/bigquery.readonly'

JOB_CREATE_IF_NEEDED = 'CREATE_IF_NEEDED'
JOB_CREATE_NEVER = 'CREATE_NEVER'
JOB_SOURCE_FORMAT_NEWLINE_DELIMITED_JSON = 'NEWLINE_DELIMITED_JSON'
JOB_SOURCE_FORMAT_DATASTORE_BACKUP = 'DATASTORE_BACKUP'
JOB_SOURCE_FORMAT_CSV = 'CSV'
JOB_WRITE_TRUNCATE = 'WRITE_TRUNCATE'
JOB_WRITE_APPEND = 'WRITE_APPEND'
JOB_WRITE_EMPTY = 'WRITE_EMPTY'
JOB_ENCODING_UTF_8 = 'UTF-8'
JOB_ENCODING_ISO_8859_1 = 'ISO-8859-1'


def get_client(project_id, credentials=None, service_account=None,
               private_key=None, readonly=True):
    """Return a singleton instance of BigQueryClient. Either
    AssertionCredentials or a service account and private key combination need
    to be provided in order to authenticate requests to BigQuery.

    Args:
        project_id: the BigQuery project id.
        credentials: an AssertionCredentials instance to authenticate requests
                     to BigQuery.
        service_account: the Google API service account name.
        private_key: the private key associated with the service account in
                     PKCS12 or PEM format.
        readonly: bool indicating if BigQuery access is read-only. Has no
                  effect if credentials are provided.

    Returns:
        an instance of BigQueryClient.
    """

    if not credentials and not (service_account and private_key):
        raise Exception('AssertionCredentials or service account and private'
                        'key need to be provided')

    bq_service = _get_bq_service(credentials=credentials,
                                 service_account=service_account,
                                 private_key=private_key,
                                 readonly=readonly)

    return BigQueryClient(bq_service, project_id)


def _get_bq_service(credentials=None, service_account=None, private_key=None,
                    readonly=True):
    """Construct an authorized BigQuery service object."""

    assert credentials or (service_account and private_key)

    if not credentials:
        scope = BIGQUERY_SCOPE_READ_ONLY if readonly else BIGQUERY_SCOPE
        credentials = _credentials()(service_account, private_key, scope=scope)

    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build('bigquery', 'v2', http=http)

    return service


def _credentials():
    """Import and return SignedJwtAssertionCredentials class"""
    from oauth2client.client import SignedJwtAssertionCredentials

    return SignedJwtAssertionCredentials


class BigQueryClient(object):
    def __init__(self, bq_service, project_id):
        self.bigquery = bq_service
        self.project_id = project_id

    def query(self, query, max_results=None, timeout=10, dry_run=False):
        """Submit a query to BigQuery.

        Args:
            query: BigQuery query string.
            max_results: maximum number of rows to return per page of results.
            timeout: how long to wait for the query to complete, in seconds,
                     before the request times out and returns.
            dry_run: if True, the query isn't actually run. A valid query will
                     return an empty response, while an invalid one will return
                     the same error message it would if it wasn't a dry run.

        Returns:
            job id and query results if query completed. If dry_run is True,
            job id will be None and results will be empty if the query is valid
            or a dict containing the response if invalid.
        """

        logger.debug('Executing query: %s' % query)

        job_collection = self.bigquery.jobs()
        query_data = {
            'query': query,
            'timeoutMs': timeout * 1000,
            'dryRun': dry_run,
            'maxResults': max_results,
        }

        try:
            query_reply = job_collection.query(
                projectId=self.project_id, body=query_data).execute()
        except HttpError, e:
            if dry_run:
                return None, json.loads(e.content)
            raise

        job_id = query_reply['jobReference'].get('jobId')
        schema = query_reply.get('schema', {'fields': None})['fields']
        rows = query_reply.get('rows', [])

        return job_id, [self._transform_row(row, schema) for row in rows]

    def get_query_schema(self, job_id):
        """Retrieve the schema of a query by job id.

        Args:
            job_id: The job_id that references a BigQuery query.
        Returns:
            A list of dictionaries that represent the schema.
        """

        job_collection = self.bigquery.jobs()
        query_reply = self._get_query_results(
            job_collection, self.project_id, job_id, offset=0, limit=0)

        if not query_reply['jobComplete']:
            logger.warning('BigQuery job %s not complete' % job_id)
            raise UnfinishedQueryException()

        return query_reply['schema']['fields']

    def get_table_schema(self, dataset, table):
        """Return the table schema.

        Args:
            dataset: the dataset containing the table.
            table: the table to get the schema for.

        Returns:
            A list of dicts that represent the table schema. If the table
            doesn't exist, None is returned.
        """

        try:
            result = self.bigquery.tables().get(
                projectId=self.project_id,
                tableId=table,
                datasetId=dataset).execute()
        except HttpError, e:
            if int(e.resp['status']) == 404:
                logger.warn('Table %s.%s does not exist', dataset, table)
                return None
            raise

        return result['schema']['fields']

    def check_job(self, job_id):
        """Return the state and number of results of a query by job id.

        Args:
            job_id: The job id of the query to check.

        Returns:
            Whether or not the query has completed and the total number of rows
            included in the query table if it has completed.
        """

        job_collection = self.bigquery.jobs()
        query_reply = self._get_query_results(
            job_collection, self.project_id, job_id, offset=0, limit=0)

        return (query_reply.get('jobComplete', False),
                query_reply.get('totalRows', 0))

    def get_query_rows(self, job_id, offset=None, limit=None):
        """Retrieve a list of rows from a query table by job id.

        Args:
            job_id: The job id that references a BigQuery query.
            offset: The offset of the rows to pull from BigQuery.
            limit: The number of rows to retrieve from a query table.

        Returns:
            A list of dictionaries that represent table rows.
        """

        job_collection = self.bigquery.jobs()
        query_reply = self._get_query_results(
            job_collection, self.project_id, job_id, offset=offset,
            limit=limit)

        if not query_reply['jobComplete']:
            logger.warning('BigQuery job %s not complete' % job_id)
            raise UnfinishedQueryException()

        schema = query_reply['schema']['fields']
        rows = query_reply.get('rows', [])

        return [self._transform_row(row, schema) for row in rows]

    def check_table(self, dataset, table):
        """Check to see if a table exists.

        Args:
            dataset: the dataset to check.
            table: the name of the table.

        Returns:
            bool indicating if the table exists.
    """

        try:
            self.bigquery.tables().get(
                projectId=self.project_id, datasetId=dataset,
                tableId=table).execute()
            return True

        except:
            return False

    def create_table(self, dataset, table, schema):
        """Create a new table in the dataset.

        Args:
            dataset: the dataset to create the table in.
            table: the name of table to create.
            schema: table schema dict.

        Returns:
            bool indicating if the table was successfully created or not.
        """

        body = {
            'schema': {'fields': schema},
            'tableReference': {
                'tableId': table,
                'projectId': self.project_id,
                'datasetId': dataset
            }
        }

        try:
            self.bigquery.tables().insert(
                projectId=self.project_id,
                datasetId=dataset,
                body=body
            ).execute()
            return True

        except:
            logger.error('Cannot create table %s.%s' % (dataset, table))
            return False

    def delete_table(self, dataset, table):
        """Delete a table from the dataset.

        Args:
            dataset: the dataset to delete the table from.
            table: the name of the table to delete.

        Returns:
            bool indicating if the table was successfully deleted or not.
        """

        try:
            self.bigquery.tables().delete(
                projectId=self.project_id,
                datasetId=dataset,
                tableId=table
            ).execute()
            return True

        except:
            logger.error('Cannot delete table %s.%s' % (dataset, table))
            return False

    def get_tables(self, dataset_id, app_id, start_time, end_time):
        """Retrieve a list of tables that are related to the given app id
        and are inside the range of start and end times.

        Args:
            dataset_id: The BigQuery dataset id to consider.
            app_id: The appspot name
            start_time: The datetime or unix time after which records will be
                        fetched.
            end_time: The datetime or unix time up to which records will be
                      fetched.

        Returns:
            A list of table names.
        """

        if isinstance(start_time, datetime):
            start_time = calendar.timegm(start_time.utctimetuple())

        if isinstance(end_time, datetime):
            end_time = calendar.timegm(end_time.utctimetuple())

        every_table = self._get_all_tables(dataset_id)
        app_tables = every_table.get(app_id, {})

        return self._filter_tables_by_time(app_tables, start_time, end_time)

    def import_data_from_uris(
            self,
            source_uris,
            dataset,
            table,
            schema=None,
            job=None,
            source_format=None,
            create_disposition=None,
            write_disposition=None,
            encoding=None,
            ignore_unknown_values=None,
            max_bad_records=None,
            allow_jagged_rows=None,
            allow_quoted_newlines=None,
            field_delimiter=None,
            quote=None,
            skip_leading_rows=None,
    ):
        """
        Imports data into a BigQuery table from cloud storage.
        Args:
            source_uris: required string or list of strings representing
                            the uris on cloud storage of the form:
                             gs://bucket/filename
            dataset: required string id of the dataset
            table: required string id of the table
            job: optional string identifying the job (a unique jobid
                    is automatically generated if not provided)
            schema: optional list representing the bigquery schema
            source_format: optional string
                    (one of the JOB_SOURCE_FORMAT_* constants)
            create_disposition: optional string
                    (one of the JOB_CREATE_* constants)
            write_disposition: optional string
                    (one of the JOB_WRITE_* constants)
            encoding: optional string default
                    (one of the JOB_ENCODING_* constants)
            ignore_unknown_values: optional boolean
            max_bad_records: optional boolean
            allow_jagged_rows: optional boolean for csv only
            allow_quoted_newlines: optional boolean for csv only
            field_delimiter: optional string for csv only
            quote: optional string the quote character for csv only
            skip_leading_rows: optional int for csv only

            Optional arguments with value None are determined by
            BigQuery as described:
            https://developers.google.com/bigquery/docs/reference/v2/jobs

        Returns:
            dict, a BigQuery job resource or None on failure
        """
        source_uris = source_uris if isinstance(source_uris, list) \
            else [source_uris]

        configuration = {
            "destinationTable": {
                "projectId": self.project_id,
                "tableId": table,
                "datasetId": dataset
            },
            "sourceUris": source_uris,
        }

        if max_bad_records:
            configuration['maxBadRecords'] = max_bad_records

        if ignore_unknown_values:
            configuration['ignoreUnknownValues'] = ignore_unknown_values

        if create_disposition:
            configuration['createDisposition'] = create_disposition

        if write_disposition:
            configuration['writeDisposition'] = write_disposition

        if encoding:
            configuration['encoding'] = encoding

        if schema:
            configuration['schema'] = schema

        if source_format:
            configuration['sourceFormat'] = source_format

        if not job:
            hex = sha256(":".join(source_uris) + str(time())).hexdigest()
            job = "{dataset}-{table}-{digest}".format(
                dataset=dataset,
                table=table,
                digest=hex
            )

        if source_format == JOB_SOURCE_FORMAT_CSV:
            if field_delimiter:
                configuration['fieldDelimiter'] = field_delimiter

            if allow_jagged_rows:
                configuration['allowJaggedRows'] = allow_jagged_rows

            if allow_quoted_newlines:
                configuration['allowQuotedNewlines'] = allow_quoted_newlines

            if quote:
                configuration['quote'] = quote

            if skip_leading_rows:
                configuration['skipLeadingRows'] = skip_leading_rows

        elif field_delimiter or allow_jagged_rows \
                or allow_quoted_newlines or quote or skip_leading_rows:
            all_values = dict(field_delimiter=field_delimiter,
                              allow_jagged_rows=allow_jagged_rows,
                              allow_quoted_newlines=allow_quoted_newlines,
                              skip_leading_rows=skip_leading_rows,
                              quote=quote)
            non_null_values = dict((k, v) for k, v
                                   in all_values.items()
                                   if v)
            raise Exception("Parameters field_delimiter, allow_jagged_rows, "
                            "allow_quoted_newlines, quote and "
                            "skip_leading_rows are only allowed when "
                            "source_format=JOB_SOURCE_FORMAT_CSV: %s"
                            % non_null_values)

        body = {
            "configuration": {
                'load': configuration
            },
            "jobReference": {
                "projectId": self.project_id,
                "jobId": job
            }
        }

        try:
            logger.info("Creating load job %s" % body)
            job_resource = self.bigquery.jobs() \
                .insert(projectId=self.project_id, body=body) \
                .execute()
            return job_resource
        except Exception, e:
            logger.error("Failed while starting uri import job: {0}"
                         .format(e))
            return None

    def wait_for_job(self, job, interval=5, timeout=None):
        """
        Waits until the job indicated by job_resource is done or has failed
        Args:
            job: dict, representing a BigQuery job resource or jobId
            interval: optional float polling interval in seconds, default = 5
            timeout: optional float timeout in seconds, default = None
        Returns:
            dict, final state of the job_resource, as described here:
            https://developers.google.com/resources/api-libraries/documentation/bigquery/v2/python/latest/bigquery_v2.jobs.html#get
        Raises:
            standard exceptions on http / auth failures (you must retry)
        """
        if isinstance(job, dict):  # job is a job resource
            complete = job.get('jobComplete')
            job_id = job['jobReference']['jobId']
        else:  # job is the jobId
            complete = False
            job_id = job
            job_resource = None

        start_time = time()
        elapsed_time = 0
        while not (complete
                   or (timeout is not None and elapsed_time > timeout)):
            sleep(interval)
            request = self.bigquery.jobs().get(projectId=self.project_id,
                                               jobId=job_id)
            job_resource = request.execute()
            error = job_resource.get('error')
            if error:
                raise Exception("{message} ({code}). Errors: {errors}",
                                **error)
            complete = job_resource.get('status').get('state') == u'DONE'
            elapsed_time = time() - start_time

        return job_resource

    def push_rows(self, dataset, table, rows, insert_id_key=None):
        """Upload rows to BigQuery table.

        Args:
            dataset: the dataset to upload to.
            table: the name of the table to insert rows into.
            rows: list of rows to add to table
            insert_id_key: key for insertId in row

        Returns:
            bool indicating if insert succeeded or not.
        """

        table_data = self.bigquery.tabledata()

        rows_data = []
        for row in rows:
            each_row = {}
            each_row["json"] = row
            if insert_id_key in row:
                each_row["insertId"] = row[insert_id_key]
            rows_data.append(each_row)

        data = {
            "kind": "bigquery#tableDataInsertAllRequest",
            "rows": rows_data
        }

        try:
            response = table_data.insertAll(
                projectId=self.project_id,
                datasetId=dataset,
                tableId=table,
                body=data
            ).execute()

            if response.get('insertErrors'):
                logger.error('BigQuery insert errors: %s' % response)
                return False

            return True

        except:
            logger.error('Problem with BigQuery insertAll')
            return False

    def _get_all_tables(self, dataset_id):
        """Retrieve a list of all tables for the dataset.

        Args:
            dataset_id: the dataset to retrieve table names for.

        Returns:
            a dictionary of app ids mapped to their table names.
        """

        result = self.bigquery.tables().list(
            projectId=self.project_id,
            datasetId=dataset_id).execute()

        return self._parse_table_list_response(result)

    def _parse_table_list_response(self, list_response):
        """Parse the response received from calling list on tables.

        Args:
            list_response: The response found by calling list on a BigQuery
                           table object.

        Returns:
            The dictionary of dates referenced by table names.
        """

        tables = defaultdict(dict)

        for table in list_response.get('tables', []):
            table_ref = table.get('tableReference')

            if not table_ref:
                continue

            table_id = table_ref.get('tableId', '')

            year_month, app_id = self._parse_table_name(table_id)

            if not year_month:
                continue

            table_date = datetime.strptime(year_month, '%Y-%m')
            unix_seconds = calendar.timegm(table_date.timetuple())
            tables[app_id].update({table_id: unix_seconds})

        # Turn off defualting
        tables.default_factory = None

        return tables

    def _parse_table_name(self, table_id):
        """Parse a table name in the form of appid_YYYY_MM or
        YYYY_MM_appid and return a tuple consisting of YYYY-MM and the app id.

        Args:
            table_id: The table id as listed by BigQuery.

        Returns:
            Tuple containing year/month and app id. Returns None, None if the
            table id cannot be parsed.
        """

        # Prefix date
        attributes = table_id.split('_')
        year_month = "-".join(attributes[:2])
        app_id = "-".join(attributes[2:])

        # Check if date parsed correctly
        if year_month.count("-") == 1 and all(
                [num.isdigit() for num in year_month.split('-')]):
            return year_month, app_id

        # Postfix date
        attributes = table_id.split('_')
        year_month = "-".join(attributes[-2:])
        app_id = "-".join(attributes[:-2])

        # Check if date parsed correctly
        if year_month.count("-") == 1 and all(
                [num.isdigit() for num in year_month.split('-')]):
            return year_month, app_id

        return None, None

    def _filter_tables_by_time(self, tables, start_time, end_time):
        """Filter a table dictionary and return table names based on the range
        of start and end times in unix seconds.

        Args:
            tables: The dictionary of dates referenced by table names
            start_time: The unix time after which records will be fetched.
            end_time: The unix time up to which records will be fetched.

        Returns:
            A list of table names that are inside the time range.
        """

        return [table_name for (table_name, unix_seconds) in tables.iteritems()
                if self._in_range(start_time, end_time, unix_seconds)]

    def _in_range(self, start_time, end_time, time):
        """Indicate if the given time falls inside of the given range.

        Args:
            start_time: The unix time for the start of the range.
            end_time: The unix time for the end of the range.
            time: The unix time to check.

        Returns:
            True if the time falls within the range, False otherwise.
        """

        ONE_MONTH = 2764800  # 32 days

        return start_time <= time <= end_time or \
               time <= start_time <= time + ONE_MONTH or \
               time <= end_time <= time + ONE_MONTH

    def _get_query_results(self, job_collection, project_id, job_id,
                           offset=None, limit=None):
        """Execute the query job indicated by the given job id.

        Args:
            job_collection: The collection the job belongs to.
            project_id: The project id of the table.
            job_id: The job id of the query to check.
            offset: The index the result set should start at.
            limit: The maximum number of results to retrieve.

        Returns:
            The query reply.
        """

        return job_collection.getQueryResults(
            projectId=project_id,
            jobId=job_id,
            startIndex=offset,
            maxResults=limit,
            timeoutMs=0).execute()

    def _transform_row(self, row, schema):
        """Apply the given schema to the given BigQuery data row.

        Args:
            row: A single BigQuery row to transform.
            schema: The BigQuery table schema to apply to the row, specifically
                    the list of field dicts.

        Returns:
            Dict containing keys that match the schema and values that match
            the row.
        """

        log = {}

        # Match each schema column with its associated row value
        for index, col_dict in enumerate(schema):
            col_name = col_dict['name']
            row_value = row['f'][index]['v']

            if row_value is None:
                log[col_name] = None
                continue

            # Recurse on nested records
            if col_dict['type'] == 'RECORD':
                row_value = self._recurse_on_row(col_dict, row_value)

            # Otherwise just cast the value
            elif col_dict['type'] == 'INTEGER':
                row_value = int(row_value)

            elif col_dict['type'] == 'FLOAT':
                row_value = float(row_value)

            elif col_dict['type'] == 'BOOLEAN':
                row_value = row_value in ('True', 'true', 'TRUE')

            log[col_name] = row_value

        return log

    def _recurse_on_row(self, col_dict, nested_value):
        """Apply the schema specified by the given dict to the nested value by
        recursing on it.

        Args:
            col_dict: A dict containing the schema to apply to the nested
                      value.
            nested_value: A value nested in a BigQuery row.
        Returns:
            Dict or list of dicts from applied schema.
        """

        row_value = None

        # Multiple nested records
        if col_dict['mode'] == 'REPEATED' and isinstance(nested_value, list):
            row_value = [self._transform_row(record['v'], col_dict['fields'])
                         for record in nested_value]

        # A single nested record
        else:
            row_value = self._transform_row(nested_value, col_dict['fields'])

        return row_value

    #
    # DataSet manipulation methods
    #

    def create_dataset(self, dataset_id, friendly_name=None, description=None,
                       access=None):
        """Create a new BigQuery dataset.

        Args:
            dataset_id: required unique string identifying the dataset with the
                        project (the referenceId of the dataset, not the
                        integer id of the dataset)
            friendly_name: optional string providing a human readable name
            description: optional longer string providing a description
            access: optional object indicating access permissions (see
                    https://developers.google.com/bigquery/docs/reference/v2/
                    datasets#resource)

        Returns:
            bool indicating if dataset was created or not
        """
        try:
            datasets = self.bigquery.datasets()
            dataset_data = self.dataset_resource(dataset_id,
                                                 friendly_name=friendly_name,
                                                 description=description,
                                                 access=access)

            datasets.insert(projectId=self.project_id,
                            body=dataset_data).execute()
            return True
        except Exception, e:
            logger.error('Cannot create dataset %s, %s' % (dataset_id, e))
            return False

    def get_datasets(self):
        """List all datasets in the project.

        Returns:
            a list of dataset resources
        """
        try:
            datasets = self.bigquery.datasets()
            request = datasets.list(projectId=self.project_id)
            result = request.execute()
            return result
        except Exception, e:
            logger.error("Cannot list datasets: %s" % e)
            return None

    def delete_dataset(self, dataset_id):
        """Delete a BigQuery dataset.

        Args:
            dataset_id: required unique string identifying the dataset with the
                        project (the referenceId of the dataset)
        Returns:
            bool indicating if the delete was successful or not

        Raises:
            HttpError 404 when dataset with dataset_id does not exist
        """
        try:
            datasets = self.bigquery.datasets()
            request = datasets.delete(projectId=self.project_id,
                                      datasetId=dataset_id)
            request.execute()
            return True
        except Exception, e:
            logger.error('Cannot delete dataset %s: %s' % (dataset_id, e))
            return None

    def update_dataset(self, dataset_id, friendly_name=None, description=None,
                       access=None):
        """Updates information in an existing dataset. The update method
        replaces the entire dataset resource, whereas the patch method only
        replaces fields that are provided in the submitted dataset resource.

        Args:
            dataset_id: required unique string identifying the dataset with the
                        project (the referenceId of the dataset).
            friendly_name: an optional descriptive name for the dataset.
            description: an optional description of the dataset.
            access: an optional object indicating access permissions.

        Returns:
            bool indicating if the update was successful or not.
        """
        try:
            datasets = self.bigquery.datasets()
            body = self.dataset_resource(dataset_id, friendly_name,
                                         description, access)
            request = datasets.update(projectId=self.project_id,
                                      datasetId=dataset_id,
                                      body=body)
            request.execute()
            return True
        except Exception, e:
            logger.error('Cannot update dataset %s: %s' % (dataset_id, e))
            return False

    def patch_dataset(self, dataset_id, friendly_name=None, description=None,
                      access=None):
        """Updates information in an existing dataset. The update method
        replaces the entire dataset resource, whereas the patch method only
        replaces fields that are provided in the submitted dataset resource.

        Args:
            dataset_id: required unique string identifying the dataset with the
                        projedct (the referenceId of the dataset).
            friendly_name: an optional descriptive name for the dataset.
            description: an optional description of the dataset.
            access: an optional object indicating access permissions.
        Returns:
            bool indicating if the patch was successful or not.
        """
        try:
            datasets = self.bigquery.datasets()
            body = self.dataset_resource(dataset_id, friendly_name,
                                         description, access)
            request = datasets.patch(projectId=self.project_id,
                                     datasetId=dataset_id, body=body)
            request.execute()
            return True
        except Exception, e:
            logger.error('Cannot patch dataset %s: %s' % (dataset_id, e))
            return False

    def dataset_resource(self, ref_id, friendly_name=None, description=None,
                         access=None):
        """See https://developers.google.com/bigquery/docs/reference/v2/
        datasets#resource

        Args:
            ref_id: string dataset id (the reference id, not the integer id)
            friendly_name: opt string
            description: opt string
            access: opt list

        Returns:
            a dictionary representing a BigQuery dataset resource
        """
        data = {
            "datasetReference": {
                "datasetId": ref_id,
                "projectId": self.project_id
            }
        }
        if friendly_name:
            data["friendlyName"] = friendly_name
        if description:
            data["description"] = description
        if access:
            data["access"] = access

        return data

    @classmethod
    def schema_from_record(cls, record):
        """Given a dict representing a record instance to be inserted into
        BigQuery, calculate the schema.

         Args:
            record: dict representing a record to be inserted into big query,
                    where all keys are strings (representing column names in
                    the record) and all values are of type int, str, unicode,
                    float,bool, timestamp or dict. A dict value represents a
                    record, and must conform to the same restrictions as record

        Returns:
            a list representing a BigQuery schema

        Note: results are undefined if a different value types are provided for
              a repeated field: E.g.
              { rfield: [ { x: 1}, {x: "a string"} ] } # undefined!
        """
        return schema_from_record(record)
