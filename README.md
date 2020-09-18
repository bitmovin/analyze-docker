## Analyzing Docker images for optimal sizes

One of the last resorts to reduce the docker size is to review all the files in a Docker container. This is relatively labour intensive, therefore we have created a tool to aid in this task.

## Usage

This script will generate a CSV, which uses tabs as separators, called:
```sh
python DockerImageToCSV.py <image_id> output.csv
```

For more information, please refer to the blog post [Bitmovin’s Intern Series: 
Analyzing Docker images for optimal sizes](https://bitmovin.com/docker-images-layers/) where we describe how the script works.