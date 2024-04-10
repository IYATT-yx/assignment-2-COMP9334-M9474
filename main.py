import sys
import simulation

def main():
    if len(sys.argv) < 2:
        print('python3 main.py [test_number]\nplease input test number!')
        exit(1)
    dispatcher = simulation.Dispatcher(int(sys.argv[1]))
    dispatcher.run()

if __name__ == '__main__':
    main()