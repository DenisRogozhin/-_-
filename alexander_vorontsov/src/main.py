from src.bot import UDPipeBot
from src.udpipe import Model
from src.train_model import Classifier


if __name__ == '__main__':
    model = Model()
    classifier = Classifier()
    bot = UDPipeBot('6299008004:AAErm1ncfIqzwLzOm0zfoGVcNHG6LJAN8mE', model, classifier)
    bot.run()
