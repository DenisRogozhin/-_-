from src.bot import UDPipeBot
from src.udpipe import Model
from src.train_model import Classifier


if __name__ == '__main__':
    model = Model()
    classifier = Classifier()
    bot = UDPipeBot(model, classifier)
    bot.run()
