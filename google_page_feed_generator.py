import boto3
import csv
import feedparser
import json
import os
import ssl
import tempfile
from urllib.request import urlopen

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def handler(event, context):
    feed_obj = __parse_xml_feed()
    url_list = __generate_url_list(feed_obj)
    s3_file_object = __upload_url_list_as_csv_to_s3(url_list)

    return {
            "statusCode": 200,
            "body": json.dumps(s3_file_object)
            }

def __generate_url_list(feed_obj):
    url_list = []

    for entry in feed_obj["entries"]:
        link = entry["link"]
        if link:
            url_list.append(link)
        else:
            continue

    return url_list

def __parse_xml_feed():
    feed_url = os.environ["WORDPRESS_FEED_URL"]
    request = urlopen(feed_url)
    xml = request.read()

    return feedparser.parse(xml)

def __upload_csv_file_to_s3(csv_file_filepath):
    client = boto3.client(
            "s3",
            aws_access_key_id=os.environ["S3_UPLOAD_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["S3_UPLOAD_AWS_SECRET_ACCESS_KEY"]
            )
    s3_file_object = client.put_object(
            ACL="public-read",
            Bucket=os.environ["S3_UPLOAD_BUCKET"],
            Body=open(csv_file_filepath, "r").read(),
            Key=os.environ["FILE_NAME"]
            )

    return s3_file_object

def __upload_url_list_as_csv_to_s3(url_list = []):
    tf = tempfile.NamedTemporaryFile(delete=False)

    try:
        with open(tf.name, "w") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Page URL"])
            for url in url_list:
                writer.writerow([url])
        csv_file.close()

        return __upload_csv_file_to_s3(tf.name)
    finally:
        os.remove(tf.name)
