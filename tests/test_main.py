
from ccli.main import ccliTest

def test_ccli(tmp):
    with ccliTest() as app:
        res = app.run()
        print(res)
        raise Exception

def test_command1(tmp):
    argv = ['command1']
    with ccliTest(argv=argv) as app:
        app.run()
