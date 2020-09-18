import json
import os
import shutil
import sys
import tarfile
import tempfile
from DockerLayer import DockerLayer


def _get_docker_layers(manifest_json, config_json):
    history_arr = config_json['history']
    layer_path_arr = manifest_json[0]['Layers']

    config_history_not_empty_arr = [historyObject for historyObject in history_arr if
                                    not historyObject.get('empty_layer')]

    docker_layer_arr = [DockerLayer(layer_path_arr[i], config_history_not_empty_arr[i]) for i in
                        range(len(layer_path_arr))]
    return docker_layer_arr


def _to_csv_line(member, layer_id, created_by):
    return '\t'.join([member.name, str(member.size), layer_id, created_by.replace("\t", "")])


def _search_for_files(docker_layer, img_id, tmp_dir):
    layer_content_tar = tarfile.open(tmp_dir.name + '/dockerimage' + img_id + '/' + docker_layer.layerContentPath)
    layer_id = docker_layer.layerContentPath[:docker_layer.layerContentPath.find('/')]
    return '\n'.join(
        [_to_csv_line(member, layer_id, docker_layer.createdBy) for member in layer_content_tar.getmembers() if
         not member.isdir()])


def _create_image_tar_and_extract(img_id, tmp_dir):
    os.system('docker save -o ' + tmp_dir.name + '/dockerimage' + img_id + '.tar ' + img_id)
    with tarfile.open(tmp_dir.name + '/dockerimage' + img_id + '.tar') as f:
        f.extractall(tmp_dir.name + '/dockerimage' + img_id)
    os.remove(f.name)


def main():
    img_id = sys.argv[1]
    tmp_dir = tempfile.TemporaryDirectory()
    try:
        _create_image_tar_and_extract(img_id, tmp_dir)

        with open(tmp_dir.name + '/dockerimage' + img_id + '/manifest.json') as manifest_json_file:
            parsed_manifest_json = json.loads(manifest_json_file.read())

        config_json_file_name = parsed_manifest_json[0]['Config']
        with open(tmp_dir.name + '/dockerimage' + img_id + '/' + config_json_file_name) as config_json_file:
            parsed_config_json = json.loads(config_json_file.read())

        docker_layers = _get_docker_layers(parsed_manifest_json, parsed_config_json)

        with open(sys.argv[2], 'w') as outputFile:
            outputFile.write(
                '\n'.join([_search_for_files(dockerLayer, img_id, tmp_dir) for dockerLayer in docker_layers]))
    finally:
        if tmp_dir is not None:
            shutil.rmtree(tmp_dir.name, ignore_errors=True)


if __name__ == "__main__":
    main()
