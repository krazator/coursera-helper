[![Latest version on PyPI](https://img.shields.io/pypi/v/coursera-helper.svg)](https://pypi.org/project/coursera-helper/)

# coursera-helper

`coursera-helper` is forked from [coursera-dl](https://github.com/coursera-dl/coursera-dl), which is no longer maintained.

<!-- TOC -->

  * [Introduction](#introduction)
  * [Installation instructions](#installation-instructions)
    + [Installation (recommended)](#installation-recommended)
    + [Manual Installation](#manual-installation)
    + [Docker container](#docker-container)
  * [Before the start](#before-the-start)
  * [Quick Start](#quick-start)
    + [List courses](#list-courses)
    + [Download course](#download-course)
    + [More download options](#more-download-options)
    + [Use configuration file](#use-configuration-file)
  * [Troubleshooting](#troubleshooting)
    + [china-issues](#china-issues)
  * [Reporting issues](#reporting-issues)
  * [Disclaimer](#disclaimer)

  <!-- /TOC -->

## Introduction

`coursera-helper` is a tool for downloading Coursera.org videos and naming them.

It is platform independent, and should work fine under Unix (Linux, BSDs etc.), Windows, or macOS.

## Installation instructions

`coursera-helper` requires Python 3 and very few other dependencies. (As of October 2023, `coursera-helper` passed tests on Python versions 3.8, 3.9, 3.10, and 3.11.)

### Installation (recommended)

Open a terminal and run:

    pip install coursera-helper

### Manual Installation

    pip install git+https://github.com/krazator/coursera-helper.git

### Docker container

You can run this application via [Docker](https://docker.com). Install Docker and run:

```
docker run --rm -it -v \
    "$(pwd):/courses" \
     krazator/coursera-helper --cauth <CAUTH-value> <course name>
```

* If the image is not found locally, Docker will download it automatically.
* **Please note:** when running in Docker mode, only the `--cauth` parameter can be used for authentication. Username/password and `--browser-cookie` authentication are not supported.
* The course files will be downloaded to your current directory.

## Before the start

`coursera-helper` supports four authentication methods:

1. **CAUTH (recommended)**

   Just use the `--cauth CAUTH-value-from-browser` option when running the program.

   [How to get the cauth value?](#CAUTH)

2. Browser cookies

   Just use the `--browser-cookie` option when running the program.

   Automatically extract the CAUTH value from the browser cookie. If this method fails, use one of the other authentication methods.

3. Username and Password

   Just use the `-u <user> -p <pass>` options when running the program.

   Please note that this method will open the browser, and you may have to complete a reCAPTCHA challenge.

4. netrc File

   Just use the `--netrc` option when running the program.

## Quick Start

Run the following command to view usage and options:

```
coursera-helper --help
```

### List courses

Run the following command to list the courses in which you are enrolled:

```
coursera-helper --cauth <CAUTH> --list-courses
```

or

```
coursera-helper --browser-cookie --list-courses
```

or

    coursera-helper -u <email or username> --list-courses

### Download course

Choose the course you are interested in, copy its course name, and use it in the following command:

    coursera-helper -u <email or username> <COURSE NAME>

Your downloaded videos will be placed in the current directory, but you can choose another destination with the `--path` argument.

### More download options

General download:

```
coursera-helper --cauth <CAUTH> <COURSE NAME>
```

Specify download location:

```
coursera-helper --cauth <CAUTH> --path <PATH> <COURSE NAME>
```

Download with subtitles:

```
coursera-helper --cauth <CAUTH> --subtitle-language en,zh-CN|zh-TW <COURSE NAME>
```

Specify video resolution:

```
coursera-helper --cauth <CAUTH> --video-resolution 720p <COURSE NAME>
```

Download with quizzes:

```
coursera-helper --cauth <CAUTH> --download-quizzes <COURSE NAME>
```

Download with notebooks:

```
coursera-helper --cauth <CAUTH> --download-notebooks <COURSE NAME>
```

### Use configuration file

Alternatively, if you want to store your preferred parameters (which might also include your username and password), create a file named `coursera-dl.conf` where the script is executed, with the following format:

```
--username <user>
--password <pass>
--subtitle-language en,zh-CN|zh-TW
--download-quizzes
--download-notebooks
--video-resolution 720p
--download-delay 10
--cauth <cauth value>
```

If you have created a file named `coursera-dl.conf`, you can download a course with:

```
coursera-helper <COURSE NAME>
```

## Troubleshooting

### CAUTH

Find your Coursera CAUTH:

* Open and log in to https://www.coursera.org/
* Right-click and select *Inspect*.
* Go to Application/Storage > Cookies > https://www.coursera.org/ > CAUTH, then copy the CAUTH value.

**Chrome**:

1. Open the browser and log in to https://www.coursera.org/
2. Open DevTools:

   Windows or Linux: Press **F12** or **Ctrl** + **Shift** + **I**.

   Mac: Press **Fn** + **F12** or **Cmd** + **Option** + **I**.

3. Open **Application** > **Storage** > **Cookies** and select https://www.coursera.org/.
4. Find and copy the CAUTH value.

**Firefox**:

1. Open the browser and log in to https://www.coursera.org/
2. Open DevTools:

   Windows or Linux: Press **F12** or **Ctrl** + **Shift** + **I**.

   Mac: Press **Fn** + **F12** or **Cmd** + **Option** + **I**.

3. Open **Storage** > **Cookies** and select https://www.coursera.org/.
4. Find and copy the CAUTH value.

### china-issues

If you are in China and have problems downloading videos, add:

```
52.84.167.78   d3c33hcgiwev3.cloudfront.net
```

to your hosts file (`/etc/hosts` or `C:\Windows\System32\drivers\etc`).

Flush DNS with:

```
ipconfig /flushdns
```

## Reporting issues

Before reporting an issue:

1. Verify that you are running the latest version:

       pip install --upgrade coursera-helper

2. If the problem persists, please [open an issue](https://github.com/krazator/coursera-helper/issues) and include as much information as possible.

## Disclaimer

`coursera-helper` is meant to be used only for material that Coursera gives you permission to access and download. We do not encourage any use that violates Coursera's Terms of Use.
