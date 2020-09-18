class DockerLayer:

    def __init__(self, layerContentPath, configHistoryData):
        self.layerContentPath = layerContentPath
        self.created = configHistoryData['created']
        self.createdBy = configHistoryData['created_by']
