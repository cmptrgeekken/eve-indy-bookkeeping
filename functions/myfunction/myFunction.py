
def lambda_handler(event, context):
    MyFunction().main()
    return "done"


class MyFunction:

    def main(self):
        pass
