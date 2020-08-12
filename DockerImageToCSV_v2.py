import json
import os
import sys
import tarfile
from DockerLayer import DockerLayer

def getDockerLayers(manifestJson, configJson):
    historyArr = configJson['history']
    layerPathArr = manifestJson[0]['Layers']

    configHistoryNotEmptyArr = [historyObject for historyObject in historyArr if not historyObject.get('empty_layer')]

    dockerLayerArr = [DockerLayer(layerPathArr[i], configHistoryNotEmptyArr[i]) for i in range(len(layerPathArr))]
    return dockerLayerArr

def toCSVLine(member, id, createdBy):
    return '\t'.join([member.name, str(member.size), id, createdBy.replace("\t", "")])

def searchForFiles(dockerLayer):
    layerContentTar = tarfile.open('/tmp/dockerimage' + imgId + '/' + dockerLayer.layerContentPath)
    layerId = dockerLayer.layerContentPath[:dockerLayer.layerContentPath.find('/')]
    return '\n'.join([toCSVLine(member, layerId, dockerLayer.createdBy) for member in layerContentTar.getmembers() if
                      not member.isdir()])

def createImageTarAndExtract(imgId):
    os.system('docker save -o /tmp/dockerimage' + imgId + '.tar ' + imgId)
    myTarfile = tarfile.open('/tmp/dockerimage' + imgId + '.tar')
    myTarfile.extractall('/tmp/dockerimage' + imgId)
    myTarfile.close()
    os.remove(myTarfile.name)

imgId = sys.argv[1]
outputFile = open(sys.argv[2], 'w')
createImageTarAndExtract(imgId)

manifestJsonFile = open('/tmp/dockerimage' + imgId + '/manifest.json')
parsedManifestJson = json.loads(manifestJsonFile.read())

configJsonFileName = parsedManifestJson[0]['Config']
configJsonFile = open('/tmp/dockerimage' + imgId + '/' + configJsonFileName)
parsedConfigJson = json.loads(configJsonFile.read())

dockerLayers = getDockerLayers(parsedManifestJson, parsedConfigJson)

outputFile.write('\n'.join([searchForFiles(dockerLayer) for dockerLayer in dockerLayers]))

outputFile.close()
