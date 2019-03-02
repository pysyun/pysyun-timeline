# Reduces the time-line to a set of unique values
class TextCorpus:

    def process(self, timeLine):
        result = []
        for i in range(len(timeLine)):
            value = timeLine[i]['value']
            result.extend(value)
        result = set(result)
        return result
