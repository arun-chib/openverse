_<TODO: This documentation is temporary and should be replaced by more thorough
documentation of our DB fields in
https://github.com/WordPress/openverse-catalog/issues/783>_

# Data Models

The following is temporary, limited documentation of the columns for each of our
Catalog data models.

## Required Fields

| field name            | description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| _foreign_identifier_  | Unique identifier for the record on the source site.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| _foreign_landing_url_ | URL of page where the record lives on the source website.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| _url_                 | Direct link to the media file.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| _license_info_        | [LicenseInfo object](https://github.com/WordPress/openverse-catalog/blob/8423590fd86a0a3272ca91bc11f2f37979048181/openverse_catalog/dags/common/licenses/licenses.py#L25) that has (1) the URL of the license for the record, (2) string representation of the license, (3) version of the license, (4) raw license URL that was by provider, if different from canonical URL. Usually generated by calling [`get_license_info`](https://github.com/WordPress/openverse-catalog/blob/8423590fd86a0a3272ca91bc11f2f37979048181/openverse_catalog/dags/common/licenses/licenses.py#L29) on respective fields returns/available from the API. |

## Optional Fields

The following fields are optional, but it is highly encouraged to populate as
much data as possible:

| field name      | description                                                                                   |
| --------------- | --------------------------------------------------------------------------------------------- |
| _thumbnail_url_ | Direct link to a thumbnail-sized version of the record.                                       |
| _filesize_      | Size of the main file in bytes.                                                               |
| _filetype_      | The filetype of the main file, eg. 'mp3', 'jpg', etc.                                         |
| _creator_       | The creator of the image.                                                                     |
| _creator_url_   | The user page, or home page of the creator.                                                   |
| _title_         | Title of the record.                                                                          |
| _meta_data_     | Dictionary of metadata about the record. Currently, a key we prefer to have is `description`. |
| _raw_tags_      | List of tags associated with the record.                                                      |
| _watermarked_   | Boolean, true if the record has a watermark.                                                  |

#### Image-specific fields

Image also has the following fields:

| field_name | description             |
| ---------- | ----------------------- |
| _width_    | Image width in pixels.  |
| _height_   | Image height in pixels. |

#### Audio-specific fields

Audio has the following fields:

| field_name       | description                                                                                                                                                                         |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| _duration_       | Audio duration in milliseconds.                                                                                                                                                     |
| _bit_rate_       | Audio bit rate as int.                                                                                                                                                              |
| _sample_rate_    | Audio sample rate as int.                                                                                                                                                           |
| _category_       | Category such as 'music', 'sound', 'audio_book', or 'podcast'.                                                                                                                      |
| _genres_         | List of genres.                                                                                                                                                                     |
| _set_foreign_id_ | Unique identifier for the audio set on the source site.                                                                                                                             |
| _audio_set_      | The name of the set (album, pack, etc) the audio is part of.                                                                                                                        |
| _set_position_   | Position of the audio in the audio_set.                                                                                                                                             |
| _set_thumbnail_  | URL of the audio_set thumbnail.                                                                                                                                                     |
| _set_url_        | URL of the audio_set.                                                                                                                                                               |
| _alt_files_      | A dictionary with information about alternative files for the audio (different formats/quality). Dict should have the following keys: _url_, _filesize_, _bit_rate_, _sample_rate_. |
