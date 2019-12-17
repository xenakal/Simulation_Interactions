#  Used if cameras are used (if agents, then use drawPredictions)
    def drawPredictionsOld(self, myRoom):
        for camera in myRoom.cameras:
            for target in myRoom.targets:
                camTargetsDetected = [x[0] for x in camera.targetDetectedList]
                if (target in camera.predictedPositions and target in camTargetsDetected):
                    self.drawTargetPrediction(target, camera.predictedPositions[target])

    def drawPredictions(self, myRoom):
        for agent in myRoom.agentCam:
            for target in myRoom.targets:
                pass
                #if (target in agent.memory.predictedPositions):
                    #self.drawTargetPrediction(target, agent.memory.predictedPositions[target])

    # predictionPos is a list with the N next predicted positions
    def drawTargetPrediction(self, target, predictionPos):
        predictedTarget = copy.deepcopy(target)
        predictionPos.insert(0, [predictedTarget.xc, predictedTarget.yc])
        pygame.draw.lines(self.screen, PREDICTION, False, predictionPos)