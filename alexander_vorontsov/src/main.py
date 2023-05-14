from bot import UDPipeBot
from udpipe import Model
from train_model import Classifier


if __name__ == '__main__':
    model = Model()
    classifier = Classifier()
    bot = UDPipeBot('6299008004:AAErm1ncfIqzwLzOm0zfoGVcNHG6LJAN8mE', model, classifier)
    bot.run()
